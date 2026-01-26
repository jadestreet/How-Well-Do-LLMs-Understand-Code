import argparse
import json
import re
from collections import defaultdict
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
# ---------- Regex for CFG dump ----------
RE_ENTRY = re.compile(r"^\s*\[B(\d+)\s*\(ENTRY\)\]\s*$")
RE_BLOCK = re.compile(r"^\s*\[B(\d+)\s*(?:\((ENTRY|EXIT)\))?\]\s*$")
RE_PREDS = re.compile(r"^\s*Preds\s*\(\d+\):\s*(.*)\s*$")
RE_STMT  = re.compile(r"^\s*\d+:\s*(.*)\s*$")

# ---------- Regex for DumpLiveVars ----------
RE_LIVE_HDR = re.compile(r"^\s*\[\s*B(\d+)\s*\(live variables at block exit\)\s*\]\s*$")
RE_LIVE_VAR = re.compile(r"^\s*([A-Za-z_]\w*)\s*<.*?>\s*$")

# ---------- Helpers ----------
RE_RETURN = re.compile(r"\breturn\b")
RE_IDENT_ONLY = re.compile(r"^\s*([A-Za-z_]\w*)\s*$")

TYPE_KEYWORDS = {
    "int","double","float","char","void","long","short","unsigned","signed",
    "struct","union","enum","const","volatile","static","inline","extern",
    "register","auto","typedef","_Bool","bool","size_t"
}
CONTROL_KEYWORDS = {
    "for","while","if","else","switch","case","break","continue","return",
    "do","default","goto"
}

def extract_func_name_from_header(header_line: str):
    """
    Function header line is immediately before [B# (ENTRY)] in DumpCFG output.
    """
    if "(" not in header_line:
        return None
    prefix = header_line.split("(", 1)[0]
    idents = re.findall(r"\b([A-Za-z_]\w*)\b", prefix)
    return idents[-1] if idents else None

def split_sections_by_entry(lines):
    """
    Split whole dump into per-function sections
    """
    starts = []
    for i, line in enumerate(lines):
        m = RE_ENTRY.match(line)
        if not m:
            continue
        # previous non-empty line is the function header
        j = i - 1
        while j >= 0 and lines[j].strip() == "":
            j -= 1
        if j < 0:
            continue
        header = lines[j].strip()
        fname = extract_func_name_from_header(header)
        if fname:
            starts.append((fname, j))

    sections = []
    for k, (fname, start) in enumerate(starts):
        end = starts[k + 1][1] if k + 1 < len(starts) else len(lines)
        sections.append((fname, start, end))
    return sections

def parse_function_section(sec_lines):
    """
    Parse CFG blocks + live-vars per block inside one function section.
    """
    blocks = defaultdict(lambda: {"kind": None, "preds": [], "stmts": []})
    live_at_exit = defaultdict(set)
    exit_block = None

    cur_block = None
    in_live = False
    cur_live_block = None

    for line in sec_lines:
        # live-vars header
        mh = RE_LIVE_HDR.match(line)
        if mh:
            in_live = True
            cur_live_block = int(mh.group(1))
            continue

        if in_live:
            mv = RE_LIVE_VAR.match(line)
            if mv:
                live_at_exit[cur_live_block].add(mv.group(1))
                continue
            # end live list on blank line or next header-ish
            if line.strip() == "" or RE_LIVE_HDR.match(line) or RE_BLOCK.match(line):
                in_live = False
                cur_live_block = None
            continue

        # CFG block header
        mb = RE_BLOCK.match(line)
        if mb:
            cur_block = int(mb.group(1))
            kind = mb.group(2)
            if kind:
                blocks[cur_block]["kind"] = kind
                if kind == "EXIT":
                    exit_block = cur_block
            continue

        if cur_block is None:
            continue

        mp = RE_PREDS.match(line)
        if mp:
            raw = mp.group(1).strip()
            preds = [int(x[1:]) for x in raw.split() if x.startswith("B") and x[1:].isdigit()]
            blocks[cur_block]["preds"] = preds
            continue

        ms = RE_STMT.match(line)
        if ms:
            blocks[cur_block]["stmts"].append(ms.group(1).strip())
            continue

    return blocks, live_at_exit, exit_block

def return_vars_patch(stmts):
    """
    Minimal return patch tailored to DumpCFG format
    """
    used = set()
    for idx, s in enumerate(stmts):
        if RE_RETURN.search(s):
            for prev in stmts[:idx]:
                m = RE_IDENT_ONLY.match(prev)
                if m:
                    v = m.group(1)
                    if v not in TYPE_KEYWORDS and v not in CONTROL_KEYWORDS:
                        used.add(v)
    return used

def compute_liveout(blocks, live_at_exit, exit_block):
    entry_block = None
    for bid, b in blocks.items():
        if b.get("kind") == "ENTRY":
            entry_block = bid
            break

    base = set()
    if entry_block is not None:
        base = set(live_at_exit.get(entry_block, set()))

    ret_vars = set()
    for bid, b in blocks.items():
        stmts = b["stmts"]
        if any(RE_RETURN.search(x) for x in stmts):
            raw = return_vars_patch(stmts)

            funcs_in_block = set()
            for idx, s in enumerate(stmts):
                m = RE_IDENT_ONLY.match(s)
                if m:
                    ident = m.group(1)

                    look = " ".join(stmts[idx:idx+4])
                    if "FunctionToPointerDecay" in look:
                        funcs_in_block.add(ident)

            raw = {v for v in raw if v not in funcs_in_block}
            ret_vars |= raw

    liveout_set = base | ret_vars

    universe = set(ret_vars)
    universe |= set(base)  # include base vars
    for vs in live_at_exit.values():
        universe |= set(vs)

    return {
        "entry_block": entry_block,
        "exit_block": exit_block,
        "base_liveout": sorted(base),
        "return_vars": sorted(ret_vars),
        "liveout": {v: (v in liveout_set) for v in sorted(universe)},
    }

def main(default_cfg_dir, default_out_dir) -> int:

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--in-dir",
        default=default_cfg_dir,
        help="Directory containing analyzer dump text files",
    )
    ap.add_argument(
        "--out-dir",
        default=default_out_dir,
        help="Directory to write parsed JSON files",
    )
    ap.add_argument(
        "--jobs",
        type=int,
        default=18,
        help="Thread workers",
    )
    ap.add_argument(
        "--ext",
        default="",
        help="Optional: only process files with this extension (e.g., .txt). Default: all files.",
    )
    args = ap.parse_args()

    in_dir = Path(args.in_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_dir.is_dir():
        raise SystemExit(f"ERROR: input directory not found: {in_dir}")

    # Collect input files
    if args.ext:
        in_files = sorted([p for p in in_dir.rglob(f"*{args.ext}") if p.is_file()])
    else:
        in_files = sorted([p for p in in_dir.rglob("*") if p.is_file()])

    empty_files = []

    def process_one(in_path: Path):
        # Output file name EXACTLY the same as input file name, in out_dir
        out_path = (out_dir / in_path.name).with_suffix(".json")
        #out_dir / in_path.name

        # Report empty files
        try:
            if in_path.stat().st_size == 0:
                return (in_path, out_path, "EMPTY")
        except Exception as e:
            return (in_path, out_path, f"STAT_ERROR: {e}")

        with in_path.open("r", encoding="utf-8", errors="replace") as f:
            text = f.read()

        if text.strip() == "":
            return (in_path, out_path, "EMPTY")

        lines = text.splitlines()
        sections = split_sections_by_entry(lines)

        results = {"file": "", "functions": {}}

        for fname, start, end in sections:
            sec_lines = lines[start:end]
            blocks, live_at_exit, exit_block = parse_function_section(sec_lines)
            results["functions"][fname] = compute_liveout(blocks, live_at_exit, exit_block)

        with out_path.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
            f.write("\n")

        return (in_path, out_path, "OK")

    # Multi-threaded execution
    failures = []
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        futs = [ex.submit(process_one, p) for p in in_files]
        for fut in as_completed(futs):
            in_path, out_path, status = fut.result()
            if status == "EMPTY":
                empty_files.append(str(in_path))
            elif status != "OK":
                failures.append((str(in_path), str(out_path), status))

    # Only report empty file names (and any failures, if you want visibility)
    if empty_files:
        for p in sorted(empty_files):
            print(f"[EMPTY] {p}")

    if failures:
        for in_p, out_p, status in sorted(failures):
            print(f"[FAIL] {in_p}")
            print(f"       out: {out_p}")
            print(f"       err: {status}")


if __name__ == "__main__":
    CUR_dir = Path(__file__).parent.resolve()
    default_cfg_dir = CUR_dir / "data/loop3_1000/CFG"    
    default_out_dir = CUR_dir / "data/loop3_1000/CFG_liveness_parsed"
    main(default_cfg_dir, default_out_dir)
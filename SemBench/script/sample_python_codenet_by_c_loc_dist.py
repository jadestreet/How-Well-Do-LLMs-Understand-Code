#!/usr/bin/env python3
import argparse
import ast
import csv
import random
import shutil
from pathlib import Path
from collections import Counter, defaultdict


DEFAULT_CSV = (
    ""
    "SemBench/data/python/codenet_python/codenet_python800_file_stats.csv"
)

DEFAULT_OUT_DIR = (
    ""
    "SemBench/data/python_codenet/code"
)

DEFAULT_MANIFEST = (
    ""
    "SemBench/data/python_codenet/selected_python_codenet_manifest.csv"
)

# Reference C SemBench LOC distribution over 1000 files.
REFERENCE_COUNTS = {
    "<= 50": 515,
    "51-100": 295,
    "101-200": 129,
    "201-500": 44,
    "501-1000": 6,
    "1001-2000": 7,
    "> 2000": 4,
}


def loc_bin(code_lines: int) -> str:
    if code_lines <= 50:
        return "<= 50"
    if code_lines <= 100:
        return "51-100"
    if code_lines <= 200:
        return "101-200"
    if code_lines <= 500:
        return "201-500"
    if code_lines <= 1000:
        return "501-1000"
    if code_lines <= 2000:
        return "1001-2000"
    return "> 2000"


def scaled_target_counts(num_files: int) -> dict:
    """
    Scale the original 1000-file C LOC distribution to any requested sample size.
    Uses largest-remainder rounding so the final total is exactly num_files.
    """
    if num_files <= 0:
        raise ValueError("--num-files must be positive")

    total_ref = sum(REFERENCE_COUNTS.values())

    raw = {
        bin_name: num_files * count / total_ref
        for bin_name, count in REFERENCE_COUNTS.items()
    }

    target = {
        bin_name: int(value)
        for bin_name, value in raw.items()
    }

    remaining = num_files - sum(target.values())

    remainders = sorted(
        raw.items(),
        key=lambda kv: kv[1] - int(kv[1]),
        reverse=True,
    )

    for bin_name, _ in remainders[:remaining]:
        target[bin_name] += 1

    return target


def has_for_loop(path: Path) -> bool:
    """
    The existing CSV has loop_count but not for-loop count.
    The requirement is specifically at least one for-loop, so verify with AST.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text, filename=str(path))
    except Exception:
        return False

    return any(isinstance(node, (ast.For, ast.AsyncFor)) for node in ast.walk(tree))


def parse_bool(x) -> bool:
    return str(x).strip().lower() in {"true", "1", "yes", "y"}


def read_candidates(csv_path: Path, require_for_loop: bool = True):
    candidates = []

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            path_str = row.get("path", "").strip()
            if not path_str:
                continue

            path = Path(path_str)

            # 1. no error files
            if not parse_bool(row.get("syntax_ok", "")):
                continue
            if row.get("error", "").strip():
                continue
            if not path.exists():
                continue

            try:
                code_lines = int(float(row["code_lines"]))
                function_count = int(float(row["function_count"]))
            except Exception:
                continue

            # 3. at least 1 function
            if function_count < 1:
                continue

            # 2. contains at least 1 for-loop
            if require_for_loop and not has_for_loop(path):
                continue

            row = dict(row)
            row["code_lines"] = code_lines
            row["function_count"] = function_count
            row["loc_bin"] = loc_bin(code_lines)
            candidates.append(row)

    return candidates


def safe_output_name(row, used_names):
    problem_id = row.get("problem_id", "").strip() or "unknown_problem"
    file_name = row.get("file_name", "").strip() or Path(row["path"]).name

    stem = Path(file_name).stem
    suffix = Path(file_name).suffix or ".py"

    base = f"{problem_id}_{stem}{suffix}"
    base = base.replace("/", "_").replace(" ", "_")

    if base not in used_names:
        used_names.add(base)
        return base

    i = 2
    while True:
        candidate = f"{problem_id}_{stem}_{i}{suffix}"
        candidate = candidate.replace("/", "_").replace(" ", "_")
        if candidate not in used_names:
            used_names.add(candidate)
            return candidate
        i += 1


def sample_exact_distribution(candidates, target_counts, seed: int):
    rng = random.Random(seed)

    by_bin = defaultdict(list)
    for row in candidates:
        by_bin[row["loc_bin"]].append(row)

    selected = []
    shortage = {}

    for bin_name, need in target_counts.items():
        pool = by_bin[bin_name]
        rng.shuffle(pool)

        if len(pool) < need:
            shortage[bin_name] = {
                "need": need,
                "available": len(pool),
                "missing": need - len(pool),
            }
            selected.extend(pool)
        else:
            selected.extend(pool[:need])

    return selected, shortage, by_bin


def copy_selected(selected, out_dir: Path, clean: bool):
    out_dir.mkdir(parents=True, exist_ok=True)

    if clean:
        for p in out_dir.glob("*.py"):
            p.unlink()

    used_names = set()
    copied = []

    for row in selected:
        src = Path(row["path"])
        out_name = safe_output_name(row, used_names)
        dst = out_dir / out_name

        shutil.copyfile(src, dst)

        copied_row = dict(row)
        copied_row["copied_file_name"] = out_name
        copied_row["copied_path"] = str(dst)
        copied.append(copied_row)

    return copied


def write_manifest(rows, manifest_path: Path):
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        return

    preferred_fieldnames = [
        "copied_file_name",
        "copied_path",
        "problem_id",
        "file_name",
        "relative_path",
        "path",
        "code_lines",
        "loc_bin",
        "function_count",
        "top_level_function_count",
        "nested_function_count",
        "class_count",
        "method_count",
        "loop_count",
        "if_count",
        "return_count",
        "assign_count",
        "call_count",
        "max_ast_depth",
        "file_size_bytes",
        "syntax_ok",
        "error",
    ]

    all_fields = set()
    for r in rows:
        all_fields.update(r.keys())

    extra_fields = sorted(all_fields - set(preferred_fieldnames))
    fieldnames = preferred_fieldnames + extra_fields

    with manifest_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def print_summary(candidates, selected, shortage, target_counts):
    candidate_counts = Counter(r["loc_bin"] for r in candidates)
    selected_counts = Counter(r["loc_bin"] for r in selected)

    print("\n========== Candidate Summary ==========")
    print(f"Total valid candidates: {len(candidates)}")
    print("Criteria:")
    print("  syntax_ok == True")
    print("  error is empty")
    print("  function_count >= 1")
    print("  contains at least one ast.For / ast.AsyncFor")

    print("\nCandidates by LOC bin:")
    for bin_name in target_counts:
        print(f"  {bin_name:>10}: {candidate_counts[bin_name]}")

    print("\n========== Target Distribution ==========")
    print(f"Requested total files: {sum(target_counts.values())}")
    for bin_name, count in target_counts.items():
        pct = 100.0 * count / sum(target_counts.values())
        print(f"  {bin_name:>10}: {count:4d} ({pct:5.2f}%)")

    print("\n========== Selected Summary ==========")
    print(f"Total selected: {len(selected)}")
    print("Selected by LOC bin:")
    for bin_name in target_counts:
        target = target_counts[bin_name]
        actual = selected_counts[bin_name]
        print(f"  {bin_name:>10}: {actual} / target {target}")

    if shortage:
        print("\nWARNING: Some bins do not have enough candidates.")
        for bin_name, info in shortage.items():
            print(
                f"  {bin_name}: need={info['need']}, "
                f"available={info['available']}, missing={info['missing']}"
            )
    else:
        print("\nExact target distribution satisfied.")

    print("=======================================\n")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Sample CodeNet Python programs to match the C SemBench LOC "
            "distribution, with selectable sample size."
        )
    )
    parser.add_argument(
        "--csv",
        default=DEFAULT_CSV,
        help="Input file statistics CSV.",
    )
    parser.add_argument(
        "--out-dir",
        default=DEFAULT_OUT_DIR,
        help="Folder to copy selected .py files into.",
    )
    parser.add_argument(
        "--manifest",
        default=DEFAULT_MANIFEST,
        help="Output manifest CSV for selected files.",
    )
    parser.add_argument(
        "--num-files",
        type=int,
        default=1000,
        help="Number of files to sample while matching the C LOC distribution.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible sampling.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove existing .py files in output dir before copying selected files.",
    )
    parser.add_argument(
        "--allow-shortage",
        action="store_true",
        help=(
            "If a LOC bin has fewer candidates than target, still copy available "
            "candidates."
        ),
    )
    parser.add_argument(
        "--no-require-for-loop",
        action="store_true",
        help=(
            "Disable the requirement that each selected file must contain at least "
            "one ast.For / ast.AsyncFor."
        ),
    )

    args = parser.parse_args()

    csv_path = Path(args.csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    manifest_path = Path(args.manifest).resolve()

    if not csv_path.exists():
        raise SystemExit(f"ERROR: CSV file does not exist: {csv_path}")

    target_counts = scaled_target_counts(args.num_files)

    candidates = read_candidates(
        csv_path,
        require_for_loop=not args.no_require_for_loop,
    )

    selected, shortage, _ = sample_exact_distribution(
        candidates,
        target_counts,
        args.seed,
    )

    print_summary(candidates, selected, shortage, target_counts)

    if shortage and not args.allow_shortage:
        raise SystemExit(
            "ERROR: Not enough candidates in some LOC bins. "
            "Use --allow-shortage to copy available candidates anyway."
        )

    copied = copy_selected(selected, out_dir, clean=args.clean)
    write_manifest(copied, manifest_path)

    print(f"Copied {len(copied)} files to: {out_dir}")
    print(f"Saved selected manifest to: {manifest_path}")


if __name__ == "__main__":
    main()

'''
cd <repo-root>

python SemBench/script/sample_python_codenet_by_c_loc_dist.py \
  --csv SemBench/data/python/codenet_python/codenet_python800_file_stats.csv \
  --out-dir SemBench/data/python_codenet/code \
  --manifest SemBench/data/python_codenet/selected_python_codenet_manifest.csv \
  --num-files 1000 \
  --seed 42 \
  --allow-shortage
  #--clean

'''

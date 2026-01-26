import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Tuple, Optional
'''
python3 generate_CFGs.py
'''
CUR_dir = Path(__file__).parent.resolve()
CODE_ROOT_DEFAULT = CUR_dir / "data/loop3_1000/code/"
OUT_DIR_DEFAULT = CUR_dir / "data/loop3_1000/CFG"
os.makedirs(OUT_DIR_DEFAULT, exist_ok=True)

# Common system include locations on many Linux distros. Adjust if your env is different.
DEFAULT_INCLUDE_DIRS = [
    "/usr/include",
    "/usr/include/x86_64-linux-gnu",
]


def find_c_files(root: Path) -> List[Path]:
    return sorted(p for p in root.rglob("*.c") if p.is_file())


def build_clang_cmd(
    clang_bin: str,
    c_file: Path,
    include_dirs: List[str],
) -> List[str]:
    cmd = [
        clang_bin,
        "--analyze",
        "-Xclang",
        "-analyzer-checker=debug.DumpCFG",
        "-Xclang",
        "-analyzer-checker=debug.DumpLiveVars",
    ]
    for inc in include_dirs:
        # Use -isystem to treat them as system headers (reduces warnings/noise)
        cmd.extend(["-isystem", inc])
    cmd.append(str(c_file))
    return cmd


def run_one(
    clang_bin: str,
    c_file: Path,
    out_dir: Path,
    include_dirs: List[str],
    timeout_sec: int,
) -> Tuple[Path, bool, Optional[str]]:
    """
    Returns: (c_file, ok, err_summary)
    Writes: <out_dir>/<same_relative_path>/<stem>.txt
    """
    rel = c_file.relative_to(out_dir.parents[0]) if False else None  # placeholder, not used

    return (c_file, False, "Internal error: run_one() called without prepared paths")


def run_one_prepared(
    clang_bin: str,
    c_file: Path,
    rel_path: Path,
    out_path: Path,
    include_dirs: List[str],
    timeout_sec: int,
) -> Tuple[Path, bool, Optional[str]]:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = build_clang_cmd(clang_bin, c_file, include_dirs)

    try:
        # Redirect stderr to the per-file output log (same spirit as `2> analyzer_dump.txt`)
        with out_path.open("wb") as f:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,  # keep logs cleaner; analyzer dumps go to stderr
                stderr=f,
                timeout=timeout_sec,
                check=False,
            )
        if proc.returncode == 0:
            return (c_file, True, None)

        # If failure, include a short, actionable summary (first non-empty lines)
        summary = extract_error_summary(out_path, max_lines=6)
        return (c_file, False, summary)

    except subprocess.TimeoutExpired:
        # Ensure something is recorded for postmortem
        try:
            with out_path.open("ab") as f:
                f.write(b"\n[TIMEOUT] clang analyze exceeded timeout.\n")
        except Exception:
            pass
        return (c_file, False, f"TIMEOUT > {timeout_sec}s")

    except FileNotFoundError:
        return (c_file, False, f"clang not found: {clang_bin}")

    except Exception as e:
        try:
            with out_path.open("ab") as f:
                f.write(f"\n[EXCEPTION] {type(e).__name__}: {e}\n".encode("utf-8", "replace"))
        except Exception:
            pass
        return (c_file, False, f"EXCEPTION {type(e).__name__}: {e}")


def extract_error_summary(log_path: Path, max_lines: int = 6) -> str:
    try:
        lines = []
        with log_path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue
                lines.append(s)
                if len(lines) >= max_lines:
                    break
        return " | ".join(lines) if lines else "Non-zero exit, empty stderr."
    except Exception as e:
        return f"Non-zero exit, and failed to read log: {e}"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Run clang static analyzer DumpCFG+DumpLiveVars on all .c files and log per-file stderr."
    )
    ap.add_argument("--code-root", default=CODE_ROOT_DEFAULT, help="Root directory containing .c files")
    ap.add_argument("--out-dir", default=OUT_DIR_DEFAULT, help="Directory to write logs. Default: <code-root>/_analyzer_dump")
    ap.add_argument("--clang", default="clang", help="clang executable (e.g., clang-17)")
    ap.add_argument("--jobs", type=int, default=18, help="Parallel workers")
    ap.add_argument("--timeout", type=int, default=120, help="Timeout seconds per file")
    ap.add_argument(
        "--include",
        action="append",
        default=[],
        help="Extra include dir (repeatable). Added after default includes.",
    )
    ap.add_argument(
        "--no-default-includes",
        action="store_true",
        help="Disable default include dirs; only use --include entries",
    )
    args = ap.parse_args()

    code_root = Path(args.code_root).resolve()
    if not code_root.is_dir():
        print(f"ERROR: code root not found: {code_root}", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir).resolve() if args.out_dir else (code_root / "_analyzer_dump")
    out_dir.mkdir(parents=True, exist_ok=True)

    include_dirs = []
    if not args.no_default_includes:
        include_dirs.extend(DEFAULT_INCLUDE_DIRS)
    include_dirs.extend(args.include)

    c_files = find_c_files(code_root)
    if not c_files:
        print(f"No .c files found under: {code_root}", file=sys.stderr)
        return 0


    tasks = []
    failures: List[Tuple[Path, Path, str]] = []

    def make_out_path(c_file: Path) -> Tuple[Path, Path]:
        rel = c_file.relative_to(code_root)
        out_path = out_dir / rel
        out_path = out_path.with_suffix(".txt")
        return rel, out_path

    with ThreadPoolExecutor(max_workers=max(18, args.jobs)) as ex:
        for c_file in c_files:
            _, out_path = make_out_path(c_file)
            tasks.append(
                ex.submit(
                    run_one_prepared,
                    args.clang,
                    c_file,
                    c_file.relative_to(code_root),
                    out_path,
                    include_dirs,
                    args.timeout,
                )
            )

        for fut in as_completed(tasks):
            c_file, ok, summary = fut.result()
            if not ok:
                _, out_path = make_out_path(c_file)
                failures.append((c_file, out_path, summary or "Unknown error"))

    # only report errors for files not able to solve
    if failures:
        # Print a clean error-only report
        for c_file, out_path, summary in sorted(failures, key=lambda x: str(x[0])):
            print(f"[FAIL] {c_file}")
            print(f"       log: {out_path}")
            print(f"       err: {summary}")

        # Also write a machine-readable summary
        err_tsv = out_dir / "errors.tsv"
        with err_tsv.open("w", encoding="utf-8") as f:
            f.write("c_file\tlog_file\tsummary\n")
            for c_file, out_path, summary in sorted(failures, key=lambda x: str(x[0])):
                f.write(f"{c_file}\t{out_path}\t{summary}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

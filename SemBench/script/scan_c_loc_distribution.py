#!/usr/bin/env python3

from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import OrderedDict
import argparse
import csv
import json
import os
import statistics


DEFAULT_ROOT = "SemBench/data/loop3_1000/code"


def strip_c_comments(text: str) -> str:
    """
    Strip // and /* */ comments from C code while preserving newlines.
    This avoids counting comment-only lines as SLOC.
    It handles string and char literals reasonably safely.
    """
    out = []
    i = 0
    n = len(text)

    state = "normal"
    escape = False

    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""

        if state == "normal":
            if ch == "/" and nxt == "/":
                state = "line_comment"
                i += 2
                continue
            elif ch == "/" and nxt == "*":
                state = "block_comment"
                i += 2
                continue
            elif ch == '"':
                state = "string"
                out.append(ch)
            elif ch == "'":
                state = "char"
                out.append(ch)
            else:
                out.append(ch)

        elif state == "line_comment":
            if ch == "\n":
                out.append("\n")
                state = "normal"

        elif state == "block_comment":
            if ch == "\n":
                out.append("\n")
            elif ch == "*" and nxt == "/":
                state = "normal"
                i += 2
                continue

        elif state == "string":
            out.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                state = "normal"

        elif state == "char":
            out.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == "'":
                state = "normal"

        i += 1

    return "".join(out)


def count_file_loc(path_str: str) -> dict:
    path = Path(path_str)

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {
            "path": str(path),
            "ok": False,
            "error": repr(e),
            "total_lines": 0,
            "nonblank_lines": 0,
            "sloc": 0,
        }

    total_lines = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
    nonblank_lines = sum(1 for line in text.splitlines() if line.strip())

    no_comments = strip_c_comments(text)
    sloc = sum(1 for line in no_comments.splitlines() if line.strip())

    return {
        "path": str(path),
        "ok": True,
        "error": "",
        "total_lines": total_lines,
        "nonblank_lines": nonblank_lines,
        "sloc": sloc,
    }


def make_bins(values, boundaries):
    """
    Example boundaries: [50, 100, 200, 500, 1000, 2000]
    Produces:
      <=50
      51-100
      101-200
      201-500
      501-1000
      1001-2000
      >2000
    """
    labels = []

    for i, upper in enumerate(boundaries):
        if i == 0:
            labels.append(f"<= {upper}")
        else:
            labels.append(f"{boundaries[i - 1] + 1}-{upper}")

    labels.append(f"> {boundaries[-1]}")

    counts = OrderedDict((label, 0) for label in labels)

    for v in values:
        placed = False
        for i, upper in enumerate(boundaries):
            if v <= upper:
                counts[labels[i]] += 1
                placed = True
                break
        if not placed:
            counts[labels[-1]] += 1

    total = len(values)
    rows = []
    for label, count in counts.items():
        pct = (count / total * 100.0) if total else 0.0
        rows.append({
            "scale": label,
            "file_count": count,
            "percentage": pct,
        })

    return rows


def percentile(values, p):
    if not values:
        return 0
    values = sorted(values)
    k = (len(values) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(values) - 1)
    if f == c:
        return values[f]
    return values[f] + (values[c] - values[f]) * (k - f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        default=DEFAULT_ROOT,
        help="Root folder containing C files.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=max(1, os.cpu_count() or 1),
        help="Number of parallel workers.",
    )
    parser.add_argument(
        "--metric",
        choices=["total_lines", "nonblank_lines", "sloc"],
        default="sloc",
        help="Metric used for final distribution. Default: sloc = nonblank non-comment lines.",
    )
    parser.add_argument(
        "--bins",
        default="50,100,200,500,1000,2000",
        help="Comma-separated LOC scale boundaries.",
    )
    parser.add_argument(
        "--out-prefix",
        default="c_loc_distribution",
        help="Output prefix for CSV/JSON files.",
    )
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    boundaries = [int(x.strip()) for x in args.bins.split(",") if x.strip()]
    boundaries = sorted(set(boundaries))

    if not root.exists():
        raise FileNotFoundError(f"Root folder does not exist: {root}")

    c_files = sorted(str(p) for p in root.rglob("*.c"))

    print(f"Root: {root}")
    print(f"Found .c files: {len(c_files)}")
    print(f"Workers: {args.workers}")
    print(f"Distribution metric: {args.metric}")
    print()

    results = []

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(count_file_loc, p) for p in c_files]

        for idx, fut in enumerate(as_completed(futures), 1):
            results.append(fut.result())
            if idx % 500 == 0:
                print(f"Processed {idx}/{len(c_files)} files...")

    ok_results = [r for r in results if r["ok"]]
    failed_results = [r for r in results if not r["ok"]]

    values = [r[args.metric] for r in ok_results]
    distribution = make_bins(values, boundaries)

    per_file_csv = f"{args.out_prefix}_per_file.csv"
    distribution_csv = f"{args.out_prefix}_summary.csv"
    distribution_json = f"{args.out_prefix}_summary.json"

    with open(per_file_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "path",
                "ok",
                "error",
                "total_lines",
                "nonblank_lines",
                "sloc",
            ],
        )
        writer.writeheader()
        writer.writerows(sorted(results, key=lambda x: x["path"]))

    with open(distribution_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["scale", "file_count", "percentage"],
        )
        writer.writeheader()
        writer.writerows(distribution)

    summary = {
        "root": str(root),
        "num_c_files": len(c_files),
        "num_success": len(ok_results),
        "num_failed": len(failed_results),
        "metric": args.metric,
        "bins": boundaries,
        "distribution": distribution,
        "statistics": {
            "min": min(values) if values else 0,
            "p25": percentile(values, 25),
            "median": statistics.median(values) if values else 0,
            "mean": statistics.mean(values) if values else 0,
            "p75": percentile(values, 75),
            "p90": percentile(values, 90),
            "p95": percentile(values, 95),
            "max": max(values) if values else 0,
        },
        "failed_files": failed_results,
    }

    with open(distribution_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\nFinal LOC Distribution")
    print("----------------------")
    print(f"Metric: {args.metric}")
    print(f"Successful files: {len(ok_results)}")
    print(f"Failed files: {len(failed_results)}")
    print()

    for row in distribution:
        print(
            f"{row['scale']:>12} : "
            f"{row['file_count']:>6} files "
            f"({row['percentage']:6.2f}%)"
        )

    print("\nStatistics")
    print("----------")
    for k, v in summary["statistics"].items():
        if isinstance(v, float):
            print(f"{k:>8}: {v:.2f}")
        else:
            print(f"{k:>8}: {v}")

    print("\nSaved files")
    print("-----------")
    print(per_file_csv)
    print(distribution_csv)
    print(distribution_json)


if __name__ == "__main__":
    main()
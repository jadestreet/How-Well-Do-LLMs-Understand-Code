#!/usr/bin/env python3
from __future__ import annotations

import argparse
import filecmp
import json
import math
import os
import re
import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd


LOC_ORDER = ["<= 50", "51-100", "101-200", "201-500", "501-1000", "1001-2000", "> 2000"]

TARGET_PCT = {
    "<= 50": 51.5,
    "51-100": 29.5,
    "101-200": 12.9,
    "201-500": 4.4,
    "501-1000": 0.6,
    "1001-2000": 0.7,
    "> 2000": 0.4,
}

DIVERSITY_NUMERIC_COLS = [
    "code_lines",
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
    "blank_lines",
    "comment_lines",
    "total_lines",
]


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


def parse_status_log(status_log: Path) -> Dict[str, str]:
    """Return {python_filename: parsed/incomplete} from parser stdout log."""
    status_by_file: Dict[str, str] = {}

    for raw in status_log.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue

        # Supports:
        #   parsed: /path/to/file.py
        #   incomplete: /path/to/file.py
        #   incomplete: /path/to/file.py: SyntaxError...
        match = re.match(r"^(parsed|incomplete):\s+(.+?\.py)(?:\s*:.*)?$", line)
        if not match:
            continue

        status, file_path = match.groups()
        status_by_file[Path(file_path).name] = status

    return status_by_file


def largest_remainder_counts(weights: Dict[str, float], total: int) -> Dict[str, int]:
    raw = {key: value * total / sum(weights.values()) for key, value in weights.items()}
    counts = {key: int(math.floor(value)) for key, value in raw.items()}

    missing = total - sum(counts.values())
    fractions = sorted(((raw[key] - counts[key], key) for key in raw), reverse=True)

    for _, key in fractions[:missing]:
        counts[key] += 1

    return counts


def diverse_select(
    pool: pd.DataFrame,
    k: int,
    *,
    seed: int,
    used_problem_ids: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """Greedy max-min diversity selection over normalized metadata features.

    The selection is still deterministic under the same seed. It prioritizes:
      1. attribute-space diversity,
      2. new problem IDs,
      3. slightly more complex files within each LOC bucket.
    """
    if k <= 0:
        return pool.iloc[[]].copy()
    if len(pool) <= k:
        return pool.copy()

    used_problem_ids = set(used_problem_ids or [])
    rng = np.random.default_rng(seed)

    df = pool.reset_index(drop=False).copy()
    numeric_cols = [col for col in DIVERSITY_NUMERIC_COLS if col in df.columns]
    if not numeric_cols:
        return df.sample(n=k, random_state=seed).set_index("index").loc[:, pool.columns].copy()

    features = df[numeric_cols].astype(float).to_numpy()
    mins = np.nanmin(features, axis=0)
    maxs = np.nanmax(features, axis=0)
    denom = np.where(maxs > mins, maxs - mins, 1.0)
    features = np.nan_to_num((features - mins) / denom)

    def col_idx(name: str, fallback: int = 0) -> int:
        return numeric_cols.index(name) if name in numeric_cols else fallback

    code_idx = col_idx("code_lines")
    loop_idx = col_idx("loop_count")
    func_idx = col_idx("function_count")
    call_idx = col_idx("call_count")

    complexity = (
        0.45 * features[:, code_idx]
        + 0.20 * features[:, loop_idx]
        + 0.20 * features[:, func_idx]
        + 0.15 * features[:, call_idx]
    )

    selected: List[int] = []
    remaining = np.arange(len(df))

    # Start from a complex file, then spread out in feature space.
    first = int(np.argmax(complexity + rng.random(len(df)) * 1e-9))
    selected.append(first)
    remaining = remaining[remaining != first]

    local_used_problem_ids = set()
    if "problem_id" in df.columns:
        local_used_problem_ids.add(df.loc[first, "problem_id"])

    while len(selected) < k:
        selected_features = features[selected]
        remaining_features = features[remaining]

        min_dist = np.sqrt(
            ((remaining_features[:, None, :] - selected_features[None, :, :]) ** 2).sum(axis=2)
        ).min(axis=1)

        if "problem_id" in df.columns:
            new_problem_bonus = np.array(
                [
                    1.0
                    if df.loc[idx, "problem_id"] not in used_problem_ids
                    and df.loc[idx, "problem_id"] not in local_used_problem_ids
                    else 0.0
                    for idx in remaining
                ]
            )
        else:
            new_problem_bonus = np.zeros(len(remaining))

        score = (
            min_dist
            + 0.12 * new_problem_bonus
            + 0.03 * complexity[remaining]
            + rng.random(len(remaining)) * 1e-9
        )

        pick_pos = int(np.argmax(score))
        pick = int(remaining[pick_pos])
        selected.append(pick)

        if "problem_id" in df.columns:
            local_used_problem_ids.add(df.loc[pick, "problem_id"])

        remaining = np.delete(remaining, pick_pos)

    return df.iloc[selected].set_index("index").loc[:, pool.columns].copy()


def choose_sample(
    manifest: pd.DataFrame,
    status_by_file: Dict[str, str],
    *,
    sample_size: int,
    seed: int,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    required_cols = {"copied_file_name", "code_lines"}
    missing_cols = required_cols - set(manifest.columns)
    if missing_cols:
        raise ValueError(f"Manifest is missing required columns: {sorted(missing_cols)}")

    data = manifest.copy()
    data["parse_status"] = data["copied_file_name"].map(status_by_file)
    data["scale"] = data["code_lines"].map(loc_bin)

    missing_status = data[data["parse_status"].isna()]
    if len(missing_status) > 0:
        raise ValueError(
            f"{len(missing_status)} manifest rows do not appear in the status log. "
            f"Example: {missing_status.iloc[0]['copied_file_name']}"
        )

    complete = data[data["parse_status"] == "parsed"].copy()
    incomplete = data[data["parse_status"] == "incomplete"].copy()

    if len(complete) < sample_size:
        raise ValueError(f"Only {len(complete)} complete files are available, cannot sample {sample_size}.")

    selected_parts: List[pd.DataFrame] = []
    used_problem_ids = set()

    # Keep all complete long programs when feasible.
    long_pool = complete[complete["code_lines"] > 200].copy()
    if len(long_pool) >= sample_size:
        selected = diverse_select(long_pool, sample_size, seed=seed, used_problem_ids=used_problem_ids)
        return selected.copy(), complete.copy(), incomplete.copy()

    selected_parts.append(long_pool)
    if "problem_id" in long_pool.columns:
        used_problem_ids.update(long_pool["problem_id"].tolist())

    remaining_total = sample_size - len(long_pool)

    # Fill the remaining sample from the three short/mid buckets according to the target distribution.
    short_bins = ["<= 50", "51-100", "101-200"]
    quotas = largest_remainder_counts({key: TARGET_PCT[key] for key in short_bins}, remaining_total)

    for bin_name in short_bins:
        available = len(complete[(complete["scale"] == bin_name) & ~complete.index.isin(long_pool.index)])
        quotas[bin_name] = min(quotas[bin_name], available)

    # Redistribute any deficit caused by unavailable buckets.
    while sum(quotas.values()) < remaining_total:
        best_bin = None
        best_score = None

        for bin_name in short_bins:
            available = len(complete[(complete["scale"] == bin_name) & ~complete.index.isin(long_pool.index)])
            remaining_capacity = available - quotas[bin_name]
            if remaining_capacity <= 0:
                continue

            ideal = TARGET_PCT[bin_name] / sum(TARGET_PCT[key] for key in short_bins) * remaining_total
            score = (ideal - quotas[bin_name], remaining_capacity)

            if best_score is None or score > best_score:
                best_score = score
                best_bin = bin_name

        if best_bin is None:
            break

        quotas[best_bin] += 1

    for offset, bin_name in enumerate(short_bins):
        pool = complete[(complete["scale"] == bin_name) & ~complete.index.isin(long_pool.index)].copy()
        part = diverse_select(pool, quotas[bin_name], seed=seed + offset + 17, used_problem_ids=used_problem_ids)
        selected_parts.append(part)

        if "problem_id" in part.columns:
            used_problem_ids.update(part["problem_id"].tolist())

    selected = pd.concat(selected_parts, ignore_index=False)
    if len(selected) != sample_size:
        raise RuntimeError(f"Expected {sample_size} selected files, got {len(selected)}.")

    return selected.copy(), complete.copy(), incomplete.copy()


def json_name(py_name: str) -> str:
    return f"{Path(py_name).stem}.json"


def find_existing_file(filename: str, directories: Sequence[Path]) -> Optional[Path]:
    for directory in directories:
        path = directory / filename
        if path.exists():
            return path
    return None


def move_file_task(filename: str, source_dirs: Sequence[str], target_dir_str: str, dry_run: bool) -> Tuple[str, str]:
    source_dirs_path = [Path(value) for value in source_dirs]
    target_dir = Path(target_dir_str)
    target = target_dir / filename

    source = find_existing_file(filename, source_dirs_path)
    if source is None:
        return "missing", filename

    if source.resolve() == target.resolve():
        return "already", str(target)

    if target.exists():
        # Avoid overwriting non-identical files.
        if source.exists() and filecmp.cmp(source, target, shallow=False):
            if not dry_run:
                source.unlink()
            return "deduplicated", f"{source} -> {target}"

        return "target_exists_skip", f"{source} -> {target}"

    if dry_run:
        return "dry_run", f"{source} -> {target}"

    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(target))
    return "moved", f"{source} -> {target}"


def run_moves(
    selected: pd.DataFrame,
    complete: pd.DataFrame,
    incomplete: pd.DataFrame,
    *,
    parsed_dir: Path,
    code_dir: Path,
    workers: int,
    dry_run: bool,
) -> Dict[str, int]:
    selected_names = set(selected["copied_file_name"].tolist())
    complete_names = set(complete["copied_file_name"].tolist())
    incomplete_names = set(incomplete["copied_file_name"].tolist())
    complete_unselected_names = sorted(complete_names - selected_names)

    parsed_others_dir = parsed_dir / "others"
    parsed_incomplete_dir = parsed_dir / "incomplete"
    code_others_dir = code_dir / "others"
    code_incomplete_dir = code_dir / "incomplete"

    for directory in [parsed_others_dir, parsed_incomplete_dir, code_others_dir, code_incomplete_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    tasks: List[Tuple[str, List[str], str, bool]] = []

    parsed_search_dirs = [str(parsed_dir), str(parsed_others_dir), str(parsed_incomplete_dir)]
    code_search_dirs = [str(code_dir), str(code_others_dir), str(code_incomplete_dir)]

    # Keep selected complete files in root folders. This also repairs a previous run.
    for py_name in sorted(selected_names):
        tasks.append((json_name(py_name), parsed_search_dirs, str(parsed_dir), dry_run))
        tasks.append((py_name, code_search_dirs, str(code_dir), dry_run))

    # Move complete but unselected files to others/.
    for py_name in complete_unselected_names:
        tasks.append((json_name(py_name), parsed_search_dirs, str(parsed_others_dir), dry_run))
        tasks.append((py_name, code_search_dirs, str(code_others_dir), dry_run))

    # Move incomplete code files to code/incomplete. Parsed JSON should live in parsed_code/incomplete if present.
    for py_name in sorted(incomplete_names):
        tasks.append((json_name(py_name), parsed_search_dirs, str(parsed_incomplete_dir), dry_run))
        tasks.append((py_name, code_search_dirs, str(code_incomplete_dir), dry_run))

    counts: Dict[str, int] = {}

    if workers <= 1:
        for task in tasks:
            status, _ = move_file_task(*task)
            counts[status] = counts.get(status, 0) + 1
        return counts

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(move_file_task, *task) for task in tasks]
        for future in as_completed(futures):
            status, _ = future.result()
            counts[status] = counts.get(status, 0) + 1

    return counts


def distribution_table(df: pd.DataFrame) -> List[Dict[str, object]]:
    total = len(df)
    rows: List[Dict[str, object]] = []

    for bin_name in LOC_ORDER:
        count = int((df["scale"] == bin_name).sum())
        rows.append(
            {
                "scale": bin_name,
                "file_count": count,
                "percentage": round(count / total * 100, 2) if total else 0.0,
            }
        )

    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sample 200 complete Python CodeNet files and reorganize parsed/code folders."
    )
    parser.add_argument("--status-log", required=True, help="parser stdout log containing parsed:/incomplete: lines")
    parser.add_argument("--manifest", required=True, help="CSV with per-file code attributes")
    parser.add_argument(
        "--base-dir",
        default="SemBench/data/python_codenet",
    )
    parser.add_argument("--parsed-dir", default=None, help="default: <base-dir>/parsed_code")
    parser.add_argument("--code-dir", default=None, help="default: <base-dir>/code")
    parser.add_argument("--sample-size", type=int, default=200)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 1) - 1))
    parser.add_argument("--dry-run", action="store_true", help="show summary without moving files")
    parser.add_argument(
        "--selected-out",
        default=None,
        help="default: <base-dir>/selected_python_codenet_200_manifest.csv",
    )
    parser.add_argument(
        "--summary-out",
        default=None,
        help="default: <base-dir>/selected_python_codenet_200_summary.json",
    )
    args = parser.parse_args()

    base_dir = Path(args.base_dir)
    parsed_dir = Path(args.parsed_dir) if args.parsed_dir else base_dir / "parsed_code"
    code_dir = Path(args.code_dir) if args.code_dir else base_dir / "code"
    selected_out = Path(args.selected_out) if args.selected_out else base_dir / "selected_python_codenet_200_manifest.csv"
    summary_out = Path(args.summary_out) if args.summary_out else base_dir / "selected_python_codenet_200_summary.json"

    status_by_file = parse_status_log(Path(args.status_log))
    manifest = pd.read_csv(args.manifest)

    selected, complete, incomplete = choose_sample(
        manifest,
        status_by_file,
        sample_size=args.sample_size,
        seed=args.seed,
    )

    selected = selected.sort_values(["scale", "code_lines", "copied_file_name"]).copy()
    selected["selected"] = True

    selected_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    selected.to_csv(selected_out, index=False)

    move_counts = run_moves(
        selected,
        complete,
        incomplete,
        parsed_dir=parsed_dir,
        code_dir=code_dir,
        workers=args.workers,
        dry_run=args.dry_run,
    )

    summary = {
        "sample_size": args.sample_size,
        "seed": args.seed,
        "dry_run": args.dry_run,
        "status_log_files": len(status_by_file),
        "manifest_rows": len(manifest),
        "complete_candidates": len(complete),
        "incomplete_files": len(incomplete),
        "selected_files": len(selected),
        "selected_unique_problem_ids": int(selected["problem_id"].nunique())
        if "problem_id" in selected.columns
        else None,
        "complete_candidate_distribution": distribution_table(complete),
        "selected_distribution": distribution_table(selected),
        "move_counts": move_counts,
        "selected_manifest": str(selected_out),
        "summary_json": str(summary_out),
        "directories": {
            "parsed_root_selected_kept_here": str(parsed_dir),
            "parsed_others_unselected_complete": str(parsed_dir / "others"),
            "parsed_incomplete": str(parsed_dir / "incomplete"),
            "code_root_selected_kept_here": str(code_dir),
            "code_others_unselected_complete": str(code_dir / "others"),
            "code_incomplete": str(code_dir / "incomplete"),
        },
    }

    summary_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
'''
python SemBench/script/sample_python_codenet_200.py \
  --status-log SemBench/data/python_codenet/python952_result.log \
  --manifest SemBench/data/python_codenet/selected_python_codenet_manifest.csv \
  --base-dir SemBench/data/python_codenet \
  --workers 32
#  --dry-run \
'''
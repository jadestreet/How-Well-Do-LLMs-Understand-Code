#!/usr/bin/env python3
"""Repair the current Python CodeNet 200-file selection.

This script keeps file movement explicit:
  - selected files move to the root folders
  - unselected parseable files move to others/
  - selected manifests and summaries are rewritten after the move
"""

from __future__ import annotations

import argparse
import csv
import filecmp
import json
import shutil
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


LOC_ORDER = ["<= 50", "51-100", "101-200", "201-500", "501-1000", "1001-2000", "> 2000"]
SEMANTIC_CATEGORIES = [
    "function_reachability",
    "loop_reachability",
    "dominators",
    "data_dependency",
    "liveness",
    "dead_code",
]
RELIABLE_LOOP_CERTAINTY = {"always_runs", "never_runs"}
REPO_ROOT = Path(__file__).resolve().parents[2]


def read_csv(path: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: Sequence[Dict[str, str]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def json_name(py_name: str) -> str:
    return f"{Path(py_name).stem}.json"


def parsed_metadata(parsed_path: Path) -> Dict[str, object]:
    return json.loads(parsed_path.read_text(encoding="utf-8"))


def semantic_presence(parsed: Dict[str, object]) -> Dict[str, bool]:
    liveness = parsed.get("liveness", {})
    live_funcs = liveness.get("functions", {}) if isinstance(liveness, dict) else {}
    return {
        "function_reachability": len(parsed.get("functions", [])) >= 2,
        "loop_reachability": len(parsed.get("loops", [])) > 0,
        "dominators": len(parsed.get("strict_dominators", [])) > 0,
        "data_dependency": len(parsed.get("var_dependencies", [])) > 0,
        "liveness": any(isinstance(blob, dict) and blob.get("liveout") for blob in live_funcs.values()),
        "dead_code": len(parsed.get("dead_code", [])) > 0,
    }


def is_all_six(parsed: Dict[str, object]) -> bool:
    return all(semantic_presence(parsed).values())


def has_reliable_loop(parsed: Dict[str, object]) -> bool:
    return any(
        isinstance(loop, dict) and loop.get("certainty") in RELIABLE_LOOP_CERTAINTY
        for loop in parsed.get("loops", [])
    )


def metadata_score(parsed_path: Path) -> int:
    parsed = json.loads(parsed_path.read_text(encoding="utf-8"))
    score = sum(
        len(parsed.get(key, []))
        for key in ["functions", "cfg_statements", "loops", "strict_dominators", "var_dependencies", "dead_code"]
    )
    score += sum(
        len(blob.get("liveout", {}))
        for blob in parsed.get("liveness", {}).get("functions", {}).values()
        if isinstance(blob, dict)
    )
    return score


def loc_bin(row: Dict[str, str]) -> str:
    return row.get("scale") or row.get("loc_bin") or ""


def int_field(row: Dict[str, str], key: str) -> int:
    try:
        return int(float(row.get(key, "") or 0))
    except ValueError:
        return 0


def distribution(rows: Iterable[Dict[str, str]]) -> List[Dict[str, object]]:
    rows = list(rows)
    total = len(rows)
    return [
        {
            "scale": bucket,
            "selected_count": sum(1 for row in rows if loc_bin(row) == bucket),
            "percentage": round(sum(1 for row in rows if loc_bin(row) == bucket) / total * 100, 2) if total else 0.0,
        }
        for bucket in LOC_ORDER
    ]


def move_one(source: Path, target: Path, dry_run: bool) -> str:
    if not source.exists():
        return f"missing: {display_path(source)}"
    if source.resolve() == target.resolve():
        return f"already: {display_path(target)}"
    if target.exists():
        if filecmp.cmp(source, target, shallow=False):
            if not dry_run:
                source.unlink()
            return f"deduplicated: {display_path(source)} -> {display_path(target)}"
        raise FileExistsError(f"Refusing to overwrite different file: {target}")
    if dry_run:
        return f"dry_run: {display_path(source)} -> {display_path(target)}"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(target))
    return f"moved: {display_path(source)} -> {display_path(target)}"


def prepare_replacement_row(row: Dict[str, str], code_dir: Path) -> Dict[str, str]:
    repaired = dict(row)
    repaired["copied_path"] = display_path(code_dir / repaired["copied_file_name"])
    if "source_path" in repaired:
        old_repo_prefix = f"{REPO_ROOT.as_posix()}/"
        repaired["source_path"] = repaired["source_path"].replace(old_repo_prefix, "")
    repaired["parse_status"] = "parsed"
    repaired["scale"] = loc_bin(repaired)
    repaired["selected"] = "True"
    return repaired


def sort_selected(rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    order = {name: idx for idx, name in enumerate(LOC_ORDER)}
    return sorted(
        rows,
        key=lambda row: (order.get(loc_bin(row), len(order)), int_field(row, "code_lines"), row["copied_file_name"]),
    )


def find_existing_path(file_name: str, root_dir: Path, others_dir: Path, suffix: str) -> Optional[Path]:
    root_path = root_dir / file_name
    if root_path.exists():
        return root_path
    others_path = others_dir / file_name
    if others_path.exists():
        return others_path
    if suffix == ".json":
        incomplete_path = others_dir / "incomplete" / file_name
        if incomplete_path.exists():
            return incomplete_path
    return None


def target_distribution(selected_rows: Sequence[Dict[str, str]]) -> Dict[str, int]:
    counts = {bucket: 0 for bucket in LOC_ORDER}
    for row in selected_rows:
        counts[loc_bin(row)] = counts.get(loc_bin(row), 0) + 1
    return counts


def selection_sort_key(item: Dict[str, object], selected_problem_ids: set[str]) -> Tuple[int, int, int, int, int, str]:
    row = item["row"]
    assert isinstance(row, dict)
    return (
        1 if row.get("problem_id", "") not in selected_problem_ids else 0,
        int(item["score"]),
        int_field(row, "function_count"),
        int_field(row, "loop_count"),
        int_field(row, "call_count"),
        row["copied_file_name"],
    )


def choose_selected_rows(
    candidate_items: Sequence[Dict[str, object]],
    current_selected_rows: Sequence[Dict[str, str]],
    *,
    limit: int = 200,
) -> List[Dict[str, str]]:
    reliable_items = [item for item in candidate_items if item["reliable"]]
    nonreliable_items = [item for item in candidate_items if not item["reliable"]]
    selected_items: List[Dict[str, object]] = []
    selected_names: set[str] = set()
    selected_problem_ids: set[str] = set()

    def pick_items(items: Sequence[Dict[str, object]], quota: int) -> None:
        nonlocal selected_items
        while len(selected_items) < quota:
            pool = [item for item in items if item["name"] not in selected_names]
            if not pool:
                break
            picked = max(pool, key=lambda item: selection_sort_key(item, selected_problem_ids))
            selected_items.append(picked)
            selected_names.add(str(picked["name"]))
            row = picked["row"]
            assert isinstance(row, dict)
            selected_problem_ids.add(row.get("problem_id", ""))

    # Reliable loops are the second hard priority after all-six semantics, so keep
    # every reliable all-six candidate when there are fewer than the requested 200.
    pick_items(reliable_items, min(limit, len(reliable_items)))

    if len(selected_items) < limit:
        targets = target_distribution(current_selected_rows)
        for bucket in LOC_ORDER:
            bucket_target = targets.get(bucket, 0)
            already_in_bucket = sum(
                1
                for item in selected_items
                if isinstance(item["row"], dict) and loc_bin(item["row"]) == bucket
            )
            need = max(0, min(bucket_target - already_in_bucket, limit - len(selected_items)))
            for _ in range(need):
                pool = [
                    item
                    for item in nonreliable_items
                    if item["name"] not in selected_names
                    and isinstance(item["row"], dict)
                    and loc_bin(item["row"]) == bucket
                ]
                if not pool:
                    break
                picked = max(pool, key=lambda item: selection_sort_key(item, selected_problem_ids))
                selected_items.append(picked)
                selected_names.add(str(picked["name"]))
                row = picked["row"]
                assert isinstance(row, dict)
                selected_problem_ids.add(row.get("problem_id", ""))

    if len(selected_items) < limit:
        pick_items(nonreliable_items, limit)

    if len(selected_items) != limit:
        raise RuntimeError(f"Only selected {len(selected_items)} all-six files; need {limit}")

    return [prepare_replacement_row(item["row"], Path(item["code_target_dir"])) for item in selected_items]  # type: ignore[arg-type]


def main() -> None:
    default_base_dir = REPO_ROOT / "SemBench" / "data" / "python_codenet"
    parser = argparse.ArgumentParser(description="Reselect Python CodeNet files with all-six semantics and reliable loops prioritized.")
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=default_base_dir,
    )
    parser.add_argument(
        "--full-manifest",
        type=Path,
        default=default_base_dir / "selected_python_codenet_manifest.csv",
    )
    parser.add_argument(
        "--selected-manifest",
        action="append",
        default=[
            default_base_dir / "selected_python_codenet_200_manifest.csv",
            REPO_ROOT / "SemBench" / "script" / "selected_python_codenet_200_manifest.csv",
        ],
    )
    parser.add_argument(
        "--summary-out",
        action="append",
        default=[
            default_base_dir / "selected_python_codenet_200_summary.json",
            REPO_ROOT / "SemBench" / "script" / "selected_python_codenet_200_summary.json",
        ],
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    base_dir = args.base_dir
    code_dir = base_dir / "code"
    parsed_dir = base_dir / "parsed_code"
    code_others_dir = code_dir / "others"
    parsed_others_dir = parsed_dir / "others"
    query_dir = base_dir / "queries"
    truth_dir = base_dir / "ground_truth"
    query_others_dir = query_dir / "others"
    truth_others_dir = truth_dir / "others"

    full_rows, _ = read_csv(args.full_manifest)
    full_rows_by_name = {row["copied_file_name"]: row for row in full_rows}
    selected_rows, selected_fieldnames = read_csv(args.selected_manifest[0])

    candidate_items: List[Dict[str, object]] = []
    skipped: Dict[str, List[str]] = {"missing_code": [], "missing_parsed": [], "not_all_six": [], "incomplete": []}
    for py_name, row in full_rows_by_name.items():
        code_path = find_existing_path(py_name, code_dir, code_others_dir, ".py")
        if code_path is None:
            skipped["missing_code"].append(py_name)
            continue
        parsed_path = find_existing_path(json_name(py_name), parsed_dir, parsed_others_dir, ".json")
        if parsed_path is None:
            skipped["missing_parsed"].append(py_name)
            continue
        if "incomplete" in parsed_path.parts:
            skipped["incomplete"].append(py_name)
            continue
        parsed = parsed_metadata(parsed_path)
        if not is_all_six(parsed):
            skipped["not_all_six"].append(py_name)
            continue
        candidate_items.append(
            {
                "name": py_name,
                "row": row,
                "code_path": code_path,
                "parsed_path": parsed_path,
                "code_target_dir": code_dir,
                "score": metadata_score(parsed_path),
                "reliable": has_reliable_loop(parsed),
            }
        )

    repaired_rows = sort_selected(choose_selected_rows(candidate_items, selected_rows, limit=200))
    selected_names = {row["copied_file_name"] for row in repaired_rows}
    current_root_names = {path.name for path in code_dir.glob("*.py")}
    parseable_names = {str(item["name"]) for item in candidate_items}
    unselected_root_names = sorted((current_root_names & parseable_names) - selected_names)
    selected_from_others = sorted(selected_names - current_root_names)

    move_log: List[str] = []
    for py_name in unselected_root_names:
        move_log.append(move_one(code_dir / py_name, code_others_dir / py_name, args.dry_run))
        move_log.append(move_one(parsed_dir / json_name(py_name), parsed_others_dir / json_name(py_name), args.dry_run))
        query_path = query_dir / json_name(py_name)
        truth_path = truth_dir / json_name(py_name)
        if query_path.exists():
            move_log.append(move_one(query_path, query_others_dir / json_name(py_name), args.dry_run))
        if truth_path.exists():
            move_log.append(move_one(truth_path, truth_others_dir / json_name(py_name), args.dry_run))

    for py_name in selected_from_others:
        move_log.append(move_one(code_others_dir / py_name, code_dir / py_name, args.dry_run))
        move_log.append(move_one(parsed_others_dir / json_name(py_name), parsed_dir / json_name(py_name), args.dry_run))

    missing_fieldnames = [name for name in repaired_rows[0].keys() if name not in selected_fieldnames]
    selected_fieldnames = [*selected_fieldnames, *missing_fieldnames]

    if not args.dry_run:
        for manifest_path in args.selected_manifest:
            write_csv(manifest_path, repaired_rows, selected_fieldnames)

    summary = {
        "dry_run": args.dry_run,
        "selected_files": len(repaired_rows),
        "all_six_candidates": len(candidate_items),
        "all_six_reliable_candidates": sum(1 for item in candidate_items if item["reliable"]),
        "selected_reliable_loop_files": sum(
            1
            for row in repaired_rows
            if any(item["name"] == row["copied_file_name"] and item["reliable"] for item in candidate_items)
        ),
        "moved_from_root_to_others": unselected_root_names,
        "moved_from_others_to_root": selected_from_others,
        "skipped_counts": {key: len(value) for key, value in skipped.items()},
        "skipped_examples": {key: value[:10] for key, value in skipped.items()},
        "previous_distribution": distribution(selected_rows),
        "selected_distribution": distribution(repaired_rows),
        "move_log": move_log,
        "updated_manifests": [display_path(path) for path in args.selected_manifest],
    }

    if not args.dry_run:
        for summary_path in args.summary_out:
            summary_path.parent.mkdir(parents=True, exist_ok=True)
            summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

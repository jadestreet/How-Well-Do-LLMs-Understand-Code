#!/usr/bin/env python3
"""Extract category accuracies and geometric mean from ablation JSONL results."""

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


DEFAULT_INPUT_DIR = Path("SemBench/data/python_codenet/llm_results/ablation")
DEFAULT_OUTPUT_FILE = Path("SemBench/data/python_codenet/llm_results/ablation_results.csv")

CATEGORY_DISPLAY_NAMES = {
    "data_dependency": "DataDep",
    "dead_code": "DeadCode",
    "dominators": "Dominators",
    "function_reachability": "FuncReach",
    "loop_reachability": "LoopReach",
    "liveness": "Liveness",
}

CATEGORY_ORDER = [
    "data_dependency",
    "dead_code",
    "dominators",
    "function_reachability",
    "loop_reachability",
    "liveness",
]

CATEGORY_ALIASES = {
    "deadcode": "dead_code",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compute per-category and geometric mean accuracies for ablation results."
    )
    parser.add_argument(
        "--input_dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help=f"Directory containing one subfolder per model (default: {DEFAULT_INPUT_DIR})",
    )
    parser.add_argument(
        "--output_file",
        type=Path,
        default=DEFAULT_OUTPUT_FILE,
        help=f"CSV output path (default: {DEFAULT_OUTPUT_FILE})",
    )
    parser.add_argument(
        "--scale",
        choices=["percent", "fraction"],
        default="percent",
        help="Write accuracies as percentages or fractions (default: percent)",
    )
    return parser.parse_args()


def display_name(category):
    return CATEGORY_DISPLAY_NAMES.get(category, category)


def canonical_category(category):
    return CATEGORY_ALIASES.get(category, category)


def sort_categories(categories):
    known_order = {category: index for index, category in enumerate(CATEGORY_ORDER)}
    return sorted(categories, key=lambda category: (known_order.get(category, len(known_order)), category))


def read_model_counts(model_dir):
    counts = defaultdict(lambda: {"correct": 0, "total": 0})

    for jsonl_file in sorted(model_dir.glob("*.jsonl")):
        with jsonl_file.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue

                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Malformed JSON in {jsonl_file}:{line_number}: {exc}") from exc

                category = record.get("category")
                if category is None:
                    raise ValueError(f"Missing category in {jsonl_file}:{line_number}")
                category = canonical_category(category)

                counts[category]["total"] += 1
                if record.get("first_response_correct") is True:
                    counts[category]["correct"] += 1

    return counts


def accuracy(correct, total):
    if total == 0:
        return None
    return correct / total


def geometric_mean(values):
    if not values:
        return None
    if any(value == 0 for value in values):
        return 0.0
    return math.prod(values) ** (1 / len(values))


def format_metric(value, scale):
    if value is None:
        return ""
    if scale == "percent":
        return f"{value * 100:.2f}"
    return f"{value:.4f}"


def extract_results(input_dir, scale):
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {input_dir}")

    model_dirs = sorted(path for path in input_dir.iterdir() if path.is_dir())
    rows = []
    all_categories = set()

    for model_dir in model_dirs:
        counts = read_model_counts(model_dir)
        category_accuracies = {
            category: accuracy(values["correct"], values["total"])
            for category, values in counts.items()
        }
        all_categories.update(category_accuracies)

        present_accuracies = [
            value for value in category_accuracies.values()
            if value is not None
        ]
        rows.append(
            {
                "model": model_dir.name,
                "accuracies": category_accuracies,
                "All_geo": geometric_mean(present_accuracies),
            }
        )

    categories = sort_categories(all_categories)
    fieldnames = ["model"] + [display_name(category) for category in categories] + ["All_geo"]

    output_rows = []
    for row in rows:
        output_row = {"model": row["model"]}
        for category in categories:
            output_row[display_name(category)] = format_metric(
                row["accuracies"].get(category), scale
            )
        output_row["All_geo"] = format_metric(row["All_geo"], scale)
        output_rows.append(output_row)

    return fieldnames, output_rows


def write_csv(output_file, fieldnames, rows):
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    args = parse_args()
    fieldnames, rows = extract_results(args.input_dir, args.scale)
    write_csv(args.output_file, fieldnames, rows)
    print(f"Saved {len(rows)} model result rows to {args.output_file}")


if __name__ == "__main__":
    main()

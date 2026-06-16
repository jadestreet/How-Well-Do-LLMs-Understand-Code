#!/usr/bin/env python3
"""Combine Python CodeNet LLM results and compute accuracy/correlation reports."""

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

from scipy.stats import kendalltau, pearsonr, spearmanr


RESULTS_ROOT = Path("SemBench/data/python_codenet/llm_results")
DEFAULT_ABLATION_DIR = RESULTS_ROOT / "ablation"
DEFAULT_DEADCODE_DIR = RESULTS_ROOT / "deadcode"
DEFAULT_FINALRESULT = Path("SemBench/finalresult.csv")
DEFAULT_ALL_OUTPUT = RESULTS_ROOT / "python_results_all200.csv"
DEFAULT_COMPLETE_OUTPUT = RESULTS_ROOT / "python_results_complete6.csv"
DEFAULT_CORRELATION_OUTPUT = RESULTS_ROOT / "python_finalresult_correlations.csv"
COMBINED_FILENAME = "combined_results.jsonl"

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

MODEL_NAME_MAP = {
    "Qwen_Qwen2.5-Coder-14B-Instruct": "Qwen2.5-Coder 14B-Instr",
    "Qwen_Qwen3-14B": "Qwen3 14B",
    "bigcode_starcoder2-7b": "StarCoder 2 7B",
    "codellama_CodeLlama-13b-Instruct-hf": "CodeLlama-13B-Instr",
    "codellama_CodeLlama-7b-Instruct-hf": "CodeLlama-7B-Instr",
    "deepseek-ai_DeepSeek-Coder-V2-Lite-Instruct": "DeepSeek-Coder V2-Lite-Instr",
    "deepseek-ai_DeepSeek-R1-Distill-Qwen-7B": "DeepSeek-R1-Distill-Qwen-7B",
    "deepseek-ai_deepseek-coder-7b-instruct-v1.5": "DeepSeek-Coder 7B-Instr v1.5",
    "meta-llama_Llama-3.1-8B-Instruct": "Llama-3 8B-Instr",
    "microsoft_Phi-4-reasoning": "Phi-4 Reasoning (14B)",
    "mistralai_Mamba-Codestral-7B-v0.1": "Mamba Codestral 7B (v0.1)",
    "mistralai_Mistral-7B-Instruct-v0.3": "Mistral 7B-Instr (v0.3)",
}

CORRELATION_METRICS = [
    "DataDep",
    "DeadCode",
    "Dominators",
    "FuncReach",
    "LoopReach",
    "Liveness",
    "All_geo",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Combine Python CodeNet LLM results and compute accuracy/correlation CSVs."
    )
    parser.add_argument("--ablation_dir", type=Path, default=DEFAULT_ABLATION_DIR)
    parser.add_argument("--deadcode_dir", type=Path, default=DEFAULT_DEADCODE_DIR)
    parser.add_argument("--results_root", type=Path, default=RESULTS_ROOT)
    parser.add_argument("--finalresult_csv", type=Path, default=DEFAULT_FINALRESULT)
    parser.add_argument("--all_output", type=Path, default=DEFAULT_ALL_OUTPUT)
    parser.add_argument("--complete_output", type=Path, default=DEFAULT_COMPLETE_OUTPUT)
    parser.add_argument("--correlation_output", type=Path, default=DEFAULT_CORRELATION_OUTPUT)
    return parser.parse_args()


def canonical_category(category):
    return CATEGORY_ALIASES.get(category, category)


def display_name(category):
    return CATEGORY_DISPLAY_NAMES.get(category, category)


def sort_categories(categories):
    known_order = {category: index for index, category in enumerate(CATEGORY_ORDER)}
    return sorted(categories, key=lambda category: (known_order.get(category, len(known_order)), category))


def read_jsonl(path):
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Malformed JSON in {path}:{line_number}: {exc}") from exc
            if record.get("program") is None:
                raise ValueError(f"Missing program in {path}:{line_number}")
            if record.get("category") is None:
                raise ValueError(f"Missing category in {path}:{line_number}")
            record["category"] = canonical_category(record["category"])
            yield record


def read_model_records(model_dir):
    records = []
    for path in sorted(model_dir.glob("*.jsonl")):
        records.extend(read_jsonl(path))
    return records


def model_dirs(root):
    if not root.exists():
        raise FileNotFoundError(f"Input directory does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {root}")
    return {path.name: path for path in root.iterdir() if path.is_dir()}


def collect_records(ablation_dir, deadcode_dir):
    ablation_models = model_dirs(ablation_dir)
    deadcode_models = model_dirs(deadcode_dir)
    model_names = sorted(set(ablation_models) | set(deadcode_models))
    records_by_model = {}

    for model_name in model_names:
        records = []
        if model_name in ablation_models:
            records.extend(read_model_records(ablation_models[model_name]))
        if model_name in deadcode_models:
            records.extend(read_model_records(deadcode_models[model_name]))
        records_by_model[model_name] = records

    return records_by_model


def write_combined_jsonl(records_by_model, results_root):
    for model_name, records in records_by_model.items():
        output_dir = results_root / model_name
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / COMBINED_FILENAME
        with output_file.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def complete_programs(records):
    categories_by_program = defaultdict(set)
    required_categories = set(CATEGORY_ORDER)
    for record in records:
        categories_by_program[record["program"]].add(record["category"])
    return {
        program
        for program, categories in categories_by_program.items()
        if required_categories.issubset(categories)
    }


def category_counts(records, allowed_programs=None):
    counts = defaultdict(lambda: {"correct": 0, "total": 0})
    null_count = 0
    programs = set()

    for record in records:
        program = record["program"]
        if allowed_programs is not None and program not in allowed_programs:
            continue

        programs.add(program)
        category = record["category"]
        counts[category]["total"] += 1
        if "first_response_correct" not in record or record.get("first_response_correct") is None:
            null_count += 1
        if record.get("first_response_correct") is True:
            counts[category]["correct"] += 1

    return counts, null_count, len(programs)


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


def format_metric(value):
    if value is None:
        return ""
    return f"{value * 100:.2f}"


def build_accuracy_rows(records_by_model, subset):
    rows = []
    all_categories = set()
    complete_counts = {}

    for model_name, records in records_by_model.items():
        allowed_programs = None
        if subset == "complete6":
            allowed_programs = complete_programs(records)
            complete_counts[model_name] = len(allowed_programs)

        counts, null_count, program_count = category_counts(records, allowed_programs)
        accuracies = {
            category: accuracy(values["correct"], values["total"])
            for category, values in counts.items()
        }
        all_categories.update(accuracies)
        rows.append(
            {
                "model": model_name,
                "program_count": program_count,
                "accuracies": accuracies,
                "All_geo": geometric_mean([value for value in accuracies.values() if value is not None]),
                "Null_count": null_count,
            }
        )

    categories = sort_categories(all_categories)
    fieldnames = (
        ["model"]
        + [display_name(category) for category in categories]
        + ["All_geo", "Null_count"]
    )
    output_rows = []
    for row in rows:
        output_row = {"model": row["model"]}
        for category in categories:
            output_row[display_name(category)] = format_metric(row["accuracies"].get(category))
        output_row["All_geo"] = format_metric(row["All_geo"])
        output_row["Null_count"] = row["Null_count"]
        output_rows.append(output_row)

    return fieldnames, output_rows, complete_counts


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_csv_by_model(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row["model"]: row for row in csv.DictReader(handle)}


def to_float(value):
    if value is None or value == "":
        return None
    return float(value)


def statistic_pair(x_values, y_values, fn):
    if len(x_values) < 3:
        return None, None
    result = fn(x_values, y_values)
    return float(result.statistic), float(result.pvalue)


def build_correlation_rows(result_sets, finalresult_csv):
    final_rows = read_csv_by_model(finalresult_csv)
    output_rows = []

    for subset, rows in result_sets.items():
        rows_by_model = {row["model"]: row for row in rows}
        for metric in CORRELATION_METRICS:
            x_values = []
            y_values = []
            for folder_model, final_model in MODEL_NAME_MAP.items():
                python_row = rows_by_model.get(folder_model)
                final_row = final_rows.get(final_model)
                if python_row is None or final_row is None:
                    continue
                x_value = to_float(python_row.get(metric))
                y_value = to_float(final_row.get(f"{metric}_p1"))
                if x_value is None or y_value is None:
                    continue
                x_values.append(x_value)
                y_values.append(y_value)

            spearman_rho, spearman_p = statistic_pair(x_values, y_values, spearmanr)
            kendall_tau_value, kendall_p = statistic_pair(x_values, y_values, kendalltau)
            pearson_r, pearson_p = statistic_pair(x_values, y_values, pearsonr)
            output_rows.append(
                {
                    "Subset": subset,
                    "Metric": metric,
                    "N": len(x_values),
                    "Spearman_rho": format_stat(spearman_rho),
                    "Spearman_p": format_stat(spearman_p),
                    "Kendall_tau": format_stat(kendall_tau_value),
                    "Kendall_p": format_stat(kendall_p),
                    "Pearson_r": format_stat(pearson_r),
                    "Pearson_p": format_stat(pearson_p),
                }
            )

    return output_rows


def format_stat(value):
    if value is None or math.isnan(value):
        return ""
    return f"{value:.6f}"


def main():
    args = parse_args()
    records_by_model = collect_records(args.ablation_dir, args.deadcode_dir)
    write_combined_jsonl(records_by_model, args.results_root)

    all_fieldnames, all_rows, _ = build_accuracy_rows(records_by_model, "all200")
    complete_fieldnames, complete_rows, complete_counts = build_accuracy_rows(records_by_model, "complete6")
    write_csv(args.all_output, all_fieldnames, all_rows)
    write_csv(args.complete_output, complete_fieldnames, complete_rows)

    correlation_rows = build_correlation_rows(
        {"all200": all_rows, "complete6": complete_rows},
        args.finalresult_csv,
    )
    correlation_fieldnames = [
        "Subset",
        "Metric",
        "N",
        "Spearman_rho",
        "Spearman_p",
        "Kendall_tau",
        "Kendall_p",
        "Pearson_r",
        "Pearson_p",
    ]
    write_csv(args.correlation_output, correlation_fieldnames, correlation_rows)

    complete_summary = sorted(set(complete_counts.values()))
    print(f"Saved combined JSONL files for {len(records_by_model)} models under {args.results_root}")
    print(f"Saved all-program accuracy CSV to {args.all_output}")
    print(f"Saved complete-six accuracy CSV to {args.complete_output}")
    print(f"Complete-six program counts: {complete_summary}")
    print(f"Saved correlation CSV to {args.correlation_output}")


if __name__ == "__main__":
    main()

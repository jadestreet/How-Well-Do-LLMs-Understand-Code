"""Collect summary statistics for the SemBench-Python CodeNet subset.

The default population is the current benchmark subset: Python files whose
stems appear in ``SemBench/data/python_codenet/queries``.
"""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


CATEGORY_ROWS = [
    ("dead_code", "Dead code - statement"),
    ("data_dependency", "Data dependency"),
    ("function_reachability", "Function reachability"),
    ("dominators", "Dominators"),
    ("loop_reachability", "Dead code - loop"),
    ("liveness", "Liveness"),
]

COMPOUND_NESTING_NODES = (
    ast.If,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.With,
    ast.AsyncWith,
    ast.Try,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.Match,
)


@dataclass(frozen=True)
class Summary:
    average: int
    minimum: int
    maximum: int


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    default_dataset = repo_root / "SemBench" / "data" / "python_codenet"
    default_output_dir = repo_root / "Python_workflow"

    parser = argparse.ArgumentParser(
        description="Collect SemBench-Python category and source statistics.",
    )
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=default_dataset,
        help="Root of SemBench/data/python_codenet.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_output_dir,
        help="Directory for generated JSON and LaTeX outputs.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def count_categories(query_dir: Path) -> dict[str, int]:
    counts = {key: 0 for key, _ in CATEGORY_ROWS}
    for path in sorted(query_dir.glob("*.json")):
        queries = load_json(path)
        for key in counts:
            counts[key] += len(queries.get(key, []))
    return counts


def index_by_stem(root: Path, pattern: str) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for path in sorted(root.rglob(pattern)):
        paths.setdefault(path.stem, path)
    return paths


def line_count(source: str) -> int:
    return sum(
        1
        for line in source.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )


def count_ast_nodes(tree: ast.AST, node_types: type[ast.AST] | tuple[type[ast.AST], ...]) -> int:
    return sum(isinstance(node, node_types) for node in ast.walk(tree))


def max_nesting_depth(tree: ast.AST) -> int:
    max_depth = 0

    def visit(node: ast.AST, depth: int) -> None:
        nonlocal max_depth
        next_depth = depth + 1 if isinstance(node, COMPOUND_NESTING_NODES) else depth
        if next_depth > max_depth:
            max_depth = next_depth
        for child in ast.iter_child_nodes(node):
            visit(child, next_depth)

    visit(tree, 0)
    return max_depth


def dependency_distances(parsed_path: Path | None) -> list[int]:
    if parsed_path is None:
        return []

    parsed = load_json(parsed_path)
    distances: list[int] = []
    for dependency in parsed.get("var_dependencies", []):
        from_line = dependency.get("from", {}).get("line")
        depends_on_line = dependency.get("depends_on", {}).get("line")
        if isinstance(from_line, int) and isinstance(depends_on_line, int):
            distances.append(abs(from_line - depends_on_line))
    return distances


def summarize(values: Iterable[int]) -> Summary:
    collected = list(values)
    if not collected:
        return Summary(average=0, minimum=0, maximum=0)
    return Summary(
        average=round(sum(collected) / len(collected)),
        minimum=min(collected),
        maximum=max(collected),
    )


def latex_number(value: int) -> str:
    return f"{value:,}".replace(",", r"\,")


def collect_statistics(dataset_dir: Path) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[1]
    query_dir = dataset_dir / "queries"
    code_dir = dataset_dir / "code"
    parsed_dir = dataset_dir / "parsed_code"

    query_paths = sorted(query_dir.glob("*.json"))
    query_stems = [path.stem for path in query_paths]
    code_by_stem = index_by_stem(code_dir, "*.py")
    parsed_by_stem = index_by_stem(parsed_dir, "*.json")

    missing_code = [stem for stem in query_stems if stem not in code_by_stem]
    if missing_code:
        raise FileNotFoundError(f"Missing source files for query stems: {missing_code[:10]}")

    per_file_dependency_averages: list[int] = []
    per_file_dependency_maxima: list[int] = []
    metrics: dict[str, list[int]] = {
        "file_size_bytes": [],
        "lines_of_code": [],
        "function_count": [],
        "loop_count": [],
        "max_nesting_depth": [],
    }

    for stem in query_stems:
        source_path = code_by_stem[stem]
        source_bytes = source_path.read_bytes()
        source = source_bytes.decode("utf-8", errors="replace")
        tree = ast.parse(source, filename=str(source_path))

        metrics["file_size_bytes"].append(len(source_bytes))
        metrics["lines_of_code"].append(line_count(source))
        metrics["function_count"].append(
            count_ast_nodes(tree, (ast.FunctionDef, ast.AsyncFunctionDef))
        )
        metrics["loop_count"].append(count_ast_nodes(tree, (ast.For, ast.AsyncFor, ast.While)))
        metrics["max_nesting_depth"].append(max_nesting_depth(tree))

        distances = dependency_distances(parsed_by_stem.get(stem))
        per_file_dependency_averages.append(round(sum(distances) / len(distances)) if distances else 0)
        per_file_dependency_maxima.append(max(distances) if distances else 0)

    summaries = {name: summarize(values).__dict__ for name, values in metrics.items()}
    summaries["avg_dependency_distance"] = summarize(per_file_dependency_averages).__dict__
    summaries["max_dependency_distance"] = summarize(per_file_dependency_maxima).__dict__

    try:
        dataset_label = dataset_dir.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        dataset_label = str(dataset_dir)

    return {
        "dataset_dir": dataset_label,
        "query_file_count": len(query_paths),
        "source_file_count": len(query_stems),
        "category_counts": count_categories(query_dir),
        "feature_statistics": summaries,
        "notes": {
            "population": "Files with JSON query records in SemBench/data/python_codenet/queries.",
            "lines_of_code": "Nonblank, non-comment physical source lines.",
            "max_nesting_depth": "Syntactic AST nesting over compound statements, functions, and classes.",
            "dependency_distance": "Absolute source-line distance between from.line and depends_on.line in var_dependencies.",
        },
    }


def feature_row(label: str, summary: dict[str, int]) -> str:
    avg = latex_number(summary["average"])
    minimum = latex_number(summary["minimum"])
    maximum = latex_number(summary["maximum"])
    return f"    {label:<28} & {avg:>6} & (min: {minimum}, max: {maximum})   \\\\"


def render_latex(stats: dict[str, Any]) -> str:
    counts = stats["category_counts"]
    features = stats["feature_statistics"]

    lines = [
        r"\begin{table}[h]",
        r"  \centering",
        r"  \small",
        r"  \caption{Overview of the SemBench-Python}",
        r"  \label{ap:sembench_py_overview}",
        r"  \begin{tabular}{@{}l r l@{}}",
        r"    \toprule",
        r"    \multicolumn{3}{@{}l}{\textbf{Problem counts by category}} \\",
        r"    \midrule",
    ]

    for key, label in CATEGORY_ROWS:
        lines.append(f"    {label:<28} & \\multicolumn{{2}}{{r}}{{{latex_number(counts[key])}}}          \\\\")

    lines.extend(
        [
            r"    \multicolumn{3}{@{}l}{\textbf{Feature statistics}} \\",
            r"    \midrule",
            feature_row("File size (bytes)", features["file_size_bytes"]),
            feature_row("Lines of code", features["lines_of_code"]),
            feature_row("Function count", features["function_count"]),
            feature_row("Max nesting depth", features["max_nesting_depth"]),
            feature_row("Avg dependency distance", features["avg_dependency_distance"]),
            feature_row("Max dependency distance", features["max_dependency_distance"]),
            r"    \bottomrule",
            r"  \end{tabular}",
            r"\end{table}",
            "",
            (
                r"Table~\ref{ap:sembench_py_overview} summarizes the current "
                r"SemBench-Python subset derived from CodeNet programs. The benchmark "
                rf"contains {latex_number(stats['query_file_count'])} Python files with "
                r"generated semantic questions across dead-code, data-dependency, "
                r"function-reachability, dominator, loop-reachability, and liveness "
                r"categories. File-level statistics are computed directly from the source "
                r"programs. Dependency distance is measured as the absolute source-line "
                r"distance between the queried variable definition and dependency source "
                r"in the extracted dependency records."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    stats = collect_statistics(args.dataset_dir)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "python_statistics.json"
    latex_path = args.output_dir / "python_statistics_table.tex"

    json_path.write_text(json.dumps(stats, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    latex_path.write_text(render_latex(stats), encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {latex_path}")


if __name__ == "__main__":
    main()

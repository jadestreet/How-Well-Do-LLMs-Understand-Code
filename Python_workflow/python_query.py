#!/usr/bin/env python3
"""Generate SemBench-style yes/no questions from Python parser JSON."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import permutations
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Tuple

import networkx as nx

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_DIR = REPO_ROOT / "SemBench" / "data" / "python_codenet"


TEMPLATES = {
    "function_reachability": [
        lambda src, dst: f"Is there a call path from function {src} to function {dst}?",
        lambda src, dst: f"Can function {src} eventually call function {dst}?",
    ],
    "loop_reachability": [
        lambda cond: f"Can the loop with condition {cond} be skipped entirely?",
        lambda cond: f"Is it possible that the loop with condition {cond} is never executed?",
    ],
    "dominators": [
        lambda a, b: f"Does the statement {a} dominate {b}?",
        lambda a, b: f"Is it guaranteed that whenever {b} is reached, the statement {a} has already been reached?",
    ],
    "data_dependency": [
        lambda a, b: f"Does the value of {a} depend on the value of {b}?",
        lambda a, b: f"Does {b} determine the value stored in {a}?",
    ],
    "liveness": [
        lambda func, var: f"Is variable {var} live at the end of function {func}?",
        lambda func, var: f"Does variable {var} remain in use at the end of function {func}?",
    ],
    "dead_code": [
        lambda code: f"Is the statement {code} unreachable during execution?",
        lambda code: f"Can the statement {code} be considered dead code because it is never executed?",
    ],
}


COMPLEMENTARY_TEMPLATES = {
    "function_reachability": [
        lambda src, dst: f"Is it impossible for function {src} to eventually call function {dst}?",
        lambda src, dst: f"Is there no call path from function {src} to function {dst}?",
    ],
    "loop_reachability": [
        lambda cond: f"Is the loop with condition {cond} always executed?",
    ],
    "liveness": [
        lambda func, var: f"Is variable {var} dead at the end of function {func}?",
    ],
    "dead_code": [
        lambda code: f"Can the statement {code} be reached during execution?",
        lambda code: f"Is it possible for the statement {code} to execute?",
    ],
    "data_dependency": [
        lambda a, b: f"Is the value of {a} independent of the value of {b}?",
        lambda a, b: f"Can {a} be computed without depending on {b}?",
    ],
}


QueryCandidate = Tuple[str, bool]
CategoryGenerator = Callable[[Dict[str, Any], random.Random, int], Tuple[List[str], List[bool]]]


LINE_REF_RE = re.compile(r"line (\d+): <statement>")
STATEMENT_RE = re.compile(r"<statement>.*?</statement>")
PLACEHOLDER_RE = re.compile(r"\{(?:src|dst|cond|func|var|code|a|b|a_id|b_id)\}")


def stmt_id(line: int, code: str) -> str:
    return f"line {line}: <statement> {str(code).strip()} </statement>"


def var_id(blob: Dict[str, Any]) -> str:
    return f"variable {blob['var']} at line {blob['line']}: <statement> {str(blob['code']).strip()} </statement>"


def choose_by_label(candidates: Iterable[QueryCandidate], max_query: int, rng: random.Random) -> Tuple[List[str], List[bool]]:
    by_label = {True: [], False: []}
    for query, label in candidates:
        if query and label in by_label:
            by_label[label].append(query)
    for items in by_label.values():
        rng.shuffle(items)
    queries: List[str] = []
    truth: List[bool] = []
    for label in (True, False):
        for query in by_label[label][:max_query]:
            queries.append(query)
            truth.append(label)
    combined = list(zip(queries, truth))
    rng.shuffle(combined)
    if not combined:
        return [], []
    return [q for q, _ in combined], [t for _, t in combined]


def fill_original_then_one_sided(
    original: List[QueryCandidate],
    fallback: List[QueryCandidate],
    max_query: int,
    rng: random.Random,
) -> Tuple[List[str], List[bool]]:
    labels = {label for _, label in original}
    if len(labels) >= 2:
        return choose_by_label(original, max_query, rng)
    return choose_by_label(original + fallback, max_query, rng)


def build_call_graph(parsed: Dict[str, Any]) -> nx.DiGraph:
    graph = nx.DiGraph()
    names = {fn["name"] for fn in parsed.get("functions", [])}
    for fn in parsed.get("functions", []):
        graph.add_node(fn["name"])
        for call in fn.get("calls", []):
            if call in names:
                graph.add_edge(fn["name"], call)
    return graph


def generate_function_reachability(parsed: Dict[str, Any], rng: random.Random, max_query: int) -> Tuple[List[str], List[bool]]:
    graph = build_call_graph(parsed)
    pairs = sorted(permutations(graph.nodes, 2))
    rng.shuffle(pairs)
    original: List[QueryCandidate] = []
    complementary: List[QueryCandidate] = []
    for src, dst in pairs:
        label = nx.has_path(graph, src, dst)
        original.append((rng.choice(TEMPLATES["function_reachability"])(src, dst), label))
        complementary.append((rng.choice(COMPLEMENTARY_TEMPLATES["function_reachability"])(src, dst), not label))
    return fill_original_then_one_sided(original, complementary, max_query, rng)


def generate_loop_reachability(parsed: Dict[str, Any], rng: random.Random, max_query: int) -> Tuple[List[str], List[bool]]:
    original: List[QueryCandidate] = []
    complementary: List[QueryCandidate] = []
    for loop in sorted(parsed.get("loops", []), key=lambda x: (x["function"], x["line"])):
        certainty = loop.get("certainty", "unknown")
        cond = str(loop.get("cond", "")).strip()
        if certainty == "unknown" or not cond:
            continue
        label = certainty == "never_runs"
        original.append((rng.choice(TEMPLATES["loop_reachability"])(cond), label))
        complementary.append((rng.choice(COMPLEMENTARY_TEMPLATES["loop_reachability"])(cond), not label))
    return fill_original_then_one_sided(original, complementary, max_query, rng)


def generate_dominators(parsed: Dict[str, Any], rng: random.Random, max_query: int) -> Tuple[List[str], List[bool]]:
    positives = parsed.get("strict_dominators", [])
    original: List[QueryCandidate] = []
    reversed_pairs: List[QueryCandidate] = []
    pos_set = {(r["function"], r["a_line"], r["a_code"], r["b_line"], r["b_code"]) for r in positives}
    for rec in positives:
        if not str(rec.get("a_code", "")).strip() or not str(rec.get("b_code", "")).strip():
            continue
        a = stmt_id(rec["a_line"], rec["a_code"])
        b = stmt_id(rec["b_line"], rec["b_code"])
        original.append((rng.choice(TEMPLATES["dominators"])(a, b), True))
        rev_key = (rec["function"], rec["b_line"], rec["b_code"], rec["a_line"], rec["a_code"])
        if rev_key in pos_set:
            continue
        rev_a = stmt_id(rec["b_line"], rec["b_code"])
        rev_b = stmt_id(rec["a_line"], rec["a_code"])
        reversed_pairs.append((rng.choice(TEMPLATES["dominators"])(rev_a, rev_b), False))
    return fill_original_then_one_sided(original, reversed_pairs, max_query, rng)


def generate_data_dependency(parsed: Dict[str, Any], rng: random.Random, max_query: int) -> Tuple[List[str], List[bool]]:
    deps = parsed.get("var_dependencies", [])
    original: List[QueryCandidate] = []
    flipped_or_complementary: List[QueryCandidate] = []
    must_set = {
        (
            rec["from"]["var"],
            rec["from"]["line"],
            rec["depends_on"]["var"],
            rec["depends_on"]["line"],
        )
        for rec in deps
        if rec.get("label") == "must"
    }
    for rec in deps:
        label = rec.get("label")
        if label not in {"must", "negative"}:
            continue
        try:
            target = var_id(rec["from"])
            source = var_id(rec["depends_on"])
        except KeyError:
            continue
        truth = label == "must"
        original.append((rng.choice(TEMPLATES["data_dependency"])(target, source), truth))
        reverse_key = (
            rec["depends_on"]["var"],
            rec["depends_on"]["line"],
            rec["from"]["var"],
            rec["from"]["line"],
        )
        if label == "must" and reverse_key not in must_set:
            flipped_or_complementary.append((rng.choice(TEMPLATES["data_dependency"])(source, target), False))
        elif label == "negative":
            flipped_or_complementary.append((rng.choice(COMPLEMENTARY_TEMPLATES["data_dependency"])(target, source), True))
    return fill_original_then_one_sided(original, flipped_or_complementary, max_query, rng)


def generate_liveness(parsed: Dict[str, Any], rng: random.Random, max_query: int) -> Tuple[List[str], List[bool]]:
    original: List[QueryCandidate] = []
    complementary: List[QueryCandidate] = []
    funcs = parsed.get("liveness", {}).get("functions", {})
    for func in sorted(funcs):
        liveout = funcs[func].get("liveout", {})
        for var in sorted(liveout):
            label = bool(liveout[var])
            original.append((rng.choice(TEMPLATES["liveness"])(func, var), label))
            complementary.append((rng.choice(COMPLEMENTARY_TEMPLATES["liveness"])(func, var), not label))
    return fill_original_then_one_sided(original, complementary, max_query, rng)


def generate_dead_code(parsed: Dict[str, Any], rng: random.Random, max_query: int) -> Tuple[List[str], List[bool]]:
    original: List[QueryCandidate] = []
    complementary: List[QueryCandidate] = []
    for stmt in parsed.get("dead_code", []):
        code = str(stmt.get("code", "")).strip()
        if not code:
            continue
        label = bool(stmt.get("dead"))
        original.append((rng.choice(TEMPLATES["dead_code"])(code), label))
        complementary.append((rng.choice(COMPLEMENTARY_TEMPLATES["dead_code"])(code), not label))
    return fill_original_then_one_sided(original, complementary, max_query, rng)


def generate_queries(parsed: Dict[str, Any], rng: random.Random, max_query: int) -> Tuple[Dict[str, List[str]], Dict[str, List[bool]]]:
    generators = {
        "function_reachability": generate_function_reachability,
        "loop_reachability": generate_loop_reachability,
        "dominators": generate_dominators,
        "data_dependency": generate_data_dependency,
        "liveness": generate_liveness,
        "dead_code": generate_dead_code,
    }
    queries: Dict[str, List[str]] = {}
    truth: Dict[str, List[bool]] = {}
    if parsed.get("unsupported"):
        return {key: [] for key in generators}, {key: [] for key in generators}
    for category, generator in generators.items():
        q, t = generator(parsed, rng, max_query)
        queries[category] = q
        truth[category] = t
    return queries, truth


def stable_file_seed(seed: int, name: str) -> int:
    digest = hashlib.sha256(f"{seed}:{name}".encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def source_line_numbers(code_path: Path) -> set[int]:
    try:
        return set(range(1, len(code_path.read_text(encoding="utf-8").splitlines()) + 1))
    except UnicodeDecodeError:
        return set(range(1, len(code_path.read_text(errors="ignore").splitlines()) + 1))


def parsed_line_numbers(parsed: Dict[str, Any]) -> set[int]:
    lines: set[int] = set()
    for key in ("cfg_statements", "dead_code", "loops"):
        for item in parsed.get(key, []):
            if isinstance(item, dict) and isinstance(item.get("line"), int):
                lines.add(item["line"])
    for item in parsed.get("strict_dominators", []):
        for field in ("a_line", "b_line"):
            if isinstance(item.get(field), int):
                lines.add(item[field])
    for item in parsed.get("var_dependencies", []):
        for field in ("from", "depends_on"):
            blob = item.get(field, {})
            if isinstance(blob, dict) and isinstance(blob.get("line"), int):
                lines.add(blob["line"])
    return lines


def validate_outputs(
    path: Path,
    code_path: Path,
    parsed: Dict[str, Any],
    queries: Dict[str, List[str]],
    truth: Dict[str, List[bool]],
    max_query: int,
) -> None:
    parsed_lines = parsed_line_numbers(parsed)
    source_lines = source_line_numbers(code_path)
    for category, prompts in queries.items():
        labels = truth.get(category)
        if labels is None:
            raise ValueError(f"{path.name}: missing ground truth for {category}")
        if len(prompts) != len(labels):
            raise ValueError(f"{path.name}: query/truth length mismatch in {category}")
        if len(prompts) > max_query * 2:
            raise ValueError(f"{path.name}: too many queries in {category}: {len(prompts)}")
        if labels.count(True) > max_query or labels.count(False) > max_query:
            raise ValueError(f"{path.name}: too many same-label queries in {category}: {labels}")
        for query in prompts:
            if not query or not query.strip():
                raise ValueError(f"{path.name}: empty query in {category}")
            prompt_without_code = STATEMENT_RE.sub("<statement></statement>", query)
            if PLACEHOLDER_RE.search(prompt_without_code):
                raise ValueError(f"{path.name}: unresolved placeholder in {category}: {query}")
            if "<statement>  </statement>" in query:
                raise ValueError(f"{path.name}: empty statement in {category}: {query}")
            if "unknown" in query.lower():
                raise ValueError(f"{path.name}: unresolved unknown value in {category}: {query}")
            for line in map(int, LINE_REF_RE.findall(query)):
                if line not in parsed_lines:
                    raise ValueError(f"{path.name}: line {line} not found in parsed JSON for {category}")
                if line not in source_lines:
                    raise ValueError(f"{path.name}: line {line} not found in source file for {category}")


def process_file(path: Path, code_path: Path, query_dir: Path, truth_dir: Path, seed: int, max_query: int) -> str:
    parsed = json.loads(path.read_text(encoding="utf-8"))
    rng = random.Random(stable_file_seed(seed, path.name))
    queries, truth = generate_queries(parsed, rng, max_query)
    validate_outputs(path, code_path, parsed, queries, truth, max_query)
    (query_dir / path.name).write_text(json.dumps(queries, indent=2, sort_keys=True), encoding="utf-8")
    (truth_dir / path.name).write_text(json.dumps(truth, indent=2, sort_keys=True), encoding="utf-8")
    return "skipped unsupported" if parsed.get("unsupported") else "generated"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Python SemBench-style questions.")
    parser.add_argument("--parsed-dir", type=Path, default=DEFAULT_DATASET_DIR / "parsed_code")
    parser.add_argument("--code-dir", type=Path, default=DEFAULT_DATASET_DIR / "code")
    parser.add_argument("--query-dir", type=Path, default=DEFAULT_DATASET_DIR / "queries")
    parser.add_argument("--ground-truth-dir", type=Path, default=DEFAULT_DATASET_DIR / "ground_truth")
    parser.add_argument("--max-query", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--workers", type=int, default=max(1, os.cpu_count() or 4))
    args = parser.parse_args()

    parsed_dir = args.parsed_dir
    code_dir = args.code_dir
    query_dir = args.query_dir
    truth_dir = args.ground_truth_dir
    query_dir.mkdir(parents=True, exist_ok=True)
    truth_dir.mkdir(parents=True, exist_ok=True)
    paths = sorted(path for path in parsed_dir.glob("*.json") if (code_dir / f"{path.stem}.py").is_file())
    missing_code = sorted(path.stem for path in parsed_dir.glob("*.json") if not (code_dir / f"{path.stem}.py").is_file())
    for stem in missing_code:
        print(f"skipped missing source: {stem}")

    if args.workers == 1:
        for path in paths:
            status = process_file(path, code_dir / f"{path.stem}.py", query_dir, truth_dir, args.seed, args.max_query)
            print(f"{status}: {path.stem}")
        return

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(process_file, path, code_dir / f"{path.stem}.py", query_dir, truth_dir, args.seed, args.max_query): path
            for path in paths
        }
        for future in as_completed(futures):
            path = futures[future]
            status = future.result()
            print(f"{status}: {path.stem}")


if __name__ == "__main__":
    main()
'''
python Python_workflow/python_query.py \
--parsed-dir SemBench/data/python_codenet/parsed_code \
--code-dir SemBench/data/python_codenet/code \
--query-dir SemBench/data/python_codenet/queries \
--ground-truth-dir SemBench/data/python_codenet/ground_truth \
--workers 20
'''

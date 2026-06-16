#!/usr/bin/env python3
"""Run semantic self-checks for the Python SemBench workflow."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "Python_workflow"
TOY_DIR = WORKFLOW / "tests" / "toy_programs"
EXPECTED = WORKFLOW / "tests" / "expected_labels.json"


def contains_code(records: List[Dict[str, Any]], code_substring: str, **fields: Any) -> bool:
    for rec in records:
        if code_substring not in rec.get("code", ""):
            continue
        if all(rec.get(key) == value for key, value in fields.items()):
            return True
    return False


def build_graph(parsed: Dict[str, Any]) -> nx.DiGraph:
    graph = nx.DiGraph()
    names = {fn["name"] for fn in parsed.get("functions", [])}
    for fn in parsed.get("functions", []):
        graph.add_node(fn["name"])
        for call in fn.get("calls", []):
            if call in names:
                graph.add_edge(fn["name"], call)
    return graph


def check_function_reachability(parsed: Dict[str, Any], expected: Dict[str, Any]) -> Tuple[bool, str, str]:
    graph = build_graph(parsed)
    extracted = {
        "reachable": [[a, b] for a, b in expected["reachable"] if nx.has_path(graph, a, b)],
        "not_reachable": [[a, b] for a, b in expected["not_reachable"] if not nx.has_path(graph, a, b)],
    }
    return extracted == expected, json.dumps(expected, sort_keys=True), json.dumps(extracted, sort_keys=True)


def check_dead_code(parsed: Dict[str, Any], expected: Dict[str, Any]) -> Tuple[bool, str, str]:
    extracted = {"dead": [], "reachable": []}
    for code in expected["dead"]:
        if contains_code(parsed["dead_code"], code, dead=True):
            extracted["dead"].append(code)
    for code in expected["reachable"]:
        if contains_code(parsed["dead_code"], code, dead=False):
            extracted["reachable"].append(code)
    return extracted == expected, json.dumps(expected, sort_keys=True), json.dumps(extracted, sort_keys=True)


def check_loop_reachability(parsed: Dict[str, Any], expected: Dict[str, Any]) -> Tuple[bool, str, str]:
    extracted = {"never_runs": [], "always_runs": []}
    for loop in parsed.get("loops", []):
        cond = loop.get("cond", "")
        if loop.get("certainty") in extracted:
            for wanted in expected[loop["certainty"]]:
                if wanted in cond and wanted not in extracted[loop["certainty"]]:
                    extracted[loop["certainty"]].append(wanted)
    return extracted == expected, json.dumps(expected, sort_keys=True), json.dumps(extracted, sort_keys=True)


def check_dominators(parsed: Dict[str, Any], expected: Dict[str, Any]) -> Tuple[bool, str, str]:
    pos = []
    neg = []
    doms = parsed.get("strict_dominators", [])
    for a, b in expected["dominates"]:
        if any(a in rec["a_code"] and b in rec["b_code"] for rec in doms):
            pos.append([a, b])
    for a, b in expected["does_not_dominate"]:
        if not any(rec["a_code"] == a and b in rec["b_code"] for rec in doms):
            neg.append([a, b])
    extracted = {"dominates": pos, "does_not_dominate": neg}
    return extracted == expected, json.dumps(expected, sort_keys=True), json.dumps(extracted, sort_keys=True)


def check_data_dependency(parsed: Dict[str, Any], expected: Dict[str, Any]) -> Tuple[bool, str, str]:
    must = []
    neg = []
    deps = parsed.get("var_dependencies", [])
    for target, source in expected["must"]:
        if any(rec["label"] == "must" and rec["from"]["var"] == target and rec["depends_on"]["var"] == source for rec in deps):
            must.append([target, source])
    for target, source in expected["negative"]:
        if any(rec["label"] == "negative" and rec["from"]["var"] == target and rec["depends_on"]["var"] == source for rec in deps):
            neg.append([target, source])
    extracted = {"must": must, "negative": neg}
    return extracted == expected, json.dumps(expected, sort_keys=True), json.dumps(extracted, sort_keys=True)


def check_liveness(parsed: Dict[str, Any], expected: Dict[str, Any]) -> Tuple[bool, str, str]:
    funcs = parsed.get("liveness", {}).get("functions", {})
    extracted = {"liveout": {}, "live_before": []}
    for func, vars_map in expected["liveout"].items():
        extracted["liveout"][func] = {}
        liveout = funcs.get(func, {}).get("liveout", {})
        for var, expected_value in vars_map.items():
            if liveout.get(var) == expected_value:
                extracted["liveout"][func][var] = expected_value
    for item in expected["live_before"]:
        func = item["function"]
        line_contains = item["code"]
        var = item["var"]
        points = funcs.get(func, {}).get("live_before", [])
        if any(line_contains in point.get("code", "") and var in point.get("vars", []) for point in points):
            extracted["live_before"].append(item)
    return extracted == expected, json.dumps(expected, sort_keys=True), json.dumps(extracted, sort_keys=True)


CHECKERS = {
    "function_reachability": check_function_reachability,
    "dead_code": check_dead_code,
    "loop_reachability": check_loop_reachability,
    "dominators": check_dominators,
    "data_dependency": check_data_dependency,
    "liveness": check_liveness,
}


def main() -> int:
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="python_workflow_self_check_") as tmp:
        out_dir = Path(tmp) / "parsed"
        subprocess.run(
            [sys.executable, str(WORKFLOW / "python_parser.py"), "--code-dir", str(TOY_DIR), "--output-dir", str(out_dir)],
            check=True,
            cwd=str(ROOT),
        )
        parsed = {path.name: json.loads(path.read_text(encoding="utf-8")) for path in sorted(out_dir.glob("*.json"))}

    failures = 0
    for category, spec in expected.items():
        file_name = spec["file"]
        category_expected = spec["labels"]
        category_parsed = parsed[file_name]
        print(f"\n[{category}] extracted records:")
        if category == "function_reachability":
            print(json.dumps(category_parsed.get("functions", []), indent=2))
        elif category == "dead_code":
            print(json.dumps(category_parsed.get("dead_code", []), indent=2))
        elif category == "loop_reachability":
            print(json.dumps(category_parsed.get("loops", []), indent=2))
        elif category == "dominators":
            print(json.dumps(category_parsed.get("strict_dominators", [])[:20], indent=2))
        elif category == "data_dependency":
            print(json.dumps(category_parsed.get("var_dependencies", []), indent=2))
        elif category == "liveness":
            print(json.dumps(category_parsed.get("liveness", {}), indent=2))

        ok, expected_text, extracted_text = CHECKERS[category](category_parsed, category_expected)
        if ok:
            print(f"PASS {category}")
        else:
            failures += 1
            print(f"FAIL {category}")
            print(f"  expected:  {expected_text}")
            print(f"  extracted: {extracted_text}")

    if failures:
        print(f"\nSelf-check failed: {failures} category/categories failed.")
        return 1
    print("\nSelf-check PASS: all categories matched expected labels.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

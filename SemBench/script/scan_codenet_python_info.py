#!/usr/bin/env python3
import ast
import csv
import statistics
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed


DEFAULT_ROOT = Path(
    ""
    "SemBench/data/python/codenet_python/Project_CodeNet_Python800"
)

DEFAULT_OUT = Path(
    ""
    "SemBench/data/python/codenet_python/codenet_python800_file_stats.csv"
)


def count_source_lines(text: str):
    lines = text.splitlines()
    total_lines = len(lines)
    blank_lines = sum(1 for ln in lines if not ln.strip())
    comment_lines = sum(1 for ln in lines if ln.strip().startswith("#"))
    code_lines = total_lines - blank_lines - comment_lines
    return total_lines, code_lines, blank_lines, comment_lines


class ASTCounter(ast.NodeVisitor):
    def __init__(self):
        self.function_count = 0
        self.top_level_function_count = 0
        self.nested_function_count = 0
        self.class_count = 0
        self.method_count = 0
        self.loop_count = 0
        self.if_count = 0
        self.return_count = 0
        self.assign_count = 0
        self.call_count = 0
        self.max_depth = 0
        self._function_depth = 0
        self._node_depth = 0
        self._class_depth = 0

    def generic_visit(self, node):
        self._node_depth += 1
        self.max_depth = max(self.max_depth, self._node_depth)
        super().generic_visit(node)
        self._node_depth -= 1

    def visit_FunctionDef(self, node):
        self.function_count += 1
        if self._class_depth > 0:
            self.method_count += 1
        elif self._function_depth == 0:
            self.top_level_function_count += 1
        else:
            self.nested_function_count += 1

        self._function_depth += 1
        self.generic_visit(node)
        self._function_depth -= 1

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node):
        self.class_count += 1
        self._class_depth += 1
        self.generic_visit(node)
        self._class_depth -= 1

    def visit_For(self, node):
        self.loop_count += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.loop_count += 1
        self.generic_visit(node)

    def visit_If(self, node):
        self.if_count += 1
        self.generic_visit(node)

    def visit_Return(self, node):
        self.return_count += 1
        self.generic_visit(node)

    def visit_Assign(self, node):
        self.assign_count += 1
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        self.assign_count += 1
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        self.assign_count += 1
        self.generic_visit(node)

    def visit_Call(self, node):
        self.call_count += 1
        self.generic_visit(node)


def scan_one(path: Path, root: Path):
    rel_path = path.relative_to(root)

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {
            "path": str(path),
            "relative_path": str(rel_path),
            "problem_id": rel_path.parts[0] if len(rel_path.parts) >= 2 else "",
            "file_name": path.name,
            "file_size_bytes": path.stat().st_size if path.exists() else -1,
            "syntax_ok": False,
            "error": f"read_error: {e}",
        }

    total_lines, code_lines, blank_lines, comment_lines = count_source_lines(text)

    row = {
        "path": str(path),
        "relative_path": str(rel_path),
        "problem_id": rel_path.parts[0] if len(rel_path.parts) >= 2 else "",
        "file_name": path.name,
        "file_size_bytes": path.stat().st_size,
        "total_lines": total_lines,
        "code_lines": code_lines,
        "blank_lines": blank_lines,
        "comment_lines": comment_lines,
        "syntax_ok": True,
        "error": "",
        "function_count": 0,
        "top_level_function_count": 0,
        "nested_function_count": 0,
        "class_count": 0,
        "method_count": 0,
        "loop_count": 0,
        "if_count": 0,
        "return_count": 0,
        "assign_count": 0,
        "call_count": 0,
        "max_ast_depth": 0,
    }

    try:
        tree = ast.parse(text, filename=str(path))
        counter = ASTCounter()
        counter.visit(tree)

        row.update({
            "function_count": counter.function_count,
            "top_level_function_count": counter.top_level_function_count,
            "nested_function_count": counter.nested_function_count,
            "class_count": counter.class_count,
            "method_count": counter.method_count,
            "loop_count": counter.loop_count,
            "if_count": counter.if_count,
            "return_count": counter.return_count,
            "assign_count": counter.assign_count,
            "call_count": counter.call_count,
            "max_ast_depth": counter.max_depth,
        })
    except SyntaxError as e:
        row["syntax_ok"] = False
        row["error"] = f"syntax_error: line {e.lineno}: {e.msg}"
    except Exception as e:
        row["syntax_ok"] = False
        row["error"] = f"ast_error: {type(e).__name__}: {e}"

    return row


def percentile(values, p):
    if not values:
        return None
    values = sorted(values)
    idx = round((len(values) - 1) * p / 100)
    return values[idx]


def print_summary(rows):
    total = len(rows)
    syntax_ok = sum(1 for r in rows if r.get("syntax_ok") is True)
    syntax_bad = total - syntax_ok

    code_lines = [int(r["code_lines"]) for r in rows if r.get("syntax_ok") is True]
    functions = [int(r["function_count"]) for r in rows if r.get("syntax_ok") is True]
    loops = [int(r["loop_count"]) for r in rows if r.get("syntax_ok") is True]
    classes = [int(r["class_count"]) for r in rows if r.get("syntax_ok") is True]

    def stat_block(name, vals):
        if not vals:
            print(f"{name}: no valid values")
            return
        print(f"{name}:")
        print(f"  min={min(vals)}")
        print(f"  p25={percentile(vals, 25)}")
        print(f"  median={percentile(vals, 50)}")
        print(f"  mean={statistics.mean(vals):.2f}")
        print(f"  p75={percentile(vals, 75)}")
        print(f"  p90={percentile(vals, 90)}")
        print(f"  max={max(vals)}")

    print("\n========== CodeNet Python800 Scan Summary ==========")
    print(f"Total files: {total}")
    print(f"AST-parseable files: {syntax_ok}")
    print(f"Syntax/error files: {syntax_bad}")

    problem_ids = {r["problem_id"] for r in rows if r.get("problem_id")}
    print(f"Problem subdirs: {len(problem_ids)}")

    print("\n--- Distribution ---")
    stat_block("Code lines", code_lines)
    stat_block("Function count", functions)
    stat_block("Loop count", loops)
    stat_block("Class count", classes)

    print("\n--- Useful selection counts ---")
    candidates = [
        r for r in rows
        if r.get("syntax_ok") is True
        and 20 <= int(r["code_lines"]) <= 500
        and int(r["function_count"]) >= 1
        and int(r["loop_count"]) >= 1
    ]
    print("syntax_ok && 20<=code_lines<=500 && function_count>=1 && loop_count>=1:")
    print(f"  {len(candidates)}")

    multi_func = [r for r in candidates if int(r["function_count"]) >= 2]
    print("above + function_count>=2:")
    print(f"  {len(multi_func)}")

    no_class = [r for r in candidates if int(r["class_count"]) == 0]
    print("above + class_count==0:")
    print(f"  {len(no_class)}")

    print("====================================================\n")


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="Root directory to scan")
    parser.add_argument("--output", default=str(DEFAULT_OUT), help="Output CSV path")
    parser.add_argument("--workers", type=int, default=16, help="Number of worker processes")
    parser.add_argument(
        "--all-files",
        action="store_true",
        help="Scan all files. By default, scan files ending with .py or files without suffix.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    if not root.is_dir():
        raise SystemExit(f"ERROR: root directory does not exist: {root}")

    if args.all_files:
        files = [p for p in root.rglob("*") if p.is_file()]
    else:
        files = [
            p for p in root.rglob("*")
            if p.is_file() and (p.suffix == ".py" or p.suffix == "")
        ]

    print(f"Scanning root: {root}")
    print(f"Candidate files: {len(files)}")
    print(f"Output CSV: {output}")

    rows = []
    with ProcessPoolExecutor(max_workers=max(1, args.workers)) as ex:
        futures = [ex.submit(scan_one, p, root) for p in files]
        for i, fut in enumerate(as_completed(futures), 1):
            rows.append(fut.result())
            if i % 5000 == 0:
                print(f"Processed {i}/{len(files)} files")

    fieldnames = [
        "problem_id",
        "file_name",
        "relative_path",
        "path",
        "file_size_bytes",
        "total_lines",
        "code_lines",
        "blank_lines",
        "comment_lines",
        "syntax_ok",
        "error",
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
    ]

    rows.sort(key=lambda r: (r.get("problem_id", ""), r.get("relative_path", "")))

    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print_summary(rows)
    print(f"Saved CSV to: {output}")


if __name__ == "__main__":
    main()

'''
cd <repo-root>

python SemBench/script/scan_codenet_python_info.py \
  --root SemBench/data/python/codenet_python/Project_CodeNet_Python800 \
  --output SemBench/data/python/codenet_python/codenet_python800_file_stats.csv \
  --workers 32
'''

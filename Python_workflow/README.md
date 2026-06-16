# Python SemBench Workflow

This folder contains a conservative Python counterpart to the C SemBench parser/query workflow.

## Run The Parser

From the repository root:

```bash
python Python_workflow/python_parser.py \
  --code-dir SemBench/data/python/code \
  --output-dir SemBench/data/python/parsed_code
```

The parser emits one JSON file per input program. Files with unsupported dynamic behavior still get a JSON file, but include `unsupported: true` and `unsupported_reasons`.

## Run The Query Generator

```bash
python Python_workflow/python_query.py \
  --parsed-dir Python_workflow/parsed_code \
  --query-dir Python_workflow/queries \
  --ground-truth-dir Python_workflow/ground_truth
```

Unsupported files are skipped by the query generator and receive empty category lists.

## Run The Self-Check

```bash
python Python_workflow/run_self_check.py
```

The self-check parses toy programs in `Python_workflow/tests/toy_programs`, prints extracted records, compares them against `Python_workflow/tests/expected_labels.json`, and reports PASS/FAIL per category.

## Unsupported In This First Version

The workflow is intentionally conservative. It marks files unsupported when it sees `eval`, `exec`, `getattr`, `globals`, `locals`, `__import__`, unresolved non-builtin function calls, unresolved attribute calls, decorators, async functions, lambdas, `with`, `try`, or attribute assignment. This avoids producing labels for dynamic dispatch, reflection, monkey patching, or behavior that would require whole-program/runtime analysis.

## Semantic Approximations

- Function reachability: top-level `def` functions form a directed call graph. Only direct calls to known top-level functions are included.
- Loop reachability / dead-code-loop: `while False`, `for ... in range(0)`, and empty literal iterables are `never_runs`; literal non-empty ranges/iterables and `while True` are `always_runs`; other loops are retained as `unknown` and skipped by the query generator.
- Dead-code statement: a source-level CFG marks statements unreachable after unconditional terminators and inside statically false branches or never-run loop bodies.
- Dominators: statement-level strict dominators are computed over the custom source CFG with `networkx` graph data structures.
- Data dependency: assignments produce `must` dependencies from assigned variables to variables used in the right-hand side, including simple transitive dependencies. Constant assignments produce no positive dependencies and may be used for negative examples.
- Liveness: "live at the end of function" is defined as live immediately before a function returns. Variables used in return expressions are `liveout: true`; other local variables are false unless they are return variables. The parser also emits `live_before` records from a backward source-level def-use pass.

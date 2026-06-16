"""Conservative Python semantic extractor for SemBench-style questions.

The parser is source-level and deterministic. It intentionally avoids runtime
execution and marks files with dynamic or unresolved behavior as unsupported
instead of forcing questionable labels.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import symtable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union
from concurrent.futures import ProcessPoolExecutor, as_completed

import networkx as nx

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PYTHON_DATA_DIR = REPO_ROOT / "SemBench" / "data" / "python"


SAFE_BUILTIN_CALLS = {
    "abs",
    "all",
    "any",
    "bool",
    "callable",
    "chr",
    "dict",
    "divmod",
    "enumerate",
    "filter",
    "float",
    "hash",
    "int",
    "isinstance",
    "iter",
    "len",
    "list",
    "map",
    "max",
    "min",
    "next",
    "ord",
    "print",
    "range",
    "reversed",
    "round",
    "set",
    "slice",
    "sorted",
    "str",
    "sum",
    "tuple",
    "type",
    "zip",
}

SAFE_EXCEPTION_CALLS = {
    "ArithmeticError",
    "AssertionError",
    "AttributeError",
    "Exception",
    "IndexError",
    "KeyError",
    "LookupError",
    "RuntimeError",
    "StopIteration",
    "TypeError",
    "ValueError",
}

SAFE_COLLECTION_CONSTRUCTORS = {"Counter", "OrderedDict", "defaultdict", "deque"}

SAFE_METHOD_CALLS = {
    "add",
    "append",
    "appendleft",
    "clear",
    "count",
    "discard",
    "endswith",
    "extend",
    "get",
    "index",
    "insert",
    "isalnum",
    "isdigit",
    "isspace",
    "items",
    "join",
    "keys",
    "lower",
    "lstrip",
    "pop",
    "popitem",
    "popleft",
    "remove",
    "move_to_end",
    "replace",
    "reverse",
    "rstrip",
    "setdefault",
    "sort",
    "split",
    "startswith",
    "strip",
    "upper",
    "update",
    "values",
}

MUTATING_METHOD_CALLS = {
    "add",
    "append",
    "appendleft",
    "clear",
    "discard",
    "extend",
    "insert",
    "move_to_end",
    "pop",
    "popitem",
    "popleft",
    "remove",
    "reverse",
    "setdefault",
    "sort",
    "update",
}

SAFE_MODULE_CALLS = {
    "heapq": {"heapify", "heappop", "heappush"},
}

SAFE_DECORATORS = {"dataclass", "staticmethod", "classmethod", "property"}

DYNAMIC_CALLS = {"eval", "exec", "getattr", "globals", "locals", "__import__", "setattr", "delattr"}
SUPPORTED_EXTENSIONS = (".py",)
TERMINATORS = (ast.Return, ast.Raise, ast.Break, ast.Continue)
MODULE_SCOPE = "__module__"
StaticValue = Union[int, Tuple[str, int]]

def is_incomplete_record(parsed: Dict[str, Any]) -> bool:
    return bool(
        parsed.get("unsupported")
        #or parsed.get("unsupported_reasons")
        #or parsed.get("unsupported_categories")
    )


def process_one_file(path_str: str, output_dir_str: str) -> Tuple[str, str]:
    path = Path(path_str)
    out_dir = Path(output_dir_str)
    incomplete_dir = out_dir / "incomplete"

    try:
        parsed = parse_python_file(str(path))
        target_dir = incomplete_dir if is_incomplete_record(parsed) else out_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        (target_dir / output_name(path)).write_text(
            json.dumps(parsed, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        status = "incomplete" if target_dir == incomplete_dir else "parsed"
        return status, str(path)

    except SyntaxError as exc:
        skipped = {
            "file": str(path),
            "unsupported": True,
            "unsupported_reasons": [f"syntax error: {exc}"],
            "unsupported_categories": {},
        }
        incomplete_dir.mkdir(parents=True, exist_ok=True)
        (incomplete_dir / output_name(path)).write_text(
            json.dumps(skipped, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return "incomplete", f"{path}: {exc}"


def source_segment(source: str, node: ast.AST) -> str:
    segment = ast.get_source_segment(source, node)
    if segment:
        return " ".join(segment.strip().split())
    lineno = getattr(node, "lineno", None)
    if lineno is None:
        return ast.dump(node)
    lines = source.splitlines()
    if 1 <= lineno <= len(lines):
        return lines[lineno - 1].strip()
    return ast.dump(node)


def expr_text(source: str, node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return source_segment(source, node)


def literal_bool(node: ast.AST) -> Optional[bool]:
    if isinstance(node, ast.Constant) and isinstance(node.value, bool):
        return node.value
    if isinstance(node, ast.Constant) and node.value in (0, 1, "", (), [], {}):
        return bool(node.value)
    return None


def stable_name(node: ast.AST) -> Optional[str]:
    """Return a deterministic source-level name for simple variables/fields.

    Attribute names such as ``self.x`` are intentionally treated as variables.
    This is object-insensitive, but good enough for conservative SemBench
    def-use questions without pretending to know aliases.
    """
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = stable_name(node.value)
        if base:
            return f"{base}.{node.attr}"
    if isinstance(node, ast.Subscript):
        return stable_name(node.value)
    return None


def assigned_names(target: ast.AST) -> Set[str]:
    names: Set[str] = set()
    name = stable_name(target)
    if name:
        names.add(name)
    elif isinstance(target, (ast.Tuple, ast.List)):
        for elt in target.elts:
            names.update(assigned_names(elt))
    return names


def target_uses(target: ast.AST) -> Set[str]:
    """Uses needed to address a target, e.g. ``arr[i] = x`` uses ``i``."""
    if isinstance(target, ast.Subscript):
        return loaded_names(target.slice)
    if isinstance(target, ast.Tuple) or isinstance(target, ast.List):
        uses: Set[str] = set()
        for elt in target.elts:
            uses.update(target_uses(elt))
        return uses
    return set()


class UseCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.names: Set[str] = set()
        self._bound_stack: List[Set[str]] = [set()]

    @property
    def bound(self) -> Set[str]:
        return self._bound_stack[-1]

    def visit_Name(self, node: ast.Name) -> Any:
        if isinstance(node.ctx, ast.Load) and node.id not in self.bound:
            self.names.add(node.id)

    def visit_Attribute(self, node: ast.Attribute) -> Any:
        if isinstance(node.ctx, ast.Load):
            name = stable_name(node)
            if name and name.split(".")[0] not in self.bound:
                self.names.add(name)
            return
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        base = stable_name(node.value)
        if base and base.split(".")[0] not in self.bound:
            self.names.add(base)
        self.visit(node.slice)

    def visit_Call(self, node: ast.Call) -> Any:
        # Calls use their receiver and arguments. The callee name itself is
        # resolved separately for reachability, so it is not a value dependency.
        if isinstance(node.func, ast.Attribute):
            receiver = stable_name(node.func.value)
            if receiver and receiver.split(".")[0] not in self.bound:
                self.names.add(receiver)
        for arg in node.args:
            self.visit(arg)
        for kw in node.keywords:
            if kw.value:
                self.visit(kw.value)

    def visit_ListComp(self, node: ast.ListComp) -> Any:
        self._visit_comprehension(node.elt, node.generators)

    def visit_SetComp(self, node: ast.SetComp) -> Any:
        self._visit_comprehension(node.elt, node.generators)

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> Any:
        self._visit_comprehension(node.elt, node.generators)

    def visit_DictComp(self, node: ast.DictComp) -> Any:
        self._visit_comprehension(node.key, node.generators)
        self.visit(node.value)

    def _visit_comprehension(self, elt: ast.AST, generators: List[ast.comprehension]) -> None:
        bound = set(self.bound)
        self._bound_stack.append(bound)
        try:
            for gen in generators:
                self.visit(gen.iter)
                bound.update(assigned_names(gen.target))
                for cond in gen.ifs:
                    self.visit(cond)
            self.visit(elt)
        finally:
            self._bound_stack.pop()


def loaded_names(node: ast.AST) -> Set[str]:
    collector = UseCollector()
    collector.visit(node)
    return collector.names


def stmt_defs_uses(stmt: ast.stmt) -> Tuple[Set[str], Set[str]]:
    defs: Set[str] = set()
    uses: Set[str] = set()
    if isinstance(stmt, ast.Assign):
        for target in stmt.targets:
            defs.update(assigned_names(target))
            uses.update(target_uses(target))
        uses.update(loaded_names(stmt.value))
    elif isinstance(stmt, ast.AnnAssign):
        defs.update(assigned_names(stmt.target))
        uses.update(target_uses(stmt.target))
        if stmt.value:
            uses.update(loaded_names(stmt.value))
    elif isinstance(stmt, ast.AugAssign):
        defs.update(assigned_names(stmt.target))
        uses.update(loaded_names(stmt.target))
        uses.update(target_uses(stmt.target))
        uses.update(loaded_names(stmt.value))
    elif isinstance(stmt, ast.For):
        defs.update(assigned_names(stmt.target))
        uses.update(target_uses(stmt.target))
        uses.update(loaded_names(stmt.iter))
    elif isinstance(stmt, ast.While):
        uses.update(loaded_names(stmt.test))
    elif isinstance(stmt, ast.If):
        uses.update(loaded_names(stmt.test))
    elif isinstance(stmt, ast.Return) and stmt.value:
        uses.update(loaded_names(stmt.value))
    elif isinstance(stmt, ast.Expr):
        uses.update(loaded_names(stmt.value))
        if isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Attribute):
            receiver = stable_name(stmt.value.func.value)
            if receiver and stmt.value.func.attr in MUTATING_METHOD_CALLS:
                defs.add(receiver)
    elif isinstance(stmt, ast.Raise) and stmt.exc:
        uses.update(loaded_names(stmt.exc))
    return defs, uses


def simple_statement_nodes(body: Iterable[ast.stmt]) -> List[ast.stmt]:
    nodes: List[ast.stmt] = []
    for stmt in body:
        nodes.append(stmt)
        if isinstance(stmt, ast.If):
            nodes.extend(simple_statement_nodes(stmt.body))
            nodes.extend(simple_statement_nodes(stmt.orelse))
        elif isinstance(stmt, (ast.For, ast.While)):
            nodes.extend(simple_statement_nodes(stmt.body))
            nodes.extend(simple_statement_nodes(stmt.orelse))
        elif isinstance(stmt, (ast.Try, ast.With, ast.AsyncWith)):
            for attr in ("body", "orelse", "finalbody"):
                nodes.extend(simple_statement_nodes(getattr(stmt, attr, [])))
            if isinstance(stmt, ast.Try):
                for handler in stmt.handlers:
                    nodes.extend(simple_statement_nodes(handler.body))
        elif isinstance(stmt, (ast.FunctionDef, ast.ClassDef)):
            # Nested function/class bodies are parsed as their own scopes, not as
            # statements that execute in the enclosing function.
            continue
    return sorted(nodes, key=lambda n: (getattr(n, "lineno", 0), getattr(n, "col_offset", 0)))


def static_int_value(node: ast.AST, env: Dict[str, StaticValue]) -> Optional[int]:
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    if isinstance(node, ast.Name):
        value = env.get(node.id)
        return value if isinstance(value, int) else None
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        value = static_int_value(node.operand, env)
        return -value if value is not None else None
    if isinstance(node, ast.BinOp):
        left = static_int_value(node.left, env)
        right = static_int_value(node.right, env)
        if left is None or right is None:
            return None
        try:
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.FloorDiv) and right != 0:
                return left // right
        except Exception:
            return None
    return None


def range_length(args: List[ast.AST], env: Optional[Dict[str, StaticValue]] = None) -> Optional[int]:
    env = env or {}
    values: List[int] = []
    for arg in args:
        value = static_int_value(arg, env)
        if value is None:
            return None
        values.append(value)
    try:
        return len(range(*values))
    except TypeError:
        return None


def static_iter_size(node: ast.AST, env: Dict[str, StaticValue]) -> Optional[int]:
    if isinstance(node, ast.Name):
        value = env.get(node.id)
        if isinstance(value, tuple) and value[0] == "len":
            return value[1]
        return None
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "range":
        return range_length(node.args, env)
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return len(node.elts)
    if isinstance(node, ast.Dict):
        return len(node.keys)
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return len(node.value)
    return None


def assigned_root_names(target: ast.AST) -> Set[str]:
    roots: Set[str] = set()
    if isinstance(target, ast.Name):
        roots.add(target.id)
    elif isinstance(target, (ast.Tuple, ast.List)):
        for elt in target.elts:
            roots.update(assigned_root_names(elt))
    elif isinstance(target, ast.Subscript):
        base = target.value
        if isinstance(base, ast.Name):
            roots.add(base.id)
    elif isinstance(target, ast.Attribute):
        base = target.value
        if isinstance(base, ast.Name):
            roots.add(base.id)
    return roots


def update_static_env(stmt: ast.stmt, env: Dict[str, StaticValue]) -> Dict[str, StaticValue]:
    updated = dict(env)
    if isinstance(stmt, ast.Assign):
        for target in stmt.targets:
            for name in assigned_root_names(target):
                updated.pop(name, None)
        if len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
            name = stmt.targets[0].id
            int_value = static_int_value(stmt.value, updated)
            size = static_iter_size(stmt.value, updated)
            if int_value is not None:
                updated[name] = int_value
            elif size is not None:
                updated[name] = ("len", size)
        return updated
    if isinstance(stmt, ast.AnnAssign):
        for name in assigned_root_names(stmt.target):
            updated.pop(name, None)
        if isinstance(stmt.target, ast.Name) and stmt.value is not None:
            int_value = static_int_value(stmt.value, updated)
            size = static_iter_size(stmt.value, updated)
            if int_value is not None:
                updated[stmt.target.id] = int_value
            elif size is not None:
                updated[stmt.target.id] = ("len", size)
        return updated
    if isinstance(stmt, (ast.AugAssign, ast.Delete)):
        targets = [stmt.target] if isinstance(stmt, ast.AugAssign) else stmt.targets
        for target in targets:
            for name in assigned_root_names(target):
                updated.pop(name, None)
        return updated
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Attribute):
        method = stmt.value.func.attr
        receiver = stmt.value.func.value
        if method in MUTATING_METHOD_CALLS and isinstance(receiver, ast.Name):
            updated.pop(receiver.id, None)
    return updated


def loop_certainty(stmt: ast.stmt, env: Optional[Dict[str, StaticValue]] = None) -> Tuple[str, bool]:
    """Return (certainty, reachable_body).

    certainty is one of never_runs, always_runs, unknown. reachable_body follows
    the schema's existing convention: False only when statically never executed.
    """
    env = env or {}
    if isinstance(stmt, ast.While):
        known = literal_bool(stmt.test)
        if known is False:
            return "never_runs", False
        if known is True:
            return "always_runs", True
        return "unknown", True
    if isinstance(stmt, ast.For):
        size = static_iter_size(stmt.iter, env)
        if size == 0:
            return "never_runs", False
        if size is not None and size > 0:
            return "always_runs", True
        return "unknown", True
    return "unknown", True


@dataclass
class CFGNode:
    node_id: int
    function: str
    line: int
    code: str
    kind: str


class CFGBuilder:
    def __init__(self, source: str, function: str):
        self.source = source
        self.function = function
        self.graph = nx.DiGraph()
        self.entry = 0
        self.next_id = 1
        self.nodes: Dict[int, CFGNode] = {}
        self.ast_by_id: Dict[int, ast.stmt] = {}
        self.loop_records: List[Dict[str, Any]] = []
        self.graph.add_node(self.entry)

    def add_stmt(self, stmt: ast.stmt) -> int:
        node_id = self.next_id
        self.next_id += 1
        code = source_segment(self.source, stmt)
        meta = CFGNode(
            node_id=node_id,
            function=self.function,
            line=getattr(stmt, "lineno", -1),
            code=code,
            kind=type(stmt).__name__,
        )
        self.nodes[node_id] = meta
        self.ast_by_id[node_id] = stmt
        self.graph.add_node(node_id)
        return node_id

    def connect(self, preds: Iterable[int], node_id: int) -> None:
        for pred in preds:
            self.graph.add_edge(pred, node_id)

    def build(self, body: List[ast.stmt]) -> None:
        self.build_block(body, [self.entry], {})

    def build_block(self, body: List[ast.stmt], preds: List[int], env: Optional[Dict[str, StaticValue]] = None) -> List[int]:
        current = list(preds)
        static_env = dict(env or {})
        for stmt in body:
            node_id = self.add_stmt(stmt)
            self.connect(current, node_id)

            if isinstance(stmt, ast.If):
                known = literal_bool(stmt.test)
                exits: List[int] = []
                if known is not False:
                    exits.extend(self.build_block(stmt.body, [node_id], static_env.copy()))
                else:
                    self.build_block(stmt.body, [], static_env.copy())
                if known is not True:
                    if stmt.orelse:
                        exits.extend(self.build_block(stmt.orelse, [node_id], static_env.copy()))
                    else:
                        exits.append(node_id)
                elif stmt.orelse:
                    self.build_block(stmt.orelse, [], static_env.copy())
                current = exits
            elif isinstance(stmt, (ast.For, ast.While)):
                certainty, reachable = loop_certainty(stmt, static_env)
                cond = expr_text(self.source, stmt.test) if isinstance(stmt, ast.While) else source_segment(self.source, stmt).split(":")[0]
                self.loop_records.append(
                    {
                        "function": self.function,
                        "header_id": node_id,
                        "line": getattr(stmt, "lineno", -1),
                        "cond": cond,
                        "code": source_segment(self.source, stmt).split(":")[0] + ":",
                        "reachable": reachable,
                        "certainty": certainty,
                    }
                )
                body_preds = [node_id] if reachable else []
                body_env = static_env.copy()
                if isinstance(stmt, ast.For):
                    for name in assigned_root_names(stmt.target):
                        body_env.pop(name, None)
                body_exits = self.build_block(stmt.body, body_preds, body_env)
                for exit_id in body_exits:
                    self.graph.add_edge(exit_id, node_id)
                exits = [node_id]
                if stmt.orelse:
                    exits = self.build_block(stmt.orelse, exits, static_env.copy())
                current = exits
            elif isinstance(stmt, ast.Try):
                # Conservative try CFG: both normal try-body execution and each
                # exception handler are reachable from the try node. This avoids
                # claiming try-body statements dominate code after the handler.
                exits = self.build_block(stmt.body, [node_id], static_env.copy())
                for handler in stmt.handlers:
                    exits.extend(self.build_block(handler.body, [node_id], static_env.copy()))
                if stmt.orelse:
                    exits = self.build_block(stmt.orelse, exits, static_env.copy())
                if stmt.finalbody:
                    current = self.build_block(stmt.finalbody, exits or [node_id], static_env.copy())
                else:
                    current = exits or [node_id]
            elif isinstance(stmt, TERMINATORS):
                current = []
            else:
                current = [node_id]
            static_env = update_static_env(stmt, static_env)
        return current


@dataclass
class FunctionScope:
    name: str
    node: ast.FunctionDef
    parent: Optional[str] = None
    class_name: Optional[str] = None


@dataclass
class AnalysisContext:
    functions: Dict[str, FunctionScope]
    function_order: List[str]
    top_level_functions: Set[str]
    class_names: Set[str]
    class_methods: Dict[str, Dict[str, str]]
    nested_by_parent: Dict[str, Dict[str, str]]
    parent_by_function: Dict[str, Optional[str]]
    class_by_function: Dict[str, Optional[str]]
    imported_names: Dict[str, str]
    module_aliases: Dict[str, str]

    def resolve_name_call(self, current: Optional[str], name: str) -> Optional[str]:
        scope = current
        while scope:
            if self.functions[scope].name.split(".")[-1] == name:
                return scope
            nested = self.nested_by_parent.get(scope, {})
            if name in nested:
                return nested[name]
            scope = self.parent_by_function.get(scope)
        if name in self.top_level_functions:
            return name
        class_name = self.class_constructor_name(name)
        if class_name and f"{class_name}.__init__" in self.functions:
            return f"{class_name}.__init__"
        return None

    def class_constructor_name(self, name: str) -> Optional[str]:
        if name in self.class_names:
            return name
        return None

    def resolve_attribute_call(self, current: Optional[str], call: ast.Call) -> Optional[str]:
        if not isinstance(call.func, ast.Attribute):
            return None
        receiver = call.func.value
        method = call.func.attr
        current_class = self.class_by_function.get(current or "")
        if isinstance(receiver, ast.Name) and receiver.id in {"self", "cls"} and current_class:
            return self.class_methods.get(current_class, {}).get(method)
        return None


def is_safe_decorator(node: ast.AST, context: AnalysisContext) -> bool:
    if isinstance(node, ast.Name):
        return node.id in SAFE_DECORATORS or context.imported_names.get(node.id, "").endswith(tuple(f".{d}" for d in SAFE_DECORATORS))
    if isinstance(node, ast.Call):
        return is_safe_decorator(node.func, context)
    if isinstance(node, ast.Attribute):
        return stable_name(node) in {"dataclasses.dataclass"}
    return False


def collect_imports(tree: ast.Module) -> Tuple[Dict[str, str], Dict[str, str]]:
    imported_names: Dict[str, str] = {}
    module_aliases: Dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name.split(".")[0]
                module_aliases[local] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                local = alias.asname or alias.name
                imported_names[local] = f"{node.module}.{alias.name}"
    return imported_names, module_aliases


def collect_analysis_context(tree: ast.Module) -> AnalysisContext:
    functions: Dict[str, FunctionScope] = {}
    function_order: List[str] = []
    top_level_functions: Set[str] = set()
    class_names: Set[str] = set()
    class_methods: Dict[str, Dict[str, str]] = {}
    nested_by_parent: Dict[str, Dict[str, str]] = {}
    parent_by_function: Dict[str, Optional[str]] = {}
    class_by_function: Dict[str, Optional[str]] = {}
    imported_names, module_aliases = collect_imports(tree)

    def add_function(node: ast.FunctionDef, qualname: str, parent: Optional[str], class_name: Optional[str]) -> None:
        functions[qualname] = FunctionScope(qualname, node, parent, class_name)
        function_order.append(qualname)
        parent_by_function[qualname] = parent
        class_by_function[qualname] = class_name
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                child_name = f"{qualname}.{child.name}"
                # Nested helpers use stable qualified names like outer.dfs.
                nested_by_parent.setdefault(qualname, {})[child.name] = child_name
                add_function(child, child_name, qualname, class_name)

    def add_class(node: ast.ClassDef, parent: Optional[str]) -> None:
        class_name = f"{parent}.{node.name}" if parent else node.name
        class_names.add(class_name)
        class_names.add(node.name)
        class_methods.setdefault(class_name, {})
        class_methods.setdefault(node.name, class_methods[class_name])
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                qualname = f"{class_name}.{child.name}"
                class_methods[class_name][child.name] = qualname
                add_function(child, qualname, None, class_name)

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            top_level_functions.add(node.name)
            add_function(node, node.name, None, None)
            for child in node.body:
                if isinstance(child, ast.ClassDef):
                    add_class(child, node.name)
        elif isinstance(node, ast.ClassDef):
            add_class(node, None)

    return AnalysisContext(
        functions=functions,
        function_order=function_order,
        top_level_functions=top_level_functions,
        class_names=class_names,
        class_methods=class_methods,
        nested_by_parent=nested_by_parent,
        parent_by_function=parent_by_function,
        class_by_function=class_by_function,
        imported_names=imported_names,
        module_aliases=module_aliases,
    )


def is_safe_name_call(name: str, context: AnalysisContext) -> bool:
    if name in SAFE_BUILTIN_CALLS or name in SAFE_EXCEPTION_CALLS or name in SAFE_COLLECTION_CONSTRUCTORS:
        return True
    imported = context.imported_names.get(name, "")
    if imported.startswith(("typing.", "dataclasses.")):
        return True
    if imported.split(".")[-1] in SAFE_COLLECTION_CONSTRUCTORS:
        return True
    return False


def is_safe_attribute_call(call: ast.Call, context: AnalysisContext) -> bool:
    if not isinstance(call.func, ast.Attribute):
        return False
    receiver_name = stable_name(call.func.value)
    method = call.func.attr
    if receiver_name:
        root = receiver_name.split(".")[0]
        module_name = context.module_aliases.get(root, root)
        if module_name in SAFE_MODULE_CALLS and method in SAFE_MODULE_CALLS[module_name]:
            return True
    # Container/string methods are treated as safe external/library calls: they
    # affect def-use through the receiver/arguments but not user reachability.
    return method in SAFE_METHOD_CALLS


def lambda_usage_is_safe(node: ast.Lambda, parent: Optional[ast.AST]) -> bool:
    if isinstance(parent, ast.keyword) and parent.arg == "key":
        return True
    return False


def is_function_object(value: ast.AST, context: AnalysisContext) -> bool:
    if isinstance(value, (ast.Lambda, ast.FunctionDef)):
        return True
    if isinstance(value, ast.Name):
        return value.id in context.top_level_functions or any(value.id in nested for nested in context.nested_by_parent.values())
    if isinstance(value, ast.Attribute):
        parts = stable_name(value)
        if parts:
            root, _, method = parts.partition(".")
            return method in context.class_methods.get(root, {})
    return False


def is_monkey_patch_assignment(target: ast.AST, value: ast.AST, context: AnalysisContext) -> bool:
    if not isinstance(target, ast.Attribute):
        return False
    base = stable_name(target.value)
    if not base:
        return True
    if base in context.class_names:
        return True
    if is_function_object(value, context):
        return True
    return False


class UnsupportedScanner(ast.NodeVisitor):
    def __init__(self, context: AnalysisContext):
        self.context = context
        self.reasons: Set[str] = set()
        self.fatal_reasons: Set[str] = set()
        self.unsupported_categories: Dict[str, Set[str]] = {}
        self.current_function: Optional[str] = None
        self.parents: Dict[ast.AST, ast.AST] = {}

    def visit(self, node: ast.AST) -> Any:
        for child in ast.iter_child_nodes(node):
            self.parents[child] = node
        return super().visit(node)

    def add_fatal(self, reason: str) -> None:
        self.reasons.add(reason)
        self.fatal_reasons.add(reason)

    def add_note(self, reason: str) -> None:
        self.reasons.add(reason)

    def add_category_note(self, category: str, reason: str) -> None:
        self.reasons.add(reason)
        self.unsupported_categories.setdefault(category, set()).add(reason)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        if any(not is_safe_decorator(dec, self.context) for dec in node.decorator_list):
            self.add_fatal(f"decorated function at line {node.lineno}")
        previous = self.current_function
        for qualname, scope in self.context.functions.items():
            if scope.node is node:
                self.current_function = qualname
                break
        self.generic_visit(node)
        self.current_function = previous

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        if any(not is_safe_decorator(dec, self.context) for dec in node.decorator_list):
            self.add_fatal(f"decorated class at line {node.lineno}")
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        self.add_fatal(f"async function at line {node.lineno}")

    def visit_Lambda(self, node: ast.Lambda) -> Any:
        if not lambda_usage_is_safe(node, self.parents.get(node)):
            self.add_fatal(f"lambda at line {node.lineno}")

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        if node.module == "importlib":
            self.add_fatal(f"dynamic import helper at line {node.lineno}")
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> Any:
        if any(alias.name == "importlib" or alias.name.startswith("importlib.") for alias in node.names):
            self.add_fatal(f"dynamic import helper at line {node.lineno}")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> Any:
        if isinstance(node.func, ast.Attribute):
            if self.context.resolve_attribute_call(self.current_function, node):
                pass
            elif is_safe_attribute_call(node, self.context):
                pass
            else:
                receiver = stable_name(node.func.value) or "unknown"
                if node.func.attr.startswith("__"):
                    self.add_fatal(f"dynamic attribute call {receiver}.{node.func.attr} at line {node.lineno}")
                else:
                    self.add_category_note("function_reachability", f"external attribute call skipped {receiver}.{node.func.attr} at line {node.lineno}")
        elif isinstance(node.func, ast.Name):
            name = node.func.id
            if name in DYNAMIC_CALLS:
                self.add_fatal(f"dynamic call {name} at line {node.lineno}")
            elif self.context.resolve_name_call(self.current_function, name):
                pass
            elif self.context.class_constructor_name(name):
                pass
            elif is_safe_name_call(name, self.context):
                pass
            else:
                self.add_category_note("function_reachability", f"external call skipped {name} at line {node.lineno}")
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> Any:
        for target in node.targets:
            if is_monkey_patch_assignment(target, node.value, self.context):
                self.add_fatal(f"dynamic attribute assignment at line {node.lineno}")
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> Any:
        if is_monkey_patch_assignment(node.target, node.value, self.context):
            self.add_fatal(f"dynamic attribute assignment at line {node.lineno}")
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> Any:
        if node.value and is_monkey_patch_assignment(node.target, node.value, self.context):
            self.add_fatal(f"dynamic attribute assignment at line {node.lineno}")
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> Any:
        self.add_note(f"with statement approximated at line {node.lineno}")
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> Any:
        self.generic_visit(node)


def function_symbols(path: str, source: str) -> Dict[str, Set[str]]:
    try:
        table = symtable.symtable(source, path, "exec")
    except SyntaxError:
        return {}
    result: Dict[str, Set[str]] = {}
    for child in table.get_children():
        if child.get_type() == "function":
            names = {sym.get_name() for sym in child.get_symbols() if sym.is_local() or sym.is_parameter()}
            result[child.get_name()] = names
    return result


def local_variables(fn: ast.FunctionDef) -> Set[str]:
    variables = {arg.arg for arg in fn.args.args + fn.args.posonlyargs + fn.args.kwonlyargs}
    if fn.args.vararg:
        variables.add(fn.args.vararg.arg)
    if fn.args.kwarg:
        variables.add(fn.args.kwarg.arg)
    for stmt in simple_statement_nodes(fn.body):
        defs, uses = stmt_defs_uses(stmt)
        variables.update(defs)
        variables.update(uses)
    return variables


def call_nodes_in_function(fn: ast.FunctionDef) -> Iterable[ast.Call]:
    def visit_stmt(stmt: ast.stmt) -> Iterable[ast.Call]:
        if isinstance(stmt, (ast.FunctionDef, ast.ClassDef)):
            return
        for child in ast.walk(stmt):
            if isinstance(child, (ast.FunctionDef, ast.ClassDef)):
                continue
            if isinstance(child, ast.Call):
                yield child

    for stmt in fn.body:
        yield from visit_stmt(stmt)


def extract_functions(tree: ast.Module, source: str, symbols: Dict[str, Set[str]], context: Optional[AnalysisContext] = None) -> List[Dict[str, Any]]:
    if context is None:
        context = collect_analysis_context(tree)
    functions: List[Dict[str, Any]] = []
    for qualname in context.function_order:
        scope = context.functions[qualname]
        fn = scope.node
        calls: Set[str] = set()
        variables = set(symbols.get(fn.name, set())) | local_variables(fn)
        for child in call_nodes_in_function(fn):
            resolved: Optional[str] = None
            if isinstance(child.func, ast.Name):
                resolved = context.resolve_name_call(qualname, child.func.id)
            elif isinstance(child.func, ast.Attribute):
                resolved = context.resolve_attribute_call(qualname, child)
            if resolved:
                calls.add(resolved)
        functions.append(
            {
                "name": qualname,
                "lineno": fn.lineno,
                "end_lineno": getattr(fn, "end_lineno", fn.lineno),
                "calls": sorted(calls),
                "variables": sorted(variables),
            }
        )
    return functions


def compute_dominators(graph: nx.DiGraph, entry: int) -> Dict[int, Set[int]]:
    reachable = {entry} | nx.descendants(graph, entry)
    sub = graph.subgraph(reachable).copy()
    dom: Dict[int, Set[int]] = {node: set(reachable) for node in reachable}
    dom[entry] = {entry}
    changed = True
    while changed:
        changed = False
        for node in sorted(reachable):
            if node == entry:
                continue
            preds = list(sub.predecessors(node))
            if not preds:
                new_dom = {node}
            else:
                new_dom = {node} | set.intersection(*(dom[p] for p in preds))
            if new_dom != dom[node]:
                dom[node] = new_dom
                changed = True
    return dom


def cfg_records_for_body(body: List[ast.stmt], source: str, record_name: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    builder = CFGBuilder(source, record_name)
    builder.build(body)
    reachable = {builder.entry} | nx.descendants(builder.graph, builder.entry)

    dead_code: List[Dict[str, Any]] = []
    statements: List[Dict[str, Any]] = []
    for node_id, meta in sorted(builder.nodes.items(), key=lambda kv: (kv[1].line, kv[0])):
        rec = {
            "function": meta.function,
            "node_id": node_id,
            "line": meta.line,
            "code": meta.code,
            "kind": meta.kind,
            "dead": node_id not in reachable,
        }
        dead_code.append({"line": meta.line, "code": meta.code, "dead": rec["dead"]})
        statements.append(rec)

    dominators: List[Dict[str, Any]] = []
    dom = compute_dominators(builder.graph, builder.entry)
    for b_id, a_ids in sorted(dom.items()):
        if b_id == builder.entry:
            continue
        for a_id in sorted(a_ids):
            if a_id in (builder.entry, b_id):
                continue
            a = builder.nodes[a_id]
            b = builder.nodes[b_id]
            dominators.append(
                {
                    "function": record_name,
                    "a_line": a.line,
                    "a_code": a.code,
                    "b_line": b.line,
                    "b_code": b.code,
                }
            )
    return dead_code, dominators, builder.loop_records, statements


def cfg_records_for_function(fn: ast.FunctionDef, source: str, function_name: Optional[str] = None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    return cfg_records_for_body(fn.body, source, function_name or fn.name)


def dependency_records_for_body(
    body: Iterable[ast.stmt],
    source: str,
    variables: Set[str],
    *,
    args: Iterable[ast.arg] = (),
    scope_line: int = 1,
    scope_code: str = MODULE_SCOPE,
) -> List[Dict[str, Any]]:
    latest_def: Dict[str, Dict[str, Any]] = {
        arg.arg: {"var": arg.arg, "line": scope_line, "code": scope_code}
        for arg in args
    }
    value_deps: Dict[str, Set[str]] = {arg.arg: {arg.arg} for arg in args}
    records: List[Dict[str, Any]] = []
    positive_keys: Set[Tuple[int, str, str]] = set()

    for stmt in simple_statement_nodes(body):
        target_names: Set[str] = set()
        rhs_vars: Set[str] = set()
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                target_names.update(assigned_names(target))
                rhs_vars.update(target_uses(target))
            rhs_vars.update(loaded_names(stmt.value))
        elif isinstance(stmt, ast.AnnAssign):
            target_names.update(assigned_names(stmt.target))
            rhs_vars.update(target_uses(stmt.target))
            if stmt.value:
                rhs_vars.update(loaded_names(stmt.value))
        elif isinstance(stmt, ast.AugAssign):
            target_names.update(assigned_names(stmt.target))
            rhs_vars.update(target_uses(stmt.target))
            rhs_vars.update(loaded_names(stmt.target))
            rhs_vars.update(loaded_names(stmt.value))
        else:
            continue

        if not target_names:
            continue

        transitive: Set[str] = set()
        for var in rhs_vars:
            transitive.add(var)
            transitive.update(value_deps.get(var, set()))

        code = source_segment(source, stmt)
        line = getattr(stmt, "lineno", -1)
        for target in sorted(target_names):
            from_rec = {"var": target, "line": line, "code": code}
            for dep in sorted(v for v in transitive if v != target or v in rhs_vars):
                dep_rec = latest_def.get(dep, {"var": dep, "line": line, "code": code})
                key = (line, target, dep)
                if key not in positive_keys:
                    records.append({"label": "must", "from": from_rec, "depends_on": dep_rec})
                    positive_keys.add(key)
            value_deps[target] = set(transitive)
            latest_def[target] = from_rec

            candidates = sorted((variables | set(latest_def)) - value_deps[target] - {target})
            if candidates:
                neg_var = candidates[0]
                records.append(
                    {
                        "label": "negative",
                        "from": from_rec,
                        "depends_on": latest_def.get(neg_var, {"var": neg_var, "line": scope_line, "code": scope_code}),
                    }
                )
    return records


def dependency_records(fn: ast.FunctionDef, source: str, variables: Set[str]) -> List[Dict[str, Any]]:
    return dependency_records_for_body(
        fn.body,
        source,
        variables,
        args=fn.args.args,
        scope_line=fn.lineno,
        scope_code=source_segment(source, fn).split(":")[0] + ":",
    )


def liveness_records_for_body(
    body: Iterable[ast.stmt],
    source: str,
    variables: Set[str],
    *,
    args: Iterable[ast.arg] = (),
) -> Dict[str, Any]:
    stmts = simple_statement_nodes(body)
    live_after: Set[str] = set()
    live_points: List[Dict[str, Any]] = []
    for stmt in reversed(stmts):
        defs, uses = stmt_defs_uses(stmt)
        before = (live_after - defs) | uses
        live_points.append(
            {
                "line": getattr(stmt, "lineno", -1),
                "code": source_segment(source, stmt),
                "vars": sorted(before),
            }
        )
        live_after = before
    live_points.reverse()

    return_vars: Set[str] = set()
    for stmt in stmts:
        if isinstance(stmt, ast.Return) and stmt.value:
            return_vars.update(loaded_names(stmt.value))

    all_vars = set(variables) | {arg.arg for arg in args}
    for stmt in stmts:
        defs, uses = stmt_defs_uses(stmt)
        all_vars.update(defs)
        all_vars.update(uses)

    liveout = {var: var in return_vars for var in sorted(all_vars)}
    return {"liveout": liveout, "return_vars": sorted(return_vars), "base_liveout": sorted(return_vars), "live_before": live_points}


def liveness_records(fn: ast.FunctionDef, source: str, variables: Set[str]) -> Dict[str, Any]:
    return liveness_records_for_body(fn.body, source, variables, args=fn.args.args)


def module_executable_body(tree: ast.Module) -> List[ast.stmt]:
    return [
        stmt
        for stmt in tree.body
        if not isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    ]


def parse_python_file(path: str) -> Dict[str, Any]:
    source = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=path)
    symbols = function_symbols(path, source)
    context = collect_analysis_context(tree)

    scanner = UnsupportedScanner(context)
    scanner.visit(tree)

    functions = extract_functions(tree, source, symbols, context)
    fn_variables = {fn["name"]: set(fn.get("variables", [])) for fn in functions}

    loops: List[Dict[str, Any]] = []
    dead_code: List[Dict[str, Any]] = []
    strict_dominators: List[Dict[str, Any]] = []
    cfg_statements: List[Dict[str, Any]] = []
    var_dependencies: List[Dict[str, Any]] = []
    liveness: Dict[str, Any] = {"functions": {}}

    module_body = module_executable_body(tree)
    if module_body:
        module_dead, module_doms, module_loops, module_stmts = cfg_records_for_body(module_body, source, MODULE_SCOPE)
        dead_code.extend(module_dead)
        strict_dominators.extend(module_doms)
        loops.extend(module_loops)
        cfg_statements.extend(module_stmts)
        module_variables: Set[str] = set()
        for stmt in simple_statement_nodes(module_body):
            defs, uses = stmt_defs_uses(stmt)
            module_variables.update(defs)
            module_variables.update(uses)
        var_dependencies.extend(
            dependency_records_for_body(
                module_body,
                source,
                module_variables,
                scope_line=1,
                scope_code=MODULE_SCOPE,
            )
        )
        liveness["functions"][MODULE_SCOPE] = liveness_records_for_body(module_body, source, module_variables)

    for qualname in context.function_order:
        fn = context.functions[qualname].node
        fn_dead, fn_doms, fn_loops, fn_stmts = cfg_records_for_function(fn, source, qualname)
        dead_code.extend(fn_dead)
        strict_dominators.extend(fn_doms)
        loops.extend(fn_loops)
        cfg_statements.extend(fn_stmts)
        variables = fn_variables.get(qualname, set())
        var_dependencies.extend(dependency_records(fn, source, variables))
        liveness["functions"][qualname] = liveness_records(fn, source, variables)

    return {
        "file": path,
        "unsupported": bool(scanner.fatal_reasons),
        "unsupported_reasons": sorted(scanner.reasons),
        "unsupported_categories": {key: sorted(value) for key, value in sorted(scanner.unsupported_categories.items())},
        "functions": functions,
        "loops": sorted(loops, key=lambda x: (x["function"], x["line"], x["header_id"])),
        "dead_code": sorted(dead_code, key=lambda x: (x["line"], x["code"])),
        "strict_dominators": strict_dominators,
        "cfg_statements": cfg_statements,
        "var_dependencies": var_dependencies,
        "liveness": liveness,
    }


def output_name(path: Path) -> str:
    return f"{path.stem}.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse Python files into SemBench-style semantic JSON records.")
    parser.add_argument("--code-dir", type=Path, default=DEFAULT_PYTHON_DATA_DIR / "code", help="directory containing .py inputs")
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "Python_workflow" / "parsed_code", help="directory for output JSON files")
    parser.add_argument("--file", default=None, help="optional single Python file to parse")
    parser.add_argument(
        "--workers",
        type=int,
        default=max(1, (os.cpu_count() or 1) - 1),
        help="number of worker processes",
    )
    args = parser.parse_args()

    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "incomplete").mkdir(parents=True, exist_ok=True)

    if args.file:
        files = [Path(args.file)]
    else:
        files = sorted(args.code_dir.glob("*.py"))

    if args.workers <= 1 or len(files) <= 1:
        for path in files:
            status, message = process_one_file(str(path), str(out_dir))
            print(f"{status}: {message}")
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(process_one_file, str(path), str(out_dir)): path
                for path in files
            }

            for future in as_completed(futures):
                status, message = future.result()
                print(f"{status}: {message}")
    '''
    parser = argparse.ArgumentParser(description="Parse Python files into SemBench-style semantic JSON records.")
    parser.add_argument("--code-dir", default="SemBench/data/python/code", help="directory containing .py inputs")
    parser.add_argument("--output-dir", default="Python_workflow/parsed_code", help="directory for output JSON files")
    parser.add_argument("--file", default=None, help="optional single Python file to parse")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.file:
        files = [Path(args.file)]
    else:
        files = sorted(Path(args.code_dir).glob("*.py"))

    for path in files:
        try:
            parsed = parse_python_file(str(path))
            (out_dir / output_name(path)).write_text(json.dumps(parsed, indent=2, sort_keys=True), encoding="utf-8")
            status = "unsupported" if parsed.get("unsupported") else "parsed"
            print(f"{status}: {path}")
        except SyntaxError as exc:
            skipped = {"file": str(path), "unsupported": True, "unsupported_reasons": [f"syntax error: {exc}"], "unsupported_categories": {}}
            (out_dir / output_name(path)).write_text(json.dumps(skipped, indent=2, sort_keys=True), encoding="utf-8")
            print(f"unsupported: {path}: {exc}")
    '''

if __name__ == "__main__":
    main()

'''
python Python_workflow/python_parser.py \
--code-dir SemBench/data/python_codenet/code \
--output-dir SemBench/data/python_codenet/parsed_code \
--workers 32
'''

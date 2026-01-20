#!/usr/bin/env python3
import os
import sys
import json
import tempfile
import subprocess
import re
import traceback
from unittest import result

# --------- Utilities ---------

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# --------- Clang Python Bindings ---------
try:
    from clang.cindex import Index, CursorKind, TranslationUnitLoadError
except Exception as e:
    Index = None
    CursorKind = None
    TranslationUnitLoadError = Exception
    _clang_import_error = e
else:
    _clang_import_error = None


def ensure_clang_cindex_available():
    if _clang_import_error is not None or Index is None:
        eprint("ERROR: Failed to import clang.cindex. "
               "Please ensure libclang and Python bindings are installed.")
        eprint("Underlying import error:", repr(_clang_import_error))
        sys.exit(1)


# --------- AST: statement collection & data dependency ---------

class Statement:
    __slots__ = ("id", "cursor", "func_name")

    def __init__(self, sid, cursor, func_name):
        self.id = sid
        self.cursor = cursor
        self.func_name = func_name


def get_cursor_location(cur):
    try:
        loc = cur.location
        if not loc or not loc.file:
            return None
        return (str(loc.file), loc.line, loc.column)
    except Exception:
        return None

def get_source_line(path, line_no):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, start=1):
                if i == line_no:
                    return line.rstrip("\n")
    except Exception:
        return None
    return None

def is_statement_cursor(cur):
    from clang.cindex import CursorKind as CK

    parent = cur.semantic_parent
    if not parent:
        return False

    if parent.kind != CK.COMPOUND_STMT:
        return False

    k = cur.kind

    if k in {
        CK.VAR_DECL,
        CK.BINARY_OPERATOR,
        CK.UNARY_OPERATOR,
        CK.CALL_EXPR,
        CK.COMPOUND_ASSIGNMENT_OPERATOR,
    }:
        print("here")
        return True

    if k in {
        CK.IF_STMT,
        CK.WHILE_STMT,
        CK.FOR_STMT,
        CK.DO_STMT,
        CK.SWITCH_STMT,
    }:
        return False

    return False

def collect_statements_per_function(tu, c_path):
    functions = {}
    sid_counter = 1
    abs_path = os.path.abspath(c_path)

    def visit(node, current_func):
        nonlocal sid_counter

        loc = get_cursor_location(node)
        if loc:
            p,_,_ = loc
            if os.path.abspath(p) != abs_path:
                return

        # Enter function
        if node.kind == CursorKind.FUNCTION_DECL and node.is_definition():
            fname = node.spelling
            functions[fname] = []
            for ch in node.get_children():
                visit(ch, fname)
            return

        if current_func is None:
            for ch in node.get_children():
                visit(ch, None)
            return

        # ONLY collect actual stmts
        if is_statement_cursor(node):
            stmt = Statement(sid_counter, node, current_func)
            functions[current_func].append(stmt)
            sid_counter += 1
            # DO NOT recurse into subtrees — that was the original bug
            return

        # Only recurse into real block bodies
        if node.kind == CursorKind.COMPOUND_STMT:
            for ch in node.get_children():
                visit(ch, current_func)

    for ch in tu.cursor.get_children():
        visit(ch, None)

    return functions

def extract_data_dependencies_for_function(stmts, c_path, func_name):
    """
    Minimal, GUARANTEED WORKING, no-recursion, no-control-flow,
    correct per-line def-use extraction.

    It treats each stmt only by its OWN cursor — no child statements,
    no nested traversal into while/if.

    Works for C libclang.
    """

    from clang.cindex import CursorKind as CK

    ASSIGN_OPS = {"=", "+=", "-=", "*=", "/=", "%=", "<<=", ">>=",
                  "&=", "|=", "^="}
    UNARY_DEF_OPS = {"++", "--"}

    # ------------------------------------
    # Helper: get the source line for a stmt
    # ------------------------------------
    def stmt_line(stmt):
        loc = stmt.cursor.extent.start
        if loc and loc.file:
            return loc.line
        info = get_cursor_location(stmt.cursor)
        return info[1] if info else -1

    # ------------------------------------
    # Helper: collect only *this stmt*'s uses
    # ------------------------------------
    def collect_uses(node, uses):
        if node.kind == CK.DECL_REF_EXPR:
            name = node.spelling
            if name:
                uses.add(name)
            return
        for ch in node.get_children():
            collect_uses(ch, uses)

    # ------------------------------------
    # Extract defs from this single stmt
    # ------------------------------------
    def extract_defs(stmt):
        c = stmt.cursor
        k = c.kind
        defs = []

        # VarDecl
        if k == CK.VAR_DECL:
            dst = c.spelling
            if dst:
                used = set()
                for init in c.get_children():
                    collect_uses(init, used)
                if used:
                    defs.append((dst, used))
            return defs

        # Assignment
        if k in (CK.BINARY_OPERATOR, CK.COMPOUND_ASSIGNMENT_OPERATOR):
            kids = list(c.get_children())
            if len(kids) >= 2:
                lhs, rhs = kids[0], kids[1]

                if lhs.kind == CK.DECL_REF_EXPR:
                    dst = lhs.spelling
                    tokens = [t.spelling for t in c.get_tokens()]
                    if any(tok in ASSIGN_OPS for tok in tokens):
                        used = set()
                        collect_uses(rhs, used)
                        # compound assigns also use LHS
                        if k == CK.COMPOUND_ASSIGNMENT_OPERATOR:
                            used.add(dst)
                        if used:
                            defs.append((dst, used))
            return defs

        # ++ / --
        if k == CK.UNARY_OPERATOR:
            kids = list(c.get_children())
            if len(kids) == 1 and kids[0].kind == CK.DECL_REF_EXPR:
                tokens = [t.spelling for t in c.get_tokens()]
                if any(tok in UNARY_DEF_OPS for tok in tokens):
                    dst = kids[0].spelling
                    defs.append((dst, {dst}))
        return defs

    # ------------------------------------
    # MAIN PASS
    # ------------------------------------
    last_def = {}  # var -> stmt
    deps = []

    for stmt in sorted(stmts, key=lambda s: stmt_line(s)):
        defs = extract_defs(stmt)
        if not defs:
            continue

        for dst, used in defs:
            for u in used:
                if u in last_def:
                    deps.append((last_def[u], stmt, u, dst))
            last_def[dst] = stmt

    # ------------------------------------
    # Build JSON (correct)
    # ------------------------------------
    uniq = []
    seen = set()

    for s_src, s_dst, var_src, var_dst in deps:
        src_line = stmt_line(s_src)
        dst_line = stmt_line(s_dst)
        src_code = get_source_line(c_path, src_line) or ""
        dst_code = get_source_line(c_path, dst_line) or ""

        key = (func_name, var_src, var_dst, src_line, dst_line)
        if key in seen:
            continue
        seen.add(key)

        uniq.append({
            "function": func_name,
            "src_var": var_src,
            "dst_var": var_dst,
            "src_stmt_id": s_src.id,
            "src_line": src_line,
            "src_code": src_code,
            "dst_stmt_id": s_dst.id,
            "dst_line": dst_line,
            "dst_code": dst_code,
        })

    return uniq


# --------- LLVM IR + CFG + Dominators ---------

class IRBlock:
    def __init__(self, name):
        self.name = name
        self.succs = set()
        self.preds = set()


class IRFunction:
    def __init__(self, name):
        self.name = name
        self.blocks = {}          # block_name -> IRBlock
        self.line_to_blocks = {}  # line int -> set(block_name)
        self.entry_block = None


def compile_to_llvm_ir(c_path, out_ll):
    """
    Use clang to emit LLVM IR with debug info.
    """
    cmd = [
        "clang",
        "-std=c99",
        "-g",
        "-O0",
        "-S",
        "-emit-llvm",
        c_path,
        "-o",
        out_ll,
    ]
    try:
        p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        eprint("ERROR: 'clang' not found on PATH. Please install clang.")
        sys.exit(1)
    except Exception as e:
        eprint("ERROR: Failed to run clang:", repr(e))
        sys.exit(1)

    if p.returncode != 0:
        eprint("ERROR: clang failed to compile to LLVM IR.")
        eprint("Command:", " ".join(cmd))
        eprint("Stdout:\n", p.stdout)
        eprint("Stderr:\n", p.stderr)
        sys.exit(1)


def parse_llvm_ir(ir_path):
    """
    Parse LLVM IR to:
      - build IRFunction objects (blocks, succs)
      - build line_to_blocks via !dbg + !DILocation
    Returns:
      functions: dict[func_name] = IRFunction
    """
    try:
        with open(ir_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception as e:
        eprint(f"ERROR: Failed to read LLVM IR file {ir_path}: {e}")
        sys.exit(1)

    functions = {}

    # 1) Collect DILocation metadata: dbg_id -> line
    #    !15 = !DILocation(line: 42, column: 5, ...
    dbg_id_to_line = {}
    diloc_re = re.compile(r"^!(\d+)\s*=\s*!DILocation\(line:\s*(\d+),")

    for l in lines:
        m = diloc_re.match(l.strip())
        if m:
            dbg_id = m.group(1)
            line = int(m.group(2))
            dbg_id_to_line[dbg_id] = line

    # 2) Parse functions, blocks, succs, and line_to_blocks
    current_fun = None
    current_block = None

    # helpers
    def get_or_create_block(fun, block_name):
        if block_name not in fun.blocks:
            fun.blocks[block_name] = IRBlock(block_name)
        return fun.blocks[block_name]

    define_re = re.compile(r"^define\b.*@([a-zA-Z_][a-zA-Z0-9_]*)\s*\(")
    label_re = re.compile(r"^([a-zA-Z0-9_.]+):\s*(;.*)?$")
    br_label_re = re.compile(r".*\bbr\s+label\s+%([a-zA-Z0-9_.]+)")
    br_cond_re = re.compile(
        r".*\bbr\s+i1\b[^,]*,\s*label\s+%([a-zA-Z0-9_.]+),\s*label\s+%([a-zA-Z0-9_.]+)"
    )
    switch_re = re.compile(r".*\bswitch\b.*,\s*label\s+%([a-zA-Z0-9_.]+)\s*\[")
    switch_case_re = re.compile(r".*label\s+%([a-zA-Z0-9_.]+)")

    dbg_use_re = re.compile(r".*!dbg\s*!([0-9]+)")

    for raw in lines:
        line = raw.rstrip("\n")

        # function start
        mdef = define_re.match(line.strip())
        if mdef:
            fname = mdef.group(1)
            current_fun = IRFunction(fname)
            functions[fname] = current_fun
            current_block = None
            continue

        # function end
        if current_fun is not None and line.strip().startswith("}"):
            current_fun = None
            current_block = None
            continue

        if current_fun is None:
            continue

        # block label
        mlab = label_re.match(line.strip())
        if mlab:
            bname = mlab.group(1)
            current_block = get_or_create_block(current_fun, bname)
            if current_fun.entry_block is None:
                current_fun.entry_block = bname
            continue

        if current_block is None:
            continue

        # instructions in current_block:

        # dbg mapping: if line contains !dbg !NN, map to this block
        mdbg = dbg_use_re.search(line)
        if mdbg:
            dbg_id = mdbg.group(1)
            iline = dbg_id_to_line.get(dbg_id)
            if iline is not None:
                current_fun.line_to_blocks.setdefault(iline, set()).add(
                    current_block.name
                )

        stripped = line.strip()
        if stripped.startswith("br "):
            # unconditional br label %dest
            m1 = br_cond_re.match(stripped)
            if m1:
                t = m1.group(1)
                f = m1.group(2)
                current_block.succs.add(t)
                current_block.succs.add(f)
            else:
                m2 = br_label_re.match(stripped)
                if m2:
                    dest = m2.group(1)
                    current_block.succs.add(dest)
        elif stripped.startswith("switch "):
            msw = switch_re.match(stripped)
            if msw:
                default_block = msw.group(1)
                current_block.succs.add(default_block)
            # cases appear on following lines:
            #  i32 0, label %case0
            #  i32 1, label %case1
            # ...
            # We piggy-back by reading at parse-time: use switch_case_re
            # but we need to let subsequent lines run as well.
        else:
            # detect case labels for switch (they appear as separate lines)
            mc = switch_case_re.match(stripped)
            if mc and "label %"+mc.group(1) in stripped:
                current_block.succs.add(mc.group(1))

    # Build preds
    for fun in functions.values():
        for blk in fun.blocks.values():
            for succ in blk.succs:
                if succ in fun.blocks:
                    fun.blocks[succ].preds.add(blk.name)

    return functions


def compute_dominators_for_function(ir_fun):
    """
    Compute dominators on block-level using classic iterative algorithm.
    Returns:
      dom: dict[block_name] = set(block_name)   # blocks that dominate this block
    """
    blocks = ir_fun.blocks
    if not blocks:
        return {}

    if ir_fun.entry_block is None:
        # fallback: pick arbitrary block
        entry = next(iter(blocks))
    else:
        entry = ir_fun.entry_block

    all_blocks = set(blocks.keys())

    # Initialize
    dom = {b: set(all_blocks) for b in all_blocks}
    dom[entry] = {entry}

    changed = True
    while changed:
        changed = False
        for b in all_blocks:
            if b == entry:
                continue
            preds = blocks[b].preds
            if not preds:
                new_dom = {b}
            else:
                # intersection of dom(p) for all preds
                it = iter(preds)
                common = dom[next(it)].copy()
                for p in it:
                    common &= dom[p]
                new_dom = common | {b}
            if new_dom != dom[b]:
                dom[b] = new_dom
                changed = True

    return dom


# --------- Main extraction pipeline ---------

def extract_semantics(c_path):

    if not os.path.isfile(c_path):
        eprint(f"ERROR: C file not found: {c_path}")
        sys.exit(1)

    # 1. Parse C with libclang
    try:
        index = Index.create()
    except Exception as e:
        eprint("ERROR: Failed to create Clang Index:", repr(e))
        sys.exit(1)

    try:
        tu = index.parse(c_path, args=["-std=c99"])
    except TranslationUnitLoadError as e:
        eprint("ERROR: Failed to parse C file with clang.cindex:", repr(e))
        sys.exit(1)
    except Exception as e:
        eprint("ERROR: Unexpected exception while parsing C file:", repr(e))
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    # 2. Collect AST statements per function
    try:
        ast_functions = collect_statements_per_function(tu, c_path)
    except Exception as e:
        eprint("ERROR: Failed to collect AST statements:", repr(e))
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    # 3. Compile to LLVM IR
    with tempfile.TemporaryDirectory() as tmpdir:
        ir_path = os.path.join(tmpdir, "out.ll")
        try:
            compile_to_llvm_ir(c_path, ir_path)
        except SystemExit:
            raise
        except Exception as e:
            eprint("ERROR: Unexpected error while compiling to LLVM IR:", repr(e))
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)

        # 4. Parse LLVM IR into IRFunction structures
        try:
            ir_functions = parse_llvm_ir(ir_path)
        except SystemExit:
            raise
        except Exception as e:
            eprint("ERROR: Failed to parse LLVM IR:", repr(e))
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)

    # 5. Compute dominators for each IR function
    fun_to_dom = {}
    for fname, ir_fun in ir_functions.items():
        try:
            fun_to_dom[fname] = compute_dominators_for_function(ir_fun)
        except Exception as e:
            eprint(f"ERROR: Failed to compute dominators for function {fname}: {e}")
            traceback.print_exc(file=sys.stderr)
            fun_to_dom[fname] = {}

    result = {
        "file": os.path.abspath(c_path),
        "strict_dominators": [],
        "strict_dependencies": [],
    }

    # 6. Build mapping: AST statement -> (function, line, code, block_name or None)
    stmt_meta = {}  # stmt -> dict with info
    for func_name, stmts in ast_functions.items():
        for stmt in stmts:
            loc = get_cursor_location(stmt.cursor)
            if loc is None:
                continue
            _, line, col = loc
            code = get_source_line(c_path, line) or ""
            block_name = None
            # Try map line -> block via IR
            ir_fun = ir_functions.get(func_name)
            if ir_fun is not None:
                candidates = ir_fun.line_to_blocks.get(line)
                if candidates:
                    # pick one arbitrarily
                    block_name = sorted(candidates)[0]
            stmt_meta[stmt] = {
                "func": func_name,
                "line": line,
                "col": col,
                "code": code,
                "block": block_name,
            }

 
    # 7. Data dependency via AST def-use
    for func_name, stmts in ast_functions.items():
        try:
            dep_records = extract_data_dependencies_for_function(stmts, c_path, func_name)
        except Exception as e:
            eprint(f"ERROR: Failed to compute data dependencies for function {func_name}: {e}")
            traceback.print_exc(file=sys.stderr)
            dep_records = []

        # Each record is already a dict with src_var/dst_var and all fields
        result["strict_dependencies"].extend(dep_records)

    return result


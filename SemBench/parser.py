import os
import shutil
import argparse
import re
import json
import subprocess
import sys
import tempfile
from collections import defaultdict
import networkx as nx
from clang.cindex import Index, CursorKind
from clang import cindex
CURDIR = os.path.join(os.getcwd(), "data", "loop3_1000")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DIR = os.path.join(BASE_DIR, "test")
if TEST_DIR not in sys.path:
    sys.path.insert(0, TEST_DIR)
from parser_helper import extract_semantics



SUPPORTED_EXTENSIONS = ('.c')

parser = argparse.ArgumentParser(description="Parse C and C++ files with LLVM/Clang")
parser.add_argument("--clang-bin",   default="clang", help="clang binary")
parser.add_argument("--opt-bin",     default="opt",   help="opt binary")
parser.add_argument("--libclang-so", default=os.getenv('CONDA_PREFIX')+"/lib/libclang.so.17",
                    help="path to libclang.so")
parser.add_argument("--code-dir",    default=os.path.join(CURDIR, "code"),
                    help="directory of .c and .cpp files")
parser.add_argument("--output-dir",  default=os.path.join(CURDIR, "parsed_code"),
                    help="output JSON directory")
args = parser.parse_args()

CLANG = shutil.which(args.clang_bin) or args.clang_bin
OPT   = shutil.which(args.opt_bin)   or args.opt_bin
cindex.Config.set_library_file(args.libclang_so)
CODE_DIR = args.code_dir
OUTPUT_DIR = args.output_dir
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------- libclang configuration ----------
def _configure_libclang(user_path: str):
    """
    Try several candidate paths for libclang.so.
    If none are found we return False (parser will fall back to regex).
    """
    candidates = [
        user_path,
        os.getenv("LLVM_LIBCLANG"),
        os.path.join(os.getenv("CONDA_PREFIX", ""), "lib", "libclang.so"),
        os.path.join(os.getenv("CONDA_PREFIX", ""), "lib", "libclang.so.17"),
        "/usr/lib/llvm-17/lib/libclang.so.17",
        "/usr/lib/libclang.so"
    ]
    for p in candidates:
        if p and os.path.exists(p):
            try:
                cindex.Config.set_library_file(p)
                print(f"Loaded libclang from: {p}")
                return True
            except Exception:
                continue
    return False

HAS_LIBCLANG = _configure_libclang(args.libclang_so)
if not HAS_LIBCLANG:
    print(f"Error: could not load libclang from {args.libclang_so} or fallbacks.")
    exit(1)

def _get_parse_args(path: str):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.c':
        return ['-std=c99']
    return []

def preprocess(path: str) -> str:
    try:
        return subprocess.check_output([CLANG, '-E', path], text=True)
    except subprocess.CalledProcessError:
        return open(path).read()
    
# ---------- Helpers ----------
def has_flag(opt_bin: str, flag: str) -> bool:
    """Return True if `opt_bin --help-hidden` mentions `flag`."""
    try:
        help_out = subprocess.check_output(
            [opt_bin, "--help-hidden"], text=True, stderr=subprocess.DEVNULL
        )
        return flag in help_out
    except subprocess.CalledProcessError:
        return False

C_KEYWORDS = {'for', 'while', 'if', 'switch', 'return', 'sizeof'}

# 1. Functions + Calls
def extract_brace_block(text, idx):
    cnt, i = 0, idx
    while i < len(text):
        if text[i] == '{': cnt += 1
        elif text[i] == '}':
            cnt -= 1
            if cnt == 0:
                return text[idx:i+1], i+1
        i += 1
    return "", i

def extract_functions_and_calls(path_or_code):
    if HAS_LIBCLANG and os.path.isfile(path_or_code):
        try:
            index = Index.create()
            parse_args = _get_parse_args(path_or_code)
            tu = index.parse(path_or_code, args=parse_args)
            funcs = []
            for node in tu.cursor.walk_preorder():
                if node.kind == CursorKind.FUNCTION_DECL and node.is_definition():
                    name = node.spelling
                    if name in C_KEYWORDS:
                        continue
                    calls = set()
                    for child in node.walk_preorder():
                        if child.kind == CursorKind.CALL_EXPR:
                            callee = child.displayname or child.spelling
                            if callee and callee not in C_KEYWORDS:
                                calls.add(callee)
                    funcs.append({"name": name, "calls": sorted(calls)})
            if funcs:
                return funcs
        except Exception as e:
            print("libclang parse failed, fallback to regex. Reason:", e)
    code = preprocess(path_or_code) if os.path.isfile(path_or_code) else path_or_code
    sig = re.compile(r"^\s*[\w\s\*]+?\s+(\w+)\s*\([^)]*\)\s*\{", re.M)
    funcs = []
    for m in sig.finditer(code):
        name = m.group(1)
        if name in C_KEYWORDS:
            continue
        body, _ = extract_brace_block(code, m.end() - 1)
        raw_calls = set(re.findall(r"\b(\w+)\s*\(", body))
        calls = [c for c in raw_calls if c != name and c not in C_KEYWORDS]
        funcs.append({"name": name, "calls": calls})
    return funcs
# 2. Loops + Dominators with feature-probed fallback
def llvm_analyze_loops(path: str):
    bc = tempfile.NamedTemporaryFile(suffix='.bc', delete=False).name
    subprocess.run([CLANG, "-O1", "-emit-llvm", "-c", path, "-o", bc], check=True)
    try:
        # JSON dump if supported (LLVM ≥19)
        if has_flag(OPT, "-scev-dump-json"):
            scev = subprocess.check_output([
                OPT, "-passes=scalar-evolution", "-scev-dump-json", bc
            ], text=True)
            dom = subprocess.check_output([
                OPT, "-passes=domtree", "-dump-domtree-json", bc
            ], text=True)
            return json.loads(scev), json.loads(dom)

        # New PassManager print<> approach (LLVM ≥14)
        try:
            scev_txt = subprocess.check_output([
                OPT,
                "-passes=require<scalar-evolution>,print<scalar-evolution>",
                "-disable-output", bc
            ], text=True)
            dom_txt = subprocess.check_output([
                OPT,
                "-passes=require<domtree>,print<domtree>",
                "-disable-output", bc
            ], text=True)
            return parse_scev_text(scev_txt), parse_domtree_text(dom_txt)
        except subprocess.CalledProcessError:
            pass

        # Legacy driver (only if -analyze still supported)
        if has_flag(OPT, "-analyze"):
            scev_txt = subprocess.check_output([
                OPT, "-analyze", "-scalar-evolution", bc
            ], text=True)
            dom_txt = subprocess.check_output([
                OPT, "-analyze", "-domtree", bc
            ], text=True)
            return parse_scev_text(scev_txt), parse_domtree_text(dom_txt)

        raise RuntimeError(
            f"No supported opt flags for loop analysis (JSON? {has_flag(OPT,'-scev-dump-json')}, "
            f"NewPM? True, Legacy? {has_flag(OPT,'-analyze')})"
        )
    finally:
        os.remove(bc)

def parse_scev_text(txt: str) -> dict:
    loops = {}
    for m in re.finditer(r"Loop #(\d+):.*Backedge.*count is (\d+|unknown)", txt):
        hid, val = m.group(1), m.group(2)
        loops[hid] = {"maxTripCount": None if val == 'unknown' else int(val)}
    return {"loops": loops}

def parse_domtree_text(txt: str) -> dict:
    dom = {"dominates": {}}
    for m in re.finditer(r"Node\s+(?P<id>\d+) dominates:\s*(?P<nodes>[\d, ]+)", txt):
        dom[ m.group('id') ] = [x.strip() for x in m.group('nodes').split(',')]
    return dom
# 3. Extract loops and dominators in source
def extract_loops_and_dominators(code: str, path: str) -> list:
    loops=[]
    for_pat   = re.compile(r"for\s*\(([^;]+);([^;]*);([^)]+)\)")
    while_pat = re.compile(r"while\s*\(([^)]*)\)")
    do_pat    = re.compile(r"do\s*\{")
    for i,m in enumerate(for_pat.finditer(code)):   loops.append({"header_id":i,           "cond":m.group(2).strip()})
    for j,m in enumerate(while_pat.finditer(code), start=len(loops)): loops.append({"header_id":j, "cond":m.group(1).strip()})
    for k,m in enumerate(do_pat.finditer(code),    start=len(loops)+len(while_pat.findall(code))): loops.append({"header_id":k, "cond":"do-while"})
    scev_map,dom_map = llvm_analyze_loops(path)
    for L in loops:
        hid=str(L['header_id'])
        trip=scev_map.get('loops',{}).get(hid)
        L['reachable']=trip is None or trip.get('maxTripCount',0)>0
        L['dominates_body']=hid in dom_map.get('dominates',{})
    return loops
# 4. Dead code via Clang Static Analyzer
def detect_dead_code(path: str) -> list:
    dead = set()
    with tempfile.TemporaryDirectory() as td:
        try:
            result = subprocess.run(
                [CLANG, "--analyze",
                 "-Xclang", "-analyzer-checker=alpha.deadcode.UnreachableCode",
                 "-o", os.devnull,
                 path],
                cwd=td,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False
            )
            for line in result.stdout.splitlines():
                m = re.match(r".*:(\d+):\d+: warning: unreachable code", line)
                if m:
                    dead.add(int(m.group(1)))
        except Exception:
            dead = set()

    stmts = []
    with open(path) as src:
        for i, text in enumerate(src, start=1):
            code = text.strip()
            if not code or code in ("{", "}"):
                continue
            stmts.append({"line": i, "code": code, "dead": (i in dead)})
    return stmts

# 5. Def-use & liveness (simple regex fallback)
IDENT_RE      = re.compile(r"\b([A-Za-z_]\w*)\b")
TYPE_KEYWORDS = {'int','double','float','char','void','long','short','unsigned','signed'}
CONTROL_KEYWORDS = {"for","while","if","else","switch","case","break","continue","return","do","default","goto"}

def extract_def_use_and_liveness(path: str) -> tuple:
    text = open(path).read()
    if HAS_LIBCLANG:
        index = Index.create()
        tu = index.parse(path, args=_get_parse_args(path))
        # collect declarations
        decls = {n.spelling for n in tu.cursor.walk_preorder()
                 if n.kind in (CursorKind.VAR_DECL, CursorKind.PARM_DECL)}
        # scan tokens for occurrences
        deps = []
        for tok in tu.get_tokens(extent=tu.cursor.extent):
            var = tok.spelling
            if var in decls:
                ln = tok.location.line
                deps.append({
                    "var": var,
                    "line": ln,
                    "used_after_definition": True
                })
        live = []
        for var in decls:
            live_out = re.search(r"\b" + re.escape(var) + r"\b", text[-120:]) is not None
            live.append({"var": var, "live_out": bool(live_out)})
        return deps, live

    lines = text.splitlines()
    cand = {v for v in re.findall(r"\b([A-Za-z_]\w*)\b", text)
            if v not in TYPE_KEYWORDS | CONTROL_KEYWORDS and not v.isdigit()}
    deps, live = [], []
    for i, ln in enumerate(lines, start=1):
        for var in cand:
            if re.search(r"\b" + re.escape(var) + r"\b", ln):
                deps.append({"var": var, "line": i, "used_after_definition": True})
    for var in cand:
        live_out = re.search(r"\b" + re.escape(var) + r"\b", text[-120:]) is not None
        live.append({"var": var, "live_out": bool(live_out)})
    return deps, live

def _attach_liveness_to_functions(info, path):
    index = Index.create()
    tu = index.parse(path, args=_get_parse_args(path))
    lines = open(path).read().splitlines()
    for func in info["functions"]:
        node = next((n for n in tu.cursor.walk_preorder()
                     if n.kind == CursorKind.FUNCTION_DECL
                     and n.is_definition()
                     and n.spelling == func["name"]), None)
        if not node:
            func["live_out"] = {}
            continue

        vars_decl = set()
        for child in node.walk_preorder():
            if child.kind in (CursorKind.PARM_DECL, CursorKind.VAR_DECL):
                vars_decl.add(child.spelling)

        start, end = node.extent.start, node.extent.end
        body = "\n".join(lines[start.line-1:end.line])
        tail = body[-120:]
        live_map = {v: (re.search(r"\b" + re.escape(v) + r"\b", tail) is not None)
                    for v in vars_decl}
        func["live_out"] = live_map
        
def parse_c_file(path: str) -> dict:
    code = open(path).read()
    info = {
        'functions': extract_functions_and_calls(path),
        'loops': extract_loops_and_dominators(code, path),
        'dead_code': detect_dead_code(path)
    }
    _attach_liveness_to_functions(info, path)
    deps, live = extract_def_use_and_liveness(path)
    info['dependencies'] = deps
    info['liveness'] = live
    info.update(extract_semantics(path))
    return info

if __name__ == '__main__':
    from concurrent.futures import ProcessPoolExecutor, as_completed

    def _proc(fn):
        p = os.path.join(CODE_DIR, fn)
        out = parse_c_file(p)
        base, _ = os.path.splitext(fn)
        with open(os.path.join(OUTPUT_DIR, base + '.json'), 'w') as f:
            json.dump(out, f, indent=2)
        return fn

    files = [f for f in os.listdir(CODE_DIR)
             if f.lower().endswith(SUPPORTED_EXTENSIONS)]
    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(_proc, fn): fn for fn in files}
        for future in as_completed(futures):
            fn = futures[future]
            try:
                print("Parsed", future.result())
            except Exception as e:
                print(f"Error on {fn}:", e)
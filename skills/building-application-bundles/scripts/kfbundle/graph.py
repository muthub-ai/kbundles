"""Deterministic code-graph extractor (py-tree-sitter + structured inventory).

Honesty contract (plan §5.2, review finding P10):
  * `defines` and `imports` are exact (imports resolve tsconfig `paths`
    aliases, index files, extension inference, Python relative imports).
  * `calls`/`renders` carry a mandatory `resolution`: local | import-bound |
    name-only. Unresolvable targets become `ref:<name>` placeholders — never
    guessed. Calls through arbitrary receivers (obj.method()) are NOT
    extracted; only identifiers, self/this members and import-bound members.
  * Files that fail to parse are `parse_error` nodes, never dropped.

Output: sorted JSONL in canonical form — byte-reproducible for a given
source commit, options and toolchain (gate G11 re-runs this and compares).
"""
from __future__ import annotations

import json
import posixpath
import re
import subprocess
from collections import defaultdict
from urllib.parse import unquote

import yaml

from . import EXTRACTOR_ID, GRAPH_SCHEMA
from .common import canonical_json, match_any
from .languages import classify, get_language, toolchain_versions

# Files larger than this are inventoried by size only: a 1 MB source file is
# almost always generated or vendored, and parsing it would dominate the graph.
MAX_PARSE_BYTES = 1_000_000
# Inventory lists are capped so one huge config cannot bloat the graph.
MAX_LIST = 40

DEFAULT_THIRD_PARTY = ["**/node_modules/**", "**/vendor/**", "**/*.min.js", "**/third_party/**"]
# Build outputs and lockfiles are inventoried (size/lines) but never parsed:
# they are machine-generated and would swamp metrics with noise.
DEFAULT_GENERATED = ["**/dist/**", "**/build/**", "**/package-lock.json", "**/pnpm-lock.yaml",
                     "**/yarn.lock", "**/*.lock"]

# Fixed literal lists (not dir(builtins)) so graphs are identical across
# Python versions. Calls to these names are skipped, not recorded as refs.
PY_BUILTINS = set("""abs all any ascii bin bool breakpoint bytearray bytes callable chr classmethod
compile complex delattr dict dir divmod enumerate eval exec filter float format frozenset getattr
globals hasattr hash help hex id input int isinstance issubclass iter len list locals map max
memoryview min next object oct open ord pow print property range repr reversed round set setattr
slice sorted staticmethod str sum super tuple type vars zip __import__ NotImplementedError
ValueError TypeError KeyError IndexError RuntimeError Exception SystemExit OSError
FileNotFoundError AttributeError StopIteration AssertionError PermissionError
UnicodeDecodeError ImportError LookupError ArithmeticError ZeroDivisionError""".split())
JS_GLOBALS = set("""console Math JSON Object Array Promise String Number Boolean Date Error
TypeError RangeError Map Set WeakMap WeakSet Symbol RegExp parseInt parseFloat isNaN isFinite
setTimeout clearTimeout setInterval clearInterval queueMicrotask fetch encodeURIComponent
decodeURIComponent encodeURI decodeURI structuredClone URL URLSearchParams Buffer process
require describe it test expect beforeEach afterEach beforeAll afterAll vi jest Response
Request Headers TextEncoder TextDecoder AbortController BigInt Intl Reflect Proxy""".split())

NEXT_ROUTE_RE = re.compile(
    r"(^|/)(app/(.*/)?(page|layout|route|loading|error|not-found|template|default)\.(tsx|ts|jsx|js)"
    r"|pages/.+\.(tsx|ts|jsx|js)|middleware\.(ts|js))$")
MCP_RE = re.compile(rb"\.(tool|registerTool|setRequestHandler|resource|prompt)\s*\(")
PY_MAIN_RE = re.compile(rb"if\s+__name__\s*==\s*['\"]__main__['\"]")

JS_EXTS = [".ts", ".tsx", ".d.ts", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts", ".json"]


# --------------------------------------------------------------------------- utils

def _txt(node) -> str:
    return node.text.decode("utf-8", errors="replace") if node is not None else ""


def _strip_quotes(s: str) -> str:
    if len(s) >= 2 and s[0] in "'\"`" and s[-1] == s[0]:
        return s[1:-1]
    return s


def _walk(root):
    """Iterative pre-order walk yielding (node, depth-stack-events)."""
    stack = [(root, False)]
    while stack:
        node, done = stack.pop()
        if done:
            yield node, "exit"
            continue
        yield node, "enter"
        stack.append((node, True))
        for child in reversed(node.children):
            stack.append((child, False))


def _jsonc_loads(text: str):
    """Parse JSON-with-comments (tsconfig) safely: strip comments outside strings."""
    out, i, n, in_str, esc = [], 0, len(text), False, False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            i += 1
        elif c == '"':
            in_str = True
            out.append(c)
            i += 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j < 0 else j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            i = n if j < 0 else j + 2
        else:
            out.append(c)
            i += 1
    cleaned = re.sub(r",(\s*[}\]])", r"\1", "".join(out))
    return json.loads(cleaned)


# ----------------------------------------------------------------------- per file

class FileInfo:
    def __init__(self, path: str, lang: str):
        self.path = path
        self.lang = lang
        self.attrs: dict = {}
        self.symbols: list[dict] = []          # node records for defined symbols
        self.defs_top: dict[str, str] = {}     # top-level name -> node id
        self.class_members: dict[str, dict[str, str]] = defaultdict(dict)
        self.bindings: dict[str, tuple] = {}   # local name -> ("module", spec) | ("symbol", spec, name)
        self.imports: list[dict] = []          # raw import specs
        self.calls: list[tuple] = []           # (caller_id, form, payload, edge_kind)
        self.defines: list[tuple] = []         # (src_id, dst_id)
        self.links: list[tuple] = []           # markdown: (raw_target, style)
        self.declares: list[tuple] = []        # manifests: (package, scope)


def _add_symbol(fi: FileInfo, qual: str, kind: str, node, parent_id: str) -> str:
    sid = f"{fi.path}::{qual}"
    fi.symbols.append({
        "rec": "node", "id": sid, "kind": kind, "file": fi.path,
        "line": node.start_point[0] + 1, "end": node.end_point[0] + 1,
    })
    fi.defines.append((parent_id, sid))
    return sid


# ------------------------------------------------------------------------ python

def _py_extract(fi: FileInfo, tree, src: bytes):
    scope: list[tuple[str, str, str]] = []  # (kind, name, id)
    for node, ev in _walk(tree.root_node):
        t = node.type
        if ev == "exit":
            if t in ("function_definition", "class_definition") and scope and scope[-1][3] is node:
                scope.pop()
            continue
        if t in ("function_definition", "class_definition"):
            name = _txt(node.child_by_field_name("name"))
            if not name:
                continue
            parent_id = scope[-1][2] if scope else fi.path
            qual = ".".join([s[1] for s in scope] + [name])
            in_class = bool(scope) and scope[-1][0] == "class"
            kind = "class" if t == "class_definition" else ("method" if in_class else "function")
            sid = _add_symbol(fi, qual, kind, node, parent_id)
            if not scope:
                fi.defs_top[name] = sid
            elif in_class and len(scope) == 1:
                fi.class_members[scope[0][1]][name] = sid
            scope.append(("class" if t == "class_definition" else "def", name, sid, node))
        elif t == "import_statement":
            for ch in node.named_children:
                if ch.type == "dotted_name":
                    mod = _txt(ch)
                    fi.imports.append({"lang": "python", "module": mod, "level": 0})
                    fi.bindings[mod.split(".")[0]] = ("module", ("py", mod, 0))
                elif ch.type == "aliased_import":
                    mod = _txt(ch.child_by_field_name("name"))
                    alias = _txt(ch.child_by_field_name("alias"))
                    fi.imports.append({"lang": "python", "module": mod, "level": 0})
                    fi.bindings[alias] = ("module", ("py", mod, 0))
        elif t == "import_from_statement":
            mnode = node.child_by_field_name("module_name")
            level, mod = 0, ""
            if mnode is not None and mnode.type == "relative_import":
                for ch in mnode.children:
                    if ch.type == "import_prefix":
                        level = len(_txt(ch))
                    elif ch.type == "dotted_name":
                        mod = _txt(ch)
            else:
                mod = _txt(mnode)
            names = []
            for ch in node.children_by_field_name("name"):
                if ch.type == "aliased_import":
                    names.append((_txt(ch.child_by_field_name("name")), _txt(ch.child_by_field_name("alias"))))
                else:
                    names.append((_txt(ch), _txt(ch)))
            fi.imports.append({"lang": "python", "module": mod, "level": level,
                               "names": [n for n, _ in names]})
            for name, alias in names:
                fi.bindings[alias.split(".")[0]] = ("symbol", ("py", mod, level), name)
        elif t == "call":
            fn = node.child_by_field_name("function")
            caller = scope[-1][2] if scope else fi.path
            if fn is None:
                continue
            if fn.type == "identifier":
                fi.calls.append((caller, "ident", _txt(fn), "calls"))
            elif fn.type == "attribute":
                obj = fn.child_by_field_name("object")
                attr = _txt(fn.child_by_field_name("attribute"))
                if obj is not None and obj.type == "identifier":
                    oname = _txt(obj)
                    if oname in ("self", "cls"):
                        cls = next((s[1] for s in reversed(scope) if s[0] == "class"), None)
                        fi.calls.append((caller, "self", (cls, attr), "calls"))
                    else:
                        fi.calls.append((caller, "member", (oname, attr), "calls"))
    if PY_MAIN_RE.search(src):
        fi.attrs["entrypoint"] = "cli-main"


# ----------------------------------------------------------------- js / ts / tsx

def _js_name(node) -> str:
    n = node.child_by_field_name("name")
    return _txt(n)


def _js_extract(fi: FileInfo, tree, src: bytes):
    scope: list[tuple] = []
    for node, ev in _walk(tree.root_node):
        t = node.type
        if ev == "exit":
            if scope and scope[-1][3] is node:
                scope.pop()
            continue
        sym_kind, name = None, ""
        if t in ("function_declaration", "generator_function_declaration"):
            sym_kind, name = "function", _js_name(node)
        elif t in ("class_declaration", "abstract_class_declaration", "class"):
            sym_kind, name = "class", _js_name(node)
        elif t == "method_definition":
            sym_kind, name = "method", _js_name(node)
        elif t in ("interface_declaration", "type_alias_declaration", "enum_declaration"):
            sym_kind, name = "type", _js_name(node)
        elif t == "variable_declarator":
            val = node.child_by_field_name("value")
            nm = node.child_by_field_name("name")
            if val is not None and nm is not None and nm.type == "identifier" and val.type in (
                    "arrow_function", "function_expression", "function", "generator_function"):
                sym_kind, name = "function", _txt(nm)
        if sym_kind and name:
            parent_id = scope[-1][2] if scope else fi.path
            in_class = bool(scope) and scope[-1][0] == "class"
            if sym_kind == "method" and not in_class:
                sym_kind = "function"  # object-literal method: record as function
            qual = ".".join([s[1] for s in scope] + [name])
            sid = _add_symbol(fi, qual, sym_kind, node, parent_id)
            if not scope:
                fi.defs_top[name] = sid
            elif in_class and len(scope) == 1:
                fi.class_members[scope[0][1]][name] = sid
            scope.append(("class" if sym_kind == "class" else "def", name, sid, node))
            continue
        caller = scope[-1][2] if scope else fi.path
        if t == "import_statement":
            srcn = node.child_by_field_name("source")
            spec = _strip_quotes(_txt(srcn))
            fi.imports.append({"lang": "js", "spec": spec})
            for ch in node.named_children:
                if ch.type != "import_clause":
                    continue
                for cc in ch.named_children:
                    if cc.type == "identifier":
                        fi.bindings[_txt(cc)] = ("symbol", ("js", spec), "default")
                    elif cc.type == "namespace_import":
                        ident = next((x for x in cc.named_children if x.type == "identifier"), None)
                        if ident is not None:
                            fi.bindings[_txt(ident)] = ("module", ("js", spec))
                    elif cc.type == "named_imports":
                        for spc in cc.named_children:
                            if spc.type != "import_specifier":
                                continue
                            nm = _txt(spc.child_by_field_name("name"))
                            al = _txt(spc.child_by_field_name("alias")) or nm
                            fi.bindings[al] = ("symbol", ("js", spec), nm)
        elif t == "export_statement":
            srcn = node.child_by_field_name("source")
            if srcn is not None:
                fi.imports.append({"lang": "js", "spec": _strip_quotes(_txt(srcn)), "reexport": True})
        elif t == "call_expression":
            fn = node.child_by_field_name("function")
            if fn is None:
                continue
            if fn.type == "import":
                arg = node.child_by_field_name("arguments")
                lit = next((c for c in (arg.named_children if arg else []) if c.type == "string"), None)
                if lit is not None:
                    fi.imports.append({"lang": "js", "spec": _strip_quotes(_txt(lit)), "dynamic": True})
            elif fn.type == "identifier":
                nm = _txt(fn)
                if nm == "require":
                    arg = node.child_by_field_name("arguments")
                    lit = next((c for c in (arg.named_children if arg else []) if c.type == "string"), None)
                    if lit is not None:
                        fi.imports.append({"lang": "js", "spec": _strip_quotes(_txt(lit))})
                else:
                    fi.calls.append((caller, "ident", nm, "calls"))
            elif fn.type == "member_expression":
                obj = fn.child_by_field_name("object")
                prop = _txt(fn.child_by_field_name("property"))
                if obj is not None and obj.type == "this":
                    cls = next((s[1] for s in reversed(scope) if s[0] == "class"), None)
                    fi.calls.append((caller, "self", (cls, prop), "calls"))
                elif obj is not None and obj.type == "identifier":
                    fi.calls.append((caller, "member", (_txt(obj), prop), "calls"))
        elif t == "new_expression":
            ctor = node.child_by_field_name("constructor")
            if ctor is not None and ctor.type == "identifier":
                fi.calls.append((caller, "ident", _txt(ctor), "calls"))
        elif t in ("jsx_opening_element", "jsx_self_closing_element"):
            nm = node.child_by_field_name("name")
            if nm is not None and nm.type == "identifier":
                tag = _txt(nm)
                if tag[:1].isupper():
                    fi.calls.append((caller, "ident", tag, "renders"))
    if NEXT_ROUTE_RE.search(fi.path):
        fi.attrs["entrypoint"] = "next-route"
    elif MCP_RE.search(src) and b"mcp" in src.lower():
        fi.attrs["entrypoint"] = "mcp-tool"
    elif src.startswith(b"#!") and b"node" in src.split(b"\n", 1)[0]:
        fi.attrs["entrypoint"] = "cli-main"


# -------------------------------------------------------------------------- bash

def _bash_extract(fi: FileInfo, tree, src: bytes):
    scope: list[tuple] = []
    for node, ev in _walk(tree.root_node):
        t = node.type
        if ev == "exit":
            if scope and scope[-1][3] is node:
                scope.pop()
            continue
        if t == "function_definition":
            name = _txt(node.child_by_field_name("name"))
            if name:
                sid = _add_symbol(fi, name, "function", node, fi.path)
                fi.defs_top[name] = sid
                scope.append(("def", name, sid, node))
        elif t == "command":
            cn = node.child_by_field_name("name")
            cmd = _txt(cn).strip()
            caller = scope[-1][2] if scope else fi.path
            if cmd in ("source", "."):
                args = [c for c in node.children_by_field_name("argument")]
                if args:
                    fi.imports.append({"lang": "bash", "spec": _strip_quotes(_txt(args[0]))})
            elif cmd:
                fi.calls.append((caller, "bash", cmd, "calls"))
    if src.startswith(b"#!"):
        fi.attrs["entrypoint"] = "cli-main"


# --------------------------------------------------------------------- inventory

MD_LINK_RE = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
WIKI_LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
EXTERNAL_LINK_RE = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//|#)", re.I)


def _md_inventory(fi: FileInfo, src: bytes):
    text = src.decode("utf-8", errors="replace")
    body = text
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end > 0:
            try:
                fm = yaml.safe_load(text[4:end])
                if isinstance(fm, dict):
                    fi.attrs["frontmatter_keys"] = sorted(str(k) for k in fm)[:MAX_LIST]
                    if isinstance(fm.get("type"), str):
                        fi.attrs["okf_type"] = fm["type"]
            except yaml.YAMLError:
                fi.attrs["parse_error"] = True
            body = text[end + 5:]
    headings, in_fence = [], False
    for line in body.split("\n"):
        s = line.strip()
        if s.startswith("```") or s.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.+?)\s*#*$", line)
        if m and len(headings) < MAX_LIST:
            headings.append(f"{'#' * len(m.group(1))} {m.group(2)}")
        for lm in MD_LINK_RE.finditer(line):
            target = lm.group(1)
            if not EXTERNAL_LINK_RE.match(target):
                fi.links.append((target, "md"))
        for wm in WIKI_LINK_RE.finditer(line):
            fi.links.append((wm.group(1).strip(), "wiki"))
    if headings:
        fi.attrs["headings"] = headings


def _yaml_inventory(fi: FileInfo, src: bytes):
    try:
        docs = [d for d in yaml.safe_load_all(src.decode("utf-8", errors="replace"))]
    except yaml.YAMLError:
        fi.attrs["parse_error"] = True
        return
    fi.attrs["documents"] = len(docs)
    first = docs[0] if docs else None
    if isinstance(first, dict):
        fi.attrs["top_keys"] = sorted(str(k) for k in first)[:MAX_LIST]
        for key in ("kind", "apiVersion", "id", "name", "type", "version"):
            val = first.get(key)
            if isinstance(val, (str, int, float)) and not isinstance(val, bool):
                fi.attrs[f"yaml_{key}"] = str(val)
    if fi.path.endswith(("requirements.txt",)):
        pass


def _json_inventory(fi: FileInfo, src: bytes):
    try:
        data = json.loads(src.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        try:
            data = _jsonc_loads(src.decode("utf-8", errors="replace"))
        except ValueError:
            fi.attrs["parse_error"] = True
            return
    if isinstance(data, dict):
        fi.attrs["top_keys"] = sorted(str(k) for k in data)[:MAX_LIST]
        if fi.path.rsplit("/", 1)[-1] == "package.json":
            for scope in ("dependencies", "devDependencies", "peerDependencies"):
                deps = data.get(scope)
                if isinstance(deps, dict):
                    for pkg in sorted(deps):
                        fi.declares.append((pkg, scope))
            if isinstance(data.get("bin"), (dict, str)):
                fi.attrs["package_bin"] = True
    elif isinstance(data, list):
        fi.attrs["items"] = len(data)


REGO_PKG_RE = re.compile(r"^package\s+([\w.]+)", re.M)
REGO_IMPORT_RE = re.compile(r"^import\s+(data\.[\w.]+)", re.M)
REGO_RULE_RE = re.compile(r"^([a-zA-Z_]\w*)\s*(?:\[[^\]]*\])?\s*(?::=|=|\{|if\b|contains\b)", re.M)
MAKE_TARGET_RE = re.compile(r"^([A-Za-z0-9][\w./-]*)\s*:(?!=)", re.M)
REQ_RE = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)", re.M)


def _rego_inventory(fi: FileInfo, src: bytes):
    text = src.decode("utf-8", errors="replace")
    fi.attrs["extractor"] = "regex"
    m = REGO_PKG_RE.search(text)
    if m:
        fi.attrs["rego_package"] = m.group(1)
    rules = sorted({r for r in REGO_RULE_RE.findall(text) if r not in ("package", "import", "default")})
    if rules:
        fi.attrs["rules"] = rules[:MAX_LIST]
    for imp in sorted(set(REGO_IMPORT_RE.findall(text))):
        fi.imports.append({"lang": "rego", "spec": imp})


def _make_inventory(fi: FileInfo, src: bytes):
    fi.attrs["extractor"] = "regex"
    targets = sorted({t for t in MAKE_TARGET_RE.findall(src.decode("utf-8", errors="replace"))
                      if not t.startswith(".")})
    if targets:
        fi.attrs["targets"] = targets[:MAX_LIST]


def _requirements_inventory(fi: FileInfo, src: bytes):
    for line in src.decode("utf-8", errors="replace").split("\n"):
        s = line.strip()
        if not s or s.startswith(("#", "-")):
            continue
        m = REQ_RE.match(s)
        if m:
            fi.declares.append((m.group(1).lower(), "requirements"))


# ------------------------------------------------------------------- resolution

class Resolver:
    def __init__(self, files: set[str], tsconfigs: dict[str, dict]):
        self.files = files
        self.dirs = {posixpath.dirname(f) for f in files}
        self.tsconfigs = tsconfigs  # dir -> {"base": dir, "paths": {...}}
        self.md_by_stem: dict[str, list[str]] = defaultdict(list)
        for f in files:
            if f.endswith((".md", ".mdx")):
                stem = posixpath.basename(f).rsplit(".", 1)[0].lower()
                self.md_by_stem[stem].append(f)
        self.rego_pkgs: dict[str, str] = {}

    def _try(self, base: str):
        base = posixpath.normpath(base)
        if base.startswith("../") or base == "..":
            return None
        base = "" if base == "." else base
        if base in self.files:
            return base
        for ext in JS_EXTS:
            if base + ext in self.files:
                return base + ext
        for ext in JS_EXTS:
            cand = posixpath.join(base, "index" + ext) if base else "index" + ext
            if cand in self.files:
                return cand
        for js_ext, ts_exts in ((".js", (".ts", ".tsx")), (".jsx", (".tsx",)), (".mjs", (".mts",))):
            if base.endswith(js_ext):
                stem = base[: -len(js_ext)]
                for te in ts_exts:
                    if stem + te in self.files:
                        return stem + te
        return None

    def _tsconfig_for(self, path: str):
        d = posixpath.dirname(path)
        while True:
            if d in self.tsconfigs:
                return self.tsconfigs[d]
            if not d:
                return None
            d = posixpath.dirname(d)

    def resolve_js(self, path: str, spec: str):
        """Return (target, resolution): target is a repo path, 'ext:<pkg>' or 'ref:<spec>'."""
        if spec.startswith("."):
            hit = self._try(posixpath.join(posixpath.dirname(path), spec))
            return (hit, "exact") if hit else (f"ref:{spec}", "unresolved")
        cfg = self._tsconfig_for(path)
        if cfg:
            for pattern, targets in sorted(cfg["paths"].items()):
                if "*" in pattern:
                    pre, post = pattern.split("*", 1)
                    if spec.startswith(pre) and spec.endswith(post) and len(spec) >= len(pre) + len(post):
                        star = spec[len(pre): len(spec) - len(post)] if post else spec[len(pre):]
                        for tgt in targets:
                            hit = self._try(posixpath.join(cfg["base"], tgt.replace("*", star)))
                            if hit:
                                return hit, "exact"
                elif spec == pattern:
                    for tgt in targets:
                        hit = self._try(posixpath.join(cfg["base"], tgt))
                        if hit:
                            return hit, "exact"
        if spec.startswith("node:"):
            return f"ext:{spec}", "external"
        parts = spec.split("/")
        pkg = "/".join(parts[:2]) if spec.startswith("@") and len(parts) > 1 else parts[0]
        return f"ext:{pkg}", "external"

    def resolve_py(self, path: str, module: str, level: int, name: str | None = None):
        mparts = module.split(".") if module else []
        if level > 0:
            base = posixpath.dirname(path)
            for _ in range(level - 1):
                base = posixpath.dirname(base)
            roots = [base]
        else:
            roots, d = [], posixpath.dirname(path)
            while True:
                roots.append(d)
                if not d:
                    break
                d = posixpath.dirname(d)
        for root in roots:
            stem = posixpath.join(root, *mparts) if mparts else root
            if name:
                for cand in (posixpath.join(stem, name + ".py"), posixpath.join(stem, name, "__init__.py")):
                    if cand in self.files:
                        return cand, "exact"
            if mparts or level > 0:
                for cand in (stem + ".py", posixpath.join(stem, "__init__.py")):
                    cand = cand.lstrip("/")
                    if cand in self.files:
                        return cand, "exact"
        if level > 0:
            return f"ref:{'.' * level}{module}", "unresolved"
        return f"ext:{mparts[0] if mparts else module}", "external"

    def resolve_link(self, path: str, target: str, style: str):
        if style == "wiki":
            hits = self.md_by_stem.get(posixpath.basename(target).lower(), [])
            if len(hits) == 1:
                return hits[0], "basename"
            return f"ref:{target}", "ambiguous" if hits else "unresolved"
        target = unquote(target.split("#", 1)[0].split("?", 1)[0])
        if not target:
            return None, None
        full = target.lstrip("/") if target.startswith("/") else posixpath.normpath(
            posixpath.join(posixpath.dirname(path), target))
        if full in self.files:
            return full, "exact"
        for cand in (posixpath.join(full, "README.md"), posixpath.join(full, "index.md"), full + ".md"):
            if cand in self.files:
                return cand, "exact"
        if full in self.dirs:
            return None, None  # directory link: not a file edge
        return f"ref:{target}", "unresolved"


# ------------------------------------------------------------------------ driver

def _git_files(repo_dir: str) -> list[tuple[str, str]]:
    out = subprocess.run(["git", "-C", repo_dir, "ls-files", "-s", "-z"], check=True,
                         capture_output=True).stdout.decode("utf-8", errors="surrogateescape")
    files = []
    for entry in out.split("\0"):
        if not entry:
            continue
        meta, path = entry.split("\t", 1)
        mode = meta.split()[0]
        files.append((path, mode))
    return sorted(files)


def extract(repo_dir: str, repo: str, commit_sha: str, options: dict | None = None,
            inventory_only: bool = False) -> list[dict]:
    """Extract graph records for a git checkout. Deterministic for fixed inputs."""
    options = options or {}
    third_party = DEFAULT_THIRD_PARTY + list(options.get("third_party_globs", []))
    generated = DEFAULT_GENERATED + list(options.get("generated_globs", []))
    exclude = list(options.get("exclude_globs", []))
    entries = [(p, m) for p, m in _git_files(repo_dir) if not match_any(p, exclude)]
    file_set = {p for p, m in entries if m not in ("160000", "120000")}

    # tsconfig path aliases, keyed by the tsconfig's directory
    tsconfigs = {}
    for p in sorted(file_set):
        if posixpath.basename(p) == "tsconfig.json":
            try:
                with open(posixpath.join(repo_dir, p), "rb") as fh:
                    cfg = _jsonc_loads(fh.read().decode("utf-8", errors="replace"))
            except (OSError, ValueError):
                continue
            co = cfg.get("compilerOptions", {}) if isinstance(cfg, dict) else {}
            d = posixpath.dirname(p)
            base = posixpath.normpath(posixpath.join(d, co.get("baseUrl", "."))) if co else d
            base = "" if base == "." else base
            paths = co.get("paths") if isinstance(co.get("paths"), dict) else {}
            tsconfigs[d] = {"base": base, "paths": {k: list(v) for k, v in paths.items()}}
    resolver = Resolver(file_set, tsconfigs)

    infos: dict[str, FileInfo] = {}
    nodes: dict[str, dict] = {}
    for path, mode in entries:
        if mode == "160000":
            nodes[path] = {"rec": "node", "id": path, "kind": "submodule"}
            continue
        if mode == "120000":
            nodes[path] = {"rec": "node", "id": path, "kind": "symlink"}
            continue
        with open(posixpath.join(repo_dir, path), "rb") as fh:
            src = fh.read()
        lang = classify(path, src[:512])
        fi = FileInfo(path, lang)
        fi.attrs["bytes"] = len(src)
        if lang != "asset":
            fi.attrs["lines"] = src.count(b"\n") + (0 if src.endswith(b"\n") or not src else 1)
        if match_any(path, third_party):
            fi.attrs["third_party"] = True
        if match_any(path, generated):
            fi.attrs["generated"] = True
        elif len(src) > MAX_PARSE_BYTES:
            fi.attrs["large"] = True
        elif lang in ("python", "javascript", "typescript", "tsx", "bash") and not inventory_only:
            parser = __import__("tree_sitter").Parser(get_language(lang))
            tree = parser.parse(src)
            if tree.root_node.has_error:
                fi.attrs["parse_error"] = True
            {"python": _py_extract, "bash": _bash_extract}.get(lang, _js_extract)(fi, tree, src)
        elif lang == "markdown":
            _md_inventory(fi, src)
        elif lang == "yaml":
            _yaml_inventory(fi, src)
        elif lang == "json":
            _json_inventory(fi, src)
        elif lang == "rego":
            _rego_inventory(fi, src)
        elif lang == "make":
            _make_inventory(fi, src)
        elif lang == "text" and posixpath.basename(path).startswith("requirements") and path.endswith(".txt"):
            _requirements_inventory(fi, src)
        infos[path] = fi
        if fi.attrs.get("rego_package"):
            resolver.rego_pkgs[fi.attrs["rego_package"]] = path

    edges: dict[tuple, dict] = {}

    def add_edge(src_id, dst_id, kind, **attrs):
        key = (src_id, kind, dst_id, attrs.get("resolution", ""))
        if key in edges:
            edges[key]["count"] = edges[key].get("count", 1) + 1
            return
        rec = {"rec": "edge", "src": src_id, "dst": dst_id, "kind": kind}
        rec.update({k: v for k, v in attrs.items() if v not in (None, False)})
        edges[key] = rec

    def ensure_placeholder(nid: str):
        if nid not in nodes and nid.startswith(("ext:", "ref:")):
            nodes[nid] = {"rec": "node", "id": nid,
                          "kind": "external" if nid.startswith("ext:") else "unresolved"}

    def target_of(fi: FileInfo, spec_tuple):
        if spec_tuple[0] == "py":
            return resolver.resolve_py(fi.path, spec_tuple[1], spec_tuple[2])[0]
        return resolver.resolve_js(fi.path, spec_tuple[1])[0]

    for path, fi in sorted(infos.items()):
        rec = {"rec": "node", "id": path, "kind": "file", "lang": fi.lang}
        rec.update({k: v for k, v in sorted(fi.attrs.items()) if v not in (None, False)})
        nodes[path] = rec
        for sym in fi.symbols:
            nodes[sym["id"]] = sym
        for s, d in fi.defines:
            add_edge(s, d, "defines")
        for imp in fi.imports:
            if imp["lang"] == "python":
                tgt, res = resolver.resolve_py(path, imp["module"], imp["level"])
                add_edge(path, tgt, "imports", resolution=res)
                for name in imp.get("names", []):
                    sub, sres = resolver.resolve_py(path, imp["module"], imp["level"], name)
                    if sres == "exact" and sub != tgt and sub.endswith((f"/{name}.py", f"/{name}/__init__.py")):
                        add_edge(path, sub, "imports", resolution=sres)
                        fi.bindings[name] = ("module", ("path", sub))
            elif imp["lang"] == "rego":
                pkg = imp["spec"][len("data."):]
                hit = None
                while pkg and not hit:
                    hit = resolver.rego_pkgs.get(pkg)
                    pkg = pkg.rsplit(".", 1)[0] if "." in pkg else ""
                add_edge(path, hit or f"ref:{imp['spec']}", "imports",
                         resolution="exact" if hit else "unresolved")
            elif imp["lang"] == "bash":
                spec = imp["spec"]
                if "$" in spec:
                    continue
                cand = posixpath.normpath(posixpath.join(posixpath.dirname(path), spec))
                hit = cand if cand in file_set else (spec if spec in file_set else None)
                add_edge(path, hit or f"ref:{spec}", "imports", resolution="exact" if hit else "unresolved")
            else:
                tgt, res = resolver.resolve_js(path, imp["spec"])
                add_edge(path, tgt, "imports", resolution=res,
                         reexport=imp.get("reexport"), dynamic=imp.get("dynamic"))
        for target, style in fi.links:
            tgt, res = resolver.resolve_link(path, target, style)
            if tgt:
                add_edge(path, tgt, "links", resolution=res)
        for pkg, scope in fi.declares:
            add_edge(path, f"ext:{pkg}", "declares", resolution="external", scope=scope)

    # resolve calls (second pass: needs every file's top-level definitions)
    def bound_target(fi: FileInfo, binding, member: str | None):
        """Resolve an import binding (+ optional member) to (dst id, symbol attr)."""
        kind, spec = binding[0], binding[1]
        tfile = spec[1] if spec[0] == "path" else target_of(fi, spec)
        tinfo = infos.get(tfile)
        if kind == "module":
            if tinfo is not None and member and member in tinfo.defs_top:
                return tinfo.defs_top[member], None
            return tfile, member
        name = binding[2]
        if member is None:
            if tinfo is not None and name in tinfo.defs_top:
                return tinfo.defs_top[name], None
            return tfile, None if name == "default" else name
        if tinfo is not None:
            cm = tinfo.class_members.get(name, {})
            if member in cm:
                return cm[member], None
            return tfile, f"{name}.{member}"
        return tfile, member if name == "default" else f"{name}.{member}"

    for path, fi in sorted(infos.items()):
        for caller, form, payload, ekind in fi.calls:
            if form == "ident":
                name = payload
                if name in fi.defs_top:
                    add_edge(caller, fi.defs_top[name], ekind, resolution="local")
                elif name in fi.bindings:
                    dst, sym = bound_target(fi, fi.bindings[name], None)
                    add_edge(caller, dst, ekind, resolution="import-bound", symbol=sym)
                elif name in PY_BUILTINS or name in JS_GLOBALS:
                    continue
                else:
                    add_edge(caller, f"ref:{name}", ekind, resolution="name-only")
            elif form == "self":
                cls, attr = payload
                member_id = fi.class_members.get(cls, {}).get(attr) if cls else None
                if member_id:
                    add_edge(caller, member_id, ekind, resolution="local")
                else:
                    add_edge(caller, f"ref:{attr}", ekind, resolution="name-only")
            elif form == "member":
                obj, attr = payload
                if obj in fi.bindings:
                    dst, sym = bound_target(fi, fi.bindings[obj], attr)
                    add_edge(caller, dst, ekind, resolution="import-bound", symbol=sym)
            elif form == "bash":
                if payload in fi.defs_top:
                    add_edge(caller, fi.defs_top[payload], ekind, resolution="local")

    for rec in edges.values():
        ensure_placeholder(rec["dst"])

    meta = {
        "rec": "meta", "schema": GRAPH_SCHEMA, "extractor": EXTRACTOR_ID,
        "toolchain": toolchain_versions(), "inventory_only": inventory_only,
        "source": {"repo": repo, "commit_sha": commit_sha},
        "options": {"third_party_globs": sorted(set(third_party)), "exclude_globs": sorted(exclude),
                    "generated_globs": sorted(set(generated))},
    }
    node_recs = [nodes[k] for k in sorted(nodes)]
    edge_recs = sorted(edges.values(), key=lambda e: (e["src"], e["kind"], e["dst"], e.get("resolution", "")))
    return [meta] + node_recs + edge_recs


def to_jsonl(records: list[dict]) -> str:
    return "".join(canonical_json(r) + "\n" for r in records)


def load_jsonl(text: str) -> list[dict]:
    return [json.loads(line) for line in text.splitlines() if line.strip()]

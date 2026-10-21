"""Derived artifacts from a code graph: metrics.json and Mermaid views.

Everything here is a pure function of the graph records plus the bundle's
fixed metadata, so G11 can regenerate and byte-compare it. Views aggregate
to directory level and are capped (≤50 nodes, ≤150 edges) so GitHub's
Mermaid renderer can draw them; "hotspots" are fan-in/fan-out only — churn
needs history and bundles pin a single commit.
"""
from __future__ import annotations

import posixpath
from collections import Counter, defaultdict

from . import BUNDLE_SCHEMA, VIEWS_ID
from .common import dump_frontmatter, pretty_json

MAX_VIEW_NODES = 50    # GitHub Mermaid stays legible and under its size limits
MAX_VIEW_EDGES = 150
TOP_N = 15             # fan-in / fan-out tables
TOP_EXT = 30           # external dependency table
WEIGHTED_KINDS = ("calls", "renders", "imports", "links")


def _dir_key(path: str) -> str:
    d = posixpath.dirname(path)
    if not d:
        return "(root)"
    parts = d.split("/")
    return "/".join(parts[:2])


def _internal(nodes: dict, nid: str) -> bool:
    n = nodes.get(nid)
    if n is None or n["kind"] in ("external", "unresolved", "submodule", "symlink"):
        return False
    fid = n.get("file", nid)
    f = nodes.get(fid, {})
    return not (f.get("third_party") or f.get("generated"))


def compute_metrics(records: list[dict], graph_sha256: str) -> dict:
    meta = records[0]
    nodes = {r["id"]: r for r in records if r["rec"] == "node"}
    edges = [r for r in records if r["rec"] == "edge"]
    files = [n for n in nodes.values() if n["kind"] == "file"]
    fan_in, fan_out = Counter(), Counter()
    ext_users: dict[str, set] = defaultdict(set)
    for e in edges:
        w = e.get("count", 1)
        if e["kind"] in WEIGHTED_KINDS and _internal(nodes, e["src"]):
            if _internal(nodes, e["dst"]):
                fan_in[e["dst"]] += w
            fan_out[e["src"]] += w
        if e["dst"].startswith("ext:") and e["kind"] in ("imports", "declares"):
            src_file = nodes.get(e["src"], {}).get("file", e["src"])
            if _internal(nodes, src_file):
                ext_users[e["dst"][4:]].add(src_file)

    def top(counter):
        return [{"id": k, "weight": v} for k, v in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[:TOP_N]]

    return {
        "schema": "kf-code-graph-metrics/1",
        "graph_sha256": graph_sha256,
        "source": meta["source"],
        "counts": {
            "files_by_lang": dict(sorted(Counter(f["lang"] for f in files).items())),
            "nodes_by_kind": dict(sorted(Counter(n["kind"] for n in nodes.values()).items())),
            "edges_by_kind": dict(sorted(Counter(
                f"{e['kind']}:{e.get('resolution', '-')}" for e in edges).items())),
            "third_party_files": sum(1 for f in files if f.get("third_party")),
            "generated_files": sum(1 for f in files if f.get("generated")),
        },
        "entrypoints": sorted(f"{f['id']} ({f['entrypoint']})" for f in files if f.get("entrypoint")),
        "parse_errors": sorted(f["id"] for f in files if f.get("parse_error")),
        "fan_in_top": top(fan_in),
        "fan_out_top": top(fan_out),
        "external_dependencies": [
            {"package": k, "files": len(v)}
            for k, v in sorted(ext_users.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:TOP_EXT]],
        "hotspot_definition": "fan-in/fan-out of internal nodes over calls+renders+imports+links; no churn",
    }


def _view_frontmatter(appid: str, title: str, description: str, generated_at: str,
                      graph_sha256: str, view: str) -> str:
    fm = {
        "type": "application-bundle/code-graph-view",
        "title": title,
        "description": description,
        "generated": {"by": VIEWS_ID, "at": generated_at},
        "sources": [{"id": "g1", "kind": "code-graph", "path": "code-graph/code-graph.jsonl",
                     "sha256": graph_sha256}],
        "x_kf": {"schema": BUNDLE_SCHEMA, "appid": appid, "bundle_kind": "application",
                 "view": view, "derived": True},
    }
    return dump_frontmatter(fm)


def _mermaid_id(i: int) -> str:
    return f"n{i}"


def modules_view(records: list[dict], appid: str, generated_at: str, graph_sha256: str) -> str:
    nodes = {r["id"]: r for r in records if r["rec"] == "node"}
    files = [n for n in nodes.values() if n["kind"] == "file" and _internal(nodes, n["id"])]
    dir_files, dir_syms = Counter(), Counter()
    for f in files:
        dir_files[_dir_key(f["id"])] += 1
    for n in nodes.values():
        if n["kind"] in ("class", "function", "method", "type") and _internal(nodes, n["id"]):
            dir_syms[_dir_key(n["file"])] += 1
    dep = Counter()
    for e in records:
        if e["rec"] != "edge" or e["kind"] not in ("imports", "links"):
            continue
        if not (_internal(nodes, e["src"]) and _internal(nodes, e["dst"])):
            continue
        a = _dir_key(nodes[e["src"]].get("file", e["src"]))
        b = _dir_key(nodes[e["dst"]].get("file", e["dst"]))
        if a != b:
            dep[(a, b, e["kind"])] += e.get("count", 1)
    involvement = Counter(dir_files)
    for (a, b, _), w in dep.items():
        involvement[a] += w
        involvement[b] += w
    keep = [d for d, _ in sorted(involvement.items(), key=lambda kv: (-kv[1], kv[0]))[:MAX_VIEW_NODES]]
    keep_set = set(keep)
    edges = [(k, w) for k, w in dep.items() if k[0] in keep_set and k[1] in keep_set]
    edges = sorted(edges, key=lambda kw: (-kw[1], kw[0]))[:MAX_VIEW_EDGES]
    ids = {d: _mermaid_id(i) for i, d in enumerate(sorted(keep_set))}
    out = [_view_frontmatter(appid, f"Module view — {appid}",
                             "Directory-level dependency view derived from the code graph "
                             "(solid = imports, dotted = document links).",
                             generated_at, graph_sha256, "modules")]
    out.append(f"# Module view — {appid}\n\n")
    out.append("Derived from `code-graph/code-graph.jsonl`; regenerated by the bundle builder and "
               "verified by reproduction (gate G11). Directories are aggregated to two path "
               f"segments; at most {MAX_VIEW_NODES} directories and {MAX_VIEW_EDGES} edges are drawn.\n\n")
    out.append("```mermaid\nflowchart LR\n")
    for d in sorted(keep_set):
        out.append(f'  {ids[d]}["{d} ({dir_files.get(d, 0)} {"file" if dir_files.get(d, 0) == 1 else "files"})"]\n')
    for (a, b, kind), w in sorted(edges, key=lambda kw: kw[0]):
        arrow = "-->" if kind == "imports" else "-.->"
        out.append(f"  {ids[a]} {arrow}|{w}| {ids[b]}\n")
    out.append("```\n\n")
    out.append("| Directory | Files | Symbols | Outgoing deps | Incoming deps |\n|---|---:|---:|---:|---:|\n")
    outgoing, incoming = Counter(), Counter()
    for (a, b, _), w in dep.items():
        outgoing[a] += w
        incoming[b] += w
    for d in sorted(dir_files):
        out.append(f"| `{d}` | {dir_files[d]} | {dir_syms.get(d, 0)} | {outgoing.get(d, 0)} | {incoming.get(d, 0)} |\n")
    return "".join(out)


def dependencies_view(metrics: dict, records: list[dict], appid: str, generated_at: str,
                      graph_sha256: str) -> str:
    nodes = {r["id"]: r for r in records if r["rec"] == "node"}
    out = [_view_frontmatter(appid, f"Dependencies and hotspots — {appid}",
                             "External dependencies, entry points and fan-in hotspots derived from "
                             "the code graph.", generated_at, graph_sha256, "dependencies")]
    out.append(f"# Dependencies and hotspots — {appid}\n\n")
    out.append("Derived from `code-graph/code-graph.jsonl` and `code-graph/metrics.json`. Hotspots "
               "are fan-in counts only (calls, renders, imports and links into a node); the bundle "
               "pins one commit, so there is no churn signal.\n\n")
    out.append("## External dependencies\n\n| Package | Files that import or declare it |\n|---|---:|\n")
    for dep in metrics["external_dependencies"]:
        out.append(f"| `{dep['package']}` | {dep['files']} |\n")
    out.append("\n## Entry points\n\n")
    if metrics["entrypoints"]:
        out.extend(f"- `{e}`\n" for e in metrics["entrypoints"])
    else:
        out.append("No framework, CLI or MCP entry points were detected.\n")
    out.append("\n## Fan-in hotspots\n\n")
    hot = [h for h in metrics["fan_in_top"][:12]]
    callers: dict[str, Counter] = defaultdict(Counter)
    hot_ids = {h["id"] for h in hot}
    for e in records:
        if e["rec"] == "edge" and e["dst"] in hot_ids and e["kind"] in WEIGHTED_KINDS \
                and _internal(nodes, e["src"]):
            callers[e["dst"]][_dir_key(nodes[e["src"]].get("file", e["src"]))] += e.get("count", 1)
    if hot:
        names = sorted(hot_ids | {d for c in callers.values() for d, _ in c.most_common(5)})
        ids = {n: _mermaid_id(i) for i, n in enumerate(names)}
        out.append("```mermaid\nflowchart LR\n")
        for n in names:
            label = n.split("::", 1)[-1] if n in hot_ids else n
            shape = f'(["{label}"])' if n in hot_ids else f'["{label}"]'
            out.append(f"  {ids[n]}{shape}\n")
        for h in sorted(hot_ids):
            for d, w in sorted(callers[h].items(), key=lambda kv: (-kv[1], kv[0]))[:5]:
                out.append(f"  {ids[d]} -->|{w}| {ids[h]}\n")
        out.append("```\n\n| Node | Fan-in |\n|---|---:|\n")
        out.extend(f"| `{h['id']}` | {h['weight']} |\n" for h in hot)
    else:
        out.append("No internal fan-in was recorded.\n")
    return "".join(out)


def build_derived(records: list[dict], graph_text: str, appid: str, generated_at: str) -> dict[str, str]:
    """Return {relative path: content} for every derived code-graph artifact."""
    from .common import sha256_text
    gsha = sha256_text(graph_text)
    metrics = compute_metrics(records, gsha)
    return {
        "code-graph/code-graph.jsonl": graph_text,
        "code-graph/metrics.json": pretty_json(metrics),
        "code-graph/views/modules.md": modules_view(records, appid, generated_at, gsha),
        "code-graph/views/dependencies.md": dependencies_view(metrics, records, appid, generated_at, gsha),
    }

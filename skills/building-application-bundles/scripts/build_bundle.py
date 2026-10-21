#!/usr/bin/env python3
"""Build the deterministic parts of an application bundle.

  build_bundle.py init     --bundle DIR --appid ID --title T --repo O/R --repo-id N
                           --source DIR --approver @h [--generated-at ISO] [--third-party GLOB ...]
  build_bundle.py graph    --bundle DIR --source DIR      # code graph + metrics + views
  build_bundle.py controls --bundle DIR [--log-summary S --log-bullet B ...]
                                                          # manifest + index (+ root log block)

Sections and domain maps are authored between `graph` and `controls`
(see reference/section-authoring-guide.md), then citations are filled with
fill_citations.py and everything is checked with validate_bundle.py.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kfbundle import controls, graph, views  # noqa: E402


def _head_sha(src: str) -> str:
    return subprocess.run(["git", "-C", src, "rev-parse", "HEAD"], check=True,
                          capture_output=True, text=True).stdout.strip()


def cmd_init(a) -> int:
    os.makedirs(os.path.join(a.bundle, "sections"), exist_ok=True)
    os.makedirs(os.path.join(a.bundle, "domains-maps"), exist_ok=True)
    os.makedirs(os.path.join(a.bundle, "code-graph", "views"), exist_ok=True)
    sha = _head_sha(a.source)
    generated_at = a.generated_at or dt.datetime.now().astimezone().replace(microsecond=0).isoformat()
    opts = {"third_party_globs": sorted(a.third_party or []), "generated_globs": sorted(a.generated or []),
            "exclude_globs": sorted(a.exclude or [])}
    text = controls.knowledge_source(a.appid, a.title, a.repo, a.repo_id, sha, generated_at,
                                     a.approver, opts, a.bootstrap)
    with open(os.path.join(a.bundle, "knowledge-source.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print(f"initialized {a.bundle} at {a.repo}@{sha[:12]}")
    return 0


def cmd_graph(a) -> int:
    ks = controls.load_json(os.path.join(a.bundle, "knowledge-source.json"))
    sha = _head_sha(a.source)
    if sha != ks["source"]["commit_sha"]:
        print(f"ERROR: source checkout is at {sha[:12]} but knowledge-source.json pins "
              f"{ks['source']['commit_sha'][:12]}. Check out the pinned commit or re-run init.")
        return 2
    recs = graph.extract(a.source, ks["source"]["repo"], sha, ks.get("graph_options"),
                         inventory_only=a.inventory_only)
    text = graph.to_jsonl(recs)
    for rel, content in views.build_derived(recs, text, ks["appid"], ks["generated_at"]).items():
        path = os.path.join(a.bundle, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
    nodes = sum(1 for r in recs if r["rec"] == "node")
    print(f"graph: {nodes} nodes, {len(recs) - nodes - 1} edges, {len(text) // 1024} KB")
    return 0


def stamp_sources(bundle: str, ks: dict) -> int:
    """Point every section/domain map at the current source pin and graph hash."""
    from kfbundle.common import dump_frontmatter, sha256_bytes, split_frontmatter
    with open(os.path.join(bundle, "code-graph", "code-graph.jsonl"), "rb") as fh:
        gsha = sha256_bytes(fh.read())
    changed = 0
    for sub in ("sections", "domains-maps"):
        d = os.path.join(bundle, sub)
        for name in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            path = os.path.join(d, name)
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            fm, body, err = split_frontmatter(text)
            if fm is None or err:
                continue
            for s in fm.get("sources") or []:
                if isinstance(s, dict) and s.get("kind") == "source-repo":
                    s["repo"], s["commit_sha"] = ks["source"]["repo"], ks["source"]["commit_sha"]
                elif isinstance(s, dict) and s.get("kind") == "code-graph":
                    s["path"], s["sha256"] = "code-graph/code-graph.jsonl", gsha
            new = dump_frontmatter(fm) + body
            if new != text:
                with open(path, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(new)
                changed += 1
    return changed


def cmd_controls(a) -> int:
    ks = controls.load_json(os.path.join(a.bundle, "knowledge-source.json"))
    appid = ks["appid"]
    stamped = stamp_sources(a.bundle, ks)
    if stamped:
        print(f"stamped source pin + graph hash into {stamped} file(s)")
    controls.write_manifest(a.bundle, appid, ks["generated_at"])
    controls.write_index(a.bundle, appid, ks)
    log_path = os.path.join(a.bundle, "log.md")
    if a.log_summary:
        date = ks["generated_at"][:10]
        block = controls.log_block(date, a.log_summary, a.log_bullet or [])
        if os.path.exists(log_path):
            with open(log_path, encoding="utf-8") as fh:
                text = controls.insert_log_block(fh.read(), block, date)
            with open(log_path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
        else:
            controls.write_initial_log(a.bundle, appid, block)
    elif not os.path.exists(log_path):
        print("ERROR: no log.md yet — pass --log-summary for the first controls run")
        return 2
    print(f"controls written for {appid}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init")
    for flag in ("--bundle", "--appid", "--title", "--repo", "--source", "--approver"):
        i.add_argument(flag, required=True)
    i.add_argument("--repo-id", type=int, required=True)
    i.add_argument("--generated-at")
    i.add_argument("--third-party", action="append")
    i.add_argument("--generated", action="append")
    i.add_argument("--exclude", action="append")
    i.add_argument("--bootstrap", action="store_true")
    g = sub.add_parser("graph")
    g.add_argument("--bundle", required=True)
    g.add_argument("--source", required=True)
    g.add_argument("--inventory-only", action="store_true",
                   help="degraded mode when tree-sitter grammars are unavailable")
    c = sub.add_parser("controls")
    c.add_argument("--bundle", required=True)
    c.add_argument("--log-summary")
    c.add_argument("--log-bullet", action="append")
    a = p.parse_args(argv)
    return {"init": cmd_init, "graph": cmd_graph, "controls": cmd_controls}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())

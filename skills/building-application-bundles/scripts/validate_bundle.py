#!/usr/bin/env python3
"""Validate an application bundle with the same rules the gate enforces.

  validate_bundle.py --bundle DIR [--source DIR] [--registry .github/kf/config.yml]
                     [--reproduce] [--json]

  --source     verify every `src` citation hash at the pinned commit (B6)
  --reproduce  re-run the extractor and byte-compare graph, metrics and views (G11)
Exit 0 only when there are no errors. Fix, re-run, repeat until it passes.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kfbundle import controls, graph, lint, views  # noqa: E402
from kfbundle.lint import Finding  # noqa: E402


def reproduce(bundle: str, source: str) -> list[Finding]:
    ks = controls.load_json(os.path.join(bundle, "knowledge-source.json"))
    sha = subprocess.run(["git", "-C", source, "rev-parse", "HEAD"], capture_output=True,
                         text=True).stdout.strip()
    if sha != ks["source"]["commit_sha"]:
        return [Finding("G11", "code-graph", 0, f"source checkout {sha[:12]} is not the pinned commit")]
    recs = graph.extract(source, ks["source"]["repo"], sha, ks.get("graph_options"))
    out = []
    for rel, content in views.build_derived(recs, graph.to_jsonl(recs), ks["appid"], ks["generated_at"]).items():
        try:
            with open(os.path.join(bundle, rel), encoding="utf-8") as fh:
                current = fh.read()
        except OSError:
            current = None
        if current != content:
            out.append(Finding("G11", rel, 0, "derived artifact does not reproduce byte-for-byte — "
                                              "regenerate with the pinned toolchain (build_bundle.py graph)"))
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--bundle", required=True)
    p.add_argument("--source")
    p.add_argument("--registry")
    p.add_argument("--reproduce", action="store_true")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    reader = None
    if a.source:
        ks = controls.load_json(os.path.join(a.bundle, "knowledge-source.json"))
        reader = controls.git_reader(a.source, ks["source"]["commit_sha"])
    registry = None
    if a.registry:
        with open(a.registry, encoding="utf-8") as fh:
            registry = yaml.safe_load(fh)
    findings = lint.lint_bundle(a.bundle, reader, registry)
    if a.reproduce:
        if not a.source:
            print("--reproduce needs --source")
            return 2
        findings += reproduce(a.bundle, a.source)
    errors = [f for f in findings if f.severity == "error"]
    if a.json:
        print(json.dumps([f.as_dict() for f in findings], indent=2))
    else:
        for f in findings:
            print(f"{f.severity.upper():5} {f.code:4} {f.path}:{f.line}  {f.message}")
        print(f"{len(errors)} error(s), {len(findings) - len(errors)} warning(s) — "
              + ("PASS" if not errors else "FAIL"))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())

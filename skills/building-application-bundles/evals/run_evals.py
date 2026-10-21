#!/usr/bin/env python3
"""Deterministic half of the skill evals (no model needed)."""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "scripts")
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, SCRIPTS)

from kfbundle import controls, graph  # noqa: E402
from kfbundle.lint import lint_bundle  # noqa: E402


def source(pin, cache):
    path = os.path.join(cache, pin["repo"].split("/")[1]) if cache else None
    if path and os.path.isdir(path):
        head = subprocess.run(["git", "-C", path, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        if head == pin["commit_sha"]:
            return path
    d = tempfile.mkdtemp(prefix="kf-eval-")
    for cmd in (["git", "init", "-q", d], ["git", "-C", d, "fetch", "-q", "--depth", "1",
                f"https://github.com/{pin['repo']}", pin["commit_sha"]], ["git", "-C", d, "checkout", "-q", "FETCH_HEAD"]):
        subprocess.run(cmd, check=True)
    return d


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-cache")
    a = p.parse_args()
    failed = 0
    for path in sorted(glob.glob(os.path.join(HERE, "0*.json"))):
        ev = json.load(open(path))
        pin, chk = ev["pinned"], ev["deterministic_checks"]
        src = source(pin, a.source_cache)
        problems = []
        recs = graph.extract(src, pin["repo"], pin["commit_sha"])
        nodes = [r for r in recs if r["rec"] == "node"]
        edges = [r for r in recs if r["rec"] == "edge"]
        kinds = Counter(e["kind"] for e in edges)
        if "nodes_between" in chk and not chk["nodes_between"][0] <= len(nodes) <= chk["nodes_between"][1]:
            problems.append(f"{len(nodes)} nodes outside {chk['nodes_between']}")
        if "edges_between" in chk and not chk["edges_between"][0] <= len(edges) <= chk["edges_between"][1]:
            problems.append(f"{len(edges)} edges outside {chk['edges_between']}")
        for k, n in chk.get("min_edges_by_kind", {}).items():
            if kinds[k] < n:
                problems.append(f"{kinds[k]} {k} edges < {n}")
        for f in chk.get("parse_errors_include", []):
            if not any(r["id"] == f and r.get("parse_error") for r in nodes):
                problems.append(f"{f} not flagged parse_error")
        bundle = os.path.join(REPO, "application-bundles", pin["appid"])
        if "corrupt_citation" in chk:
            tmp = tempfile.mkdtemp(prefix="kf-eval-bundle-")
            shutil.copytree(bundle, os.path.join(tmp, pin["appid"]))
            bundle = os.path.join(tmp, pin["appid"])
            cc = chk["corrupt_citation"]
            fp = os.path.join(bundle, cc["file"])
            text = open(fp).read()
            import re
            text = re.sub(rf"(\[\^{cc['footnote']}\]: src · [^#]+#)L\d+-L\d+", rf"\g<1>{cc['range']}", text)
            open(fp, "w").write(text)
        if "validator" in chk:
            found = lint_bundle(bundle, controls.git_reader(src, pin["commit_sha"]), None)
            errs = [f for f in found if f.severity == "error"]
            if chk["validator"] == "pass" and errs:
                problems.append(f"validator failed: {errs[0].message}")
            if chk["validator"] == "fail" and not any(f.code == chk.get("error_code") for f in errs):
                problems.append("validator did not fail with " + chk.get("error_code", "?"))
        failed += bool(problems)
        print(f"{'PASS' if not problems else 'FAIL'} {os.path.basename(path)} — {len(nodes)} nodes, {len(edges)} edges"
              + ("" if not problems else f" — {'; '.join(problems)}"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

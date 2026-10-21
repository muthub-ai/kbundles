#!/usr/bin/env python3
"""Post-merge tripwire: re-lint every bundle on main and report (alert-only, never blocks).

Catches what per-PR gates cannot: two independently valid PRs whose merge
produced an invalid main (e.g. two manifest hunks that merged cleanly into
bad JSON), or a ceremony file present on disk but not registered.
"""
import glob
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "skills", "building-application-bundles", "scripts"))

import yaml  # noqa: E402

from kfbundle.lint import lint_bundle  # noqa: E402
from kfbundle.manifest import ManifestError, parse_manifest  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "gate"))
from kfgate.owners import parse as owners_parse  # noqa: E402


def main() -> int:
    with open(os.path.join(ROOT, ".github/kf/config.yml"), encoding="utf-8") as fh:
        registry = yaml.safe_load(fh)
    alerts = []
    for bdir in sorted(glob.glob(os.path.join(ROOT, "application-bundles", "*"))):
        appid = os.path.basename(bdir)
        alerts += [f"{appid}/{f.path}: {f.message}" for f in lint_bundle(bdir, None, registry) if f.severity == "error"]
        try:
            with open(os.path.join(bdir, "bundle-manifest.json"), encoding="utf-8") as fh:
                _, entries, _ = parse_manifest(fh.read())
            registered = {o["path"] for _, o in entries}
        except (OSError, ManifestError) as exc:
            alerts.append(f"{appid}/bundle-manifest.json: {exc}")
            continue
        for path in glob.glob(os.path.join(bdir, "knowledge-sources", "agile-ceremonies", "*", "*", "*.md")):
            rel = os.path.relpath(path, bdir).replace(os.sep, "/")
            if rel.endswith("/log.md") or rel in registered:      # legacy files are also in the manifest
                continue
            fname = os.path.basename(rel)
            log = os.path.join(os.path.dirname(path), "log.md")
            text = open(log, encoding="utf-8").read() if os.path.exists(log) else ""
            if f"[{fname}]({fname})" not in text:
                alerts.append(f"{appid}/{rel}: ceremony file on main is not registered in its team log.md")
        if os.path.exists(os.path.join(bdir, "OWNERS")):
            _, err = owners_parse(open(os.path.join(bdir, "OWNERS"), encoding="utf-8").read())
            if err:
                alerts.append(f"{appid}/OWNERS: {err}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    lines = ["## kf-tripwire", ""] + ([f"- ⚠️ {a}" for a in alerts] or ["✅ main is consistent: every bundle lints clean."])
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
    for a in alerts:
        print(f"::warning title=kf-tripwire::{a}")
    print("\n".join(lines))
    return 0   # alert-only by design


if __name__ == "__main__":
    sys.exit(main())

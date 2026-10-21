#!/usr/bin/env python3
"""Verify every appid's numeric repo_id in the trust root against the GitHub API.

The id is the rename-proof identity of a source repo (B3 compares bundles
against the registry; this compares the registry against GitHub). Runs in
kf-tripwire with the workflow token; exits 1 on any mismatch or lookup failure.
"""
import json
import os
import sys
import urllib.request

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def main() -> int:
    with open(os.path.join(ROOT, ".github/kf/config.yml"), encoding="utf-8") as fh:
        apps = yaml.safe_load(fh)["appids"]
    token, bad = os.environ.get("GITHUB_TOKEN"), 0
    for appid, reg in sorted(apps.items()):
        req = urllib.request.Request(f"https://api.github.com/repos/{reg['repo']}",
                                     headers={"Accept": "application/vnd.github+json",
                                              **({"Authorization": f"Bearer {token}"} if token else {})})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                actual = json.load(resp)["id"]
        except Exception as exc:  # noqa: BLE001
            print(f"::error::{appid}: cannot look up {reg['repo']}: {exc}")
            bad += 1
            continue
        ok = actual == reg["repo_id"]
        bad += not ok
        print(f"::{'notice' if ok else 'error'}::{appid}: {reg['repo']} registry id {reg['repo_id']} "
              f"{'matches' if ok else 'DIFFERS from'} GitHub id {actual}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

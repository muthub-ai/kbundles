#!/usr/bin/env python3
"""Append sha256 span hashes to `src · path#La-Lb` footnotes in bundle markdown.

  fill_citations.py --bundle DIR --source DIR [FILE ...]

Reads cited lines from the source repo at the commit pinned in
knowledge-source.json (git blobs, not the working tree). Existing hashes are
left untouched; validate_bundle.py re-verifies all of them.
"""
from __future__ import annotations

import argparse
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kfbundle import citations, controls  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--bundle", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("files", nargs="*")
    a = p.parse_args(argv)
    ks = controls.load_json(os.path.join(a.bundle, "knowledge-source.json"))
    read = controls.git_reader(a.source, ks["source"]["commit_sha"])
    files = a.files or sorted(glob.glob(os.path.join(a.bundle, "sections", "*.md"))
                              + glob.glob(os.path.join(a.bundle, "domains-maps", "*.md")))
    failed = 0
    for path in files:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        new, errors = citations.fill(text, read)
        for e in errors:
            print(f"{path}: {e}")
        failed += len(errors)
        if new != text:
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(new)
            print(f"filled {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Thin orchestrator over the canonical skill scripts (one implementation, by construction).

  tools/bundle_builder/build.py <build_bundle|fill_citations|validate_bundle> [args...]
"""
import os
import runpy
import sys

SCRIPTS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "skills",
                                       "building-application-bundles", "scripts"))
TOOLS = {"build_bundle", "fill_citations", "validate_bundle"}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in TOOLS:
        sys.exit(f"usage: build.py {{{'|'.join(sorted(TOOLS))}}} [args...]")
    tool = sys.argv.pop(1)
    sys.argv[0] = os.path.join(SCRIPTS, f"{tool}.py")
    sys.path.insert(0, SCRIPTS)
    runpy.run_path(sys.argv[0], run_name="__main__")

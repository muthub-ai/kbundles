"""G9 — deterministic PII denylist (emails, phone numbers, employee ids) on changed knowledge."""
from kfgate.context import Finding

from kfbundle.pii import scan

GATE = "G9"
SKIP_SUFFIXES = ("/code-graph/code-graph.jsonl",)   # derived from public source; verified by G11


def check(ctx):
    out = []
    for c in ctx.changes:
        if c.status == "D" or not c.path.startswith("application-bundles/") or c.path.endswith(SKIP_SUFFIXES):
            continue
        text = ctx.head_text(c.path) or ""
        for line, kind, hit in scan(text):
            out.append(Finding(GATE, f"line {line}: possible {kind} {hit!r} — PII may not enter the knowledge "
                                     "repo", c.path))
    return out

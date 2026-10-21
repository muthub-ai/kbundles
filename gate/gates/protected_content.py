"""Protected content — applies to EVERY PR except a verified revert.

Accepted ceremony knowledge (anything under knowledge-sources/) is immutable;
its manifest entries stay byte-identical; every log.md is insert-only.
"""
from kfgate.context import Finding
from kfgate.textdiff import insertions

from kfbundle.manifest import CEREMONY_PREFIX, ManifestError, parse_manifest

GATE = "PC"


def check(ctx):
    if ctx.cls == "revert":
        return []
    out = []
    for c in ctx.changes:
        p = c.path
        if not p.startswith("application-bundles/"):
            continue
        if p.endswith("/log.md"):
            if c.status == "D":
                out.append(Finding(GATE, "log.md files may never be deleted", p))
            elif c.status == "M" and insertions(ctx.mb_text(p) or "", ctx.head_text(p) or "") is None:
                out.append(Finding(GATE, "log.md is insert-only — existing lines were removed or edited", p))
        elif "/knowledge-sources/" in p and c.status in ("M", "D", "T"):
            out.append(Finding(GATE, "accepted ceremony knowledge may only be removed by a verified revert "
                                     "and never edited in place", p))
        elif p.endswith("/bundle-manifest.json") and c.status in ("M", "D"):
            if c.status == "D":
                out.append(Finding(GATE, "bundle-manifest.json may not be deleted", p))
                continue
            try:
                _, base_e, _ = parse_manifest(ctx.mb_text(p) or "")
                _, head_e, _ = parse_manifest(ctx.head_text(p) or "")
            except ManifestError as exc:
                out.append(Finding(GATE, f"manifest unreadable: {exc}", p))
                continue
            head_lines = {b for b, _ in head_e}
            for body, obj in base_e:
                if obj["path"].startswith(CEREMONY_PREFIX) and body not in head_lines:
                    out.append(Finding(GATE, f"ceremony manifest entry for {obj['path']} was removed or "
                                             "altered", p))
    return out

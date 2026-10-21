"""G6 — provenance: every item cites a span; every span is in the PR body and hashes to its footnote.

Verbatim evidence lives only in the scrub-able PR body; git holds the hashes.
"""
from kfgate.ceremony_doc import parse_evidence, span_sha
from kfgate.context import Finding

GATE = "G6"


def check(ctx):
    n, out = ctx.notes, []
    doc, fm = n.get("cer_doc"), n.get("cer_fm")
    if doc is None or not fm:
        return out
    path = n["cer_path"]
    src_ids = {s.get("id") for s in (fm.get("sources") or []) if isinstance(s, dict)}
    used = set()
    for item in doc.items:
        if not item.refs:
            out.append(Finding(GATE, f"line {item.line}: item has no evidence footnote", path))
        for r in item.refs:
            used.add(r)
            if r not in doc.footnotes:
                out.append(Finding(GATE, f"line {item.line}: footnote [^{r}] is not defined (or malformed)", path))
    for line, raw in doc.bad_footnotes:
        out.append(Finding(GATE, f"line {line}: footnote must be `[^id]: sN · \"Locator\" segment · "
                                 f"span_sha256:<64 hex>` — got {raw[:60]!r}", path))
    evidence = parse_evidence(ctx.pr.body)
    for fid, note in sorted(doc.footnotes.items()):
        if fid not in used:
            out.append(Finding(GATE, f"footnote [^{fid}] is never cited (orphan)", path))
        if note["src"] not in src_ids:
            out.append(Finding(GATE, f"[^{fid}] cites undeclared source {note['src']}", path))
        ev = evidence.get(fid)
        if ev is None:
            out.append(Finding(GATE, f"[^{fid}] has no verbatim evidence span in the PR body", path))
        elif ev[0] != note["src"] or span_sha(ev[1]) != note["sha"]:
            out.append(Finding(GATE, f"[^{fid}] evidence span does not hash to its span_sha256 "
                                     "(tampered or mismatched evidence)", path))
    return out

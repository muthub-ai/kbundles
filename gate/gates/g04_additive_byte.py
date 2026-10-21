"""G4 — semantic + byte additive-only.

Ceremony file is added (accepted knowledge is never edited in place); the
ceremony-team log (which registers the file — ceremony PRs never touch the
manifest, spec v0.5) either is created as title + exactly one block, or
gains exactly one block at its newest-first position with every other byte kept.
"""
from kfgate.ceremony_doc import log_blocks
from kfgate.context import Finding
from kfgate.textdiff import insertions

GATE = "G4"


def _check_log(old, new, out, path):
    if new is None:
        out.append(Finding(GATE, "the ceremony-team log.md must be created or updated", path))
        return
    if old is None:
        blocks = log_blocks(new)
        title = new.split("\n", 1)[0] + "\n\n" if new.startswith("# ") else ""
        if len(blocks) != 1 or new != (title + blocks[0][1] if title else blocks[0][1]):
            out.append(Finding(GATE, "a newly created ceremony-team log must contain exactly an optional "
                                     "title line plus ONE entry block — no other history", path))
        return
    groups = insertions(old, new)
    if groups is None:
        out.append(Finding(GATE, "log.md lines were removed or edited — logs are insert-only", path))
        return
    inserted = [ln for g in groups for ln in g]
    heads = [ln for ln in inserted if ln.startswith("## ")]
    if len(heads) != 1:
        out.append(Finding(GATE, f"exactly one new log block must be inserted (found {len(heads)} headings)", path))
    dates = [h[3:13] for h, _ in log_blocks(new)]
    if dates != sorted(dates, reverse=True):
        out.append(Finding(GATE, "log blocks are not newest-first — insert at the date-ordered position", path))


def check(ctx):
    n, out = ctx.notes, []
    if "cer_path" not in n:
        return out
    for c in n["ceremony_files"]:
        if c.status != "A":
            out.append(Finding(GATE, "accepted ceremony knowledge is immutable — a ceremony PR may only "
                                     "ADD its file (corrections go through the revert class)", c.path))
    _check_log(ctx.mb_text(n["log_path"]), ctx.head_text(n["log_path"]), out, n["log_path"])
    return out

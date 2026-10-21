"""Line-level diff helpers for insert-only rules."""
from __future__ import annotations

import difflib


def insertions(old: str, new: str) -> list[list[str]] | None:
    """Return the inserted line groups if `new` only inserts into `old`; None if anything
    was deleted or replaced."""
    a, b = old.splitlines(keepends=True), new.splitlines(keepends=True)
    groups = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if op in ("delete", "replace"):
            return None
        if op == "insert":
            groups.append(b[j1:j2])
    return groups


def line_delta(old: str | None, new: str | None) -> tuple[frozenset, frozenset]:
    a = (old or "").splitlines()
    b = (new or "").splitlines()
    sa, sb = set(a), set(b)
    return frozenset(sb - sa), frozenset(sa - sb)

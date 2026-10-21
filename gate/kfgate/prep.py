"""Parse the ceremony PR's files once; every ceremony gate reads ctx.notes."""
from __future__ import annotations

import os
import sys

from .ceremony_doc import FILE_RE, PATH_RE, log_path, parse_body

_LIB = os.path.join(os.path.dirname(__file__), "..", "..", "skills", "building-application-bundles", "scripts")
sys.path.insert(0, os.path.abspath(_LIB))

from kfbundle.common import split_frontmatter  # noqa: E402


def fm_offset(text: str) -> int:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end > 0:
            return text[: end + 5].count("\n")
    return 0


def prep_ceremony(ctx) -> None:
    files = [c for c in ctx.changes if PATH_RE.match(c.path) and not c.path.endswith("/log.md")]
    ctx.notes["ceremony_files"] = files
    if not files or not ctx.appid:
        return
    path = files[0].path
    m = PATH_RE.match(path)
    ctx.appid, ctx.ceremony, ctx.team = m.group("appid"), m.group("ceremony"), m.group("team")
    fmatch = FILE_RE.match(m.group("file"))
    text = ctx.head_text(path) if files[0].status != "D" else None
    ctx.notes.update(cer_path=path, cer_file=m.group("file"), cer_date=fmatch.group("date") if fmatch else None,
                     cer_name_ceremony=fmatch.group("ceremony") if fmatch else None, cer_text=text)
    ctx.notes["log_path"] = log_path(ctx.appid, ctx.ceremony, ctx.team)
    ctx.notes["manifest_path"] = f"application-bundles/{ctx.appid}/bundle-manifest.json"
    if text is None:
        return
    fm, body, err = split_frontmatter(text)
    off = fm_offset(text)
    ctx.notes.update(cer_fm=fm or {}, cer_body=body, cer_err=err, cer_off=off,
                     cer_doc=parse_body(body, off))

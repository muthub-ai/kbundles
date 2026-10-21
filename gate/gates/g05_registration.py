"""G5 — registration: the manifest entry and the log block describe exactly the new file."""
import datetime as dt
from zoneinfo import ZoneInfo

from kfgate.ceremony_doc import log_blocks
from kfgate.context import Finding

from kfbundle.common import get_path

GATE = "G5"


def check(ctx):
    n, out = ctx.notes, []
    fm = n.get("cer_fm")
    if not fm or "cer_path" not in n:
        return out
    entry = n.get("manifest_entry")
    if entry:
        want = {"type": fm.get("type"), "team": ctx.team, "added": get_path(fm, "generated.at"),
                "generated_by": get_path(fm, "generated.by")}
        for k, v in want.items():
            if entry.get(k) != v:
                out.append(Finding(GATE, f"manifest entry {k}={entry.get(k)!r} but the file says {v!r}",
                                   n["manifest_path"]))
        if get_path(entry, "review.approver") != get_path(fm, "x_kf.review.approver"):
            out.append(Finding(GATE, "manifest entry approver differs from the file's x_kf.review.approver",
                               n["manifest_path"]))
    log = ctx.head_text(n["log_path"]) or ""
    link = f"[{n['cer_file']}]({n['cer_file']})"
    blocks = [b for b in log_blocks(log) if link in b[1]]
    if len(blocks) != 1:
        out.append(Finding(GATE, f"exactly one log block must link {link} (found {len(blocks)})", n["log_path"]))
        return out
    tz = ((ctx.appid_cfg() or {}).get("teams") or {}).get(ctx.team, {}).get("timezone")
    gat = get_path(fm, "generated.at")
    try:
        when = dt.datetime.fromisoformat(str(gat))
        day = when.astimezone(ZoneInfo(tz)).date().isoformat() if tz else when.date().isoformat()
        if not blocks[0][0].startswith(f"## {day}: "):
            out.append(Finding(GATE, f"log heading must use the run date {day} (date of generated.at in the "
                                     f"team time zone), found '{blocks[0][0]}'", n["log_path"]))
    except (ValueError, TypeError):
        pass  # G2 already reports a bad generated.at
    return out

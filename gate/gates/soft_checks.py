"""Soft checks (warnings only): first contribution to a team, stale generation time."""
import datetime as dt
import os

from kfgate import git
from kfgate.context import Finding

from kfbundle.common import get_path, split_frontmatter

GATE = "S"
STALE_DAYS = 7     # a recap distilled more than a week before review is usually a forgotten branch


def check(ctx):
    n, out = ctx.notes, []
    fm = n.get("cer_fm")
    if not fm or ctx.cls != "ceremony":
        return out
    team_dir = os.path.dirname(n["cer_path"])
    listing = git.git(ctx.repo, "ls-tree", "--name-only", f"{ctx.base}:{team_dir}", check=False).split()
    people = set()
    for name in listing:
        if name.endswith(".md") and name != "log.md":
            prior_fm, _, _ = split_frontmatter(ctx.base_text(f"{team_dir}/{name}") or "")
            for key in ("x_kf.review.approver", "x_kf.review.requested_by"):
                v = get_path(prior_fm or {}, key)
                if v:
                    people.add(str(v).lstrip("@").lower())
    approver = str(get_path(fm, "x_kf.review.approver") or "").lstrip("@").lower()
    if listing and ctx.pr.author.lower() not in people and approver not in people:
        out.append(Finding(GATE, f"first contribution to team '{ctx.team}': neither @{ctx.pr.author} nor "
                                 f"@{approver} appears on any earlier {ctx.ceremony} file for this team — "
                                 "check this is the right appid/team", n["cer_path"], "warn"))
    try:
        gat = dt.datetime.fromisoformat(str(get_path(fm, "generated.at")))
        if (ctx.now - gat).days > STALE_DAYS:
            out.append(Finding(GATE, f"generated.at is {(ctx.now - gat).days} days old", n["cer_path"], "warn"))
    except (ValueError, TypeError):
        pass
    return out

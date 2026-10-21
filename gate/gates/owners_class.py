"""Owners class (spec v0.5): the only way to create or change an app's OWNERS file.

Write-set: exactly `application-bundles/<appid>/OWNERS` of one registered appid.
Naming: branch `owners/<appid>`, title `[KF-OWNERS] <appid> — <summary>`.
Approval (engine): one of the app's CURRENT approvers (base-ref OWNERS), or a
KF steward when the app has no OWNERS file yet ("claim").
"""
import re

from kfgate.context import Finding
from kfgate.owners import approvers_for, owners_path, parse

GATE = "OW"


def check(ctx):
    out = []
    appids = ctx.notes.get("appids", [])
    if len(appids) != 1:
        return [Finding(GATE, f"an owners PR must touch exactly one appid; found {', '.join(appids)}")]
    appid = ctx.appid
    path = owners_path(appid)
    for c in ctx.changes:
        if c.path != path:
            out.append(Finding(GATE, "owners PRs may change only application-bundles/<appid>/OWNERS", c.path))
        elif c.status == "D":
            out.append(Finding(GATE, "OWNERS may not be deleted (the app would silently fall back to the "
                                     "stewards); replace its approvers instead", c.path))
        elif c.new_mode in ("120000", "160000"):
            out.append(Finding(GATE, "OWNERS must be a regular file", c.path))
    if ctx.appid_cfg() is None:
        out.append(Finding(GATE, f"appid '{appid}' is not registered in .github/kf/config.yml"))
    if not ctx.bootstrap:
        if ctx.pr.branch != f"owners/{appid}":
            out.append(Finding(GATE, f"branch must be exactly 'owners/{appid}' (found '{ctx.pr.branch}')"))
        if not re.match(rf"^\[KF-OWNERS\] {re.escape(appid)} — \S.*$", ctx.pr.title or ""):
            out.append(Finding(GATE, f"title must look like '[KF-OWNERS] {appid} — <what changed>' "
                                     f"(found '{ctx.pr.title}')"))
    new, err = parse(ctx.head_text(path))
    if err:
        out.append(Finding(GATE, err, path))
    for login in new or []:
        if not ctx.ids.exists(login):
            out.append(Finding(GATE, f"@{login} is not a resolvable GitHub user", path))
        elif not ctx.ids.can_write(login):
            out.append(Finding(GATE, f"@{login} lacks write permission, so their approval could never count", path))
    if new and len(new) < 2:
        out.append(Finding(GATE, "list at least two approvers so the app is not blocked when one is away",
                           path, "warn"))
    current, source = approvers_for(ctx, appid)
    ctx.notes["owners_approvers"] = current
    ctx.notes["owners_source"] = source
    return out

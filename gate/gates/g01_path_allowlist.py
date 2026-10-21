"""G1 — path allowlist (ceremony class): exactly one appid+team, three files.

Allowed: the ceremony file, that team's ceremony-team log.md, the appid's
bundle-manifest.json. Symlinks, gitlinks and mode changes are rejected.
"""
from kfgate.context import Finding

GATE = "G1"


def check(ctx):
    out = []
    for c in ctx.changes:
        if c.new_mode in ("120000", "160000"):
            out.append(Finding(GATE, "symlinks and submodules are not allowed in knowledge PRs", c.path))
        elif c.status == "M" and c.old_mode != c.new_mode:
            out.append(Finding(GATE, f"file mode change {c.old_mode}→{c.new_mode} is not allowed", c.path))
    appids = ctx.notes.get("appids", [])
    if len(appids) != 1:
        return out + [Finding(GATE, f"a ceremony PR must touch exactly one appid; found {', '.join(appids)}")]
    if "cer_path" not in ctx.notes:
        return out + [Finding(GATE, "no ceremony file found under knowledge-sources/agile-ceremonies/")]
    allowed = {ctx.notes["cer_path"], ctx.notes["log_path"], ctx.notes["manifest_path"]}
    for p in ctx.paths:
        if p in allowed:
            continue
        if p == f"application-bundles/{ctx.appid}/log.md":
            out.append(Finding(GATE, "ceremony PRs may never touch the appid-root log.md (D16)", p))
        elif "/agile-ceremonies/" in p:
            out.append(Finding(GATE, f"second ceremony/team path in one PR — only {ctx.ceremony}/{ctx.team} "
                                     "is allowed here", p))
        else:
            out.append(Finding(GATE, "outside the ceremony write-set (ceremony file + ceremony-team log + "
                                     "manifest of one appid)", p))
    return out

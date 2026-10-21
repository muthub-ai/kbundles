"""G10 — client trailer on every commit. Traceability only: a trailer is spoofable,
so absence fails and presence proves little."""
from kfgate import git
from kfgate.context import Finding

GATE = "G10"
TRAILERS = {"ceremony": "KF-Grill-Client:", "bundle-update": "KF-Bundle-Builder:", "revert": "KF-Revert-Of:"}


def check(ctx):
    want = TRAILERS.get(ctx.cls)
    if not want:
        return []
    out = []
    for sha in git.commits(ctx.repo, ctx.mb, ctx.head):
        if not any(line.startswith(want) for line in git.message(ctx.repo, sha).splitlines()):
            out.append(Finding(GATE, f"commit {sha[:12]} lacks the '{want}' trailer"))
    return out

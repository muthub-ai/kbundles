"""PR class dispatch — FAIL CLOSED (plan §6.1, review finding P1).

  ceremony       knowledge-sources/agile-ceremonies/** of one appid+team, or a grill/ branch
  bundle-update  sections/, code-graph/, domains-maps/, control files of one appid, or a bundle/ branch
  revert         deletes accepted ceremony knowledge (verified as a semantic inverse), revert/ branch
                 or kf-revert label
  owners         exactly application-bundles/<appid>/OWNERS of one appid (owners/<appid> branch)
  tooling        trust root and tooling only (.github/, gate/, tools/, skills/, scenarios/):
                 needs a code owner's approval
  other          README.md, PRODUCTION.md, docs/** only
  unknown        anything else, or any mix of the above → failure
"""
from __future__ import annotations

from . import BUNDLES_ROOT, git
from .ceremony_doc import PATH_RE

TOOLING_PREFIXES = (".github/", "gate/", "tools/", "skills/", "scenarios/")
OTHER_FILES = {"README.md", "PRODUCTION.md", ".gitignore"}
OTHER_PREFIXES = ("docs/",)
REVERT_TRAILER = "KF-Revert-Of:"


def _kind(path: str) -> str:
    if path.startswith(BUNDLES_ROOT + "/"):
        return "bundle"
    if path.startswith(TOOLING_PREFIXES):
        return "tooling"
    if path in OTHER_FILES or path.startswith(OTHER_PREFIXES):
        return "other"
    return "unknown"


def _is_owners(path: str) -> bool:
    parts = path.split("/")
    return len(parts) == 3 and parts[0] == BUNDLES_ROOT and parts[2] == "OWNERS"


def revert_target(ctx) -> str | None:
    for sha in git.commits(ctx.repo, ctx.mb, ctx.head):
        for line in git.message(ctx.repo, sha).splitlines():
            if line.startswith(REVERT_TRAILER):
                return line[len(REVERT_TRAILER):].strip()
    return None


def classify(ctx) -> str:
    kinds = {_kind(p) for p in ctx.paths}
    branch = ctx.pr.branch or ""
    if not ctx.paths:
        ctx.cls = "other"
    elif "unknown" in kinds or len(kinds - {"other"}) > 1 or ("bundle" in kinds and "other" in kinds):
        ctx.cls = "unknown"
        ctx.notes["unknown_reason"] = (
            "paths outside every known PR class" if "unknown" in kinds else
            "PR mixes knowledge with tooling/docs changes — split it")
    elif "bundle" in kinds and any(_is_owners(p) for p in ctx.paths):
        appids = sorted({p.split("/")[1] for p in ctx.paths if p.count("/") >= 2})
        ctx.notes["appids"] = appids
        ctx.appid = appids[0] if len(appids) == 1 else None
        if all(_is_owners(p) for p in ctx.paths):
            ctx.cls = "owners"
        else:
            ctx.cls = "unknown"
            ctx.notes["unknown_reason"] = "PR mixes an OWNERS change with other files — split it"
    elif "bundle" in kinds:
        deletes = any(c.status == "D" and "/knowledge-sources/" in c.path for c in ctx.changes)
        if "kf-revert" in ctx.pr.labels or branch.startswith("revert/") or revert_target(ctx) or deletes:
            ctx.cls = "revert"
        elif branch.startswith("grill/"):
            ctx.cls = "ceremony"
        elif branch.startswith("bundle/"):
            ctx.cls = "bundle-update"
        elif any("/knowledge-sources/" in p for p in ctx.paths):
            ctx.cls = "ceremony"
        else:
            ctx.cls = "bundle-update"
        appids = sorted({p.split("/")[1] for p in ctx.paths if p.count("/") >= 2})
        ctx.notes["appids"] = appids
        ctx.appid = appids[0] if len(appids) == 1 else None
        for p in ctx.paths:
            m = PATH_RE.match(p)
            if m and m.group("file") != "log.md":
                ctx.ceremony, ctx.team = m.group("ceremony"), m.group("team")
                break
        else:
            for p in ctx.paths:
                m = PATH_RE.match(p)
                if m:
                    ctx.ceremony, ctx.team = m.group("ceremony"), m.group("team")
                    break
    elif "tooling" in kinds:
        ctx.cls = "tooling"
    else:
        ctx.cls = "other"
    return ctx.cls

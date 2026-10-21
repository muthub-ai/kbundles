"""Revert class (spec §8.5, plan §6.1): the sanctioned exit for bad or sensitive knowledge.

A revert PR must be the SEMANTIC inverse of one merged ceremony squash commit:
the ceremony file deleted, its manifest entry removed by inverse splice, its
log block removed — plus exactly one added `## <date>: Reverted <file> — <reason>`
block so the removal stays visible. Bootstrapped (never-approved) files are
not revert targets. Approval: the original approver OR the fallback team.
"""
import re

from kfgate import git
from kfgate.ceremony_doc import PATH_RE, log_blocks, log_path, rel_to_bundle
from kfgate.classes import revert_target
from kfgate.context import Finding
from kfgate.textdiff import insertions

from kfbundle.common import get_path, split_frontmatter
from kfbundle.manifest import ManifestError, splice_remove

GATE = "RV"


def check(ctx):
    out = []
    f = lambda msg, path="": out.append(Finding(GATE, msg, path))  # noqa: E731
    target = revert_target(ctx)
    if not target:
        return [Finding(GATE, "deleting ceremony knowledge requires a revert PR whose commits carry "
                              "'KF-Revert-Of: <merged commit sha>'")]
    try:
        tsha = git.rev(ctx.repo, target)
    except git.GitError:
        return [Finding(GATE, f"revert target {target} is not a known commit")]
    if not git.is_ancestor(ctx.repo, tsha, ctx.base):
        return [Finding(GATE, f"revert target {tsha[:12]} is not merged into main")]
    tchanges = git.changes(ctx.repo, f"{tsha}^", tsha)
    cer = [c for c in tchanges if PATH_RE.match(c.path) and not c.path.endswith("/log.md")]
    if len(cer) != 1 or cer[0].status != "A":
        return [Finding(GATE, f"target {tsha[:12]} is not a single merged ceremony commit")]
    fpath = cer[0].path
    m = PATH_RE.match(fpath)
    appid, ceremony, team, fname = m.group("appid"), m.group("ceremony"), m.group("team"), m.group("file")
    ctx.appid, ctx.ceremony, ctx.team = appid, ceremony, team
    fm, _, _ = split_frontmatter(git.read_text(ctx.repo, tsha, fpath) or "")
    fm = fm or {}
    if get_path(fm, "x_kf.bootstrap") is True:
        f("the target was landed by direct bootstrap and never approved — it is not a revert target "
          "(remove it through a tooling cleanup with code-owner review)", fpath)
    lpath, mpath = log_path(appid, ceremony, team), f"application-bundles/{appid}/bundle-manifest.json"
    allowed = {fpath, lpath, mpath}
    for c in ctx.changes:
        if c.path not in allowed:
            f("a revert may change only the target file, its manifest entry and its ceremony-team log", c.path)
    if not any(c.path == fpath and c.status == "D" for c in ctx.changes):
        f("the target ceremony file must be deleted", fpath)
    legacy = any(c.path == mpath for c in tchanges)   # pre-v0.5 ceremony commits also spliced the manifest
    try:
        if legacy and ctx.head_text(mpath) != splice_remove(ctx.mb_text(mpath) or "", rel_to_bundle(fpath)):
            f("manifest must equal the base with exactly the target entry removed (inverse splice)", mpath)
        elif not legacy and any(c.path == mpath for c in ctx.changes):
            f("the target never touched the manifest, so its revert may not either", mpath)
    except ManifestError as exc:
        f(f"manifest: {exc}", mpath)
    base_log, head_log = ctx.mb_text(lpath) or "", ctx.head_text(lpath)
    link = f"[{fname}]({fname})"
    tblocks = [b for _, b in log_blocks(base_log) if link in b and "Reverted" not in b.split("\n", 1)[0]]
    if len(tblocks) != 1 or head_log is None:
        f("the target's log block must exist exactly once and the log must remain (never deleted)", lpath)
    else:
        without = base_log.replace(tblocks[0], "", 1)
        groups = insertions(without, head_log)
        added = [ln for g in groups for ln in g] if groups is not None else None
        heads = [ln for ln in (added or []) if ln.startswith("## ")]
        pat = re.compile(rf"^## \d{{4}}-\d{{2}}-\d{{2}}: Reverted {re.escape(fname)} — \S.*$")
        if groups is None or len(heads) != 1 or not pat.match(heads[0].rstrip("\n")):
            f(f"the log must lose exactly the target block and gain one '## <date>: Reverted {fname} — "
              "<reason>' block", lpath)
    if not ctx.bootstrap and "kf-revert" not in ctx.pr.labels:
        f("revert PRs must carry the 'kf-revert' label")
    original = str(get_path(fm, "x_kf.review.approver") or "").lstrip("@")
    ctx.notes["revert_approvers"] = sorted({original} | {a.lstrip("@") for a in
                                                          (ctx.config or {}).get("revert_fallback_approvers", [])})
    ctx.notes["revert_target"] = tsha
    return out

"""Bundle-update class structure gates (D18): B1 write-set, B3 coherence/registry, B4 manifest,
root log and index rules."""
import json
import re

from kfgate.context import Finding
from kfgate.textdiff import insertions
from kfgate.ceremony_doc import log_blocks

from kfbundle.common import get_path
from kfbundle.lint import BUNDLE_FILE_RE
from kfbundle.manifest import verify_bundle_ops

CEREMONY_LINK_RE = re.compile(r"\]\((knowledge-sources/agile-ceremonies/[^)]*\.md)\)")


def load_ks(ctx, ref="head"):
    text = (ctx.head_text if ref == "head" else ctx.mb_text)(f"application-bundles/{ctx.appid}/knowledge-source.json")
    try:
        return json.loads(text) if text else None
    except ValueError:
        return None


def check(ctx):
    out = []
    appids = ctx.notes.get("appids", [])
    if len(appids) != 1:
        return [Finding("B1", f"a bundle-update PR must touch exactly one appid; found {', '.join(appids)}")]
    root = f"application-bundles/{ctx.appid}/"
    for c in ctx.changes:
        rel = c.path[len(root):]
        if c.new_mode in ("120000", "160000"):
            out.append(Finding("B1", "symlinks and submodules are not allowed", c.path))
        if rel.startswith("knowledge-sources/"):
            out.append(Finding("B1", "bundle-update PRs may not touch knowledge-sources/ — ceremony knowledge "
                                     "changes only through the ceremony and revert classes", c.path))
        elif not BUNDLE_FILE_RE.match(rel):
            out.append(Finding("B1", "outside the application-bundle write-set (sections/, code-graph/, "
                                     "domains-maps/, control files)", c.path))
    cfg, reg = ctx.config or {}, ctx.appid_cfg()
    if ctx.appid in (cfg.get("reserved_appids") or []):
        out.append(Finding("B3", f"appid '{ctx.appid}' is reserved"))
    if not re.match(r"^[a-z]{5}$", ctx.appid or ""):
        out.append(Finding("B3", "appid must be exactly 5 lowercase letters"))
    if reg is None:
        return out + [Finding("B3", f"appid '{ctx.appid}' is not registered in .github/kf/config.yml")]
    ks = load_ks(ctx)
    ctx.notes["ks"] = ks
    if ks is None:
        return out + [Finding("B3", "knowledge-source.json is missing or not JSON", root + "knowledge-source.json")]
    if ks.get("appid") != ctx.appid:
        out.append(Finding("B3", "knowledge-source.json appid differs from the folder", root + "knowledge-source.json"))
    if get_path(ks, "source.repo") != reg.get("repo") or get_path(ks, "source.repo_id") != reg.get("repo_id"):
        out.append(Finding("B3", "source repo/repo_id disagree with the trust-root registry (rename-proof id)",
                           root + "knowledge-source.json"))
    sha = str(get_path(ks, "source.commit_sha") or "")
    want = f"bundle/{ctx.appid}/{sha[:12]}"
    if not ctx.bootstrap and ctx.pr.branch != want:
        out.append(Finding("B3", f"branch must be '{want}' (found '{ctx.pr.branch}')"))
    mpath = root + "bundle-manifest.json"
    for prob in verify_bundle_ops(ctx.mb_text(mpath), ctx.head_text(mpath) or ""):
        out.append(Finding("B4", prob, mpath))
    lpath = root + "log.md"
    old, new = ctx.mb_text(lpath), ctx.head_text(lpath)
    if new is None:
        out.append(Finding("B4", "the bundle-root log.md must exist", lpath))
    elif old is not None and old != new:
        groups = insertions(old, new)
        heads = [ln for g in (groups or []) for ln in g if ln.startswith("## ")]
        if groups is None or len(heads) != 1:
            out.append(Finding("B4", "bundle-root log.md is insert-only: exactly one new block per bundle update",
                               lpath))
    elif old is None:
        if len(log_blocks(new)) != 1:
            out.append(Finding("B4", "a new bundle-root log must start with exactly one block", lpath))
    index = ctx.head_text(root + "index.md") or ""
    for m in CEREMONY_LINK_RE.finditer(index):
        out.append(Finding("B4", f"index.md links ceremony file {m.group(1)} — link directories only so the "
                                 "index never goes stale", root + "index.md"))
    return out

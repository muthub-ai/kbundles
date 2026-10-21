"""Content-bound approval by a named human (spec §8.2, invariant I8).

An approval attaches to WHAT was approved, not to a SHA: the key is the set
of changed blobs plus the manifest entries and log lines the PR adds or
removes, each measured against that commit's own merge-base with main. A
`--refresh` that only re-seats the same entries on newer main keeps the key,
so approval survives; any content change invalidates it.
"""
from __future__ import annotations

from . import git
from .textdiff import line_delta

import sys, os  # noqa: E401
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "skills",
                                                "building-application-bundles", "scripts")))
from kfbundle.manifest import ManifestError, parse_manifest, render_entry  # noqa: E402


def _entries(text: str | None) -> dict[str, str]:
    if not text:
        return {}
    try:
        _, ents, _ = parse_manifest(text)
    except ManifestError:
        return {"<unparseable>": text}
    return {o["path"]: render_entry(o) for _, o in ents}


def content_key(repo: str, main: str, commit: str) -> tuple:
    mb = git.merge_base(repo, main, commit)
    key = []
    for c in git.changes(repo, mb, commit):
        if c.path.endswith("bundle-manifest.json"):
            old, new = _entries(git.read_text(repo, mb, c.path)), _entries(git.read_text(repo, commit, c.path))
            changed = frozenset((p, v) for p, v in new.items() if old.get(p) != v)
            gone = frozenset(p for p in old if p not in new)
            key.append((c.path, "manifest", changed, gone))
        elif c.path.endswith("/log.md"):
            added, removed = line_delta(git.read_text(repo, mb, c.path), git.read_text(repo, commit, c.path))
            key.append((c.path, "log", added, removed))
        else:
            key.append((c.path, c.status, git.blob_sha(repo, commit, c.path)))
    return tuple(sorted(key, key=repr))


def evaluate(ctx, allowed: set[str], fetch=None) -> tuple[bool, str]:
    """Return (approved, explanation). `fetch(sha)` makes an approved commit available locally."""
    allowed_l = {a.lower().lstrip("@") for a in allowed if a}
    latest: dict[str, object] = {}
    for r in ctx.pr.reviews:
        if r.state in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED"):
            latest[r.user.lower()] = r
    head_key = content_key(ctx.repo, ctx.base, ctx.head)
    stale = []
    for user, r in sorted(latest.items()):
        if r.state != "APPROVED" or user not in allowed_l or user == ctx.pr.author.lower():
            continue
        try:
            git.rev(ctx.repo, r.commit_id)
        except git.GitError:
            if fetch is None or not fetch(r.commit_id):
                stale.append(f"@{user} (approved commit {r.commit_id[:12]} unavailable)")
                continue
        if content_key(ctx.repo, ctx.base, r.commit_id) == head_key:
            return True, f"approved by @{user} on content identical to head (commit {r.commit_id[:12]})"
        stale.append(f"@{user} (approved different content at {r.commit_id[:12]})")
    who = ", ".join(f"@{a}" for a in sorted(allowed_l)) or "(nobody eligible)"
    note = f"awaiting approval from {who}"
    others = [u for u, r in latest.items() if r.state == "APPROVED" and u not in allowed_l]
    if others:
        note += f"; approvals from {', '.join('@' + u for u in sorted(others))} do not count"
    if stale:
        note += f"; stale: {', '.join(stale)}"
    return False, note

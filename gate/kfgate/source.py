"""Source-repo checkout at a pinned SHA — DATA ONLY (I6): no install, no build, no hooks.

One shallow fetch serves both G6-bundle citation checks and the G11
extractor re-run. A failed fetch is a gate FAILURE, never a pass.
"""
from __future__ import annotations

import os
import subprocess
import tempfile

_CACHE: dict[tuple[str, str], str] = {}


class FetchError(RuntimeError):
    pass


def checkout(repo: str, sha: str, local_cache: str | None = None) -> str:
    key = (repo, sha)
    if key in _CACHE:
        return _CACHE[key]
    if local_cache:
        cand = os.path.join(local_cache, repo.split("/", 1)[1])
        if os.path.isdir(cand):
            head = subprocess.run(["git", "-C", cand, "rev-parse", "HEAD"], capture_output=True,
                                  text=True).stdout.strip()
            if head == sha:
                _CACHE[key] = cand
                return cand
    d = tempfile.mkdtemp(prefix="kf-src-")
    env = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1", GIT_TERMINAL_PROMPT="0")
    cmds = [["git", "init", "-q", d],
            ["git", "-C", d, "-c", "core.hooksPath=/dev/null", "fetch", "-q", "--depth", "1",
             f"https://github.com/{repo}", sha],
            ["git", "-C", d, "-c", "core.hooksPath=/dev/null", "-c", "advice.detachedHead=false",
             "checkout", "-q", "FETCH_HEAD"]]
    for cmd in cmds:
        res = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if res.returncode != 0:
            raise FetchError(f"could not fetch {repo}@{sha[:12]}: {res.stderr.strip()[:300]} — "
                             "re-run the check; a fetch failure never passes")
    _CACHE[key] = d
    return d

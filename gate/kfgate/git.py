"""Thin, read-only git helpers. Head content is only ever READ as data."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass


class GitError(RuntimeError):
    pass


def git(repo: str, *args: str, check: bool = True, binary: bool = False):
    res = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if check and res.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed: {res.stderr.decode(errors='replace').strip()}")
    return res.stdout if binary else res.stdout.decode("utf-8", errors="surrogateescape")


def rev(repo: str, ref: str) -> str:
    return git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}").strip()


def merge_base(repo: str, a: str, b: str) -> str:
    return git(repo, "merge-base", a, b).strip()


def read(repo: str, ref: str, path: str) -> bytes | None:
    res = subprocess.run(["git", "-C", repo, "cat-file", "blob", f"{ref}:{path}"], capture_output=True)
    return res.stdout if res.returncode == 0 else None


def read_text(repo: str, ref: str, path: str) -> str | None:
    data = read(repo, ref, path)
    return None if data is None else data.decode("utf-8", errors="surrogateescape")


def blob_sha(repo: str, ref: str, path: str) -> str | None:
    res = subprocess.run(["git", "-C", repo, "rev-parse", f"{ref}:{path}"], capture_output=True, text=True)
    return res.stdout.strip() if res.returncode == 0 else None


@dataclass(frozen=True)
class Change:
    path: str
    status: str     # A, M, D, T
    old_mode: str
    new_mode: str


def changes(repo: str, base: str, head: str) -> list[Change]:
    """Normative changed-file set: `git diff --raw --no-renames base...head`.

    Renames appear as delete + add (both judged); mode changes are reported;
    symlinks (120000) and gitlinks (160000) are visible through their modes."""
    out = git(repo, "diff", "--raw", "--no-renames", "--no-abbrev", "-z", base, head)
    parts = [p for p in out.split("\0")]
    result, i = [], 0
    while i < len(parts) - 1:
        meta = parts[i]
        if not meta.startswith(":"):
            i += 1
            continue
        fields = meta[1:].split()
        old_mode, new_mode, status = fields[0], fields[1], fields[4][0]
        path = parts[i + 1]
        result.append(Change(path, status, old_mode, new_mode))
        i += 2
    return sorted(result, key=lambda c: c.path)


def commits(repo: str, base: str, head: str) -> list[str]:
    out = git(repo, "rev-list", "--reverse", f"{base}..{head}")
    return [c for c in out.split() if c]


def message(repo: str, sha: str) -> str:
    return git(repo, "log", "-1", "--format=%B", sha)


def log_paths_authors(repo: str, ref: str, path_prefix: str) -> set[str]:
    """Author e-mail local parts / GitHub logins seen in commits touching a path (best effort)."""
    out = git(repo, "log", "--format=%an%x09%(trailers:key=KF-Approver,valueonly,separator=%x09)",
              ref, "--", path_prefix, check=False)
    seen = set()
    for line in out.splitlines():
        for tok in line.split("\t"):
            tok = tok.strip().lstrip("@")
            if tok:
                seen.add(tok.lower())
    return seen


def is_ancestor(repo: str, a: str, b: str) -> bool:
    return subprocess.run(["git", "-C", repo, "merge-base", "--is-ancestor", a, b]).returncode == 0

"""Everything a gate needs to judge one PR, gathered once."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

import yaml

from . import git
from .identities import Identities


@dataclass
class Review:
    user: str
    state: str          # APPROVED | CHANGES_REQUESTED | COMMENTED | DISMISSED
    commit_id: str


@dataclass
class PR:
    number: int | None
    author: str
    branch: str
    body: str
    labels: list[str] = field(default_factory=list)
    reviews: list[Review] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "PR":
        return cls(number=d.get("number"), author=str(d.get("author", "")).lstrip("@"),
                   branch=d.get("branch", ""), body=d.get("body", "") or "",
                   labels=list(d.get("labels", [])),
                   reviews=[Review(str(r["user"]).lstrip("@"), r["state"], r["commit_id"])
                            for r in d.get("reviews", [])])


@dataclass
class Finding:
    gate: str
    message: str
    path: str = ""
    severity: str = "error"     # error | warn

    def as_dict(self):
        return {"gate": self.gate, "severity": self.severity, "path": self.path, "message": self.message}


class Context:
    def __init__(self, repo: str, base: str, head: str, pr: PR, identities: Identities,
                 now: dt.datetime, bootstrap: bool = False, source_cache: str | None = None):
        self.repo = repo
        self.base = git.rev(repo, base)
        self.head = git.rev(repo, head)
        self.mb = git.merge_base(repo, self.base, self.head)
        self.pr = pr
        self.ids = identities
        self.now = now.astimezone(dt.timezone.utc)
        self.bootstrap = bootstrap
        self.source_cache = source_cache
        self.changes = git.changes(repo, self.mb, self.head)
        cfg_text = git.read_text(repo, self.base, ".github/kf/config.yml")
        self.config = yaml.safe_load(cfg_text) if cfg_text else None
        self.cls = "unknown"
        self.appid: str | None = None
        self.team: str | None = None
        self.ceremony: str | None = None
        self.notes: dict = {}         # scratch shared between gates

    # ---- reading (head is DATA: read, never executed) -------------------------
    def head_text(self, path: str) -> str | None:
        return git.read_text(self.repo, self.head, path)

    def base_text(self, path: str) -> str | None:
        return git.read_text(self.repo, self.base, path)

    def mb_text(self, path: str) -> str | None:
        return git.read_text(self.repo, self.mb, path)

    @property
    def paths(self) -> list[str]:
        return [c.path for c in self.changes]

    def appid_cfg(self, appid: str | None = None) -> dict | None:
        appid = appid or self.appid
        if not self.config or not appid:
            return None
        return (self.config.get("appids") or {}).get(appid)

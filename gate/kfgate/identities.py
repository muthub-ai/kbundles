"""Who exists and who may write — from GitHub in CI, from a fixture locally."""
from __future__ import annotations

import yaml

WRITE_LEVELS = {"admin", "maintain", "write"}


class Identities:
    def exists(self, user: str) -> bool:
        raise NotImplementedError

    def permission(self, user: str) -> str | None:
        raise NotImplementedError

    def can_write(self, user: str) -> bool:
        return (self.permission(user) or "") in WRITE_LEVELS


class FixtureIdentities(Identities):
    """users: {login: {permission: write}} — used by local mode and CI fixtures."""

    def __init__(self, data: dict):
        self.users = {k.lower().lstrip("@"): (v or {}) for k, v in (data.get("users") or {}).items()}

    @classmethod
    def load(cls, path: str) -> "FixtureIdentities":
        with open(path, encoding="utf-8") as fh:
            return cls(yaml.safe_load(fh) or {})

    def exists(self, user: str) -> bool:
        return user.lower().lstrip("@") in self.users

    def permission(self, user: str) -> str | None:
        return self.users.get(user.lower().lstrip("@"), {}).get("permission")


class GitHubIdentities(Identities):
    def __init__(self, api, repo: str):
        self.api, self.repo, self._cache = api, repo, {}

    def exists(self, user: str) -> bool:
        status, _ = self.api.get(f"/users/{user.lstrip('@')}")
        return status == 200

    def permission(self, user: str) -> str | None:
        u = user.lstrip("@")
        if u not in self._cache:
            status, body = self.api.get(f"/repos/{self.repo}/collaborators/{u}/permission")
            self._cache[u] = body.get("permission") if status == 200 and isinstance(body, dict) else None
        return self._cache[u]

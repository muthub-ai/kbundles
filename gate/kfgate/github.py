"""GitHub REST client + publishing the verdict (check run, sticky comment, labels, reviews).

Only deterministic code writes to GitHub. The demo-grade identity is the
workflow's GITHUB_TOKEN (the GitHub Actions app); PRODUCTION.md documents the
KF Gate App identity that closes the same-name check-forgery path.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from . import CHECK_NAME

API = "https://api.github.com"
MARKER = "<!-- kf-knowledge-gate:sticky -->"


class API_:
    def __init__(self, token: str):
        self.token = token

    def _req(self, method: str, path: str, body=None):
        url = path if path.startswith("http") else API + path
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method, headers={
            "Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "kf-knowledge-gate"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
                return resp.status, json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            try:
                return exc.code, json.loads(raw) if raw else {}
            except ValueError:
                return exc.code, {"message": raw.decode(errors="replace")}

    def get(self, path):
        return self._req("GET", path)

    def post(self, path, body):
        return self._req("POST", path, body)

    def patch(self, path, body):
        return self._req("PATCH", path, body)

    def put(self, path, body):
        return self._req("PUT", path, body)

    def delete(self, path):
        return self._req("DELETE", path)

    def paged(self, path):
        out, page = [], 1
        while True:
            sep = "&" if "?" in path else "?"
            status, body = self.get(f"{path}{sep}per_page=100&page={page}")
            if status != 200 or not isinstance(body, list):
                break
            out.extend(body)
            if len(body) < 100:
                break
            page += 1
        return out


def pr_payload(api: API_, repo: str, number: int) -> dict:
    status, pr = api.get(f"/repos/{repo}/pulls/{number}")
    if status != 200:
        raise RuntimeError(f"cannot read PR #{number}: {pr}")
    reviews = [{"user": r["user"]["login"], "state": r["state"], "commit_id": r["commit_id"]}
               for r in api.paged(f"/repos/{repo}/pulls/{number}/reviews") if r.get("user")]
    return {"number": number, "author": pr["user"]["login"], "branch": pr["head"]["ref"], "title": pr.get("title") or "",
            "body": pr.get("body") or "", "labels": [lb["name"] for lb in pr.get("labels", [])],
            "reviews": reviews, "head_sha": pr["head"]["sha"], "base_ref": pr["base"]["ref"]}


def render_summary(v, pr_number) -> tuple[str, str]:
    icon = {"success": "✅", "action_required": "⏳", "failure": "❌"}.get(v.conclusion, "•")
    title = {"success": "All gates passed and the named approver approved this content",
             "action_required": v.approval or "Gates passed — awaiting the named approver",
             "failure": f"{len(v.errors)} gate violation(s): {', '.join(v.failing_gates())}"}.get(v.conclusion, v.conclusion)
    lines = [MARKER, f"## {icon} {CHECK_NAME}: {v.conclusion}", "",
             f"**Class:** `{v.cls}`" + (f" · **appid:** `{v.appid}`" if v.appid else "")
             + (f" · **team:** `{v.team}`" if v.team else "") + (f" · **ceremony:** `{v.ceremony}`" if v.ceremony else ""),
             ""]
    if v.errors:
        lines += ["### Hard gate failures", "", "| Gate | File | Problem |", "|---|---|---|"]
        lines += [f"| `{f.gate}` | `{f.path or '—'}` | {f.message.replace('|', '/')} |" for f in v.errors]
        lines.append("")
    if v.warnings:
        lines += ["### Warnings (advisory)", ""] + [f"- `{f.gate}` {f.path}: {f.message}" for f in v.warnings] + [""]
    if v.approval:
        lines += [f"**Approval:** {v.approval}", ""]
    lines += ["<sub>Demo-grade check identity (GitHub Actions app). The gate only comments, labels and requests "
              "changes; it never approves, merges or closes. See PRODUCTION.md.</sub>"]
    return title, "\n".join(lines)


def publish(api: API_, repo: str, pr: dict, v, run_url: str | None) -> list[str]:
    """Write the verdict to GitHub. Returns non-fatal problems (logged, never flip the verdict)."""
    problems = []
    number, head = pr["number"], pr["head_sha"]
    title, summary = render_summary(v, number)
    body = {"name": CHECK_NAME, "head_sha": head, "status": "completed",
            "conclusion": v.conclusion, "output": {"title": title[:250], "summary": summary[:65000]}}
    if run_url:
        body["details_url"] = run_url
    status, resp = api.post(f"/repos/{repo}/check-runs", body)
    if status not in (200, 201):
        problems.append(f"check run not created: {status} {resp.get('message')}")
    comments = api.paged(f"/repos/{repo}/issues/{number}/comments")
    mine = [c for c in comments if MARKER in (c.get("body") or "")]
    if mine:
        api.patch(f"/repos/{repo}/issues/comments/{mine[0]['id']}", {"body": summary})
    else:
        api.post(f"/repos/{repo}/issues/{number}/comments", {"body": summary})
    want = {"kf-knowledge", {"failure": "kf-gate/failed"}.get(v.conclusion, "kf-gate/passed")}
    if v.warnings:
        want.add("kf-gate/warn")
    if v.ceremony:
        want.add(f"ceremony/{v.ceremony}")
    if v.cls == "revert":
        want.add("kf-revert")
    stale = {"kf-gate/failed", "kf-gate/passed", "kf-gate/warn"} - want
    for lb in pr.get("labels", []):
        if lb in stale:
            api.delete(f"/repos/{repo}/issues/{number}/labels/{lb}")
    api.post(f"/repos/{repo}/issues/{number}/labels", {"labels": sorted(want)})
    reviews = api.paged(f"/repos/{repo}/pulls/{number}/reviews")
    bot_changes = [r for r in reviews if r.get("state") == "CHANGES_REQUESTED"
                   and (r.get("user") or {}).get("login") == "github-actions[bot]"]
    if v.conclusion == "failure":
        if not bot_changes or bot_changes[-1].get("commit_id") != head:
            s, r = api.post(f"/repos/{repo}/pulls/{number}/reviews",
                            {"commit_id": head, "event": "REQUEST_CHANGES",
                             "body": f"{CHECK_NAME}: {title}. Details in the sticky comment and check run."})
            if s not in (200, 201):
                problems.append(f"request-changes review not posted: {s} {r.get('message')}")
    else:
        for r in bot_changes:
            api.put(f"/repos/{repo}/pulls/{number}/reviews/{r['id']}/dismissals",
                    {"message": "kf-knowledge-gate: hard gates now pass", "event": "DISMISS"})
        approver = (v.approval_user or "") if hasattr(v, "approval_user") else ""
        if v.conclusion == "action_required" and approver:
            api.post(f"/repos/{repo}/pulls/{number}/requested_reviewers", {"reviewers": [approver]})
    return problems

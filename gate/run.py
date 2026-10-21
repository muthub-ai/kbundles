#!/usr/bin/env python3
"""kf-knowledge-gate entrypoint.

Local mode (fixtures, bootstrap verdicts, reviewers reproducing CI offline):
  python3 gate/run.py --repo . --base main --head my-branch --pr-json pr.json \
      [--identities ids.yml] [--now 2026-10-20T12:00:00Z] [--bootstrap] [--source-cache DIR] [--json]

GitHub mode (CI; executes BASE-ref code, reads PR head as data):
  python3 gate/run.py --github --pr 42 --head-ref refs/kf/pr-head
Exit code: 0 success/action_required/bootstrap-ok, 1 failure, 2 usage/infra error.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kfgate import CHECK_NAME  # noqa: E402
from kfgate.context import PR, Context  # noqa: E402
from kfgate.engine import evaluate  # noqa: E402
from kfgate.identities import FixtureIdentities  # noqa: E402


def _print(v, as_json: bool):
    if as_json:
        print(json.dumps(v.as_dict(), indent=2))
        return
    print(f"{CHECK_NAME}: class={v.cls} conclusion={v.conclusion}"
          + (f" appid={v.appid}" if v.appid else "") + (f" team={v.team}" if v.team else ""))
    for f in v.findings:
        print(f"  {f.severity.upper():5} {f.gate:6} {f.path or '-'}: {f.message}")
    if v.approval:
        print(f"  approval: {v.approval}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo", default=".")
    p.add_argument("--base", default="origin/main")
    p.add_argument("--head")
    p.add_argument("--pr-json")
    p.add_argument("--identities")
    p.add_argument("--now")
    p.add_argument("--bootstrap", action="store_true")
    p.add_argument("--source-cache")
    p.add_argument("--json", action="store_true")
    p.add_argument("--github", action="store_true")
    p.add_argument("--pr", type=int)
    p.add_argument("--head-ref", default="refs/kf/pr-head")
    a = p.parse_args(argv)
    now = dt.datetime.fromisoformat(a.now.replace("Z", "+00:00")) if a.now else dt.datetime.now(dt.timezone.utc)

    if a.github:
        from kfgate.github import API_, pr_payload, publish
        from kfgate.identities import GitHubIdentities
        repo_full = os.environ["GITHUB_REPOSITORY"]
        api = API_(os.environ["GITHUB_TOKEN"])
        payload = pr_payload(api, repo_full, a.pr)
        subprocess.run(["git", "-C", a.repo, "fetch", "-q", "origin",
                        f"+refs/pull/{a.pr}/head:{a.head_ref}"], check=True)

        def fetch(sha):
            return subprocess.run(["git", "-C", a.repo, "fetch", "-q", "origin", sha]).returncode == 0

        ctx = Context(a.repo, f"origin/{payload['base_ref']}", a.head_ref, PR.from_dict(payload),
                      GitHubIdentities(api, repo_full), now)
        if ctx.head != payload["head_sha"]:
            print(f"head moved ({ctx.head[:12]} vs {payload['head_sha'][:12]}); a newer run will judge it")
            return 0
        v = evaluate(ctx, fetch)
        v.approval_user = _approver(ctx, v)
        run_url = (f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo_full}/actions/runs/"
                   f"{os.environ.get('GITHUB_RUN_ID', '')}") if os.environ.get("GITHUB_RUN_ID") else None
        problems = publish(api, repo_full, payload, v, run_url)
        for prob in problems:
            print(f"warning: {prob}")
        _print(v, a.json)
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            from kfgate.github import render_summary
            with open(summary, "a", encoding="utf-8") as fh:
                fh.write(render_summary(v, a.pr)[1] + "\n")
        # The verdict lives in the check run; the job fails only if that check could not be written.
        return 2 if any(p.startswith("check run not created") for p in problems) else 0

    if not a.head:
        p.error("--head is required in local mode")
    pr = PR.from_dict(json.load(open(a.pr_json, encoding="utf-8")) if a.pr_json else {})
    ids = FixtureIdentities.load(a.identities) if a.identities else FixtureIdentities({})
    ctx = Context(a.repo, a.base, a.head, pr, ids, now, bootstrap=a.bootstrap, source_cache=a.source_cache)
    v = evaluate(ctx)
    _print(v, a.json)
    return 1 if v.conclusion == "failure" else 0


def _approver(ctx, v) -> str:
    if v.conclusion != "action_required":
        return ""
    if v.cls == "ceremony":
        return str((((ctx.notes.get("cer_fm") or {}).get("x_kf") or {}).get("review") or {}).get("approver", "")).lstrip("@")
    if v.cls == "bundle-update":
        return str(((ctx.notes.get("ks") or {}).get("review") or {}).get("approver", "")).lstrip("@")
    return ""


if __name__ == "__main__":
    sys.exit(main())

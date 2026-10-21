#!/usr/bin/env python3
"""Open the `live: true` scenarios of scenarios/matrix.yml as real pull requests.

For each live scenario: replay its steps in a fresh scratch clone (exactly as
run_fixtures.py does, so the local verdict is known before anything is
pushed), then push the scenario's PR head to GitHub with the safe-push rules
of spec §7.2 — author check on any open PR for the branch, then an
explicit-SHA lease (never a bare --force) — and open or update the PR. The
gate on GitHub (pull_request_target, base-ref code) then posts the
`kf-knowledge-gate` check run. Finally the README live-PRs table is rewritten.

  python3 scenarios/open_live_prs.py [--only R01,R06] [--dry-run] [--write-readme README.md]

Every live PR is red by design; with one real identity each also carries a
G7 finding (the fixture approver does not exist on GitHub).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scenarios"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import run_fixtures as rf  # noqa: E402
import simulate_grill as sim  # noqa: E402

# Most red scenarios extend the same D01 meeting, so they would share one deterministic
# branch (D13: a rerun updates the same PR). Live, each needs its own PR, so each gets
# its own ceremony date; the run date (log heading) is unchanged.
LIVE_DATES = {"R01": "2026-10-06", "R03": "2026-10-07", "R06": "2026-10-08", "R08": "2026-10-09",
              "R09": "2026-10-12", "R13": "2026-10-13"}

MARK_START, MARK_END = "<!-- live-prs:start -->", "<!-- live-prs:end -->"
FOOTER = ("🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\n"
          "https://claude.ai/code/session_01XNcjE9WcYtrvi6uB5CZfqb")


def gh(*args) -> str:
    res = subprocess.run(["gh", "api", *args], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"gh api {args[0]}: {res.stderr.strip() or res.stdout.strip()}")
    return res.stdout


def dated(date: str | None):
    """Wrap sim.load_scenario so the replayed scenario uses its own ceremony date."""
    base = sim.load_scenario

    def load(path):
        sc = base(path)
        if date:
            sc["answers"]["ceremony_date"] = date
            sc["meeting"]["meeting_datetime"] = date + sc["meeting"]["meeting_datetime"][10:]
            sc["meeting"]["meeting_id"] = sc["meeting"]["meeting_id"][:-10] + date
        return sc
    return load


def replay(run: rf.Run, sc: dict) -> tuple[str, dict, dict]:
    """Run the scenario's steps up to and including its first gate step; keep the clone."""
    sim_load = sim.load_scenario
    sim.load_scenario = dated(LIVE_DATES.get(sc["id"]))
    try:
        return _replay(run, sc)
    finally:
        sim.load_scenario = sim_load


def _replay(run: rf.Run, sc: dict) -> tuple[str, dict, dict]:
    repo = run.clone()
    state = {"prs": {}, "merged": {}, "observed": []}
    for step in sc["steps"]:
        (kind, args), = step.items()
        getattr(run, f"s_{kind}")(repo, state, args or {})
        if kind == "gate":
            return repo, state["prs"][(args or {}).get("of", "pr")], args
    raise rf.Fail(f"{sc['id']}: no gate step")


def demo_note(sc: dict, gate_args: dict) -> str:
    gates = ", ".join(gate_args.get("gates", [])) or gate_args.get("class", "")
    return (f"**Demo PR — scenario {sc['id']}: {sc['title']}** ({sc.get('criterion', '')}).\n\n"
            f"Opened by `scenarios/open_live_prs.py` to show kf-knowledge-gate rejecting a bad change. "
            f"Expected check: **failure** on **{gates}**. Because this demo repository has a single real "
            f"GitHub identity, the check also reports **G7** (the fixture approver does not exist on GitHub). "
            f"Do not merge; close when done.")


def push_and_open(repo: str, full: str, me: str, pr: dict, sc: dict, gate_args: dict) -> dict:
    branch = pr["branch"]
    owner = full.split("/")[0]
    prs = json.loads(gh(f"repos/{full}/pulls?head={owner}:{branch}&state=open"))
    sim.author_check(prs, me, branch)
    url = f"https://github.com/{full}"
    remote = subprocess.run(["git", "-C", repo, "ls-remote", url, f"refs/heads/{branch}"],
                            capture_output=True, text=True, check=True).stdout.split("\t")[0].strip()
    # explicit-SHA lease: an empty expected value means "the branch must not exist yet"
    subprocess.run(["git", "-C", repo, "push", "-q", f"--force-with-lease=refs/heads/{branch}:{remote}",
                    url, f"{pr['head']}:refs/heads/{branch}"], check=True)
    body = (pr["meta"].get("body") or "") + f"\n\n---\n{demo_note(sc, gate_args)}\n\n{FOOTER}\n"
    title = f"[demo {sc['id']}] {pr.get('title') or sc['title']}"
    if prs:
        num = prs[0]["number"]
        gh(f"repos/{full}/pulls/{num}", "-X", "PATCH", "-f", f"title={title}", "-f", f"body={body}")
        action = "updated"
    else:
        num = json.loads(gh(f"repos/{full}/pulls", "-f", f"title={title}", "-f", f"head={branch}",
                            "-f", "base=main", "-f", f"body={body}"))["number"]
        action = "opened"
    print(f"{sc['id']}: {action} PR #{num} ({branch} @ {pr['head'][:12]})")
    return {"id": sc["id"], "title": sc["title"], "number": num, "url": f"{url}/pull/{num}",
            "expect": gate_args.get("gates", []) or [gate_args.get("class", "")]}


def write_readme(path: str, rows: list[dict]) -> None:
    lines = ["| Scenario | What it does | Pull request | Expected failing gates |", "|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['id']} | {r['title']} | [#{r['number']}]({r['url']}) | "
                     f"{', '.join(r['expect'])} (+ G7 in demo mode) |")
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    a, b = text.index(MARK_START) + len(MARK_START), text.index(MARK_END)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text[:a] + "\n" + "\n".join(lines) + "\n" + text[b:])


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--only")
    p.add_argument("--source-cache", default=os.environ.get("KF_SOURCE_CACHE"))
    p.add_argument("--repo", default="muthub-ai/kbundles")
    p.add_argument("--dry-run", action="store_true", help="replay and gate locally; push nothing")
    p.add_argument("--write-readme")
    a = p.parse_args(argv)
    with open(os.path.join(ROOT, "scenarios", "matrix.yml"), encoding="utf-8") as fh:
        matrix = yaml.safe_load(fh)
    only = set(a.only.split(",")) if a.only else None
    live = [s for s in matrix["scenarios"] if s.get("live") and (not only or s["id"] in only)]
    run = rf.Run(matrix, a.source_cache)
    me = "" if a.dry_run else gh("user", "--jq", ".login").strip()
    rows, failed = [], 0
    for sc in live:
        repo = None
        try:
            repo, pr, gate_args = replay(run, sc)  # raises if the local verdict is not the expected one
            if a.dry_run:
                print(f"{sc['id']}: local verdict as expected ({', '.join(gate_args.get('gates', []))}); not pushed")
                continue
            rows.append(push_and_open(repo, a.repo, me, pr, sc, gate_args))
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"{sc['id']}: ERROR {exc}")
        finally:
            if repo:
                shutil.rmtree(repo, ignore_errors=True)
    if a.write_readme and rows:
        write_readme(a.write_readme, sorted(rows, key=lambda r: r["id"]))
    print(f"{len(rows)} PR(s) opened/updated, {failed} error(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Direct bootstrap (plan §7B) with a local gate verdict for every step.

Commits each application bundle and each team's seed standup as its own
commit on the current branch, runs `gate/run.py --bootstrap` (content gates
only; approval explicitly not applicable) against the previous commit, and
records every verdict under docs/bootstrap-verdicts/. Content landed this
way is flagged x_kf.bootstrap and can never be a revert target.

  tools/bootstrap.py --source-cache /path/to/source/clones [--only-seeds]
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "gate"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from kfgate.context import PR, Context  # noqa: E402
from kfgate.engine import evaluate  # noqa: E402
from kfgate.identities import FixtureIdentities  # noqa: E402

import simulate_grill as sim  # noqa: E402

TRAILERS = ("Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n"
            "Claude-Session: https://claude.ai/code/session_01XNcjE9WcYtrvi6uB5CZfqb")
NOW = dt.datetime(2026, 10, 20, 23, 59, tzinfo=dt.timezone.utc)


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], check=True, capture_output=True, text=True).stdout.strip()


def verdict(step: str, pr: dict, source_cache: str, base: str = "HEAD~1", head: str = "HEAD") -> dict:
    ctx = Context(ROOT, base, head, PR.from_dict(pr), FixtureIdentities({}), NOW, bootstrap=True,
                  source_cache=source_cache)
    v = evaluate(ctx)
    rec = v.as_dict() | {"step": step, "base": ctx.base, "head": ctx.head, "mode": "bootstrap (local gate)"}
    os.makedirs(os.path.join(ROOT, "docs", "bootstrap-verdicts"), exist_ok=True)
    with open(os.path.join(ROOT, "docs", "bootstrap-verdicts", f"{step}.json"), "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=2)
        fh.write("\n")
    print(f"{step:45} class={v.cls:13} conclusion={v.conclusion}"
          + (f"  FAILING {v.failing_gates()}" if v.errors else ""))
    for f in v.errors:
        print(f"    {f.gate} {f.path}: {f.message}")
    return rec


def reverify(source_cache: str) -> int:
    """Re-judge every bootstrap commit (found by its trailer) and rewrite its verdict file."""
    failed = 0
    for sha in git("rev-list", "--reverse", "HEAD").split():
        msg = git("log", "-1", "--format=%B", sha)
        if len(git("log", "-1", "--format=%P", sha).split()) != 1:
            continue  # root or merge commit: not a bootstrap step
        changed = git("diff", "--name-only", f"{sha}^", sha).split("\n")
        if "KF-Bundle-Builder:" in msg:
            appid = changed[0].split("/")[1]
            ks = json.loads(git("show", f"{sha}:application-bundles/{appid}/knowledge-source.json"))
            rec = verdict(f"bundle-{appid}", {"author": "muthub-ai",
                          "branch": f"bundle/{appid}/{ks['source']['commit_sha'][:12]}"}, source_cache, f"{sha}^", sha)
        elif "KF-Grill-Client:" in msg:
            seed = next(p for p in changed if p.endswith(".md") and not p.endswith("/log.md"))
            parts = seed.split("/")
            appid, cer, team, fname = parts[1], parts[4], parts[5], parts[6]
            name = f"{appid}-{team}-{cer}-{fname.split('_')[1][:-3]}"
            sc = sim.load_scenario(os.path.join(ROOT, "scenarios", "seeds", f"{name}.json"))
            r = sim.render(sc, sim.load_config(ROOT), bootstrap=True)
            rec = verdict(f"seed-{name}", {"author": "muthub-ai", "branch": r["branch"], "body": r["pr_body"]},
                          source_cache, f"{sha}^", sha)
        else:
            continue
        failed += rec["conclusion"] == "failure"
    print(f"{failed} failing step(s)")
    return 1 if failed else 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source-cache", required=True)
    p.add_argument("--only-seeds", action="store_true")
    p.add_argument("--reverify", action="store_true",
                   help="re-judge the existing bootstrap commits with the current gate code")
    a = p.parse_args()
    failed = 0
    if a.reverify:
        return reverify(a.source_cache)
    if not a.only_seeds:
        for bdir in sorted(glob.glob(os.path.join(ROOT, "application-bundles", "*"))):
            appid = os.path.basename(bdir)
            with open(os.path.join(bdir, "knowledge-source.json"), encoding="utf-8") as fh:
                ks = json.load(fh)
            sha = ks["source"]["commit_sha"]
            git("add", f"application-bundles/{appid}")
            git("commit", "-q", "-m",
                f"kf({appid}): bootstrap application bundle from {ks['source']['repo']}@{sha[:12]}\n\n"
                f"Sections, domain maps, code graph and control files (x_kf.bootstrap: true).\n\n"
                f"KF-Bundle-Builder: building-application-bundles@0.1.0\n{TRAILERS}")
            rec = verdict(f"bundle-{appid}", {"author": "muthub-ai", "branch": f"bundle/{appid}/{sha[:12]}"},
                          a.source_cache)
            failed += rec["conclusion"] == "failure"
    for seed in sorted(glob.glob(os.path.join(ROOT, "scenarios", "seeds", "*.json"))):
        sc = sim.load_scenario(seed)
        r = sim.render(sc, sim.load_config(ROOT), bootstrap=True)
        sim.write_tree(ROOT, r)
        git("add", "-A", f"application-bundles/{r['appid']}")
        git("commit", "-q", "-m", sim.commit_message(r) + TRAILERS)
        rec = verdict(f"seed-{r['appid']}-{r['team']}-{r['ceremony']}-{r['date']}",
                      {"author": "muthub-ai", "branch": r["branch"], "body": r["pr_body"]}, a.source_cache)
        failed += rec["conclusion"] == "failure"
    print(f"{failed} failing step(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

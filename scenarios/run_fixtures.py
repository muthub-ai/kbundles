#!/usr/bin/env python3
"""Run the scenario matrix (scenarios/matrix.yml) against a scratch clone of this repo.

Every scenario gets a fresh clone of the current commit, replays its steps
(simulate → gate → review → merge → refresh → revert → bundle edits) and
asserts the gate's verdict. This is how the green, approval, merge, refresh
and revert paths are proven in a repository that has only one real identity.

  scenarios/run_fixtures.py [--only F01,R06] [--source-cache DIR] [--report FILE] [--write-readme README.md]
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import traceback

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS = os.path.join(ROOT, "skills", "building-application-bundles", "scripts")
for p in (os.path.join(ROOT, "gate"), os.path.join(ROOT, "tools"), SCRIPTS):
    sys.path.insert(0, p)

import yaml  # noqa: E402

import simulate_grill as sim  # noqa: E402
from build_bundle import stamp_sources  # noqa: E402
from kfbundle import controls, graph  # noqa: E402
from kfbundle.common import canonical_json  # noqa: E402
from kfbundle.manifest import splice_remove  # noqa: E402
from kfgate.ceremony_doc import log_blocks  # noqa: E402
from kfgate.context import PR, Context  # noqa: E402
from kfgate.engine import evaluate  # noqa: E402
from kfgate.identities import FixtureIdentities  # noqa: E402

MARK_START, MARK_END = "<!-- scenario-matrix:start -->", "<!-- scenario-matrix:end -->"


class Fail(AssertionError):
    pass


def sh(repo, *args, check=True):
    res = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if check and res.returncode != 0:
        raise Fail(f"git {' '.join(args)}: {res.stderr.strip() or res.stdout.strip()}")
    return res


class Run:
    def __init__(self, matrix: dict, source_cache: str | None):
        self.m = matrix
        self.ids = FixtureIdentities.load(os.path.join(ROOT, matrix["identities"]))
        self.source_cache = source_cache
        self.default_now = dt.datetime.fromisoformat(matrix["default_now"].replace("Z", "+00:00"))

    # ------------------------------------------------------------------ scratch repo
    def clone(self) -> str:
        d = tempfile.mkdtemp(prefix="kf-fixture-")
        subprocess.run(["git", "clone", "-q", ROOT, d], check=True)
        sh(d, "config", "user.name", "kf-fixture")
        sh(d, "config", "user.email", "kf-fixture@users.noreply.github.com")
        sh(d, "switch", "-q", "-C", "main")
        return d

    def commit(self, repo, msg):
        sh(repo, "add", "-A")
        sh(repo, "commit", "-q", "--allow-empty", "-m", msg)
        return sh(repo, "rev-parse", "HEAD").stdout.strip()

    # ------------------------------------------------------------------ steps
    def run_scenario(self, sc: dict) -> dict:
        repo = self.clone()
        state = {"prs": {}, "merged": {}, "observed": []}
        try:
            for i, step in enumerate(sc["steps"], 1):
                (kind, args), = step.items()
                getattr(self, f"s_{kind}")(repo, state, args or {})
            return {"ok": True, "observed": state["observed"]}
        except Fail as exc:
            return {"ok": False, "observed": state["observed"], "error": f"step {i} ({kind}): {exc}"}
        except Exception as exc:  # noqa: BLE001 — a crashing fixture is a failing fixture
            return {"ok": False, "observed": state["observed"],
                    "error": f"step {i} ({kind}) crashed: {exc!r}\n{traceback.format_exc(limit=3)}"}
        finally:
            shutil.rmtree(repo, ignore_errors=True)

    def s_simulate(self, repo, st, a):
        sc = sim.load_scenario(os.path.join(ROOT, a["scenario"]))
        sh(repo, "switch", "-q", "main")
        r = sim.simulate(sc, repo, "main", "commit")
        if r.get("zero_findings"):
            raise Fail("scenario produced zero findings")
        st["prs"][a.get("as", "pr")] = {"branch": r["pr"]["branch"], "head": r["head"], "meta": r["pr"],
                                        "scenario": a["scenario"], "title": r["pr_title"]}

    def s_refresh(self, repo, st, a):
        pr = st["prs"][a.get("of", "pr")]
        sc = sim.load_scenario(os.path.join(ROOT, a.get("scenario", pr["scenario"])))
        sh(repo, "switch", "-q", "main")
        r = sim.simulate(sc, repo, "main", "commit", refresh=True)
        if r["pr"]["branch"] != pr["branch"]:
            raise Fail(f"rerun produced a different branch {r['pr']['branch']} (expected {pr['branch']})")
        pr.update(head=r["head"], meta={**r["pr"], "reviews": pr["meta"].get("reviews", [])})
        grill = [b for b in sh(repo, "branch", "--list", "grill/*").stdout.split() if b != "*"]
        if len([b for b in grill if b.startswith(pr["branch"])]) != 1:
            raise Fail(f"expected exactly one branch {pr['branch']}, found {grill}")

    def s_zero(self, repo, st, a):
        sc = sim.load_scenario(os.path.join(ROOT, a["scenario"]))
        r = sim.simulate(sc, repo, "main", "commit")
        if not r.get("zero_findings"):
            raise Fail("expected zero findings (no file, no PR)")
        st["observed"].append("zero findings → no file, no PR")

    def s_review(self, repo, st, a):
        pr = st["prs"][a.get("of", "pr")]
        pr["meta"].setdefault("reviews", []).append(
            {"user": a["user"], "state": a.get("state", "APPROVED"), "commit_id": pr["head"]})

    def s_gate(self, repo, st, a):
        pr = st["prs"][a.get("of", "pr")]
        now = dt.datetime.fromisoformat(a["now"].replace("Z", "+00:00")) if a.get("now") else self.default_now
        meta = copy.deepcopy(pr["meta"])
        ctx = Context(repo, "main", pr["head"], PR.from_dict(meta), self.ids, now, source_cache=self.source_cache)
        v = evaluate(ctx)
        gates, warns = v.failing_gates(), sorted({f.gate for f in v.warnings})
        st["observed"].append(f"{v.cls}:{v.conclusion}" + (f" [{','.join(gates)}]" if gates else "")
                              + (f" warn[{','.join(warns)}]" if a.get("warns") else ""))
        pr["last_verdict"] = v
        if v.conclusion != a["expect"]:
            detail = "; ".join(f"{f.gate}: {f.message[:120]}" for f in v.errors[:4]) or v.approval
            raise Fail(f"expected {a['expect']}, got {v.conclusion} ({detail})")
        if a.get("class") and v.cls != a["class"]:
            raise Fail(f"expected class {a['class']}, got {v.cls}")
        missing = [g for g in a.get("gates", []) if g not in gates]
        if missing:
            raise Fail(f"expected failing gate(s) {missing}; failing: {gates}")
        missing = [g for g in a.get("warns", []) if g not in warns]
        if missing:
            raise Fail(f"expected warning(s) {missing}; warnings: {warns}")

    def s_merge(self, repo, st, a):
        pr = st["prs"][a.get("of", "pr")]
        sh(repo, "switch", "-q", "main")
        res = sh(repo, "merge", "--squash", pr["head"], check=False)
        if res.returncode != 0:
            sh(repo, "reset", "-q", "--hard", "HEAD")
            if a.get("expect_conflict"):
                st["observed"].append("merge conflict (expected)")
                return
            raise Fail(f"unexpected merge conflict: {res.stdout.strip()[-200:]}")
        if a.get("expect_conflict"):
            raise Fail("expected a merge conflict but the squash applied cleanly")
        body = sh(repo, "log", "-1", "--format=%B", pr["head"]).stdout
        trailers = "\n".join(ln for ln in body.splitlines() if ln.startswith("KF-"))
        sha = self.commit(repo, f"{pr['title']} (squash)\n\n{trailers}")
        st["merged"][a.get("of", "pr")] = sha
        st["observed"].append("squash-merged")

    def s_revert(self, repo, st, a):
        if "of" in a:
            target = st["merged"][a["of"]]
        else:
            path = a["seed_path"]
            target = sh(repo, "log", "--diff-filter=A", "--format=%H", "main", "--", path).stdout.split()[0]
        changes = sh(repo, "diff", "--name-status", "--no-renames", f"{target}^", target).stdout.split("\n")
        cer = [ln.split("\t")[1] for ln in changes if ln.startswith("A\t") and not ln.endswith("/log.md")
               and "/knowledge-sources/" in ln]
        fpath = cer[0]
        appid, fname = fpath.split("/")[1], fpath.rsplit("/", 1)[1]
        sh(repo, "switch", "-q", "-C", f"revert/{target[:12]}", "main")
        if a.get("literal"):
            # What GitHub's Revert button does to a first-run commit: the file AND the log it
            # created are deleted, and the manifest entry is dropped. (A real `git revert` of an
            # early commit usually conflicts once later entries exist — the spec's point.)
            os.remove(os.path.join(repo, fpath))
            os.remove(os.path.join(repo, os.path.dirname(fpath), "log.md"))
            mpath = os.path.join(repo, "application-bundles", appid, "bundle-manifest.json")
            with open(mpath, encoding="utf-8") as fh:
                m = fh.read()
            with open(mpath, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(splice_remove(m, fpath.split("/", 2)[2]))
        else:
            os.remove(os.path.join(repo, fpath))
            mpath = os.path.join(repo, "application-bundles", appid, "bundle-manifest.json")
            with open(mpath, encoding="utf-8") as fh:
                m = fh.read()
            with open(mpath, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(splice_remove(m, fpath.split("/", 2)[2]))
            lpath = os.path.join(repo, os.path.dirname(fpath), "log.md")
            with open(lpath, encoding="utf-8") as fh:
                log = fh.read()
            block = next(b for _, b in log_blocks(log) if f"[{fname}]({fname})" in b)
            date = a.get("date", "2026-10-21")
            new = controls.insert_log_block(log.replace(block, "", 1),
                                            f"## {date}: Reverted {fname} — {a.get('reason', 'fixture revert')}\n\n"
                                            f"- Removed by revert of {target[:12]}.\n\n", date)
            with open(lpath, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(new)
        head = self.commit(repo, f"revert: {fname}\n\nKF-Revert-Of: {target}")
        st["prs"][a.get("as", "revert")] = {"branch": f"revert/{target[:12]}", "head": head, "title": f"revert {fname}",
                                            "meta": {"author": a.get("author", "kf-writer-demo"),
                                                     "branch": f"revert/{target[:12]}",
                                                     "labels": a.get("labels", ["kf-revert"]),
                                                     "body": f"Reverts: {target}"}}

    def _edit(self, repo, ops):
        for op in ops:
            path = os.path.join(repo, op["file"]) if "file" in op else None
            if op["op"] == "replace":
                with open(path, encoding="utf-8") as fh:
                    text = fh.read()
                if op["find"] not in text:
                    raise Fail(f"edit: {op['find']!r} not in {op['file']}")
                with open(path, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(text.replace(op["find"], op["replace"], 1))
            elif op["op"] == "write":
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(op["content"])
            elif op["op"] == "graph_bump_bytes":
                with open(path, encoding="utf-8") as fh:
                    recs = graph.load_jsonl(fh.read())
                node = next(r for r in recs if r.get("rec") == "node" and "bytes" in r)
                node["bytes"] += 1
                with open(path, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write("".join(canonical_json(r) + "\n" for r in recs))
            elif op["op"] == "set_approver":
                with open(path, encoding="utf-8") as fh:
                    ks = json.load(fh)
                ks["review"]["approver"] = op["value"]
                with open(path, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(json.dumps(ks, sort_keys=True, indent=2) + "\n")
            else:
                raise Fail(f"unknown edit op {op['op']}")

    def s_bundle_edit(self, repo, st, a):
        appid = a["appid"]
        bdir = os.path.join(repo, "application-bundles", appid)
        ks = controls.load_json(os.path.join(bdir, "knowledge-source.json"))
        branch = a.get("branch", f"bundle/{appid}/{ks['source']['commit_sha'][:12]}")
        sh(repo, "switch", "-q", "-C", branch, "main")
        self._edit(repo, [dict(op, file=os.path.join("application-bundles", appid, op["file"]))
                          if op["file"][:1] != "/" and not op["file"].startswith("application-bundles/") else op
                          for op in a["ops"]])
        if a.get("stamp", True):
            stamp_sources(bdir, ks)
        controls.write_manifest(bdir, appid, ks["generated_at"])
        controls.write_index(bdir, appid, ks)
        with open(os.path.join(bdir, "log.md"), encoding="utf-8") as fh:
            log = fh.read()
        date = a.get("log_date", "2026-10-20")
        with open(os.path.join(bdir, "log.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(controls.insert_log_block(log, controls.log_block(date, a.get("summary", "Bundle update"),
                                                                      [a.get("bullet", "Fixture bundle update.")]), date))
        head = self.commit(repo, f"kf({appid}): bundle update\n\nKF-Bundle-Builder: building-application-bundles@0.1.0")
        st["prs"][a.get("as", "pr")] = {"branch": branch, "head": head, "title": f"bundle update {appid}",
                                        "meta": {"author": a.get("author", "kf-writer-demo"), "branch": branch,
                                                 "body": ""}}

    def s_edit(self, repo, st, a):
        sh(repo, "switch", "-q", "-C", a["branch"], "main")
        self._edit(repo, a["ops"])
        head = self.commit(repo, a.get("message", "chore: edit"))
        st["prs"][a.get("as", "pr")] = {"branch": a["branch"], "head": head, "title": a["branch"],
                                        "meta": {"author": a.get("author", "kf-writer-demo"), "branch": a["branch"],
                                                 "body": ""}}

    def s_unit(self, repo, st, a):
        if a["check"] == "author_check":
            try:
                sim.author_check([{"number": 7, "user": {"login": "someone-else"}}], "kf-writer-demo", "grill/x")
            except sim.SimError as exc:
                st["observed"].append(f"aborted: {str(exc)[:60]}…")
                return
            raise Fail("author check did not abort on another author's open PR")
        raise Fail(f"unknown unit check {a['check']}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--only")
    p.add_argument("--source-cache", default=os.environ.get("KF_SOURCE_CACHE"))
    p.add_argument("--report")
    p.add_argument("--write-readme")
    a = p.parse_args(argv)
    with open(os.path.join(ROOT, "scenarios", "matrix.yml"), encoding="utf-8") as fh:
        matrix = yaml.safe_load(fh)
    run = Run(matrix, a.source_cache)
    only = set(a.only.split(",")) if a.only else None
    rows, failures, t0 = [], 0, time.time()
    for sc in matrix["scenarios"]:
        if (only and sc["id"] not in only) or (sc.get("live_only") and not only):
            continue
        res = run.run_scenario(sc)
        failures += not res["ok"]
        rows.append((sc, res))
        print(f"{'PASS' if res['ok'] else 'FAIL'} {sc['id']:4} {sc['title']}")
        for o in res["observed"]:
            print(f"       → {o}")
        if not res["ok"]:
            print(f"       ✗ {res['error']}")
    table = ["| Id | Scenario | Proves (spec / plan) | Live PR | Observed | Result |", "|---|---|---|---|---|---|"]
    for sc, res in rows:
        obs = " → ".join(res["observed"]).replace("|", "/")
        table.append(f"| {sc['id']} | {sc['title']} | {sc.get('criterion', '')} | {'yes' if sc.get('live') else ''} | "
                     f"{obs} | {'✅' if res['ok'] else '❌'} |")
    summary = (f"**{len(rows) - failures}/{len(rows)} scenarios pass** "
               f"({time.time() - t0:.0f}s, gate local mode, fresh scratch clone per scenario).")
    text = "\n".join(["## Scenario matrix", "", summary, ""] + table) + "\n"
    if a.report:
        with open(a.report, "a", encoding="utf-8") as fh:
            fh.write(text)
    if a.write_readme:
        with open(a.write_readme, encoding="utf-8") as fh:
            readme = fh.read()
        start, end = readme.index(MARK_START) + len(MARK_START), readme.index(MARK_END)
        with open(a.write_readme, "w", encoding="utf-8") as fh:
            fh.write(readme[:start] + "\n" + summary + "\n\n" + "\n".join(table) + "\n" + readme[end:])
    print(summary)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

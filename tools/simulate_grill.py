#!/usr/bin/env python3
"""simulate_grill.py — stands in for the grill-me agent's P5/P6 phases. No LLM anywhere.

Takes a GrillResult-shaped scenario (canned meeting output with verbatim
evidence spans drawn from a fabricated recap) and deterministically produces
exactly what grill-me would: the ceremony file, a byte-splice of the
manifest, a date-ordered block in the ceremony-team log, the deterministic
branch, a commit with the client trailer, and the PR body with the evidence
table. Red scenarios add `tamper` operations after rendering.

  simulate_grill.py --scenario S.json --repo . --mode commit   # local branch + commit (fixtures)
  simulate_grill.py --scenario S.json --repo . --mode push     # §7.2 safe-push + open/update PR (live)
  simulate_grill.py --scenario S.json --repo . --mode seed     # write onto the current branch (bootstrap)
  ... --refresh   re-seat manifest/log on fresh main from the same GrillResult (approval survives)

Identity: process:kf-grill-sim@0.1.0 — never claims to be kf-grill-me (OKF forbids invented provenance).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "gate"))
sys.path.insert(0, os.path.join(ROOT, "skills", "building-application-bundles", "scripts"))

import yaml  # noqa: E402

from kfgate.ceremony_doc import (CEREMONY_SCHEMA, CEREMONY_TITLES, PREFIX_SECTION, body_sha,  # noqa: E402
                                 branch_name, knowledge_id, log_path, log_title, span_sha)
from kfbundle.common import dump_frontmatter, get_path, sha256_text  # noqa: E402
from kfbundle.controls import insert_log_block  # noqa: E402
from kfbundle.manifest import render_entry, splice_insert  # noqa: E402

SIM_VERSION = "0.1.0"
SIM_ID = f"process:kf-grill-sim@{SIM_VERSION}"
TRAILER = f"KF-Grill-Client: kf-grill-sim@{SIM_VERSION}"
SECTION_ORDER = ["Sprint goal", "Decisions", "Blockers", "Stories", "PRD candidates", "Action items",
                 "Risks", "Went well", "To improve"]


class SimError(RuntimeError):
    pass


def git(repo, *args, check=True):
    res = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if check and res.returncode != 0:
        raise SimError(f"git {' '.join(args)}: {res.stderr.strip()}")
    return res.stdout.strip()


def load_config(repo: str, ref: str | None = None) -> dict:
    if ref:
        text = git(repo, "show", f"{ref}:.github/kf/config.yml")
    else:
        with open(os.path.join(repo, ".github/kf/config.yml"), encoding="utf-8") as fh:
            text = fh.read()
    return yaml.safe_load(text)


def normalize(text: str) -> str:
    return text.replace("\r\n", "\n").strip() + "\n"


def render(sc: dict, cfg: dict, bootstrap: bool = False) -> dict:
    a = sc["answers"]
    appid, cer, team, date = a["appid"], a["ceremony"], a["team"], a["ceremony_date"]
    tz = (cfg["appids"].get(appid) or {}).get("teams", {}).get(team, {}).get("timezone", "UTC")
    with open(os.path.join(ROOT, sc["recap"]), encoding="utf-8") as fh:
        recap = normalize(fh.read())
    items = sc.get("items", [])
    extras = sc.get("extra", {})
    if not items and not any(extras.values()):
        return {"zero_findings": True}
    fname = f"{cer}_{date}.md"
    cer_path = f"application-bundles/{appid}/knowledge-sources/agile-ceremonies/{cer}/{team}/{fname}"
    spans, foot_lines = {}, []

    def cite(cits):
        refs = ""
        for c in cits:
            if c["span"] not in recap:
                raise SimError(f"evidence span for [^{c['fid']}] is not in the recap fixture {sc['recap']}")
            spans[c["fid"]] = (c.get("source", "s1"), c["span"])
            refs += f"[^{c['fid']}]"
        return refs

    title = f"{CEREMONY_TITLES[cer]} — {appid}/{team} — {date}"
    body = [f"\n# {title}\n"]
    by_section: dict[str, list[str]] = {}
    for it in items:
        sec = PREFIX_SECTION[it["id"].split("-")[0]]
        by_section.setdefault(sec, []).append(
            f"- **{it['id']}** *({it.get('confidence', 'medium')})* — {it['text']} {cite(it['citations'])}")
    for sec, rows in extras.items():
        for row in rows:
            by_section.setdefault(sec, []).append(f"- {row['text']} {cite(row['citations'])}")
    for sec in SECTION_ORDER:
        if by_section.get(sec):
            body.append(f"\n## {sec}\n\n" + "\n".join(by_section[sec]) + "\n")
    att = sc.get("attendance", [])
    if att:
        body.append("\n## Attendance\n\n| Name | Duration |\n|---|---|\n"
                    + "".join(f"| {p['name']} | {p['duration']} |\n" for p in att))
    for fid, (src, span) in sorted(spans.items()):
        loc = next(c["locator"] for it in items + [r for rows in extras.values() for r in rows]
                   for c in it["citations"] if c["fid"] == fid)
        foot_lines.append(f'[^{fid}]: {src} · "{loc}" segment · span_sha256:{span_sha(span)}')
    body.append("\n" + "\n".join(foot_lines) + "\n")
    body_text = "".join(body)
    att_text = "".join(f"{p['name']}\t{p['duration']}\n" for p in att)
    run_id = "sim-" + hashlib.sha256(json.dumps(sc, sort_keys=True).encode()).hexdigest()[:12]
    meeting = sc.get("meeting", {})
    sources = [{"id": "s1", "kind": "meeting-summary", "title": meeting.get("title", f"{title} recap"),
                "origin": "fixture/m365-copilot-recap", "sha256": sha256_text(recap)}]
    if meeting.get("meeting_id"):
        sources[0]["meeting_id"] = meeting["meeting_id"]
    if att:
        sources.append({"id": "s2", "kind": "attendance-report", "title": "Attendance export (fixture)",
                        "origin": "fixture/teams-attendance", "sha256": sha256_text(att_text)})
    xkf = {"schema": CEREMONY_SCHEMA, "appid": appid, "ceremony": cer, "team": team, "ceremony_date": date,
           "knowledge_id": knowledge_id(appid, cer, team, date, cfg.get("repo", "")),
           "content_sha256": body_sha(body_text),
           "review": {"submitted_as": "candidate", "approver": a["approver"],
                      "requested_by": a.get("requested_by", "@muthub-ai")},
           "run": {"client": "kf-grill-sim(local)", "run_id": run_id,
                   "user_edited_items": sc.get("user_edited_items", [])},
           "synthetic": True}
    if meeting.get("meeting_datetime"):
        xkf["meeting_datetime"] = meeting["meeting_datetime"]
    if bootstrap:
        xkf["bootstrap"] = True
    fm = {"type": f"agile-ceremony/{cer}", "title": title,
          "description": f"Illustrative candidate knowledge from the {team} team's {date} "
                         f"{CEREMONY_TITLES[cer].lower()} (synthetic fixture meeting).",
          "tags": ["agile-ceremony", cer, "candidate-knowledge", "synthetic"],
          "generated": {"by": SIM_ID, "at": sc["generated_at"]},
          "sources": sources, "x_kf": xkf}
    cer_text = dump_frontmatter(fm) + body_text
    gen = dt.datetime.fromisoformat(sc["generated_at"])
    run_date = gen.astimezone(ZoneInfo(tz)).date().isoformat()
    counts = {}
    for it in items:
        counts[it["id"].split("-")[0]] = counts.get(it["id"].split("-")[0], 0) + 1
    names = {"DEC": "decision", "BLK": "blocker", "STY": "story", "PRD": "PRD candidate", "ACT": "action",
             "RSK": "risk"}
    summary = ", ".join(f"{n} {names[k]}{'' if n == 1 else 's'}" for k, n in sorted(counts.items()))
    branch = branch_name(appid, cer, team, date)
    block = (f"## {run_date}: {CEREMONY_TITLES[cer]} {date} candidate knowledge\n\n"
             f"- Added [{fname}]({fname}) ({len(items)} items: {summary or 'retro notes only'}).\n"
             f"- Approver: {a['approver']} · Branch: {branch} · Run: {run_id}\n\n")
    entry = {"added": sc["generated_at"], "generated_by": SIM_ID,
             "path": cer_path.split("/", 2)[2], "review": {"approver": a["approver"], "submitted_as": "candidate"},
             "team": team, "type": f"agile-ceremony/{cer}"}
    ev_rows = "".join(f'| {fid} | {src} | "{span}" |\n' for fid, (src, span) in sorted(spans.items()))
    pr_body = (f"## [KF] {appid} · {team} · {cer} · {date} — candidate knowledge ({len(items)} items)\n\n"
               f"**Approver (enforced):** {a['approver']} · **Write-set:** ceremony file + ceremony-team log.md + "
               f"bundle-manifest.json of `{appid}`\n\n"
               f"Synthetic scenario `{sc.get('id', '?')}` rendered by {SIM_ID} (no model). Run: {run_id}\n\n"
               "<details><summary>Evidence spans (verbatim, hash-anchored; scrub-able after merge)</summary>\n\n"
               "| Footnote | Source | Span |\n|---|---|---|\n" + ev_rows + "\n</details>\n\n"
               "> Merge = acceptance. kf-knowledge-gate goes green only when the hard gates pass AND the named "
               "approver has approved this exact content.\n")
    return {"zero_findings": False, "appid": appid, "ceremony": cer, "team": team, "date": date,
            "cer_path": cer_path, "cer_text": cer_text, "entry": entry, "log_path": log_path(appid, cer, team),
            "log_block": block, "log_title": log_title(cer, team), "run_date": run_date, "branch": branch,
            "pr_title": f"[KF] {appid} · {team} · {cer} · {date} — candidate knowledge ({len(items)} items)",
            "pr_body": pr_body, "run_id": run_id}


def load_scenario(path: str) -> dict:
    """Load a scenario; `extends` names a base scenario that `override` deep-merges into."""
    with open(path, encoding="utf-8") as fh:
        sc = json.load(fh)
    if "extends" in sc:
        base = load_scenario(os.path.join(ROOT, sc["extends"]))

        def merge(a, b):
            for k, v in b.items():
                a[k] = merge(a.get(k, {}), v) if isinstance(v, dict) and isinstance(a.get(k), dict) else v
            return a
        sc = merge(base, {k: v for k, v in sc.items() if k != "extends"})
    return sc


def write_tree(repo: str, r: dict) -> None:
    """Apply a rendering to the working tree: add file, byte-splice manifest, insert log block."""
    cpath = os.path.join(repo, r["cer_path"])
    os.makedirs(os.path.dirname(cpath), exist_ok=True)
    with open(cpath, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(r["cer_text"])
    mpath = os.path.join(repo, f"application-bundles/{r['appid']}/bundle-manifest.json")
    if not os.path.exists(mpath):   # a brand-new (possibly unregistered) appid folder
        from kfbundle.manifest import render_manifest
        os.makedirs(os.path.dirname(mpath), exist_ok=True)
        with open(mpath, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(render_manifest(r["appid"], []))
    with open(mpath, encoding="utf-8") as fh:
        manifest = fh.read()
    with open(mpath, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(splice_insert(manifest, r["entry"]))
    lpath = os.path.join(repo, r["log_path"])
    if os.path.exists(lpath):
        with open(lpath, encoding="utf-8") as fh:
            new = insert_log_block(fh.read(), r["log_block"], r["run_date"])
    else:
        new = r["log_title"] + r["log_block"]
    with open(lpath, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new)


def tamper(repo: str, r: dict, ops: list[dict], pr: dict) -> None:
    """Red-scenario mutations applied AFTER a correct rendering (each targets one gate)."""
    for op in ops or []:
        kind = op["op"]
        target = {"ceremony": r["cer_path"], "log": r["log_path"],
                  "manifest": f"application-bundles/{r['appid']}/bundle-manifest.json"}.get(op.get("file"), op.get("file"))
        if kind == "replace_in_file":
            p = os.path.join(repo, target)
            with open(p, encoding="utf-8") as fh:
                text = fh.read()
            if op["find"] not in text:
                raise SimError(f"tamper: {op['find']!r} not found in {target}")
            with open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text.replace(op["find"], op["replace"], 1))
        elif kind == "add_file":
            p = os.path.join(repo, op["path"])
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(op.get("content", "tampered\n"))
        elif kind == "delete_file":
            git(repo, "rm", "-q", op["path"])
        elif kind == "symlink":
            p = os.path.join(repo, op["path"])
            os.makedirs(os.path.dirname(p), exist_ok=True)
            os.symlink(op["target"], p)
        elif kind == "rename":
            git(repo, "mv", op["from"], op["to"])
        elif kind == "reserialize_manifest":
            p = os.path.join(repo, target or f"application-bundles/{r['appid']}/bundle-manifest.json")
            with open(p, encoding="utf-8") as fh:
                data = json.load(fh)
            with open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(json.dumps(data, indent=2) + "\n")
        elif kind == "break_span":
            pr["body"] = pr["body"].replace(f"| {op['fid']} | ", f"| {op['fid']} | ", 1).replace(
                op["find"], op["replace"], 1)
        elif kind == "pr":
            pr[op["key"]] = op["value"]
        elif kind == "fake_history":
            p = os.path.join(repo, r["log_path"])
            with open(p, "a", encoding="utf-8", newline="\n") as fh:
                fh.write("## 2026-09-01: Standup 2026-09-01 candidate knowledge\n\n- Added (fabricated history)\n\n")
        else:
            raise SimError(f"unknown tamper op {kind!r}")


def commit(repo: str, message: str, author: str = "kf-grill-sim <kf-grill-sim@users.noreply.github.com>") -> str:
    git(repo, "add", "-A")
    name, mail = author.split(" <")
    git(repo, "-c", f"user.name={name}", "-c", f"user.email={mail.rstrip('>')}", "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def commit_message(r: dict, trailer: bool = True) -> str:
    msg = (f"kf({r['appid']}/{r['team']}): {r['ceremony']} candidate knowledge {r['date']}\n\n"
           f"ceremony={r['ceremony']} team={r['team']} date={r['date']} run={r['run_id']}\n")
    return msg + (f"\n{TRAILER}\n" if trailer else "")


def simulate(sc: dict, repo: str, base: str, mode: str, refresh: bool = False) -> dict:
    cfg = load_config(repo, base if mode != "seed" else None)
    r = render(sc, cfg, bootstrap=(mode == "seed"))
    if r["zero_findings"]:
        print("zero findings: nothing extractable — no file, no PR (I7). "
              "If an open PR exists for this ceremony-date, comment on it recommending close.")
        return {"zero_findings": True}
    pr = {"author": sc.get("pr", {}).get("author", "muthub-ai"), "branch": r["branch"], "body": r["pr_body"],
          "labels": sc.get("pr", {}).get("labels", []), "reviews": []}
    if mode in ("commit", "push"):
        git(repo, "switch", "-q", "-C", r["branch"], base)
    write_tree(repo, r)
    tamper(repo, r, sc.get("tamper"), pr)
    sha = commit(repo, commit_message(r, trailer=not sc.get("drop_trailer")))
    r.update(pr=pr, head=sha)
    if mode == "push":
        push_and_open(repo, r, sc)
    return r


def author_check(prs: list[dict], me: str, branch: str) -> None:
    """Spec §7.2 step 1 / E6: never clobber someone else's open PR on the deterministic branch.
    (A bare --force-with-lease would NOT protect it: the preceding fetch makes the lease match.)"""
    if prs and prs[0]["user"]["login"].lower() != me.lower():
        raise SimError(f"open PR #{prs[0]['number']} on {branch} belongs to @{prs[0]['user']['login']} — "
                       "aborting (author check, E6); coordinate instead of clobbering")


def push_and_open(repo: str, r: dict, sc: dict) -> None:
    """Spec §7.2: author check → explicit-SHA lease → open or update the PR (live only)."""
    full = git(repo, "remote", "get-url", "origin").rstrip("/").removesuffix(".git").split("github.com/")[-1]
    me = subprocess.run(["gh", "api", "user", "--jq", ".login"], capture_output=True, text=True).stdout.strip()
    res = subprocess.run(["gh", "api", f"repos/{full}/pulls?head={full.split('/')[0]}:{r['branch']}&state=open"],
                         capture_output=True, text=True)
    prs = json.loads(res.stdout or "[]") if res.returncode == 0 else []
    author_check(prs, me, r["branch"])
    remote = git(repo, "ls-remote", "origin", f"refs/heads/{r['branch']}").split("\t")[0]
    git(repo, "push", "-q", f"--force-with-lease=refs/heads/{r['branch']}:{remote}", "--force-if-includes",
        "origin", f"HEAD:refs/heads/{r['branch']}")
    if prs:
        print(f"updated PR #{prs[0]['number']}")
        r["pr_number"] = prs[0]["number"]
        return
    body = r["pr"]["body"] + f"\n\n---\n{sc.get('demo_note', '')}\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)\n"
    res = subprocess.run(["gh", "api", f"repos/{full}/pulls", "-f", f"title={sc.get('pr_title', r['pr_title'])}",
                          "-f", f"head={r['branch']}", "-f", "base=main", "-f", f"body={body}"],
                         capture_output=True, text=True)
    if res.returncode != 0:
        raise SimError(f"PR create failed: {res.stderr or res.stdout}")
    r["pr_number"] = json.loads(res.stdout)["number"]
    print(f"opened PR #{r['pr_number']}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--scenario", required=True)
    p.add_argument("--repo", default=ROOT)
    p.add_argument("--base", default="main")
    p.add_argument("--mode", choices=["commit", "push", "seed"], default="commit")
    p.add_argument("--refresh", action="store_true")
    p.add_argument("--pr-out")
    a = p.parse_args(argv)
    sc = load_scenario(a.scenario)
    try:
        r = simulate(sc, a.repo, a.base, a.mode, a.refresh)
    except SimError as exc:
        print(f"ERROR: {exc}")
        return 1
    if a.pr_out and not r.get("zero_findings"):
        with open(a.pr_out, "w", encoding="utf-8") as fh:
            json.dump(r["pr"], fh, indent=2)
    if not r.get("zero_findings"):
        print(f"{r['branch']} @ {r['head'][:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

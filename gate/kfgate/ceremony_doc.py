"""Ceremony knowledge file model (spec v0.4 §5) shared by the gate and the simulator."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field

CEREMONY_SCHEMA = "kf-agile-ceremony/2"
CEREMONIES = ["standup", "sprint-planning", "backlog-refinement", "retro"]
CEREMONY_TITLES = {"standup": "Standup", "sprint-planning": "Sprint planning",
                   "backlog-refinement": "Backlog refinement", "retro": "Retro"}
SECTION_PREFIX = {"Decisions": "DEC", "Blockers": "BLK", "Stories": "STY", "PRD candidates": "PRD",
                  "Action items": "ACT", "Risks": "RSK"}
PREFIX_SECTION = {v: k for k, v in SECTION_PREFIX.items()}
EXTRA_SECTIONS = {"sprint-planning": ["Sprint goal"], "retro": ["Went well", "To improve"]}
ALLOWED = {
    "standup": {"DEC", "BLK", "STY", "PRD", "ACT"},
    "sprint-planning": {"DEC", "STY", "PRD", "ACT", "RSK"},
    "backlog-refinement": {"DEC", "STY", "PRD", "RSK"},
    "retro": {"DEC", "ACT", "RSK"},
}
EXPECTED = {"standup": {"BLK", "ACT"}, "sprint-planning": {"DEC", "STY"},
            "backlog-refinement": {"STY"}, "retro": {"ACT"}}

PATH_RE = re.compile(
    r"^application-bundles/(?P<appid>[^/]+)/knowledge-sources/agile-ceremonies/(?P<ceremony>[^/]+)/"
    r"(?P<team>[^/]+)/(?P<file>[^/]+)$")
FILE_RE = re.compile(r"^(?P<ceremony>[a-z-]+)_(?P<date>\d{4}-\d{2}-\d{2})\.md$")
TEAM_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ITEM_RE = re.compile(r"^- \*\*(?P<id>[A-Z]{3}-\d+)\*\* \*\((?P<conf>[^)]*)\)\* — (?P<text>.+)$")
FOOT_RE = re.compile(r"^\[\^(?P<id>[A-Za-z0-9_-]+)\]: (?P<src>s\d+) · \"(?P<loc>[^\"]+)\" segment · "
                     r"span_sha256:(?P<h>[0-9a-f]{64})$")
ANYFOOT_RE = re.compile(r"^\[\^([A-Za-z0-9_-]+)\]:")
REF_RE = re.compile(r"\[\^([A-Za-z0-9_-]+)\](?!:)")
EVIDENCE_RE = re.compile(r"^\|\s*(?P<id>[A-Za-z0-9_-]+)\s*\|\s*(?P<src>s\d+)\s*\|\s*\"(?P<span>.*)\"\s*\|\s*$")


def knowledge_id(appid: str, ceremony: str, team: str, date: str, repo: str) -> str:
    return "sha256:" + hashlib.sha256(f"{appid}|{ceremony}|{team}|{date}|{repo}".encode()).hexdigest()


def span_sha(span: str) -> str:
    return hashlib.sha256(span.encode("utf-8")).hexdigest()


def body_sha(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def rel_to_bundle(path: str) -> str:
    """application-bundles/<appid>/X → X"""
    return path.split("/", 2)[2]


def log_path(appid: str, ceremony: str, team: str) -> str:
    return f"application-bundles/{appid}/knowledge-sources/agile-ceremonies/{ceremony}/{team}/log.md"


def branch_name(appid: str, ceremony: str, team: str, date: str) -> str:
    return f"grill/{appid}/{ceremony}/{team}/{date}"


def log_title(ceremony: str, team: str) -> str:
    return f"# {ceremony} · {team} — log\n\n"


@dataclass
class Item:
    section: str
    iid: str | None
    line: int
    text: str
    refs: list[str]


@dataclass
class CeremonyBody:
    sections: list[str] = field(default_factory=list)
    items: list[Item] = field(default_factory=list)
    footnotes: dict[str, dict] = field(default_factory=dict)
    bad_footnotes: list[tuple[int, str]] = field(default_factory=list)


def parse_body(body: str, line_offset: int = 0) -> CeremonyBody:
    out = CeremonyBody()
    current = None
    for i, line in enumerate(body.split("\n"), 1 + line_offset):
        if line.startswith("## "):
            current = line[3:].strip()
            out.sections.append(current)
            continue
        fm = FOOT_RE.match(line)
        if fm:
            out.footnotes[fm.group("id")] = {"src": fm.group("src"), "loc": fm.group("loc"),
                                             "sha": fm.group("h"), "line": i}
            continue
        if ANYFOOT_RE.match(line):
            out.bad_footnotes.append((i, line))
            continue
        if current and current != "Attendance" and line.startswith("- "):
            im = ITEM_RE.match(line)
            out.items.append(Item(current, im.group("id") if im else None, i, line, REF_RE.findall(line)))
    return out


def parse_evidence(pr_body: str) -> dict[str, tuple[str, str]]:
    """PR-body evidence table → {footnote id: (source id, verbatim span)}."""
    spans = {}
    for line in (pr_body or "").split("\n"):
        m = EVIDENCE_RE.match(line.strip())
        if m:
            spans[m.group("id")] = (m.group("src"), m.group("span"))
    return spans


def log_blocks(text: str) -> list[tuple[str, str]]:
    """[(heading line, full block text incl. trailing blank)] in file order."""
    blocks, cur, head = [], [], None
    for line in text.splitlines(keepends=True):
        if line.startswith("## "):
            if head is not None:
                blocks.append((head, "".join(cur)))
            head, cur = line.rstrip("\n"), [line]
        elif head is not None:
            cur.append(line)
    if head is not None:
        blocks.append((head, "".join(cur)))
    return blocks

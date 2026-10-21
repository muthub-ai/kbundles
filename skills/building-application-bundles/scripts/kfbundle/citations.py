"""Claim blocks and citations for application-bundle sections (gate G6-bundle).

Rule (plan §6.3, confirmed text):
  A claim block is a paragraph, list item or table row (headings, fenced
  code, Mermaid and frontmatter excluded). Every claim block is FACTUAL or an
  ASSESSMENT.
  (1) Factual: ≥1 footnote `src · <path>#L<a>-L<b> · sha256:<hex>` verified at
      the pinned SHA, or `graph · <node-id>` resolving in the code graph.
  (2) Assessment: starts exactly with `*Assessment:*`, introduces no new
      src/graph footnote, cites ≥1 footnote already used by an EARLIER
      factual block in the same section.
  (3) ≥1 factual block per section; assessments ≤ 50% of claim blocks.
  (4) Entailment of assessments is advisory (LLM pass); all else is hard.
Span hash = sha256 of the cited lines, each LF-terminated (common.span_hash).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable

from .common import span_hash

FOOTDEF_RE = re.compile(r"^\[\^([A-Za-z0-9_-]+)\]:\s*(.*)$")
SRC_RE = re.compile(r"^src · (?P<path>[^#\s]+)#L(?P<a>\d+)(?:-L(?P<b>\d+))?(?: · sha256:(?P<h>[0-9a-f]{64}))?\s*$")
GRAPH_RE = re.compile(r"^graph · (?P<node>\S.*?)\s*$")
REF_RE = re.compile(r"\[\^([A-Za-z0-9_-]+)\](?!:)")
LIST_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$")
HEADING_RE = re.compile(r"^#{1,6}(\s|$)")
HR_RE = re.compile(r"^(?:-{3,}|\*{3,}|_{3,})$")
TABLE_SEP_RE = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
ASSESSMENT = "*Assessment:*"


@dataclass
class Footnote:
    fid: str
    line: int
    kind: str              # src | graph | other
    raw: str
    path: str = ""
    start: int = 0
    end: int = 0
    sha: str | None = None
    node: str = ""


@dataclass
class Block:
    line: int
    kind: str              # paragraph | list-item | table-row | quote
    text: str
    refs: list[str] = field(default_factory=list)

    @property
    def assessment(self) -> bool:
        return self.text.lstrip().startswith(ASSESSMENT)


def parse_footnotes(body: str, line_offset: int = 0) -> dict[str, Footnote]:
    notes = {}
    for i, line in enumerate(body.split("\n"), 1 + line_offset):
        m = FOOTDEF_RE.match(line)
        if not m:
            continue
        fid, rest = m.group(1), m.group(2).strip()
        sm, gm = SRC_RE.match(rest), GRAPH_RE.match(rest)
        if sm:
            a = int(sm.group("a"))
            notes[fid] = Footnote(fid, i, "src", rest, path=sm.group("path"), start=a,
                                  end=int(sm.group("b") or a), sha=sm.group("h"))
        elif gm:
            notes[fid] = Footnote(fid, i, "graph", rest, node=gm.group("node"))
        else:
            notes[fid] = Footnote(fid, i, "other", rest)
    return notes


def claim_blocks(body: str, line_offset: int = 0) -> list[Block]:
    blocks: list[Block] = []
    cur: list[str] = []
    cur_start, cur_kind = 0, "paragraph"
    in_fence = in_comment = in_table = in_footdef = False

    def flush():
        nonlocal cur
        if cur:
            text = " ".join(cur)
            blocks.append(Block(cur_start, cur_kind, text, REF_RE.findall(text)))
        cur = []

    lines = body.split("\n")
    for idx, line in enumerate(lines):
        i = idx + 1 + line_offset
        s = line.strip()
        if in_comment:
            if "-->" in s:
                in_comment = False
            continue
        if s.startswith("```") or s.startswith("~~~"):
            flush()
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if s.startswith("<!--"):
            flush()
            in_comment = "-->" not in s
            continue
        if not s:
            flush()
            in_table = in_footdef = False
            continue
        if FOOTDEF_RE.match(s):
            flush()
            in_footdef = True
            continue
        if in_footdef and line.startswith(("  ", "\t")):
            continue
        in_footdef = False
        if HEADING_RE.match(s) or HR_RE.match(s):
            flush()
            continue
        nxt = lines[idx + 1].strip() if idx + 1 < len(lines) else ""
        if s.startswith("|") and (in_table or TABLE_SEP_RE.match(nxt)):
            flush()
            if not in_table:
                in_table = True          # header row (followed by a delimiter row): not a claim
                continue
            if TABLE_SEP_RE.match(s):
                continue
            row = s.strip("|").strip()
            blocks.append(Block(i, "table-row", row, REF_RE.findall(row)))
            continue
        in_table = False
        lm = LIST_RE.match(line)
        if lm:
            flush()
            cur, cur_start, cur_kind = [lm.group(1).strip()], i, "list-item"
            continue
        if s.startswith(">"):
            s = s.lstrip(">").strip()
        if not cur:
            cur_start, cur_kind = i, "quote" if line.strip().startswith(">") else "paragraph"
        cur.append(s)
    flush()
    return blocks


def check_claims(body: str, notes: dict[str, Footnote], line_offset: int = 0) -> list[tuple[int, str]]:
    """Apply rules (1)–(3) structurally. Returns [(line, message)]."""
    problems = []
    used_factual: set[str] = set()
    n_fact = n_assess = 0
    for b in claim_blocks(body, line_offset):
        undefined = [r for r in b.refs if r not in notes]
        if undefined:
            problems.append((b.line, f"footnote(s) {', '.join(sorted(set(undefined)))} are cited but never defined"))
        if b.assessment:
            n_assess += 1
            if not b.refs:
                problems.append((b.line, "Assessment block cites no footnote — it must inherit evidence "
                                         "from an earlier factual block in this section"))
            new = sorted({r for r in b.refs if r not in used_factual})
            if new:
                problems.append((b.line, f"Assessment block introduces footnote(s) {', '.join(new)} not used "
                                         "by an earlier factual block (assessments inherit evidence, never add it)"))
        else:
            good = [r for r in b.refs if r in notes and notes[r].kind in ("src", "graph")]
            if not good:
                preview = b.text[:70] + ("…" if len(b.text) > 70 else "")
                problems.append((b.line, f"uncited claim block ({b.kind}): \"{preview}\" — add a "
                                         "`src`/`graph` footnote or start it with *Assessment:*"))
            else:
                n_fact += 1
                used_factual.update(good)
    if n_fact == 0:
        problems.append((1 + line_offset, "section has no factual claim block"))
    total = n_fact + n_assess
    if total and n_assess * 2 > total:
        problems.append((1 + line_offset, f"assessments are {n_assess}/{total} claim blocks — the cap is 50%"))
    for fid, note in notes.items():
        if note.kind == "other":
            problems.append((note.line, f"footnote [^{fid}] must be `src · path#La-Lb · sha256:…` or "
                                        "`graph · <node-id>`"))
    return problems


Reader = Callable[[str], "bytes | None"]


MAX_SPAN_LINES = 80   # a citation wider than this is rarely the evidence for one claim


def wide_spans(notes: dict[str, Footnote]) -> list[tuple[int, str]]:
    return [(n.line, f"[^{fid}] cites {n.end - n.start + 1} lines ({n.path}#L{n.start}-L{n.end}); cite the "
                     "smallest range that supports the claim") for fid, n in sorted(notes.items())
            if n.kind == "src" and n.end - n.start + 1 > MAX_SPAN_LINES]


def verify_notes(notes: dict[str, Footnote], read_source: Reader, graph_ids: set[str]) -> list[tuple[int, str]]:
    """Verify every src span hash at the pinned commit and every graph node id."""
    problems = []
    for fid, n in sorted(notes.items()):
        if n.kind == "src":
            data = read_source(n.path)
            if data is None:
                problems.append((n.line, f"[^{fid}] cites {n.path}, which does not exist at the pinned commit"))
                continue
            try:
                actual = span_hash(data, n.start, n.end)
            except ValueError as exc:
                problems.append((n.line, f"[^{fid}] {n.path}: {exc}"))
                continue
            if n.sha is None:
                problems.append((n.line, f"[^{fid}] has no sha256 — run fill_citations.py"))
            elif n.sha != actual:
                problems.append((n.line, f"[^{fid}] span hash mismatch for {n.path}#L{n.start}-L{n.end} "
                                         f"(expected {actual[:12]}…, found {n.sha[:12]}…)"))
        elif n.kind == "graph" and n.node not in graph_ids:
            problems.append((n.line, f"[^{fid}] graph node {n.node!r} does not exist in code-graph.jsonl"))
    return problems


def fill(text: str, read_source: Reader) -> tuple[str, list[str]]:
    """Append sha256 to src footnotes that lack one. Returns (new text, errors)."""
    out, errors = [], []
    for line in text.split("\n"):
        m = FOOTDEF_RE.match(line)
        if m:
            sm = SRC_RE.match(m.group(2).strip())
            if sm and not sm.group("h"):
                path, a = sm.group("path"), int(sm.group("a"))
                b = int(sm.group("b") or a)
                data = read_source(path)
                if data is None:
                    errors.append(f"[^{m.group(1)}]: {path} not found at pinned commit")
                else:
                    try:
                        h = span_hash(data, a, b)
                        line = f"[^{m.group(1)}]: src · {path}#L{a}-L{b} · sha256:{h}"
                    except ValueError as exc:
                        errors.append(f"[^{m.group(1)}]: {path}: {exc}")
        out.append(line)
    return "\n".join(out), errors

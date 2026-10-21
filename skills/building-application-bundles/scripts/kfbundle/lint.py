"""Bundle lint — the single rulebook shared by validate_bundle.py and the gate.

Every finding is (code, path, line, message, severity). `error` blocks;
`warn` is advisory. Codes map to plan/spec gates: B2 schema, B3 coherence,
B5 registration, B6 provenance (G6-bundle), B9 PII.
"""
from __future__ import annotations

import json
import os
import posixpath
import re
from dataclasses import dataclass

from . import BUNDLE_SCHEMA, SOURCE_SCHEMA
from .citations import check_claims, parse_footnotes, verify_notes, wide_spans
from .common import get_path, is_iso_with_offset, sha256_bytes, split_frontmatter
from .manifest import CEREMONY_PREFIX, ManifestError, parse_manifest, verify_bundle_ops
from .pii import scan

SECTIONS = [
    "executive-summary", "business-architecture", "application-architecture",
    "data-architecture", "technology-architecture", "security-architecture", "operating-model",
]
REQUIRED_SECTIONS = {"executive-summary", "application-architecture", "technology-architecture",
                     "operating-model"}
APPID_RE = re.compile(r"^[a-z]{5}$")
BUNDLE_FILE_RE = re.compile(
    r"^(sections/[a-z-]+\.md|domains-maps/[a-z0-9-]+\.md|code-graph/(code-graph\.jsonl|metrics\.json"
    r"|views/[a-z-]+\.md)|index\.md|log\.md|bundle-manifest\.json|knowledge-source\.json)$")


@dataclass
class Finding:
    code: str
    path: str
    line: int
    message: str
    severity: str = "error"

    def as_dict(self):
        return {"code": self.code, "path": self.path, "line": self.line,
                "message": self.message, "severity": self.severity}


def _fm_offset(text: str) -> int:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end > 0:
            return text[: end + 5].count("\n")
    return 0


def lint_markdown(rel: str, text: str, ctx: dict) -> list[Finding]:
    """Lint one sections/ or domains-maps/ file. ctx: appid, repo, commit_sha,
    graph_sha256, graph_ids, read_source (callable or None to skip verification)."""
    out: list[Finding] = []
    f = lambda code, line, msg, sev="error": out.append(Finding(code, rel, line, msg, sev))  # noqa: E731
    fm, body, err = split_frontmatter(text)
    if err or fm is None:
        f("B2", 1, err or "missing YAML frontmatter")
        return out
    off = _fm_offset(text)
    is_section = rel.startswith("sections/")
    slug = posixpath.basename(rel)[:-3]
    if is_section and slug not in SECTIONS:
        f("B3", 1, f"unknown section '{slug}'; allowed: {', '.join(SECTIONS)}")
    expected_type = f"application-bundle/{slug}" if is_section else "application-bundle/domain-map"
    if fm.get("type") != expected_type:
        f("B2", 1, f"type must be '{expected_type}' (found {fm.get('type')!r})")
    for key in ("title", "description"):
        if not isinstance(fm.get(key), str) or not fm[key].strip():
            f("B2", 1, f"'{key}' must be a non-empty string")
    gby, gat = get_path(fm, "generated.by"), get_path(fm, "generated.at")
    if not (isinstance(gby, str) and gby.startswith(("process:", "human:"))):
        f("B2", 1, "generated.by must start with lowercase 'process:' or 'human:'")
    if not is_iso_with_offset(gat):
        f("B2", 1, "generated.at must be ISO-8601 with an explicit UTC offset")
    if "verified" in fm:
        f("B2", 1, "verified must be absent — acceptance is defined as presence on main")
    xkf = fm.get("x_kf") if isinstance(fm.get("x_kf"), dict) else {}
    if xkf.get("schema") != BUNDLE_SCHEMA:
        f("B2", 1, f"x_kf.schema must be '{BUNDLE_SCHEMA}'")
    if xkf.get("appid") != ctx["appid"]:
        f("B3", 1, f"x_kf.appid {xkf.get('appid')!r} does not match bundle folder '{ctx['appid']}'")
    if xkf.get("bundle_kind") != "application":
        f("B2", 1, "x_kf.bundle_kind must be 'application'")
    if is_section and xkf.get("section") != slug:
        f("B3", 1, f"x_kf.section must equal the file name '{slug}'")
    if not is_section and xkf.get("domain") != slug:
        f("B3", 1, f"x_kf.domain must equal the file name '{slug}'")
    synthetic = xkf.get("synthetic") is True
    if synthetic and "illustrative" not in str(fm.get("description", "")).lower():
        f("B2", 1, "synthetic content must say 'illustrative' in its description")
    if slug == "operating-model" and not synthetic:
        f("B2", 1, "operating-model is fabricated in this prototype and must set x_kf.synthetic: true")

    sources = fm.get("sources") if isinstance(fm.get("sources"), list) else []
    if not sources:
        f("B2", 1, "sources[] must be a non-empty list")
    ids = [s.get("id") for s in sources if isinstance(s, dict)]
    if len(ids) != len(set(ids)) or None in ids:
        f("B2", 1, "every source needs a unique id")
    repo_src = [s for s in sources if isinstance(s, dict) and s.get("kind") == "source-repo"]
    graph_src = [s for s in sources if isinstance(s, dict) and s.get("kind") == "code-graph"]
    if not synthetic:
        if len(repo_src) != 1 or len(graph_src) != 1:
            f("B6", 1, "sources[] must hold exactly one source-repo and one code-graph source")
        for s in repo_src:
            if s.get("repo") != ctx["repo"] or s.get("commit_sha") != ctx["commit_sha"]:
                f("B6", 1, "source-repo must match knowledge-source.json repo and commit_sha "
                           "(mixed-version bundles are rejected)")
        for s in graph_src:
            if s.get("path") != "code-graph/code-graph.jsonl" or s.get("sha256") != ctx["graph_sha256"]:
                f("B6", 1, "code-graph source must point at code-graph/code-graph.jsonl with its "
                           "current sha256")
        notes = parse_footnotes(body, off)
        for line, msg in check_claims(body, notes, off):
            f("B6", line, msg)
        for line, msg in wide_spans(notes):
            f("B6", line, msg, "warn")
        if ctx.get("read_source") is not None:
            for line, msg in verify_notes(notes, ctx["read_source"], ctx["graph_ids"]):
                f("B6", line, msg)
    for line, kind, hit in scan(text):
        f("B9", line, f"possible {kind} in knowledge text: {hit!r}")
    return out


def _read_json(path: str):
    with open(path, "rb") as fh:
        return json.loads(fh.read().decode("utf-8"))


def lint_bundle(bundle_dir: str, read_source=None, registry: dict | None = None) -> list[Finding]:
    """Lint a whole application bundle directory (bootstrap validation / tripwire)."""
    out: list[Finding] = []
    appid = posixpath.basename(bundle_dir.rstrip("/"))
    if not APPID_RE.match(appid):
        out.append(Finding("B3", appid, 0, "appid must be exactly 5 lowercase letters"))
    ks_path = os.path.join(bundle_dir, "knowledge-source.json")
    try:
        ks = _read_json(ks_path)
    except (OSError, ValueError) as exc:
        return out + [Finding("B2", "knowledge-source.json", 0, f"unreadable: {exc}")]
    if ks.get("schema") != SOURCE_SCHEMA or ks.get("appid") != appid:
        out.append(Finding("B2", "knowledge-source.json", 0, "schema/appid mismatch"))
    if registry is not None:
        reg = registry.get("appids", {}).get(appid)
        if reg is None:
            out.append(Finding("B3", "knowledge-source.json", 0, f"appid '{appid}' is not registered"))
        elif reg.get("repo") != get_path(ks, "source.repo") or reg.get("repo_id") != get_path(ks, "source.repo_id"):
            out.append(Finding("B3", "knowledge-source.json", 0,
                               "source repo / repo_id disagree with the trust-root registry"))
    gpath = os.path.join(bundle_dir, "code-graph", "code-graph.jsonl")
    try:
        with open(gpath, "rb") as fh:
            graph_bytes = fh.read()
    except OSError:
        return out + [Finding("B5", "code-graph/code-graph.jsonl", 0, "code graph missing")]
    graph_ids = set()
    for line in graph_bytes.decode("utf-8").splitlines():
        rec = json.loads(line)
        if rec.get("rec") == "node":
            graph_ids.add(rec["id"])
    ctx = {"appid": appid, "repo": get_path(ks, "source.repo"), "commit_sha": get_path(ks, "source.commit_sha"),
           "graph_sha256": sha256_bytes(graph_bytes), "graph_ids": graph_ids, "read_source": read_source}
    present = set()
    for root, _dirs, files in os.walk(bundle_dir):
        for name in files:
            rel = os.path.relpath(os.path.join(root, name), bundle_dir).replace(os.sep, "/")
            if rel.startswith(CEREMONY_PREFIX) or rel == "OWNERS":   # owned by the ceremony / owners classes
                continue
            present.add(rel)
            if not BUNDLE_FILE_RE.match(rel):
                out.append(Finding("B3", rel, 0, "file is outside the application-bundle layout"))
            if rel.startswith(("sections/", "domains-maps/")) and rel.endswith(".md"):
                with open(os.path.join(root, name), encoding="utf-8") as fh:
                    out.extend(lint_markdown(rel, fh.read(), ctx))
    om = os.path.join(bundle_dir, "sections", "operating-model.md")
    if registry is not None and os.path.exists(om):
        teams = set(((registry.get("appids") or {}).get(appid) or {}).get("teams") or {})
        with open(om, encoding="utf-8") as fh:
            om_text = fh.read()
        for team in sorted(teams):
            if f"`{team}`" not in om_text:
                out.append(Finding("B3", "sections/operating-model.md", 0,
                                   f"registered team `{team}` is missing from the operating model"))
        _, om_body, _ = split_frontmatter(om_text)
        for slug in sorted(set(re.findall(r"^\|\s*`([a-z0-9]+(?:-[a-z0-9]+)*)`\s*\|", om_body, re.M))):
            if slug not in teams and slug not in SECTIONS:
                out.append(Finding("B3", "sections/operating-model.md", 0,
                                   f"team table lists `{slug}`, which is not registered for appid '{appid}' "
                                   "(team→appid binding)", "warn"))
    for sec in sorted(REQUIRED_SECTIONS):
        if f"sections/{sec}.md" not in present:
            out.append(Finding("B5", f"sections/{sec}.md", 0, "required section missing"))
    try:
        with open(os.path.join(bundle_dir, "bundle-manifest.json"), encoding="utf-8") as fh:
            mtext = fh.read()
        _, entries, _ = parse_manifest(mtext)
        for prob in verify_bundle_ops(None, mtext):
            out.append(Finding("B5", "bundle-manifest.json", 0, prob))
        registered = {o["path"]: o for _, o in entries}
        for rel in sorted(present):
            if rel in ("index.md", "log.md", "bundle-manifest.json", "knowledge-source.json"):
                continue
            ent = registered.get(rel)
            if ent is None:
                out.append(Finding("B5", rel, 0, "file is not registered in bundle-manifest.json"))
                continue
            with open(os.path.join(bundle_dir, rel), "rb") as fh:
                if ent.get("sha256") != sha256_bytes(fh.read()):
                    out.append(Finding("B5", rel, 0, "manifest sha256 does not match the file"))
        for path in sorted(registered):
            if not path.startswith(CEREMONY_PREFIX) and path not in present:
                out.append(Finding("B5", path, 0, "manifest registers a file that does not exist"))
    except (OSError, ManifestError) as exc:
        out.append(Finding("B5", "bundle-manifest.json", 0, str(exc)))
    return out

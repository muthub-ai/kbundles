"""OKF control files for an application bundle: knowledge-source.json,
bundle-manifest.json, index.md and the bundle-root log.md."""
from __future__ import annotations

import json
import os
import subprocess

from . import BUILDER_ID, SOURCE_SCHEMA
from .common import pretty_json, sha256_bytes, split_frontmatter
from .lint import SECTIONS
from .manifest import CEREMONY_PREFIX, parse_manifest, render_manifest

SECTION_TITLES = {
    "executive-summary": "Executive summary",
    "business-architecture": "Business architecture",
    "application-architecture": "Application architecture",
    "data-architecture": "Data architecture",
    "technology-architecture": "Technology architecture",
    "security-architecture": "Security architecture",
    "operating-model": "Operating model",
}


def git_reader(src_dir: str, commit_sha: str):
    """Return read(path) -> bytes|None reading blobs at the pinned commit (not the worktree)."""
    def read(path: str):
        if path.startswith("/") or ".." in path.split("/"):
            return None
        res = subprocess.run(["git", "-C", src_dir, "cat-file", "blob", f"{commit_sha}:{path}"],
                             capture_output=True)
        return res.stdout if res.returncode == 0 else None
    return read


def knowledge_source(appid: str, title: str, repo: str, repo_id: int, commit_sha: str,
                     generated_at: str, approver: str, graph_options: dict, bootstrap: bool) -> str:
    return pretty_json({
        "schema": SOURCE_SCHEMA,
        "appid": appid,
        "bundle_kind": "application",
        "title": title,
        "source": {"repo": repo, "repo_id": repo_id, "url": f"https://github.com/{repo}",
                   "commit_sha": commit_sha},
        "builder": BUILDER_ID,
        "generated_at": generated_at,
        "graph_options": graph_options,
        "review": {"approver": approver},
        "bootstrap": bootstrap,
    })


def _frontmatter(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        fm, _, _ = split_frontmatter(fh.read())
    return fm or {}


def bundle_entries(bundle_dir: str, generated_at: str) -> list[dict]:
    entries = []
    for root, _dirs, files in os.walk(bundle_dir):
        for name in sorted(files):
            rel = os.path.relpath(os.path.join(root, name), bundle_dir).replace(os.sep, "/")
            if rel.startswith(CEREMONY_PREFIX) or rel in ("index.md", "log.md", "bundle-manifest.json",
                                                          "knowledge-source.json"):
                continue
            with open(os.path.join(root, name), "rb") as fh:
                data = fh.read()
            if rel.endswith(".md"):
                fm = _frontmatter(os.path.join(root, name))
                etype = fm.get("type", "application-bundle/unknown")
                gby = (fm.get("generated") or {}).get("by", BUILDER_ID)
            elif rel.endswith(".jsonl"):
                etype, gby = "application-bundle/code-graph", BUILDER_ID
            else:
                etype, gby = "application-bundle/code-graph-metrics", BUILDER_ID
            entries.append({"path": rel, "type": etype, "sha256": sha256_bytes(data),
                            "generated_at": generated_at, "generated_by": gby})
    return entries


def write_manifest(bundle_dir: str, appid: str, generated_at: str) -> str:
    """Rebuild bundle entries; keep every ceremony entry line byte-identical."""
    path = os.path.join(bundle_dir, "bundle-manifest.json")
    verbatim, ceremony = {}, []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            _, existing, _ = parse_manifest(fh.read())
        for body, obj in existing:
            if obj["path"].startswith(CEREMONY_PREFIX):
                verbatim[obj["path"]] = body
                ceremony.append(obj)
    text = render_manifest(appid, bundle_entries(bundle_dir, generated_at) + ceremony, verbatim)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return text


def write_index(bundle_dir: str, appid: str, ks: dict) -> None:
    repo, sha = ks["source"]["repo"], ks["source"]["commit_sha"]
    lines = ['---\nokf_version: "0.2"\n---\n',
             f"# {ks['title']} — application bundle (`{appid}`)\n",
             f"Application bundle for [`{repo}`](https://github.com/{repo}) at commit "
             f"[`{sha[:12]}`](https://github.com/{repo}/tree/{sha}). This index links to sections and "
             "directories only, so it never goes stale when ceremony knowledge lands.\n",
             "## Sections\n"]
    for slug in SECTIONS:
        p = os.path.join(bundle_dir, "sections", f"{slug}.md")
        if os.path.exists(p):
            fm = _frontmatter(p)
            tag = " *(illustrative)*" if (fm.get("x_kf") or {}).get("synthetic") else ""
            lines.append(f"- [{SECTION_TITLES[slug]}](sections/{slug}.md){tag} — {fm.get('description', '').strip()}")
    dm_dir = os.path.join(bundle_dir, "domains-maps")
    if os.path.isdir(dm_dir) and os.listdir(dm_dir):
        lines.append("\n## Domain maps\n")
        for name in sorted(os.listdir(dm_dir)):
            fm = _frontmatter(os.path.join(dm_dir, name))
            lines.append(f"- [{fm.get('title', name)}](domains-maps/{name}) — {fm.get('description', '').strip()}")
    lines += ["\n## Code graph\n",
              "- [Module view](code-graph/views/modules.md) — directory-level dependency view",
              "- [Dependencies and hotspots](code-graph/views/dependencies.md) — external packages, "
              "entry points, fan-in",
              "- [Metrics](code-graph/metrics.json) · [Graph records (JSONL)](code-graph/code-graph.jsonl)",
              "\n## Knowledge sources\n",
              "- [Agile ceremonies](knowledge-sources/agile-ceremonies/) — candidate knowledge from scrum "
              "ceremonies, one directory per ceremony and team",
              "\n## Control files\n",
              "- [Source pin](knowledge-source.json) · [Manifest](bundle-manifest.json) · [Bundle log](log.md)\n"]
    with open(os.path.join(bundle_dir, "index.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


def log_block(date: str, summary: str, bullets: list[str]) -> str:
    return f"## {date}: {summary}\n\n" + "".join(f"- {b}\n" for b in bullets) + "\n"


def write_initial_log(bundle_dir: str, appid: str, block: str) -> None:
    with open(os.path.join(bundle_dir, "log.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# {appid} — bundle log\n\n" + block)


def insert_log_block(text: str, block: str, date: str) -> str:
    """Insert `block` (which ends with a blank line) at its newest-first position.

    Pure insertion at a line boundary: every byte of `text` is preserved, which
    is what the insert-only log rule (G4/protected content) verifies. Same-date
    blocks keep their order; the new one lands below them."""
    offset = 0
    for line in text.splitlines(keepends=True):
        if line.startswith("## ") and line[3:13] < date:
            return text[:offset] + block + text[offset:]
        offset += len(line)
    if not text.endswith("\n"):
        text += "\n"
    if not text.endswith("\n\n"):
        text += "\n"
    return text + block


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)

"""bundle-manifest.json: one-entry-per-line format, byte-splice, verification.

Format (normative — review findings T2/P7): a fixed header line, then one
canonical one-line JSON object per entry, sorted by `path` in UTF-8 byte
order, then a fixed footer. Every edit is a splice of whole lines; nothing
is ever re-serialized, so concurrent PRs for different files touch
different lines and a parse→stringify rewrite is detectable byte-for-byte.
"""
from __future__ import annotations

import json

from . import MANIFEST_SCHEMA

INDENT = "    "
CEREMONY_PREFIX = "knowledge-sources/"


def render_entry(entry: dict) -> str:
    return json.dumps(entry, sort_keys=True, ensure_ascii=False, separators=(", ", ": "))


def _key(path: str) -> bytes:
    return path.encode("utf-8")


def render_manifest(appid: str, entries: list[dict], verbatim: dict[str, str] | None = None) -> str:
    """Render a whole manifest. `verbatim` maps path → existing line text to keep byte-identical."""
    verbatim = verbatim or {}
    header = {"appid": appid, "kind": "application", "okf_version": "0.2", "schema": MANIFEST_SCHEMA}
    rows = sorted(entries, key=lambda e: _key(e["path"]))
    lines = [verbatim.get(e["path"], render_entry(e)) for e in rows]
    body = ",\n".join(INDENT + ln for ln in lines)
    return ('{\n  "bundle": ' + render_entry(header) + ',\n  "entries": [\n'
            + (body + "\n" if body else "") + "  ]\n}\n")


class ManifestError(ValueError):
    pass


def parse_manifest(text: str) -> tuple[list[str], list[tuple[str, dict]], list[str]]:
    """Split into (header lines, [(entry line text sans indent/comma, obj)], footer lines)."""
    lines = text.split("\n")
    try:
        start = lines.index('  "entries": [') + 1
        end = len(lines) - 1 - lines[::-1].index("  ]")
    except ValueError as exc:
        raise ManifestError("manifest is not in the one-entry-per-line format "
                            "(missing '  \"entries\": [' / '  ]' lines)") from exc
    entries = []
    for i, raw in enumerate(lines[start:end]):
        if not raw.startswith(INDENT):
            raise ManifestError(f"entry line {start + i + 1} is not indented with 4 spaces")
        body = raw[len(INDENT):]
        is_last = i == end - start - 1
        if not is_last:
            if not body.endswith(","):
                raise ManifestError(f"entry line {start + i + 1} is missing its trailing comma")
            body = body[:-1]
        elif body.endswith(","):
            raise ManifestError(f"last entry line {start + i + 1} has a trailing comma")
        try:
            obj = json.loads(body)
        except ValueError as exc:
            raise ManifestError(f"entry line {start + i + 1} is not one JSON object: {exc}") from exc
        if not isinstance(obj, dict) or not isinstance(obj.get("path"), str):
            raise ManifestError(f"entry line {start + i + 1} has no string 'path'")
        entries.append((body, obj))
    try:
        json.loads(text)
    except ValueError as exc:
        raise ManifestError(f"manifest is not valid JSON: {exc}") from exc
    return lines[:start], entries, lines[end:]


def splice_insert(text: str, entry: dict) -> str:
    """Insert one entry at its byte-order index; every other byte is preserved."""
    header, entries, footer = parse_manifest(text)
    new_key = _key(entry["path"])
    if any(_key(o["path"]) == new_key for _, o in entries):
        raise ManifestError(f"entry for {entry['path']} already exists")
    idx = next((i for i, (_, o) in enumerate(entries) if _key(o["path"]) > new_key), len(entries))
    bodies = [b for b, _ in entries]
    bodies.insert(idx, render_entry(entry))
    mid = [INDENT + b + ("," if i < len(bodies) - 1 else "") for i, b in enumerate(bodies)]
    return "\n".join(header + mid + footer)


def splice_remove(text: str, path: str) -> str:
    """Inverse splice: remove exactly one entry line (used by the revert class)."""
    header, entries, footer = parse_manifest(text)
    bodies = [b for b, o in entries if o["path"] != path]
    if len(bodies) == len(entries):
        raise ManifestError(f"no entry for {path}")
    mid = [INDENT + b + ("," if i < len(bodies) - 1 else "") for i, b in enumerate(bodies)]
    return "\n".join(header + mid + footer)


def verify_single_splice(base: str, head: str) -> tuple[dict | None, str | None]:
    """Ceremony class: head must be base + exactly one byte-spliced entry."""
    try:
        _, bents, _ = parse_manifest(base)
        _, hents, _ = parse_manifest(head)
    except ManifestError as exc:
        return None, str(exc)
    bpaths = {o["path"] for _, o in bents}
    new = [o for _, o in hents if o["path"] not in bpaths]
    if len(new) != 1:
        return None, f"expected exactly one new manifest entry, found {len(new)}"
    expected = splice_insert(base, new[0])
    if expected != head:
        return new[0], ("manifest bytes differ from a single-entry splice of the base — the "
                        "file was re-serialized or other entries changed (byte-splice rule)")
    return new[0], None


def verify_bundle_ops(base: str | None, head: str) -> list[str]:
    """Bundle-update class: per-entry splices/replacements only; ceremony entries untouched."""
    problems = []
    try:
        hh, hents, hf = parse_manifest(head)
    except ManifestError as exc:
        return [str(exc)]
    keys = [_key(o["path"]) for _, o in hents]
    if keys != sorted(keys) or len(set(keys)) != len(keys):
        problems.append("entries are not unique and sorted by path in UTF-8 byte order")
    for body, obj in hents:
        if body != render_entry(obj) and not obj["path"].startswith(CEREMONY_PREFIX):
            problems.append(f"entry for {obj['path']} is not in canonical one-line form (re-serialized?)")
    if base is not None:
        try:
            bh, bents, bf = parse_manifest(base)
        except ManifestError as exc:
            return problems + [f"base manifest unreadable: {exc}"]
        if bh != hh or bf != hf:
            problems.append("manifest header/footer changed — only entry lines may change")
        bcer = {b for b, o in bents if o["path"].startswith(CEREMONY_PREFIX)}
        hcer = {b for b, o in hents if o["path"].startswith(CEREMONY_PREFIX)}
        if bcer != hcer:
            problems.append("ceremony (knowledge-sources/) manifest entries were added, removed or "
                            "altered — only the ceremony and revert classes may change them")
    return problems

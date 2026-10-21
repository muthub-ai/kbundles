"""Shared helpers: canonical serialization, hashing, frontmatter, globbing."""
from __future__ import annotations

import fnmatch
import hashlib
import json
import re
from typing import Any

import yaml

# Middle dot with spaces separates footnote fields: "src · path#L1-L4 · sha256:…"
SEP = " · "


def canonical_json(obj: Any) -> str:
    """One-line canonical JSON: sorted keys, no whitespace, UTF-8 preserved."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def pretty_json(obj: Any) -> str:
    """Stable human-readable JSON (sorted keys, 2-space indent, trailing LF)."""
    return json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def normalize_lines(data: bytes) -> list[str]:
    """Decode and split into lines; the only normalization is CRLF/CR → LF."""
    text = data.decode("utf-8", errors="surrogateescape").replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def span_hash(data: bytes, start: int, end: int) -> str:
    """sha256 of lines start..end (1-based, inclusive), each LF-terminated."""
    lines = normalize_lines(data)
    if start < 1 or end < start or end > len(lines):
        raise ValueError(f"line range L{start}-L{end} outside file of {len(lines)} lines")
    span = "".join(line + "\n" for line in lines[start - 1:end])
    return sha256_bytes(span.encode("utf-8", errors="surrogateescape"))


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def split_frontmatter(text: str) -> tuple[dict | None, str, str | None]:
    """Return (frontmatter dict or None, body, error). Body excludes the fence."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text, None
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as exc:  # report, never raise: callers turn this into findings
        return None, text[m.end():], f"frontmatter is not valid YAML: {exc}"
    if not isinstance(fm, dict):
        return None, text[m.end():], "frontmatter is not a YAML mapping"
    return fm, text[m.end():], None


def dump_frontmatter(fm: dict) -> str:
    return "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=100) + "---\n"


def match_any(path: str, globs: list[str]) -> bool:
    """fnmatch where '**/' also matches zero directories."""
    for g in globs:
        if fnmatch.fnmatchcase(path, g):
            return True
        if g.startswith("**/") and fnmatch.fnmatchcase(path, g[3:]):
            return True
    return False


ISO_OFFSET_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)$")


def is_iso_with_offset(value: Any) -> bool:
    return isinstance(value, str) and bool(ISO_OFFSET_RE.match(value))


def get_path(d: dict, dotted: str) -> Any:
    cur: Any = d
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur

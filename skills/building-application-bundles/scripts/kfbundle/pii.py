"""Deterministic PII denylist (gate G9). Cheap, real, and explicitly partial:
the full PII policy is deferred (spec D14)."""
from __future__ import annotations

import re

EMAIL_RE = re.compile(r"(?<![\w.+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}(?!\w)")
PHONE_RE = re.compile(
    r"(?<![\w+])(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?!\w)"
    r"|(?<![\w])\+\d{1,3}[\s.-]\d{2,4}[\s.-]\d{3,4}[\s.-]\d{3,4}(?!\w)")
EMPLOYEE_ID_RE = re.compile(r"\b(?:EMP|EID)[-_ ]?\d{5,8}\b", re.I)
# Long hex tokens (hashes, SHAs) are removed before scanning so their digit
# runs can never be mistaken for phone numbers.
HEX_TOKEN_RE = re.compile(r"\b[0-9a-f]{12,}\b", re.I)
ALLOWED_EMAILS = {"noreply@anthropic.com"}


def scan(text: str) -> list[tuple[int, str, str]]:
    """Return [(line number, kind, match)] for every PII hit."""
    hits = []
    for i, line in enumerate(text.split("\n"), 1):
        clean = HEX_TOKEN_RE.sub(" ", line)
        for m in EMAIL_RE.finditer(clean):
            if m.group(0).lower() not in ALLOWED_EMAILS:
                hits.append((i, "email", m.group(0)))
        for m in PHONE_RE.finditer(clean):
            hits.append((i, "phone", m.group(0)))
        for m in EMPLOYEE_ID_RE.finditer(clean):
            hits.append((i, "employee-id", m.group(0)))
    return hits

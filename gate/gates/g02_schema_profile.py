"""G2 — schema and ceremony profile (OKF requireds, x_kf requireds, sections)."""
import re

from kfgate.ceremony_doc import (ALLOWED, CEREMONY_SCHEMA, EXPECTED, EXTRA_SECTIONS, PREFIX_SECTION,
                                 SECTION_PREFIX, body_sha, knowledge_id)
from kfgate.context import Finding

from kfbundle.common import get_path, is_iso_with_offset

GATE = "G2"
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def check(ctx):
    n = ctx.notes
    path = n.get("cer_path", "")
    if n.get("cer_text") is None:
        return []
    if n.get("cer_err") or not n.get("cer_fm"):
        return [Finding(GATE, n.get("cer_err") or "missing YAML frontmatter", path)]
    fm, out = n["cer_fm"], []
    f = lambda msg, sev="error": out.append(Finding(GATE, msg, path, sev))  # noqa: E731
    if fm.get("type") != f"agile-ceremony/{ctx.ceremony}":
        f(f"type must be 'agile-ceremony/{ctx.ceremony}' (found {fm.get('type')!r})")
    gby = get_path(fm, "generated.by")
    if not (isinstance(gby, str) and gby.startswith("process:")):
        f("generated.by must be a 'process:' identity")
    if not is_iso_with_offset(get_path(fm, "generated.at")):
        f("generated.at must be ISO-8601 with an explicit UTC offset")
    if "verified" in fm:
        f("verified must be absent — acceptance is presence on main after the enforced approval")
    sources = fm.get("sources") if isinstance(fm.get("sources"), list) else []
    if not sources:
        f("sources[] must be non-empty")
    for s in sources:
        if not isinstance(s, dict) or not s.get("id") or not HEX64.match(str(s.get("sha256", ""))):
            f(f"every source needs an id and a 64-hex sha256 (bad: {s!r})")
    x = fm.get("x_kf") if isinstance(fm.get("x_kf"), dict) else {}
    if x.get("schema") != CEREMONY_SCHEMA:
        f(f"x_kf.schema must be '{CEREMONY_SCHEMA}'")
    for key in ("appid", "ceremony", "team", "ceremony_date", "knowledge_id", "content_sha256"):
        if not x.get(key):
            f(f"x_kf.{key} is required")
    if get_path(x, "review.submitted_as") != "candidate":
        f("x_kf.review.submitted_as must be 'candidate' (it never flips; accepted = present on main)")
    if not get_path(x, "review.approver"):
        f("x_kf.review.approver is required")
    if (ctx.config or {}).get("require_synthetic"):
        if x.get("synthetic") is not True:
            f("this repository requires x_kf.synthetic: true on fabricated meeting knowledge")
        if "illustrative" not in str(fm.get("description", "")).lower():
            f("synthetic knowledge must say 'illustrative' in its description")
    repo = (ctx.config or {}).get("repo", "")
    if x.get("appid") and x.get("ceremony") and x.get("team") and x.get("ceremony_date"):
        want = knowledge_id(x["appid"], x["ceremony"], x["team"], str(x["ceremony_date"]), repo)
        if x.get("knowledge_id") != want:
            f("x_kf.knowledge_id does not equal sha256(appid|ceremony|team|date|repo)")
    if x.get("content_sha256") and x["content_sha256"] != body_sha(n["cer_body"]):
        f("x_kf.content_sha256 does not match the file body")

    doc = n["cer_doc"]
    allowed_sections = {PREFIX_SECTION[p] for p in ALLOWED.get(ctx.ceremony, set())}
    allowed_sections |= set(EXTRA_SECTIONS.get(ctx.ceremony, [])) | {"Attendance"}
    for sec in doc.sections:
        if sec not in allowed_sections:
            f(f"section '{sec}' is not in the {ctx.ceremony} profile (allowed: {', '.join(sorted(allowed_sections))})")
        elif sec != "Attendance" and not any(i.section == sec for i in doc.items):
            f(f"section '{sec}' is empty — empty sections are always omitted")
    for item in doc.items:
        if item.section in SECTION_PREFIX:
            if not item.iid:
                f(f"line {item.line}: item must look like '- **{SECTION_PREFIX[item.section]}-n** *(confidence)* — text'")
            elif item.iid.split("-")[0] != SECTION_PREFIX[item.section]:
                f(f"line {item.line}: {item.iid} does not belong in section '{item.section}'")
            elif item.iid.split("-")[0] not in ALLOWED.get(ctx.ceremony, set()):
                f(f"line {item.line}: {item.iid.split('-')[0]}- items are not allowed in a {ctx.ceremony}")
    present = {SECTION_PREFIX[s] for s in doc.sections if s in SECTION_PREFIX}
    for missing in sorted(EXPECTED.get(ctx.ceremony, set()) - present):
        f(f"expected section '{PREFIX_SECTION[missing]}' is absent (soft check)", "warn")
    return out

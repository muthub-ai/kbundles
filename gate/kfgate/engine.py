"""Run the gates for a PR's class and produce the verdict (fail closed on any crash)."""
from __future__ import annotations

import importlib
import os
import sys
import traceback
from dataclasses import dataclass, field

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "skills",
                                                "building-application-bundles", "scripts")))

from . import GATE_VERSION, approval  # noqa: E402
from .classes import classify  # noqa: E402
from .context import Finding  # noqa: E402
from .prep import prep_ceremony  # noqa: E402

CLASS_GATES = {
    "ceremony": ["g01_path_allowlist", "g02_schema_profile", "g03_coherence", "g04_additive_byte",
                 "g05_registration", "g06_provenance", "g07_approver", "g08_sanity", "g09_pii",
                 "g10_trailer", "soft_checks", "protected_content"],
    "bundle-update": ["bundle_update", "g06b_bundle_provenance", "g11_graph_reproducible", "g07b",
                      "g09_pii", "g10_trailer", "protected_content"],
    "revert": ["revert_class", "g10_trailer", "g09_pii"],
    "tooling": ["protected_content"],
    "other": ["protected_content"],
    "unknown": [],
}


@dataclass
class Verdict:
    cls: str
    conclusion: str             # success | action_required | failure | bootstrap-ok
    findings: list[Finding] = field(default_factory=list)
    approval: str = ""
    appid: str | None = None
    team: str | None = None
    ceremony: str | None = None
    gate_version: str = GATE_VERSION

    @property
    def errors(self):
        return [f for f in self.findings if f.severity == "error"]

    @property
    def warnings(self):
        return [f for f in self.findings if f.severity == "warn"]

    def failing_gates(self) -> list[str]:
        return sorted({f.gate for f in self.errors})

    def as_dict(self):
        return {"class": self.cls, "conclusion": self.conclusion, "appid": self.appid, "team": self.team,
                "ceremony": self.ceremony, "approval": self.approval, "gate_version": self.gate_version,
                "failing_gates": self.failing_gates(),
                "findings": [f.as_dict() for f in self.findings]}


def _g07b(ctx):
    from gates.g07_approver import approver_problems
    ks = ctx.notes.get("ks") or {}
    owners = (ctx.appid_cfg() or {}).get("owners") or []
    return approver_problems(ctx, (ks.get("review") or {}).get("approver"),
                             f"application-bundles/{ctx.appid}/knowledge-source.json", owners)


def evaluate(ctx, fetch=None) -> Verdict:
    findings: list[Finding] = []
    if ctx.config is None:
        findings.append(Finding("CFG", "base ref has no readable .github/kf/config.yml trust root"))
        return Verdict("unknown", "failure", findings)
    cls = classify(ctx)
    if cls == "unknown":
        findings.append(Finding("CLASS", f"class=unknown: {ctx.notes.get('unknown_reason')} — the gate fails "
                                         "closed", ", ".join(ctx.paths[:6])))
    if cls == "ceremony":
        prep_ceremony(ctx)
    for name in CLASS_GATES[cls]:
        try:
            if name == "g07b":
                findings.extend(_g07b(ctx))
            else:
                findings.extend(importlib.import_module(f"gates.{name}").check(ctx))
        except Exception as exc:  # fail closed: a crashing gate is a failing gate
            findings.append(Finding("CRASH", f"gate {name} crashed: {exc!r} — {traceback.format_exc(limit=2)[-300:]}"))
    v = Verdict(cls, "failure", findings, appid=ctx.appid, team=ctx.team, ceremony=ctx.ceremony)
    if v.errors:
        return v
    if ctx.bootstrap:
        v.conclusion, v.approval = "bootstrap-ok", "direct bootstrap: approval not applicable (never approved)"
        return v
    if cls == "other":
        v.conclusion, v.approval = "success", "no approval required for docs-only changes"
        return v
    allowed = set()
    if cls == "ceremony":
        allowed = {str(((ctx.notes.get("cer_fm") or {}).get("x_kf") or {}).get("review", {}).get("approver", ""))}
    elif cls == "bundle-update":
        allowed = {str(((ctx.notes.get("ks") or {}).get("review") or {}).get("approver", ""))}
    elif cls == "revert":
        allowed = set(ctx.notes.get("revert_approvers", []))
    elif cls == "tooling":
        allowed = set((ctx.config or {}).get("code_owners", []))
    ok, note = approval.evaluate(ctx, allowed, fetch)
    v.approval = note
    v.conclusion = "success" if ok else "action_required"
    return v

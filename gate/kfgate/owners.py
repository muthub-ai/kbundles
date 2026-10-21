"""OWNERS files: who may approve knowledge for one appid (spec v0.5, D17).

`application-bundles/<appid>/OWNERS` lists the GitHub logins allowed to approve
that app's knowledge. It is read from the BASE ref only, so a PR can never add
its own author or approver. An app without an OWNERS file falls back to the KF
stewards in the trust root (`kf_stewards` in .github/kf/config.yml), so every
app works before anyone has claimed it.

Format (YAML):

    # OWNERS for kfcor
    approvers:
      - genlinemedia
      - muthub-ai
"""
from __future__ import annotations

import re

import yaml

LOGIN_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")


def owners_path(appid: str) -> str:
    return f"application-bundles/{appid}/OWNERS"


def parse(text: str | None) -> tuple[list[str] | None, str | None]:
    """Return (approvers, error). approvers is None when the text is absent."""
    if text is None:
        return None, None
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return [], f"OWNERS is not valid YAML: {exc}"
    if not isinstance(data, dict) or not isinstance(data.get("approvers"), list):
        return [], "OWNERS must be a YAML mapping with an 'approvers' list"
    logins, bad = [], []
    for a in data["approvers"]:
        s = str(a).lstrip("@")
        (logins if LOGIN_RE.match(s) else bad).append(s)
    if bad:
        return logins, f"not GitHub logins: {', '.join(bad)} (one login per line; no emails, no teams yet)"
    if not logins:
        return [], "OWNERS lists no approvers"
    unknown = set(data) - {"approvers", "reviewers", "notes"}
    if unknown:
        return logins, f"unknown OWNERS keys: {', '.join(sorted(unknown))}"
    return logins, None


def approvers_for(ctx, appid: str) -> tuple[list[str], str]:
    """Approvers for an appid as of the base ref, and where they came from."""
    found, _err = parse(ctx.base_text(owners_path(appid)))
    if found:
        return found, f"application-bundles/{appid}/OWNERS"
    stewards = [str(s).lstrip("@") for s in ((ctx.config or {}).get("kf_stewards") or [])]
    return stewards, "kf_stewards (no OWNERS file for this app yet)"

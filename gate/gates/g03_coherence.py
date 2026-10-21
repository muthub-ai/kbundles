"""G3 — coherence + registry (D19): path ⇔ filename ⇔ branch ⇔ frontmatter, appid registered,
team registered under that appid (hard), date not in the future anywhere on Earth."""
import datetime as dt
import re
from zoneinfo import ZoneInfo

from kfgate.ceremony_doc import TEAM_RE, branch_name
from kfgate.context import Finding

GATE = "G3"
UTC_PLUS_14 = dt.timezone(dt.timedelta(hours=14))   # earliest calendar day on Earth


def check(ctx):
    n, out = ctx.notes, []
    path = n.get("cer_path", "")
    f = lambda msg, sev="error": out.append(Finding(GATE, msg, path, sev))  # noqa: E731
    cfg = ctx.config or {}
    if not ctx.appid:
        return out          # G1 already reports a PR that spans several appids
    if ctx.appid in (cfg.get("reserved_appids") or []):
        f(f"appid '{ctx.appid}' is reserved")
    reg = ctx.appid_cfg()
    if reg is None:
        f(f"appid '{ctx.appid}' is not registered in .github/kf/config.yml (D19: unregistered folders "
          "are rejected)")
        return out
    if ctx.ceremony not in (cfg.get("ceremonies") or []):
        f(f"ceremony '{ctx.ceremony}' is not one of {cfg.get('ceremonies')}")
    team = ctx.team or ""
    aliases = reg.get("aliases") or {}
    if not TEAM_RE.match(team) or not (2 <= len(team) <= 40):
        f(f"team slug '{team}' must match ^[a-z0-9]+(-[a-z0-9]+)*$ and be 2–40 characters")
    if team in (cfg.get("reserved_team_slugs") or []):
        f(f"team slug '{team}' is reserved")
    if team in aliases:
        f(f"team '{team}' is an alias — use the canonical slug '{aliases[team]}'", "warn")
    elif team not in (reg.get("teams") or {}):
        f(f"team '{team}' is not registered under appid '{ctx.appid}' (team→appid binding is hard; "
          f"registered: {', '.join(sorted(reg.get('teams') or {}))})")
    if n.get("cer_name_ceremony") != ctx.ceremony or not n.get("cer_date"):
        f(f"file name must be '{ctx.ceremony}_YYYY-MM-DD.md'")
    fm = n.get("cer_fm") or {}
    x = fm.get("x_kf") if isinstance(fm.get("x_kf"), dict) else {}
    for key, want in (("appid", ctx.appid), ("ceremony", ctx.ceremony), ("team", ctx.team),
                      ("ceremony_date", n.get("cer_date"))):
        if x and str(x.get(key)) != str(want):
            f(f"x_kf.{key} is {x.get(key)!r} but the path says {want!r}")
    date = n.get("cer_date")
    if date:
        want_branch = branch_name(ctx.appid, ctx.ceremony, ctx.team, date)
        if not ctx.bootstrap:
            if ctx.pr.branch != want_branch or len(ctx.pr.branch.split("/")) != 5:
                f(f"branch must be exactly '{want_branch}' (found '{ctx.pr.branch}')")
        try:
            day = dt.date.fromisoformat(date)
            if day > ctx.now.astimezone(UTC_PLUS_14).date():
                f(f"ceremony date {date} is in the future in every time zone")
        except ValueError:
            f(f"'{date}' is not a valid date")
        tz = (reg.get("teams") or {}).get(team, {}).get("timezone")
        mdt = x.get("meeting_datetime") if x else None
        if tz and mdt:
            try:
                local = dt.datetime.fromisoformat(str(mdt)).astimezone(ZoneInfo(tz)).date().isoformat()
                if local != date:
                    f(f"meeting_datetime falls on {local} in the team time zone {tz}, not {date}", "warn")
            except ValueError:
                f(f"meeting_datetime {mdt!r} is not ISO-8601", "warn")
    if re.search(r"[A-Z]", path):
        f("paths must be lowercase")
    return out

"""G7 — approver: resolvable, not the author, write permission (a read-only approver could
never approve). Bundle-update PRs additionally require approver ∈ owners(appid) (D19)."""
from kfgate.context import Finding

from kfbundle.common import get_path

GATE = "G7"


def approver_problems(ctx, approver: str | None, path: str, owners: list[str] | None = None):
    out = []
    if not approver:
        return [Finding(GATE, "no approver declared", path)]
    a = approver.lstrip("@")
    if ctx.bootstrap:
        return [Finding(GATE, f"direct bootstrap — approval by @{a} was never requested (content is "
                              "flagged x_kf.bootstrap)", path, "warn")]
    if not ctx.ids.exists(a):
        out.append(Finding(GATE, f"approver @{a} is not a resolvable GitHub user", path))
    elif not ctx.ids.can_write(a):
        seen = ctx.ids.describe(a)
        out.append(Finding(GATE, f"approver @{a} lacks write permission on this repository, so their "
                                 f"approval could never count{f' ({seen})' if seen else ''}", path))
    if a.lower() == ctx.pr.author.lower():
        out.append(Finding(GATE, f"approver @{a} is the PR author — self-approval is not allowed", path))
    if owners is not None and a.lower() not in {o.lower().lstrip("@") for o in owners}:
        out.append(Finding(GATE, f"approver @{a} is not an owner of appid '{ctx.appid}' "
                                 f"(owners: {', '.join(owners)})", path))
    return out


def check(ctx):
    fm = ctx.notes.get("cer_fm")
    if not fm:
        return []
    return approver_problems(ctx, get_path(fm, "x_kf.review.approver"), ctx.notes["cer_path"])

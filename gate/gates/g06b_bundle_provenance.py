"""G6-bundle — run the shared bundle rulebook (kfbundle.lint) over the materialized head bundle:
schema (B2), coherence (B3), registration (B5), per-claim citations verified at the pinned SHA
(B6) and PII (B9). Same library the bundle builder's validator uses — no drift."""
import os
import subprocess
import tempfile

from kfgate import source
from kfgate.context import Finding

from kfbundle.controls import git_reader
from kfbundle.lint import lint_bundle


def materialize(ctx) -> str:
    d = tempfile.mkdtemp(prefix="kf-head-")
    arch = subprocess.run(["git", "-C", ctx.repo, "archive", ctx.head, f"application-bundles/{ctx.appid}"],
                          capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", d], input=arch, check=True)
    return os.path.join(d, "application-bundles", ctx.appid)


def check(ctx):
    ks = ctx.notes.get("ks")
    if not ks:
        return []
    repo, sha = ks["source"]["repo"], ks["source"]["commit_sha"]
    try:
        src = source.checkout(repo, sha, ctx.source_cache)
    except source.FetchError as exc:
        return [Finding("B6", str(exc))]
    ctx.notes["source_dir"] = src
    bundle_dir = materialize(ctx)
    ctx.notes["head_bundle_dir"] = bundle_dir
    root = f"application-bundles/{ctx.appid}/"
    return [Finding(f.code, f.message, root + f.path, f.severity)
            for f in lint_bundle(bundle_dir, git_reader(src, sha), ctx.config)]

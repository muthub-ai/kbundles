"""G11 — graph reproducibility (bundle-update only).

(i) the toolchain stamped in code-graph.jsonl must equal the BASE-ref
.github/kf/toolchain.lock (a PR cannot bump the lock and regenerate in one
step); (ii) the gate's own environment must match too; (iii) re-run the
extractor on the data-only checkout at the pinned SHA; (iv) every derived
artifact must be byte-identical. A derived artifact is verified by
reproduction, so no human has to review a large JSONL diff.
"""
import json
import os

from kfgate.context import Finding

from kfbundle import graph, views
from kfbundle.languages import toolchain_versions

GATE = "G11"


def parse_lock(text: str) -> dict[str, str]:
    pins = {}
    for line in (text or "").splitlines():
        line = line.split("#", 1)[0].strip()
        if "==" in line:
            name, ver = line.split("==", 1)
            pins[name.strip()] = ver.strip()
    return pins


def check(ctx):
    ks, src, bdir = ctx.notes.get("ks"), ctx.notes.get("source_dir"), ctx.notes.get("head_bundle_dir")
    if not (ks and src and bdir):
        return []
    root = f"application-bundles/{ctx.appid}/"
    pins = parse_lock(ctx.base_text(".github/kf/toolchain.lock"))
    if not pins:
        return [Finding(GATE, "base ref has no .github/kf/toolchain.lock — cannot verify the graph toolchain")]
    try:
        with open(os.path.join(bdir, "code-graph", "code-graph.jsonl"), encoding="utf-8") as fh:
            meta = json.loads(fh.readline())
    except (OSError, ValueError):
        return [Finding(GATE, "code-graph.jsonl is missing or unreadable", root + "code-graph/code-graph.jsonl")]
    stamped = meta.get("toolchain", {})
    if any(stamped.get(k) != v for k, v in pins.items()):
        return [Finding(GATE, f"graph toolchain {stamped} differs from the base-ref toolchain.lock {pins} — "
                              "regenerate with the pinned toolchain (bump the lock in its own tooling PR)",
                        root + "code-graph/code-graph.jsonl")]
    env = toolchain_versions()
    if any(env.get(k) != v for k, v in pins.items()):
        return [Finding(GATE, f"gate environment toolchain {env} does not match toolchain.lock — fix the gate "
                              "runner; this check never passes on a mismatched toolchain")]
    recs = graph.extract(src, ks["source"]["repo"], ks["source"]["commit_sha"], ks.get("graph_options"))
    out = []
    for rel, content in views.build_derived(recs, graph.to_jsonl(recs), ctx.appid, ks["generated_at"]).items():
        try:
            with open(os.path.join(bdir, rel), encoding="utf-8") as fh:
                current = fh.read()
        except OSError:
            current = None
        if current != content:
            out.append(Finding(GATE, "derived artifact does not reproduce byte-for-byte at the pinned SHA",
                               root + rel))
    return out

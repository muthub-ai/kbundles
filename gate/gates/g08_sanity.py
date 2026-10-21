"""G8 — size and sanity: one ceremony file, ≤256 KB, UTF-8 text, no NUL bytes."""
from kfgate.context import Finding

GATE = "G8"
MAX_BYTES = 256 * 1024   # a ceremony recap distillate is a few KB; 256 KB means something else


def check(ctx):
    files = ctx.notes.get("ceremony_files", [])
    out = []
    if len(files) != 1:
        out.append(Finding(GATE, f"exactly one ceremony file per PR (found {len(files)})"))
    for c in files:
        data = ctx.head_text(c.path)
        if data is None:
            continue
        raw = data.encode("utf-8", errors="surrogateescape")
        if len(raw) > MAX_BYTES:
            out.append(Finding(GATE, f"file is {len(raw)} bytes; limit {MAX_BYTES}", c.path))
        if b"\x00" in raw:
            out.append(Finding(GATE, "binary content (NUL byte) is not allowed", c.path))
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError:
            out.append(Finding(GATE, "file is not valid UTF-8", c.path))
    return out

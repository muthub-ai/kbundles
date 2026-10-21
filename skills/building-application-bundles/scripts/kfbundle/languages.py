"""Grammar registry and file classification for the code-graph extractor.

The extension map is normative (plan §5.2): .ts/.mts/.cts/.d.ts → typescript,
.tsx → tsx (the TS grammar mis-parses JSX and the TSX grammar mis-parses
`<T>x` assertions, so they must never be swapped), .js/.mjs/.cjs/.jsx →
javascript (that grammar handles JSX), .py → python, .sh/shebang → bash.
Everything else is a structured-inventory or plain file node.
"""
from __future__ import annotations

from importlib import metadata

TOOLCHAIN_PACKAGES = [
    "tree-sitter",
    "tree-sitter-python",
    "tree-sitter-javascript",
    "tree-sitter-typescript",
    "tree-sitter-bash",
    "PyYAML",
]

AST_EXT = {
    ".py": "python",
    ".ts": "typescript", ".mts": "typescript", ".cts": "typescript",
    ".tsx": "tsx",
    ".js": "javascript", ".mjs": "javascript", ".cjs": "javascript", ".jsx": "javascript",
    ".sh": "bash", ".bash": "bash",
}

INVENTORY_EXT = {
    ".md": "markdown", ".mdx": "markdown",
    ".yaml": "yaml", ".yml": "yaml",
    ".json": "json",
    ".rego": "rego",
}

TEXT_EXT = {
    ".txt", ".toml", ".cfg", ".ini", ".puml", ".adoc", ".scss", ".css", ".html",
    ".xml", ".svg", ".env", ".example", ".gitignore", ".gitkeep", ".ref", ".lock",
    ".csv", ".sql", ".graphql",
}

ASSET_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".ttf", ".otf", ".woff",
    ".woff2", ".pdf", ".zip", ".gz", ".mp4", ".mov", ".wasm",
}

TEXT_NAMES = {"Makefile": "make", "Dockerfile": "text", "LICENSE": "text", "CODEOWNERS": "text"}


def classify(path: str, head: bytes) -> str:
    """Return a language/kind tag for a repository path."""
    name = path.rsplit("/", 1)[-1]
    lower = name.lower()
    if lower.endswith(".d.ts"):
        return "typescript"
    if lower.endswith(".min.js"):
        return "text"  # minified: never parsed (also flagged third_party by default)
    dot = lower.rfind(".")
    ext = lower[dot:] if dot > 0 else ""
    if ext in AST_EXT:
        return AST_EXT[ext]
    if ext in INVENTORY_EXT:
        return INVENTORY_EXT[ext]
    if name in TEXT_NAMES:
        return TEXT_NAMES[name]
    if ext in ASSET_EXT:
        return "asset"
    if ext in TEXT_EXT:
        return "text"
    if head.startswith(b"#!"):
        first = head.split(b"\n", 1)[0]
        if b"bash" in first or first.rstrip().endswith(b"/sh") or b" sh" in first:
            return "bash"
        if b"node" in first:
            return "javascript"
        if b"python" in first:
            return "python"
    if b"\x00" in head:
        return "asset"
    return "text"


_LANGS: dict[str, object] = {}


def get_language(lang: str):
    """Load a tree-sitter Language lazily (import errors surface with guidance)."""
    if lang in _LANGS:
        return _LANGS[lang]
    try:
        import tree_sitter as ts
        if lang == "python":
            import tree_sitter_python as m
            obj = ts.Language(m.language())
        elif lang == "javascript":
            import tree_sitter_javascript as m
            obj = ts.Language(m.language())
        elif lang == "typescript":
            import tree_sitter_typescript as m
            obj = ts.Language(m.language_typescript())
        elif lang == "tsx":
            import tree_sitter_typescript as m
            obj = ts.Language(m.language_tsx())
        elif lang == "bash":
            import tree_sitter_bash as m
            obj = ts.Language(m.language())
        else:
            raise KeyError(lang)
    except ImportError as exc:
        raise SystemExit(
            f"tree-sitter grammar for {lang!r} is not installed ({exc}). Install the pinned "
            "toolchain: pip install -r .github/kf/toolchain.lock — or run with --inventory-only."
        ) from exc
    _LANGS[lang] = obj
    return obj


def toolchain_versions() -> dict[str, str]:
    """Installed versions of every toolchain package ('missing' when absent)."""
    out = {}
    for pkg in TOOLCHAIN_PACKAGES:
        try:
            out[pkg] = metadata.version(pkg)
        except metadata.PackageNotFoundError:
            out[pkg] = "missing"
    return out

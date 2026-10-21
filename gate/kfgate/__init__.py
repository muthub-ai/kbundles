"""kf-knowledge-gate — the server-side gate for the kbundles knowledge repo.

Implements spec v0.4 (gates G1–G10, protected content, revert class,
content-bound named-approver enforcement) plus plan D17–D19 (the
application-bundles/ prefix, the bundle-update PR class with G6-bundle and
G11, and the appid registry with team→appid binding).
"""
GATE_VERSION = "0.1.0"
CHECK_NAME = "kf-knowledge-gate"
BUNDLES_ROOT = "application-bundles"

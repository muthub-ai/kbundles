"""kfbundle — canonical library for Knowledge Foundation application bundles.

One implementation, three consumers: the building-application-bundles skill,
tools/bundle_builder, and the kf-knowledge-gate (which imports it from the
base ref so a PR can never change the rules that judge it).
"""

LIBRARY_VERSION = "0.1.0"
BUNDLE_SCHEMA = "kf-application-bundle/1"
GRAPH_SCHEMA = "kf-code-graph/1"
MANIFEST_SCHEMA = "kf-bundle-manifest/1"
SOURCE_SCHEMA = "kf-knowledge-source/1"
BUILDER_ID = f"process:building-application-bundles@{LIBRARY_VERSION}"
EXTRACTOR_ID = f"kfbundle.graph@{LIBRARY_VERSION}"
VIEWS_ID = f"process:kfbundle.views@{LIBRARY_VERSION}"

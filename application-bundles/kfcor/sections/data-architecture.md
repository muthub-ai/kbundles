---
type: application-bundle/data-architecture
title: Data architecture — Knowledge Foundation core
description: The data entities of Knowledge Foundation core (notes, raw source copies, captures, the published
  graph and release assets), their schemas and the lineage between them.
generated:
  by: process:building-application-bundles@0.1.0
  at: '2026-10-20T19:30:00-05:00'
sources:
- id: repo
  kind: source-repo
  repo: muthub-ai/knowledge-foundation
  commit_sha: 78d41952391c91356afbebfaee129b8b40a12561
- id: graph
  kind: code-graph
  path: code-graph/code-graph.jsonl
  sha256: 881e9bd0100d27591d42a861bc0797c5ae5cb88f764837f511242482b5d82a7d
x_kf:
  schema: kf-application-bundle/1
  appid: kfcor
  bundle_kind: application
  section: data-architecture
  bootstrap: true
---
# Data architecture — Knowledge Foundation core

## Entities and schemas

| Entity | Store and format | Contract |
|---|---|---|
| Note | Markdown with YAML frontmatter under a theme folder of `wiki/`; requires `type: Note`, `title`, `description`, `generated`, `sources`, `kind`, `status`, `stale_after` and `classification` | `schemas/page.schema.json` [^page-req] |
| Raw source copy | `wiki/raw/` document of type `Source`; requires `published_at`, `origin_kind` (own essay, post, talk or repo, or a third-party note or excerpt) and `license_note` | `schemas/source.schema.json` [^src-req] [^src-origin] |
| Capture | Markdown in `inbox/` with `title`, `published_at`, `origin_kind` and `license_note`; moved to `inbox/done/` after filing | `tools/librarian/ingest.py` [^cap-req] |
| Published graph | `graph.json` with an ontology, nodes and edges, plus `graph.graphml` and `report.md` | `schemas/graph.schema.json` [^graph-out] [^g-graph-schema] |

## Trust and lifecycle fields

`verified` may be a single `{by, at}` mapping or a list of them, and the trust tier is never stored: it is derived as `unverified`, `machine-confirmed` or `human-reviewed` from whether any verification comes from a `human:` actor.[^okf-trust] [^page-verified]

`normalize` fills `kind`, `status: draft`, `classification: public`, the owner actor and `stale_after` (from `generated.at` plus the months configured for the note's kind) without overwriting values already present; the page schema types `stale_after` as a date-time and describes its default as coming from a per-kind table.[^gov-normalize] [^cfg-stale] [^schema-stale]

Typed relations live in frontmatter `relations` with ten allowed types, and `ontology/edge-types.yaml` adds the four edge types the builder derives (`links_to`, `in_folder`, `draws_on`, `mentions`).[^page-relations] [^edge-types]

## Lineage

The capture's publication fields are written onto the raw copy the note's newest source points at, each note links to its raw copies through bundle-path `sources`, and the graph turns those into `draws_on` edges and a per-note `source_date`.[^ing-raw] [^graph-draws] [^graph-sources]

Every graph edge carries an `origin` of `frontmatter`, `folder`, `link`, `source` or `extracted`, and the graph records the knowledge-repository commit it was built from in `source_revision`.[^graph-origin] [^graph-rev]

Each release packages `wiki/`, `wiki.config.yaml`, `schemas/` and `ontology/` as `bundle.tgz` next to `graph.json`, `graph.graphml` and `report.md`.[^pub-assets]

*Assessment:* The `stale_after` description in the page schema points at `ontology/node-types.yaml`, but the defaults are read from `stale_after_months` in `wiki.config.yaml`; the schema text looks like it predates that move and is a small documentation drift.[^schema-stale] [^cfg-stale] [^gov-normalize]

*Assessment:* Because `origin` is mandatory on edges and trust is derived rather than stored, a consumer can always separate authored structure from machine suggestions without trusting the producer's own labels.[^graph-origin] [^okf-trust]

[^page-req]: src · schemas/page.schema.json#L1-L17 · sha256:cac1f9a203624336de31f5a0d33f52de676a7f145407d9ec64182122856958c9
[^src-req]: src · schemas/source.schema.json#L1-L13 · sha256:e0297126a46f532054dd525fa3b059ddd0f39c972762c055fc4705387c824e16
[^cap-req]: src · tools/librarian/ingest.py#L37-L57 · sha256:11675a55ea62cd084036ad342e641811a0dcf6c8155f27a561daca28e334d040
[^graph-out]: src · tools/kb/graph.py#L1-L8 · sha256:964b834e717b2d35347caa900fd1709266066480b374675651f45aa3a0e7c67d
[^g-graph-schema]: graph · schemas/graph.schema.json
[^src-origin]: src · schemas/source.schema.json#L37-L48 · sha256:9a77bc462a96091816c8eec72410299311d3b5dc7d89fafc5a0172b8dd01d116
[^okf-trust]: src · tools/kb/okf.py#L123-L140 · sha256:3a2850ba8ecefd75b581bd6ba318d9484d642ea56cefd8daec0e872ec664aa98
[^page-verified]: src · schemas/page.schema.json#L136-L149 · sha256:3d4a910dbc0745b69302976680b617201141a17fbe6c3d279fcc9550cfb7c9f9
[^gov-normalize]: src · tools/kb/governance.py#L28-L48 · sha256:ec65a0c9bfad6d78a2e5c8536940ddbb6ada2a6e4618a6b74527814db3f902c2
[^cfg-stale]: src · wiki.config.yaml#L39-L50 · sha256:693e75063600497f907320b470122da342ef0579ce21980027b7b94c74ce3ca0
[^schema-stale]: src · schemas/page.schema.json#L131-L135 · sha256:645b35025f4018cb13d8f8250fa4fa842d14a65ba583db920f68f87d3908f48b
[^page-relations]: src · schemas/page.schema.json#L166-L197 · sha256:131f80abdf47e97d230fb6de9fd5d90945bc26303739bf9885c3eab69db7e9e0
[^edge-types]: src · ontology/edge-types.yaml#L1-L17 · sha256:dba7bc6f754b2446e68a0b747f999d6672a5c96cef6cba5f39b07d8f5c9945bb
[^ing-raw]: src · tools/librarian/ingest.py#L60-L73 · sha256:b546900049f58c04024aaa962bce6257db7e706377a6d22af604d4a88a48af16
[^graph-draws]: src · tools/kb/graph.py#L107-L118 · sha256:0306a6effd1912087cca27477c06a8741efca934a89659fc9baed794b3d63805
[^graph-sources]: src · tools/kb/graph.py#L56-L65 · sha256:f4672fd7ad3dc3f364f70ea0ddd9e2eb2f95d84fee03ee4251fb64b184ebe5e0
[^graph-origin]: src · schemas/graph.schema.json#L188-L197 · sha256:7b723739aa6e90b465c3b1150caac170f148606adc6e0198f60cf33cf1c3cac2
[^graph-rev]: src · schemas/graph.schema.json#L24-L27 · sha256:9cf18b19921558eaec51f378181aa43e2296c1667bc32e05a61ad4c2b5398ea2
[^pub-assets]: src · .github/workflows/publish.yml#L39-L45 · sha256:295ed1092ce4b713878557fcf84beb90ad59339a9b702630ec5161f8b2677613

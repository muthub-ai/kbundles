---
type: application-bundle/data-architecture
title: Data architecture — Portfolio website (muthub.org)
description: Content entities, their storage as typed source files, and the derived outputs built from
  them.
generated:
  by: process:building-application-bundles@0.1.0
  at: '2026-10-20T19:30:00-05:00'
sources:
- id: repo
  kind: source-repo
  repo: muthub-ai/muthu-v0-portfolio-website
  commit_sha: 8bca37ea8df4e3f6365c20a323bcd680c986a568
- id: graph
  kind: code-graph
  path: code-graph/code-graph.jsonl
  sha256: c30e501c460d37c9779b2d401e1e376a2e5c0290377d4b5c5d3a5ba92fbfe70d
x_kf:
  schema: kf-application-bundle/1
  appid: folio
  bundle_kind: application
  section: data-architecture
  bootstrap: true
---
# Data architecture — Portfolio website (muthub.org)

## Store and entities

There is no database or CMS: every entity is a typed TypeScript object in `content/*.ts`, and git history is the editorial log.[^adr-m01]

| Entity | Key fields |
|---|---|
| Essay / Note | `slug`, `title`, `summary`, `theme` (essays), `status`, `published`, `updated`, `body: Block[]` [^essay-type][^note-type] |
| Initiative / Playbook | initiative problem, approach, governance, outcome and optional C4 levels; playbook items with a `check` and a `reviewed` date [^initiative-type][^playbook-type] |

A reference dataset outside `content/` lists first-publication dates of commonly cited sources, keyed by URL fragment, for the date-integrity tests.[^source-dates]

## Derived outputs

The sitemap, RSS feed, Markdown twins and search index are all generated at build time from the same accessors in `lib/content.ts`, so drafts drop out of every output at once in a production build.[^sitemap][^rss][^content-visible]

*Assessment:* Because most sitemap entries take `lastModified` from the build time rather than from content dates, every deploy reports nearly all pages as modified; only playbooks and essays carry their own dates.[^sitemap]

[^adr-m01]: src · docs/decisions/M01-content-as-typed-code.md#L9-L18 · sha256:9063d7c08b0faef26389b65437e25af95d401c412800b02de8635288ef02a9e9
[^essay-type]: src · content/essays.ts#L7-L20 · sha256:46df21f7ea9db4dd40138b44a137ba9038ee15f08d32c50b76c01287007157b7
[^note-type]: src · content/essays.ts#L1132-L1141 · sha256:91a8e50c64dc3f15f6ab2ad22baed70207c1bc8de89952ab7c758c2fa9d8326f
[^initiative-type]: src · content/initiatives.ts#L6-L27 · sha256:d77ee565c03446bcb5451adea0f7bf9803738b90f811110c3120daa46141b617
[^playbook-type]: src · content/playbooks.ts#L4-L19 · sha256:c868caaf3888750d474188a6310bae75739708e410acef0577b90baa3c0a3d48
[^source-dates]: src · playwright/fixtures/source-dates.ts#L1-L5 · sha256:ddc5a9c985ba16bbc200aaeb6a326d31b7b82d5005223c65023e5f3fdd2f4934
[^sitemap]: src · app/sitemap.ts#L7-L32 · sha256:690076390979a2a45480a0568bed9b7f38dacbaca88ba42fbe909b325702ce78
[^rss]: src · app/rss.xml/route.ts#L8-L14 · sha256:b1cd61fd36c6bf4d93a48c4e489902f8b0d08332c59b12272efce736f036410d
[^content-visible]: src · lib/content.ts#L9-L24 · sha256:22e0e24b470c65bc9492307a5fc5dfc8925a5feab9710dd90f4c2f3687a0a6df

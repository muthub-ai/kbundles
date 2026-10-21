---
type: application-bundle/business-architecture
title: Business architecture — Knowledge Foundation site
description: Capabilities the site provides, the actors it serves and the publishing rules it enforces.
generated:
  by: process:building-application-bundles@0.1.0
  at: '2026-10-20T19:30:00-05:00'
sources:
- id: repo
  kind: source-repo
  repo: muthub-ai/knowledge-foundation-site
  commit_sha: 3afac247ec2848aa9d8844a83f1fc982eb6a6dc0
- id: graph
  kind: code-graph
  path: code-graph/code-graph.jsonl
  sha256: 7cce3a8bffd531894689010170006598998a6a2289a14595ccd4f2dfbb604d22
x_kf:
  schema: kf-application-bundle/1
  appid: kfsit
  bundle_kind: application
  section: business-architecture
  bootstrap: true
---
# Business architecture — Knowledge Foundation site

## Actors and capabilities

The site is designed for two human audiences equally, leaders looking for an argument and engineers looking for how it works, which is why the home page is the graph rather than a list of notes.[^s02]

| Capability | What the reader gets | Evidence |
|---|---|---|
| Explore the graph | Themes as hubs, hover neighbourhoods, an inspector with review state and dates, a list view | [^readme-surfaces] |
| Read a note with its provenance | A callout with review state, verification and re-check dates, and dated sources | [^readme-surfaces][^callout] |
| Machine consumption | Markdown twins, `llms.txt`, sitemap, RSS, JSON-LD and `graph.json` with CORS | [^readme-surfaces][^cors] |

## Business rules

Machine-found structure is labelled, grey, hidden by default and never counted with authored connections, so headline numbers describe only what the author stands behind.[^s06]

*Assessment:* The site treats honesty about provenance as a product feature rather than metadata: review state is the first thing on every note page and the counting rules are written down as a decision record.[^callout][^s06]

[^s02]: src · docs/decisions/S02-the-home-page-is-the-graph.md#L5-L15 · sha256:6d6fa48fb0776a511a66ae40f3740802c2d893751dd0493b08fa226e06c7cd9e
[^readme-surfaces]: src · README.md#L16-L23 · sha256:26ada72affc80aa57e6ffad701bb8757c470247dc7cfa4ae99fdc172224e5097
[^callout]: src · kfsite/stage.py#L73-L94 · sha256:ea91b135f6f6b9dbad39b603bb3318515ac580765a60c1abf502397859270dda
[^cors]: src · vercel.json#L76-L85 · sha256:5d8703490bb95253e64f8dcf3eae8ed90cd03f6fc6d541a0585d538acf02bf2d
[^s06]: src · docs/decisions/S06-machine-structure-is-labelled-hidden-and-counted-apart.md#L10-L19 · sha256:f45e9bef709558a47e9573c818de2623284e17a5ed582c70c1848fba81ff401a

---
type: application-bundle/domain-map
title: Domain map — provenance and graph vocabulary
description: Terms the site uses for note provenance and for the knowledge graph, with their meaning and
  where they live in code.
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
  domain: provenance-and-graph
  bootstrap: true
---
# Domain map — provenance and graph vocabulary

## Provenance terms

| Term | Meaning | Where in code |
|---|---|---|
| Trust tier | `human-reviewed`, `machine-confirmed` or `unverified`, derived from a note's `verified` entries | `kfsite/bundle.py::trust_tier` [^trust][^g-trust] |
| Last verified | the latest `at` among a note's `verified` entries | `kfsite/bundle.py::last_verified` [^trust] |
| Provenance callout | the box that opens every note page with kind, status, verification, drafting and re-check dates and source count | `Stager.note` [^callout] |
| Re-check date | a note's `stale_after` value shown as "Re-check by" | `Stager.note` [^callout] |
| Raw source copy | a bundle file under `raw/`; never published, links to it go to its original resource | `Doc.is_raw`, `Stager.relink` [^raw][^relink] |
| Canonical essay | a note's `canonical_essay` URL; the page becomes a summary that links to the essay first | `Stager.note` [^canonical] |
| Markdown twin | the note's original OKF file published at the page address plus `.md`, served `noindex` | `finish`, `vercel.json` [^twin][^md-headers] |

## Graph terms

| Term | Meaning | Where in code |
|---|---|---|
| Theme | a top-level bundle folder; drawn as a hub on the ring | `Doc.theme`, `layout` [^doc-theme][^layout-ring] |
| Edge origin | how a connection was found: `frontmatter`, `link`, `folder`, `source` or `extracted` | `ORIGIN_LABEL` [^origins] |
| Entity | a semantic-layer node with an `ext:` id, retyped from its own kind and hidden by default | explorer load step [^entity][^defaults] |
| Linked notes | distinct notes connected by a link or declared relation; theme membership and sources do not count | `linkCount` [^g-linkcount][^linkcount] |
| Deep link | `/graph/?node=<id>`, written into every note's callout and honoured by the explorer | `Stager.note`, explorer start [^callout][^deeplink] |

*Assessment:* The vocabulary keeps a hard line between what a person stands behind (trust tier, declared relations, linked notes) and what a machine found (machine-confirmed, extracted, Entity), and that line is enforced in code rather than in copy.[^trust][^entity][^linkcount]

[^trust]: src · kfsite/bundle.py#L70-L83 · sha256:67f918b1aef27f7ec4440a29b23e9feca7732a51f6b5b603cdcee992ab5a0ea9
[^g-trust]: graph · kfsite/bundle.py::trust_tier
[^callout]: src · kfsite/stage.py#L73-L94 · sha256:ea91b135f6f6b9dbad39b603bb3318515ac580765a60c1abf502397859270dda
[^raw]: src · kfsite/bundle.py#L109-L111 · sha256:84d573117791b17959a4ce5b6af7543ba06c0332498058c03696d5c47ade8499
[^relink]: src · kfsite/stage.py#L47-L59 · sha256:49d72fd9dc5ed6b8301cbafad27e7b146a45505ce3118276411a347486c66637
[^canonical]: src · kfsite/stage.py#L86-L91 · sha256:bb249b9ddbcb2992d96229937292191fab5f68e772437a216679b2e7a9bb6a46
[^twin]: src · kfsite/post.py#L69-L77 · sha256:af4e33d73aca7f4ebb6a0803f0fbdf5363730ca3644d62669b6f3a879c8b3ecb
[^md-headers]: src · vercel.json#L63-L75 · sha256:af28abaa2166b360ddd8a1867452f631a2250c05d608443a1ed0ef90054e5cd5
[^doc-theme]: src · kfsite/bundle.py#L117-L119 · sha256:2ae7cd56cee4f1f0b80151f494a8819fed1fac680ee08cc60bc98e2e6adcf893
[^layout-ring]: src · explorer/src/explorer.ts#L144-L162 · sha256:e9db64af8d7d09274122d2affeab6e35d26c8bfe24d4b02a8340f595310ac7a2
[^origins]: src · explorer/src/explorer.ts#L44-L46 · sha256:f39272b1dc949f78750cbe79693cad92d7896ed792a93e0abf03229952b18545
[^entity]: src · explorer/src/explorer.ts#L777-L781 · sha256:fa6f3232ffa57aa27dc7aec3a2025cad91c4c639890206af00968081f391ee91
[^defaults]: src · explorer/src/explorer.ts#L37-L43 · sha256:f463bcd39b961bf1069df352c7eb79dff27f25f232e06ebfc1ca75c1edb096a4
[^g-linkcount]: graph · explorer/src/explorer.ts::linkCount
[^linkcount]: src · explorer/src/explorer.ts#L441-L446 · sha256:ff476f90ad4ad909c4854d9f0061c67a7966b0562d2eb893bb367cdba53f7419
[^deeplink]: src · explorer/src/explorer.ts#L890-L901 · sha256:7d28286a8d40a04434fc473b20e64170f6b03cc9bec0abf53bdfd57e1f9a2c0f

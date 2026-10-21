---
type: application-bundle/domain-map
title: Domain map — notes and governance vocabulary
description: The vocabulary of notes, sources and governance in Knowledge Foundation core, what each term
  means and where it lives in code.
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
  domain: note-governance
  bootstrap: true
---
# Domain map — notes and governance vocabulary

## Terms

| Term | Meaning | Where it lives |
|---|---|---|
| Bundle | the OKF v0.2 folder `wiki/`, named once in `wiki.config.yaml` | `wiki.config.yaml`, `Config.bundle` [^cfg-bundle] [^g-cfg-bundle] |
| Theme | a top-level bundle folder; the librarian routes by the theme descriptions, and validation refuses any other top-level folder | `wiki.config.yaml` `themes`, `validate.validate` [^cfg-themes] [^val-folders] |
| Note | an OKF document of `type: Note` outside `raw/`, with governance fields added by the curator | `schemas/page.schema.json`, `okf.notes` [^page-req] [^g-notes] |
| Raw copy | an OKF `Source` under `raw/` holding the original text (own work in full, third-party as notes and excerpt) | `schemas/source.schema.json`, `okf.raws` [^src-req] [^g-raws] |
| Capture | an `inbox/` file with the four required fields that the librarian files and then moves to `inbox/done/` | `ingest.read_capture`, `ingest.ingest` [^ing-capture] [^ing-ingest] |
| `origin_kind` | own essay, post, talk or repo, or third-party note or excerpt; third-party captures over 2,500 characters are refused | `tools/librarian/ingest.py` [^ing-capture] |
| `kind` | the page type (Concept, Pattern, Principle, Essay, Tool, Standard and others), independent of the folder | `wiki.config.yaml` `kinds`, page schema [^cfg-kinds] |
| `status` | lifecycle `draft`, `stable` or `deprecated`; `normalize` sets `draft`, an owner stamp promotes it to `stable` | page schema, `governance.stamp` [^page-status] [^gov-stamp] |
| `stale_after` | the re-verification date, defaulted from `generated.at` plus the months set for the note's kind | `governance.normalize`, `wiki.config.yaml` [^gov-normalize] [^cfg-stale] |
| `verified` | one or more `{by, at}` events, written only by the approve workflow on the owner's approval | `governance.stamp`, `approve.yml` [^gov-stamp] [^approve-stamp] |
| Trust tier | `unverified`, `machine-confirmed` or `human-reviewed`, derived from `verified` and never stored | `okf.trust_tier` [^okf-trust] [^g-trust] |
| Owner actor | the `human:` actor string recorded in stamps and as the default note owner | `wiki.config.yaml` `author.actor`, `Config.owner_actor` [^cfg-author] |
| Date rule | raw copies need `published_at`, nothing is dated in the future, and a note may not cite a source published after it was written | `dates.check_dates` [^dates-doc] [^g-dates] |
| Confidential terms | the private blocklist scanned over all public paths; hits are reported by list position only | `blocklist.scan`, `kb check` [^bl-scan] [^kb-blocklist] |
| CROW mode | the librarian mode in which a typed classifier makes filing and retrieval decisions and Claude only writes; the cloud fallback uses classic mode | `docs/local-classifier.md`, `ingest.yml` [^crow] [^ingest-classic] |

*Assessment:* Governance terms map one-to-one onto small functions (`normalize`, `stamp`, `check_dates`, `scan`), so each business rule has a single place to read and test.[^gov-normalize] [^gov-stamp] [^dates-doc] [^bl-scan]

[^cfg-bundle]: src · wiki.config.yaml#L14-L14 · sha256:03d52cb10e7dd0aaa3aff25c535f958488f3a3a792cf23c4aeeef485a5aebd2e
[^g-cfg-bundle]: graph · tools/kb/config.py::Config.bundle
[^cfg-themes]: src · wiki.config.yaml#L16-L24 · sha256:5650b7ae3a7c4afa4f0c7478db708a0fe8f95a262983a6f489b25c600855ae27
[^val-folders]: src · tools/kb/validate.py#L57-L61 · sha256:6b13d8432289e977c2f22fa4c90b781f297a4ac26b74984f87f3cab10875ceef
[^page-req]: src · schemas/page.schema.json#L1-L25 · sha256:1cd949ff4ef230be0874900059238d9737ac309f933d95bde18bb4f1a937da00
[^g-notes]: graph · tools/kb/okf.py::notes
[^src-req]: src · schemas/source.schema.json#L1-L20 · sha256:3418ec6905ac15a93a3446445d9c25f33b0d217c51ac86b476529902f7d6f053
[^g-raws]: graph · tools/kb/okf.py::raws
[^ing-capture]: src · tools/librarian/ingest.py#L37-L57 · sha256:11675a55ea62cd084036ad342e641811a0dcf6c8155f27a561daca28e334d040
[^ing-ingest]: src · tools/librarian/ingest.py#L93-L105 · sha256:ba61aef0aa797b6977e03681adbc3ffaf45eed458b90f8db152c376bcf893826
[^cfg-kinds]: src · wiki.config.yaml#L36-L37 · sha256:3bbc4da734331e477ca5a8b4472d7b31bb72aba3338af6ddc48c0a10865e7ab2
[^page-status]: src · schemas/page.schema.json#L122-L130 · sha256:f390996b90ff42c54497980df90aa56ca9fa9a67ea02b98a3b403baea91d87a2
[^gov-stamp]: src · tools/kb/governance.py#L51-L71 · sha256:c1e5a7d83bbc979d65689e62da7f159c7c88a51cc287446bdcf4bc76887c5f2f
[^gov-normalize]: src · tools/kb/governance.py#L28-L48 · sha256:ec65a0c9bfad6d78a2e5c8536940ddbb6ada2a6e4618a6b74527814db3f902c2
[^cfg-stale]: src · wiki.config.yaml#L39-L50 · sha256:693e75063600497f907320b470122da342ef0579ce21980027b7b94c74ce3ca0
[^approve-stamp]: src · .github/workflows/approve.yml#L44-L52 · sha256:ce3c196c097770b21efd910a182a1f45cacc5e74bb75033f279cbb65213cb75a
[^okf-trust]: src · tools/kb/okf.py#L133-L140 · sha256:5290c69185ba5573b4feb56a9d123b627e703063c5c59d4ce32520e2ba50375f
[^g-trust]: graph · tools/kb/okf.py::trust_tier
[^cfg-author]: src · wiki.config.yaml#L6-L8 · sha256:9bb6f25141c06874b21986f0c1c5819a2c948d2472bb41a89bc45034221d9506
[^dates-doc]: src · tools/kb/dates.py#L1-L4 · sha256:029975a5bf3f12c57b5e7d77c4bc4847375ef55246a10e54847d9617a6def142
[^g-dates]: graph · tools/kb/dates.py::check_dates
[^bl-scan]: src · tools/kb/blocklist.py#L31-L46 · sha256:32a1beaf8435d05bfc98e279eddc1ccd238a4b17008f6c299f267d625616f968
[^kb-blocklist]: src · tools/kb/__main__.py#L63-L71 · sha256:3bb29dfe2d0479c2d22b894a6ca5ba91933ee28cdbd44d93ae5716f5c477bebe
[^crow]: src · docs/local-classifier.md#L3-L4 · sha256:7c63db2714c846197e4c834f7ed304ad475c5b3675c9354b6ab5a20833732672
[^ingest-classic]: src · .github/workflows/ingest.yml#L1-L5 · sha256:2de0611ad9b28817aa335f1d70fc0eba75a5e1e588026e5b3e2fbf3f1bd17f3b

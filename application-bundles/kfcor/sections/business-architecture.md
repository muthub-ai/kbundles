---
type: application-bundle/business-architecture
title: Business architecture — Knowledge Foundation core
description: The capabilities Knowledge Foundation core provides, the actors involved, the capture-to-publication
  value stream and the business rules the repository enforces.
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
  section: business-architecture
  bootstrap: true
---
# Business architecture — Knowledge Foundation core

## Purpose

The repository serves two goals at once: it is the owner's public working knowledge, and it is a working reference for the claim that AI may write into a system of record only when every claim carries its source, every change is reviewed, and machine output stays apart from what a person stood behind.[^readme-purpose]

## Actors

| Actor | Role |
|---|---|
| Librarian (LLM-Wiki-V2) | files sources into the bundle; a local classifier decides placement and Claude writes the note [^agents-roles] [^adr013] |
| Curator agent (Claude Code) | tidies, links and checks the branch, then opens the pull request with a claims table; never merges or publishes [^agents-roles] [^skill-curate] |
| Owner | the only reviewer whose approval stamps `verified` and the only party who merges [^adr006] [^adr004] |
| GitHub App | authors bot pull requests and stamp commits so that required checks run on them [^adr005] |

## Value stream

A note moves through capture (a capture note with `title`, `published_at`, `origin_kind` and `license_note` in `inbox/`), filing by the librarian, curation into a pull request, CI checks, owner approval that stamps `verified`, a merge that cuts a release and rebuilds the site, and a weekly pass that lints and lists stale notes.[^readme-steps]

## Business rules

Only public knowledge may enter: the curator's standing orders forbid employer-internal names and figures, and every note must carry `classification: public`.[^agents-rules] [^val-public]

Every claim needs a dated source, dates are never invented, and the rule is enforced in code: no note may cite a raw copy published after the note was written.[^agents-rules] [^dates-rule]

Third-party material is limited to notes and a short excerpt of at most 2,500 characters, while the owner's own material may be kept in full.[^adr008] [^ing-limit]

Notes are deprecated, never deleted, with replacements recorded as a `supersedes` relation, and each note becomes due for re-verification after a period set by its kind, from three months for tools and standards to twelve for principles, decisions and essays.[^agents-rules] [^cfg-stale]

Questions the wiki should answer are kept in `evals/questions.yaml` with the note each should cite, and the offline check fails when an expected note is missing.[^evals-check]

*Assessment:* Trust is modelled as a fact about review (who approved, when) rather than as a score, which makes the owner's attention the scarce resource the whole process is shaped around.[^adr006] [^readme-steps]

[^readme-purpose]: src · README.md#L13-L17 · sha256:56749f43b94534073d07ef5ad0525a64060e0d1872c7a823aa9202df31e7f4f7
[^agents-roles]: src · AGENTS.md#L1-L4 · sha256:bdebd304005ddfccf845c4aec96b27ec7051dfdbdf41d0aee1c65a07f550d7f4
[^adr013]: src · decisions/013-a-local-classifier-decides-the-claude-api-writes.md#L9-L11 · sha256:f35d6dd940e27493c76a1875c87fb413ffb92ec7254ffe7718173a2017a29303
[^skill-curate]: src · skills/curate.md#L1-L14 · sha256:9573b8a189b332156b43b111a717422707b87427b9016134e832a4e4061a8818
[^adr006]: src · decisions/006-verification-is-the-owner's-approval.md#L9-L15 · sha256:8323250322bff1abb57caf0575134219dc0e0139e8b7e74708b4f2d8c5428005
[^adr004]: src · decisions/004-no-automated-commits-to-main-each-merge-publishes-a-release.md#L9-L15 · sha256:1e234b7d88e70e021ada3750c0eb39533ec0c209fdeeda76a02f3daf31655db2
[^adr005]: src · decisions/005-a-github-app-authors-automated-pull-requests-and-stamp-commi.md#L5-L15 · sha256:7b7099d813d33176cac8f4c7266c1222bb91e338b09fbaf357ac1377918baca9
[^readme-steps]: src · README.md#L81-L91 · sha256:6b6a1b2498b75eb3bd7319a41f4e031c55d5e1ba893a473d8ec00cae2f9bddd5
[^agents-rules]: src · AGENTS.md#L6-L20 · sha256:3db1b19bc3ecea83b9a8ac8aed9a91cc0add6a0d752ebf01241803fe138fdbae
[^val-public]: src · tools/kb/validate.py#L74-L75 · sha256:102a283fd4d597e9ea9df2e27dd6a9537057a4715027e38f9bdbd6174a67bf9b
[^dates-rule]: src · tools/kb/dates.py#L52-L57 · sha256:72af19129d4588cf5a923080c306d4b8e392d4aefb67a37d0956e1259222b8e2
[^adr008]: src · decisions/008-own-material-in-full-third-party-material-as-notes-and-excer.md#L9-L15 · sha256:d982c28cb71b3cad32384ee40e68bc0cad97d3db24765532b56f78e02b8e0859
[^ing-limit]: src · tools/librarian/ingest.py#L37-L57 · sha256:11675a55ea62cd084036ad342e641811a0dcf6c8155f27a561daca28e334d040
[^cfg-stale]: src · wiki.config.yaml#L39-L50 · sha256:693e75063600497f907320b470122da342ef0579ce21980027b7b94c74ce3ca0
[^evals-check]: src · tools/kb/evals.py#L22-L32 · sha256:c8c322d66be8bca24e83f3861604cf3e985ccb4bf02be6f20b0fcbfce1387b8c

---
type: application-bundle/executive-summary
title: Executive summary — Knowledge Foundation core
description: What the Knowledge Foundation core repository is, who works in it, and the shape of its governed
  knowledge pipeline on one screen.
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
  section: executive-summary
  bootstrap: true
---
# Executive summary — Knowledge Foundation core

## What it is

Knowledge Foundation core is a public Git repository that holds the owner's working knowledge on governed AI, context engineering and AI-native delivery as an Open Knowledge Format (OKF) v0.2 bundle in `wiki/`, written by an LLM librarian and approved by a human before it is published as a graph; Git is the system of record, every change arrives by pull request and no database sits behind it.[^readme-what] [^adr001]

## Shape in one screen

The bundle holds 51 notes across five themes, each with dated sources and a review state; the published graph combines a deterministic backbone with a labelled semantic layer; governance means no bot commits to `main`, an owner approval that stamps `verified`, a confidential-terms scan on every change and 16 decision records; quality gates are 64 unit tests, an end-to-end flow test, JSON Schema checks, date rules and a Semantica canary; and every merge produces a versioned release (`bundle.tgz`, `graph.json`, `report.md`) that rebuilds wiki.muthub.org.[^readme-shape]

A note travels through seven steps: capture in `inbox/`, filing by the librarian, curation by Claude Code, CI checks, owner approval through `approve.yml`, release through `publish.yml`, and a weekly freshness pass in `weekly.yml`.[^readme-flow]

The governance tooling is a single Python command line, `python -m kb`, whose `main` dispatches `check`, `validate`, `dates`, `blocklist`, `normalize`, `stamp`, `propose`, `graph`, `stale` and `evals`.[^kb-main] [^g-main]

## Why it matters

The site repository consumes only release assets and never imports code from this repository, and the essays site reads `graph.json` counts with a fallback, so dependency runs in one direction only.[^readme-repos]

*Assessment:* The design keeps machine writing, machine checking and human attestation in separate steps, and the only path to `main` passes through an owner's review; this is the property the bundle is built to demonstrate.[^readme-flow] [^readme-shape]

*Assessment:* Because the bundle is plain Markdown with YAML frontmatter in Git and the site depends only on release assets, either the writing engine or the site could be replaced without migrating the knowledge.[^adr001] [^readme-repos]

[^readme-what]: src · README.md#L13-L17 · sha256:56749f43b94534073d07ef5ad0525a64060e0d1872c7a823aa9202df31e7f4f7
[^adr001]: src · decisions/001-a-git-repository-holding-an-okf-v02-bundle-is-the-system-of.md#L9-L15 · sha256:5e7892ed47064c3257f56eff86afbf3f5444cc58c3f396bc28290b13e3cc2da1
[^readme-shape]: src · README.md#L19-L25 · sha256:adbcb5db6a0615201009f87712191d8a248fac368b3a0eba533f88c4538010d9
[^readme-flow]: src · README.md#L81-L91 · sha256:6b6a1b2498b75eb3bd7319a41f4e031c55d5e1ba893a473d8ec00cae2f9bddd5
[^kb-main]: src · tools/kb/__main__.py#L32-L58 · sha256:179500f67d6902b22acc11c8c90b947011cf5586654c8bce8f420e725836513d
[^g-main]: graph · tools/kb/__main__.py::main
[^readme-repos]: src · README.md#L53-L64 · sha256:d10579b400a708f0240b5b8413d5256b51c4329c7ae6f61fead17081f8365e56

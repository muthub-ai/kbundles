---
type: application-bundle/operating-model
title: Operating model — Knowledge Foundation core
description: An illustrative, fabricated operating model for Knowledge Foundation core (teams, ownership,
  ceremonies and decision rights); it is not drawn from the source repository.
generated:
  by: process:building-application-bundles@0.1.0
  at: '2026-10-20T19:30:00-05:00'
sources:
- id: fixture
  kind: synthetic-fixture
  path: .github/kf/config.yml
x_kf:
  schema: kf-application-bundle/1
  appid: kfcor
  bundle_kind: application
  section: operating-model
  synthetic: true
  bootstrap: true
---
# Operating model — Knowledge Foundation core

> **Illustrative only.** In the source repository a single owner reviews and merges every change. The teams, cadences
> and decision rights below are fabricated for this prototype; only the team slugs and time zones come from the
> registry in `.github/kf/config.yml`.

## Teams

| Team | Time zone | Mission | Owned components |
|---|---|---|---|
| `fabric-core` | America/Chicago | Keep the bundle's rules, schemas and release path correct | `tools/kb/` (validate, dates, blocklist, governance, okf, config), `schemas/`, `ontology/edge-types.yaml`, `approve.yml`, `publish.yml`, `tests.yml` required jobs, `decisions/` |
| `librarian-ops` | America/New_York | Turn captures into well-filed, well-sourced notes | `tools/librarian/` (ingest, seed), `inbox/`, `prompts/`, `skills/`, `AGENTS.md`, `ingest.yml`, `weekly.yml`, `evals/questions.yaml`, the local classifier setup |
| `graph-platform` | Asia/Kolkata | Build and evolve the published graph and its semantic layer | `tools/kb/graph.py`, `tools/kb/extractors/` (Semantica adapter, resolution, relations), `schemas/graph.schema.json`, the `semantica-canary` job, `kb propose` |

## Ceremonies

| Ceremony | Cadence | fabric-core | librarian-ops | graph-platform |
|---|---|---|---|---|
| Standup | daily, 15 minutes | 09:00 America/Chicago | 09:30 America/New_York | 10:00 Asia/Kolkata |
| Sprint planning | first day of each two-week sprint | yes | yes | yes |
| Backlog refinement | mid-sprint, once per sprint | yes | yes | yes |
| Retrospective | last day of each two-week sprint | yes | yes | yes |

Cross-team touchpoints in this illustration: `librarian-ops` brings the weekly lint issue to its refinement session;
`graph-platform` reviews the canary annotations from the past sprint at its retrospective; `fabric-core` hosts a short
joint review whenever a new decision record is proposed.

## Decision rights for bundle updates

| Decision | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Regenerate this application bundle at a new commit | `fabric-core` engineer on rotation | product owner (`fabric-core`) | `graph-platform` tech lead | `librarian-ops` |
| Approve a bundle update pull request | product owner of the team owning the changed section | the repository owner role | the other two tech leads | all three teams |
| Change a governance rule (schema, date rule, blocklist behaviour) | `fabric-core` | the repository owner role | `librarian-ops`, `graph-platform` | all three teams |
| Promote machine-suggested relations into notes | `graph-platform` | the repository owner role | `librarian-ops` curator lead | `fabric-core` |
| Change house style or curator standing orders | `librarian-ops` | the repository owner role | `fabric-core` | `graph-platform` |

## Ceremony knowledge flow

Notes from each ceremony are captured as Markdown files under
`knowledge-sources/agile-ceremonies/<ceremony>/<team>/`, for example
`knowledge-sources/agile-ceremonies/retrospective/graph-platform/`. Each file carries the ceremony date, the team slug
and the decisions taken. A scheduled job reads new files, proposes changes to this operating model or to the affected
section, and opens a pull request that follows the decision-rights table above; nothing from a ceremony reaches the
bundle without that review.

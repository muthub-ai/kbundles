---
type: application-bundle/operating-model
title: Operating model — C4 skills
description: An illustrative, fabricated operating model for C4 skills — teams, ownership, ceremony cadence
  and decision rights for bundle updates.
generated:
  by: process:building-application-bundles@0.1.0
  at: '2026-10-20T19:30:00-05:00'
sources:
- id: fixture
  kind: synthetic-fixture
  path: .github/kf/config.yml
x_kf:
  schema: kf-application-bundle/1
  appid: cfskl
  bundle_kind: application
  section: operating-model
  synthetic: true
  bootstrap: true
---
# Operating model — C4 skills

> This operating model is fabricated for the Knowledge Foundation prototype. The teams are the slugs registered for `cfskl` in `.github/kf/config.yml`; no real people are described, and roles stand in for individuals.

## Teams and ownership

| Team slug | Time zone | Mission | Owned components |
|---|---|---|---|
| `skill-authoring` | America/Chicago | Keep the `c4designer` skill accurate, the shared skill format consistent, and the package installable and tested | `c4designer/` (router, mode files, `mermaid-c4-syntax.md`, `level-template.md`, `review-checklist.md`, `supporting-diagrams.md`, examples), `registry.json`, `install.sh`, `Makefile`, `tests/test-skill-format.sh`, `tests/validate-c4-diagram.sh`, sandbox `tests/example-codebase/`, `.github/workflows/test.yml` |
| `adr-practice` | Asia/Singapore | Own the ADR skill and its template, and keep its validator aligned with the template | `adr-scribe/` (router, mode files, `adr-template.md`, `review-checklist.md`, example ADR), `tests/validate-adr.sh`, ADR behavioral fixtures, ADR pages of the `docs/` site |

Shared: the Docusaurus `docs/` site and `.github/workflows/docs.yml` are co-owned, with `skill-authoring` as the default reviewer.

Roles within each team: a product owner (prioritises skill modes and agent support), a skill maintainer (edits instructions and templates), and a test maintainer (owns validators and fixtures).

## Ceremony cadence

| Ceremony | `skill-authoring` (America/Chicago) | `adr-practice` (Asia/Singapore) |
|---|---|---|
| Standup | Daily, 09:15 local, 15 minutes | Daily, 09:30 local, 15 minutes |
| Sprint planning | First Monday of each two-week sprint, 60 minutes | First Monday of each two-week sprint, 60 minutes |
| Backlog refinement | Mid-sprint Wednesday, 45 minutes | Mid-sprint Wednesday, 45 minutes |
| Retro | Last Friday of each two-week sprint, 45 minutes | Last Friday of each two-week sprint, 45 minutes |

The two time zones overlap little, so cross-team items (for example the `c4-model` dependency declared by `adr-scribe`, or cross-skill prompts between `mode-update.md` and the ADR modes) are raised asynchronously in refinement notes and resolved at the next planning of the owning team.

## Decision rights for bundle updates

| Decision | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Update of sections describing `c4designer`, install or tests | `skill-authoring` skill maintainer | `skill-authoring` product owner | `adr-practice` | Application owner `@muthub-ai` |
| Update of sections describing `adr-scribe` or ADR validation | `adr-practice` skill maintainer | `adr-practice` product owner | `skill-authoring` | Application owner `@muthub-ai` |
| Re-pin of the bundle to a new commit | `skill-authoring` test maintainer | Application owner `@muthub-ai` | both teams | both teams |
| Operating-model changes | either product owner | Application owner `@muthub-ai` | both teams | both teams |

A bundle update lands only through a pull request approved by the registered owner; agent-authored content never self-approves.

## How ceremony knowledge flows into the bundle

Notes from each ceremony are captured under `knowledge-sources/agile-ceremonies/<ceremony>/<team>/`, for example `knowledge-sources/agile-ceremonies/retro/adr-practice/` or `knowledge-sources/agile-ceremonies/sprint-planning/skill-authoring/`.

Decisions recorded there that change a skill's structure, a template or a validator are carried into the relevant section of this bundle on the next re-pin, with citations to the source commit that implements them.

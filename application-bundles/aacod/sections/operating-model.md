---
type: application-bundle/operating-model
title: Operating model — Architecture as Code
description: Illustrative (fabricated) operating model for Architecture as Code — teams, ownership, ceremonies,
  cadence and decision rights for bundle updates.
generated:
  by: process:building-application-bundles@0.1.0
  at: '2026-10-20T19:30:00-05:00'
sources:
- id: fixture
  kind: synthetic-fixture
  path: .github/kf/config.yml
x_kf:
  schema: kf-application-bundle/1
  appid: aacod
  bundle_kind: application
  section: operating-model
  synthetic: true
  bootstrap: true
---
# Operating model — Architecture as Code

> This operating model is **illustrative and fabricated** for the Knowledge Foundation prototype. The teams are the slugs registered for `aacod` in `.github/kf/config.yml`. No real people are described; roles stand in for individuals.

## Teams and ownership

| Team slug | Time zone | Mission | Owned components |
|---|---|---|---|
| `model-authoring` | America/Chicago | Keep the C4 models and the editing experience accurate and usable | `model/`, `schema/application-schema.json`, Next.js app (`src/app`, `src/components`, `src/store`, `src/lib/parser`, `src/lib/layout`, `src/lib/export`), `scripts/validate-models.ts`, `scripts/build-diagrams.ts`, `scripts/build-docs.ts`, `aac` CLI (`cli/`) |
| `policy-governance` | Europe/Berlin | Own the rules, standards and exception process | `standards/`, `waivers/`, `patterns/`, `schema/standards.json`, `schema/waivers.json`, `scripts/lint-architecture.ts`, `packages/policies/` (Rego rules and bundle), scorecard logic in `src/lib/metrics/compute-metrics.ts`, `.github/workflows/aac-pipeline.yml` |
| `mcp-integrations` | Australia/Sydney | Make architecture governance usable by AI agents | `mcp-server/` (resources, `validate_architecture`, `lint_compliance`, `scaffold_waiver`, prompts), `.vscode/mcp.json`, `.github/workflows/release-cli.yml` coordination for agent-facing packages |

Shared seams: `policy-governance` and `mcp-integrations` co-own the duplicated compliance rules (pipeline linter and MCP `lint_compliance`). `model-authoring` and `policy-governance` co-own the schema files that the CLI fetches from `main`.

## Ceremonies and cadence

All teams run two-week sprints that start on the same Monday, so planning across three time zones uses one shared calendar.

| Ceremony | Cadence | model-authoring | policy-governance | mcp-integrations |
|---|---|---|---|---|
| Standup | Daily, 15 min | 09:30 America/Chicago | 09:30 Europe/Berlin | 09:30 Australia/Sydney |
| Sprint planning | Day 1 of each two-week sprint, 90 min | Monday 10:00 local | Monday 10:00 local | Monday 10:00 local |
| Backlog refinement | Once per sprint, mid-sprint Wednesday, 60 min | Wednesday 14:00 local | Wednesday 14:00 local | Wednesday 14:00 local |
| Retro | Last day of each sprint, 60 min | Friday 15:00 local | Friday 15:00 local | Friday 15:00 local |

A monthly cross-team governance sync, scheduled in the Europe/Berlin morning, reviews waivers near expiry and any drift between the pipeline linter and the MCP tool. Its notes are filed under the `policy-governance` backlog-refinement folder.

## Decision rights for bundle updates

| Decision | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Update a section of this application bundle | Owning team's tech lead | Repository code owner (approver of record) | Other two teams | All `aacod` teams |
| Change governance content (standards, waivers, Rego) reflected in the bundle | `policy-governance` | Repository code owner | `model-authoring`, `mcp-integrations` | Bundle readers |
| Change agent-facing behavior described in the bundle | `mcp-integrations` | Repository code owner | `policy-governance` | `model-authoring` |
| Re-pin the bundle to a new source commit | Owning team for the changed area | Repository code owner | Other two teams | All `aacod` teams |

Only an approving review by the code owner on the pull request accepts a bundle change. Machine-generated drafts are never self-approving.

## Ceremony knowledge flow

Each ceremony's notes are captured as markdown under `knowledge-sources/agile-ceremonies/<ceremony>/<team>/`, for example `knowledge-sources/agile-ceremonies/retro/policy-governance/` or `knowledge-sources/agile-ceremonies/standup/mcp-integrations/`. The ceremony folder names are fixed (`standup`, `sprint-planning`, `backlog-refinement`, `retro`), and the team folder is one of this app's three slugs.

Decisions recorded in planning or refinement that change architecture, such as adding an OPA evaluation step or fixing the active-waiver filter, are raised as pull requests against the source repository. This bundle is then re-pinned through the decision process above.

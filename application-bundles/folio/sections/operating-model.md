---
type: application-bundle/operating-model
title: Operating model — Portfolio website (muthub.org)
description: Illustrative, fabricated operating model for the muthub.org site — teams, ownership, ceremony
  cadence and decision rights for this prototype.
generated:
  by: process:building-application-bundles@0.1.0
  at: '2026-10-20T19:30:00-05:00'
sources:
- id: fixture
  kind: synthetic-fixture
  path: .github/kf/config.yml
x_kf:
  schema: kf-application-bundle/1
  appid: folio
  bundle_kind: application
  section: operating-model
  synthetic: true
  bootstrap: true
---
# Operating model — Portfolio website (muthub.org)

> **Illustrative.** The site is maintained by its owner alone. The two teams, their ceremonies and the RACI below are fabricated for the Knowledge Foundation prototype so that ceremony knowledge has somewhere to land. Team slugs and time zones are the ones registered for `folio` in `.github/kf/config.yml`.

## Teams

| Team slug | Time zone | Mission | Owned components |
|---|---|---|---|
| `web-experience` | America/Chicago | Keep the site fast, accessible, secure and readable by agents | `app/` pages and route handlers, `lib/markdown.ts`, `lib/search.ts`, `lib/search-score.ts`, `lib/seo.ts`, `components/` (header, footer, search, assessment, Knowledge Foundation band, JSON-LD), `next.config.mjs` headers and redirects, `.github/workflows/ci.yml`, Vercel project |
| `content-ops` | America/Los_Angeles | Publish essays, notes, initiatives and playbooks that pass the integrity and confidentiality rules | `content/*.ts`, `content/tags.ts`, `playwright/fixtures/source-dates.ts`, `playwright/tests/content.spec.ts`, `scripts/check-public-content.mjs` and the private term list, `scripts/og/make-images.py`, `.github/workflows/weekly-links.yml` triage |

Roles inside each team (illustrative): a product owner, a tech lead, and two to three engineers or editors. No individual is named.

## Ceremony cadence

Both teams run two-week sprints that start on Monday.

| Ceremony | `web-experience` (America/Chicago) | `content-ops` (America/Los_Angeles) |
|---|---|---|
| Standup | Daily, 09:15, 15 minutes | Daily, 09:30, 15 minutes |
| Sprint planning | Sprint day 1, 10:00, 90 minutes | Sprint day 1, 11:00, 60 minutes |
| Backlog refinement | Sprint day 6, 14:00, 60 minutes | Sprint day 6, 13:00, 60 minutes |
| Retro | Sprint day 10, 15:00, 45 minutes | Sprint day 10, 14:00, 45 minutes |

Cross-team touchpoints (illustrative): `content-ops` raises any new content block type, figure or page section in `web-experience` refinement, because a new `Block` variant needs a renderer in `components/rich-text.tsx`, in `lib/content.ts::blocksToMarkdown` and in the search index. The Monday weekly-links issue is triaged in the `content-ops` standup.

## Decision rights

| Decision | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Publish or update an essay, note, initiative or playbook | `content-ops` editor | `content-ops` product owner | `web-experience` tech lead (new block types only) | both teams |
| Add a private blocklist term or a source-date fixture row | `content-ops` editor | `content-ops` product owner | none | `web-experience` |
| Change security headers, CSP, redirects or CI | `web-experience` engineer | `web-experience` tech lead | `content-ops` product owner | both teams |
| Approve a bundle update for `folio` (sections, code graph, domain maps) | team whose components changed | the `folio` owner registered in `.github/kf/config.yml` | the other team's tech lead | both teams |
| Accept ceremony knowledge into the bundle | ceremony facilitator | team product owner | the other team | the `folio` owner |

Bundle updates follow the gate: the approver must be an owner registered for `folio`, and acceptance means the change is merged to `main` after that approval.

## How ceremony knowledge flows into the bundle

1. Each ceremony produces a short note, filed under `knowledge-sources/agile-ceremonies/<ceremony>/<team>/` in this bundle, for example `knowledge-sources/agile-ceremonies/standup/web-experience/` or `knowledge-sources/agile-ceremonies/retro/content-ops/`.
2. The note lands through a ceremony pull request that touches only that ceremony directory, its team log and the manifest entry.
3. Decisions that change how the site works (for example a new header, a new content rule) are proposed as a decision record in the application repository's `docs/decisions/`, and then reflected here through a separate bundle update with fresh citations.
4. Retro actions that affect publishing rules feed `content-ops` refinement; those affecting the build or headers feed `web-experience` refinement.

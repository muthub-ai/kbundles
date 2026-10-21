---
type: application-bundle/operating-model
title: Operating model — Knowledge Foundation site
description: An illustrative, fabricated operating model for the site's two teams, their ownership, ceremonies
  and bundle-update decision rights.
generated:
  by: process:building-application-bundles@0.1.0
  at: '2026-10-20T19:30:00-05:00'
sources:
- id: fixture
  kind: synthetic-fixture
  path: .github/kf/config.yml
x_kf:
  schema: kf-application-bundle/1
  appid: kfsit
  bundle_kind: application
  section: operating-model
  synthetic: true
  bootstrap: true
---
# Operating model — Knowledge Foundation site

> Illustrative only. The teams, ceremonies and decision rights below are fabricated for this prototype; only the team slugs and time zones come from the trust-root registry.

## Teams

| Team slug | Time zone | Mission | Owned components |
|---|---|---|---|
| `site-build` | America/Chicago | Keep the release-to-site pipeline reproducible and the deploy green | `kfsite/` (`bundle.py`, `stage.py`, `post.py`), `scripts/build.sh`, `scripts/vercel_build.sh`, `scripts/fetch_release.py`, `scripts/make_quartz_config.py`, `quartz.ref`, `vercel.json`, `.github/workflows/ci.yml` |
| `explorer-ux` | Europe/London | Make the graph explorer legible, accessible and honest about machine-found structure | `explorer/src/explorer.ts`, `explorer/index.html`, `explorer/explorer.css`, `explorer/theme.js`, committed `explorer/dist/explorer.js`, `tests/e2e/explorer.spec.ts` |

Shared surfaces: `tests/serve.py` and the CSP headers in `vercel.json` are co-owned, because a CSP change is both a hosting and an explorer concern.

## Ceremonies

| Ceremony | `site-build` | `explorer-ux` |
|---|---|---|
| Standup | daily, 09:15 America/Chicago, 15 minutes | daily, 09:30 Europe/London, 15 minutes |
| Sprint planning | first Monday of each two-week sprint, 60 minutes | first Monday of each two-week sprint, 60 minutes |
| Backlog refinement | Wednesday of week one, 45 minutes | Wednesday of week one, 45 minutes |
| Retro | last Friday of the sprint, 45 minutes | last Friday of the sprint, 45 minutes |

The two teams overlap for roughly three working hours a day; cross-team topics (CSP changes, new `graph.json` node or edge kinds) go to a shared 30-minute slot after `site-build` standup on planning day.

## Decision rights for bundle updates

| Decision | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Regenerate this application bundle after a site release | `site-build` engineer on rotation | `site-build` product owner | `explorer-ux` tech lead | both teams |
| Change explorer-related sections or the domain map | `explorer-ux` engineer | `explorer-ux` product owner | `site-build` tech lead | both teams |
| Approve and merge a bundle-update pull request | registered code owner | registered code owner | owning team's tech lead | both teams |
| Change the operating model itself | both product owners | registered code owner | both teams | both teams |

## Ceremony knowledge flow

Notes from each ceremony are filed as ceremony records under `knowledge-sources/agile-ceremonies/<ceremony>/<team>/`, for example `knowledge-sources/agile-ceremonies/retro/explorer-ux/` or `knowledge-sources/agile-ceremonies/sprint-planning/site-build/`.

Decisions taken in a ceremony that change how the site works are also written up as a decision record in the site repository's `docs/decisions/`, and the next bundle regeneration picks them up through the normal citation process.

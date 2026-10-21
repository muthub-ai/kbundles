---
type: application-bundle/code-graph-view
title: Dependencies and hotspots — folio
description: External dependencies, entry points and fan-in hotspots derived from the code graph.
generated:
  by: process:kfbundle.views@0.1.0
  at: '2026-10-20T19:30:00-05:00'
sources:
- id: g1
  kind: code-graph
  path: code-graph/code-graph.jsonl
  sha256: c30e501c460d37c9779b2d401e1e376a2e5c0290377d4b5c5d3a5ba92fbfe70d
x_kf:
  schema: kf-application-bundle/1
  appid: folio
  bundle_kind: application
  view: dependencies
  derived: true
---
# Dependencies and hotspots — folio

Derived from `code-graph/code-graph.jsonl` and `code-graph/metrics.json`. Hotspots are fan-in counts only (calls, renders, imports and links into a node); the bundle pins one commit, so there is no churn signal.

## External dependencies

| Package | Files that import or declare it |
|---|---:|
| `next` | 26 |
| `react` | 13 |
| `@playwright/test` | 5 |
| `next-themes` | 3 |
| `@vercel/analytics` | 2 |
| `@vercel/speed-insights` | 2 |
| `clsx` | 2 |
| `node:child_process` | 2 |
| `node:fs` | 2 |
| `node:path` | 2 |
| `tailwind-merge` | 2 |
| `tailwindcss` | 2 |
| `@hookform/resolvers` | 1 |
| `@radix-ui/react-accordion` | 1 |
| `@radix-ui/react-alert-dialog` | 1 |
| `@radix-ui/react-aspect-ratio` | 1 |
| `@radix-ui/react-avatar` | 1 |
| `@radix-ui/react-checkbox` | 1 |
| `@radix-ui/react-collapsible` | 1 |
| `@radix-ui/react-context-menu` | 1 |
| `@radix-ui/react-dialog` | 1 |
| `@radix-ui/react-dropdown-menu` | 1 |
| `@radix-ui/react-hover-card` | 1 |
| `@radix-ui/react-label` | 1 |
| `@radix-ui/react-menubar` | 1 |
| `@radix-ui/react-navigation-menu` | 1 |
| `@radix-ui/react-popover` | 1 |
| `@radix-ui/react-progress` | 1 |
| `@radix-ui/react-radio-group` | 1 |
| `@radix-ui/react-scroll-area` | 1 |

## Entry points

- `.github/ci-run.sh (cli-main)`
- `app/about/page.tsx (next-route)`
- `app/error.tsx (next-route)`
- `app/initiatives/[slug]/page.tsx (next-route)`
- `app/initiatives/page.tsx (next-route)`
- `app/layout.tsx (next-route)`
- `app/llms.txt/route.ts (next-route)`
- `app/md/[[...path]]/route.ts (next-route)`
- `app/not-found.tsx (next-route)`
- `app/now/page.tsx (next-route)`
- `app/page.tsx (next-route)`
- `app/playbooks/[slug]/assessment/page.tsx (next-route)`
- `app/playbooks/[slug]/page.tsx (next-route)`
- `app/playbooks/page.tsx (next-route)`
- `app/reach/page.tsx (next-route)`
- `app/rss.xml/route.ts (next-route)`
- `app/search-index.json/route.ts (next-route)`
- `app/search/page.tsx (next-route)`
- `app/writing/[slug]/page.tsx (next-route)`
- `app/writing/page.tsx (next-route)`
- `app/writing/tag/[tag]/page.tsx (next-route)`
- `app/writing/theme/[theme]/page.tsx (next-route)`
- `scripts/check-links.mjs (cli-main)`
- `scripts/check-public-content.mjs (cli-main)`
- `scripts/og/make-images.py (cli-main)`

## Fan-in hotspots

```mermaid
flowchart LR
  n0["(root)"]
  n1["app"]
  n2["app/about"]
  n3["app/initiatives"]
  n4["app/md"]
  n5["app/now"]
  n6["app/playbooks"]
  n7["app/rss.xml"]
  n8["app/writing"]
  n9["components"]
  n10(["content/playbooks.ts"])
  n11(["content/site.ts"])
  n12(["content/tags.ts"])
  n13["lib"]
  n14(["lib/content.ts"])
  n15(["dateLabel"])
  n16(["getEssays"])
  n17(["getInitiatives"])
  n18(["getNotes"])
  n19(["plain"])
  n20(["lib/seo.ts"])
  n21(["pageMetadata"])
  n22["playwright/tests"]
  n23(["token"])
  n6 -->|7| n10
  n1 -->|5| n10
  n13 -->|5| n10
  n22 -->|4| n10
  n4 -->|2| n10
  n1 -->|9| n11
  n9 -->|9| n11
  n13 -->|7| n11
  n8 -->|6| n11
  n4 -->|2| n11
  n13 -->|3| n12
  n1 -->|2| n12
  n4 -->|2| n12
  n8 -->|2| n12
  n22 -->|1| n12
  n1 -->|2| n14
  n3 -->|2| n14
  n8 -->|2| n14
  n13 -->|2| n14
  n4 -->|1| n14
  n13 -->|8| n15
  n8 -->|2| n15
  n9 -->|2| n15
  n1 -->|1| n15
  n13 -->|10| n16
  n1 -->|3| n16
  n8 -->|3| n16
  n4 -->|1| n16
  n7 -->|1| n16
  n13 -->|4| n17
  n3 -->|3| n17
  n1 -->|2| n17
  n4 -->|1| n17
  n13 -->|6| n18
  n1 -->|1| n18
  n4 -->|1| n18
  n7 -->|1| n18
  n8 -->|1| n18
  n13 -->|9| n19
  n8 -->|4| n20
  n6 -->|3| n20
  n1 -->|2| n20
  n3 -->|2| n20
  n2 -->|1| n20
  n8 -->|4| n21
  n6 -->|3| n21
  n3 -->|2| n21
  n1 -->|1| n21
  n2 -->|1| n21
  n0 -->|16| n23
```

| Node | Fan-in |
|---|---:|
| `content/site.ts` | 41 |
| `content/playbooks.ts` | 23 |
| `lib/content.ts::getEssays` | 19 |
| `tailwind.config.ts::token` | 16 |
| `lib/seo.ts` | 15 |
| `lib/seo.ts::pageMetadata` | 14 |
| `lib/content.ts::dateLabel` | 13 |
| `lib/content.ts` | 11 |
| `lib/content.ts::getNotes` | 11 |
| `content/tags.ts` | 10 |
| `lib/content.ts::getInitiatives` | 10 |
| `lib/search.ts::plain` | 9 |

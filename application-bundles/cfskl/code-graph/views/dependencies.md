---
type: application-bundle/code-graph-view
title: Dependencies and hotspots — cfskl
description: External dependencies, entry points and fan-in hotspots derived from the code graph.
generated:
  by: process:kfbundle.views@0.1.0
  at: '2026-10-20T19:30:00-05:00'
sources:
- id: g1
  kind: code-graph
  path: code-graph/code-graph.jsonl
  sha256: 2d93dd527a4f4487fb0c2f46ec9a8333874f5fab7fc841dda265894565e2e8db
x_kf:
  schema: kf-application-bundle/1
  appid: cfskl
  bundle_kind: application
  view: dependencies
  derived: true
---
# Dependencies and hotspots — cfskl

Derived from `code-graph/code-graph.jsonl` and `code-graph/metrics.json`. Hotspots are fan-in counts only (calls, renders, imports and links into a node); the bundle pins one commit, so there is no churn signal.

## External dependencies

| Package | Files that import or declare it |
|---|---:|
| `react` | 4 |
| `express` | 2 |
| `pg` | 2 |
| `prism-react-renderer` | 2 |
| `react-dom` | 2 |
| `` | 1 |
| `@docusaurus/ComponentCreator` | 1 |
| `@docusaurus/core` | 1 |
| `@docusaurus/module-type-aliases` | 1 |
| `@docusaurus/preset-classic` | 1 |
| `@docusaurus/theme-mermaid` | 1 |
| `@docusaurus/types` | 1 |
| `@generated/docusaurus-plugin-content-docs` | 1 |
| `@mdx-js/react` | 1 |
| `@site/docs` | 1 |
| `@theme/DocItem` | 1 |
| `@theme/DocRoot` | 1 |
| `@theme/DocVersionRoot` | 1 |
| `@theme/DocsRoot` | 1 |
| `clsx` | 1 |

## Entry points

- `install.sh (cli-main)`
- `tests/test-skill-format.sh (cli-main)`
- `tests/validate-adr.sh (cli-main)`
- `tests/validate-c4-diagram.sh (cli-main)`

## Fan-in hotspots

```mermaid
flowchart LR
  n0["adr-scribe"]
  n1(["adr-scribe/SKILL.md"])
  n2(["adr-scribe/adr-template.md"])
  n3(["adr-scribe/review-checklist.md"])
  n4["c4designer"]
  n5(["c4designer/SKILL.md"])
  n6(["c4designer/level-template.md"])
  n7(["c4designer/mermaid-c4-syntax.md"])
  n8(["c4designer/mode-document-code.md"])
  n9(["c4designer/mode-update.md"])
  n10(["c4designer/review-checklist.md"])
  n11["tests"]
  n12(["fail"])
  n13(["info"])
  n14(["pass"])
  n0 -->|4| n1
  n0 -->|6| n2
  n0 -->|6| n3
  n4 -->|10| n5
  n4 -->|5| n6
  n4 -->|10| n7
  n4 -->|4| n8
  n4 -->|8| n9
  n4 -->|12| n10
  n11 -->|15| n12
  n11 -->|5| n13
  n11 -->|14| n14
```

| Node | Fan-in |
|---|---:|
| `tests/test-skill-format.sh::fail` | 15 |
| `tests/test-skill-format.sh::pass` | 14 |
| `c4designer/review-checklist.md` | 12 |
| `c4designer/SKILL.md` | 10 |
| `c4designer/mermaid-c4-syntax.md` | 10 |
| `c4designer/mode-update.md` | 8 |
| `adr-scribe/adr-template.md` | 6 |
| `adr-scribe/review-checklist.md` | 6 |
| `c4designer/level-template.md` | 5 |
| `tests/test-skill-format.sh::info` | 5 |
| `adr-scribe/SKILL.md` | 4 |
| `c4designer/mode-document-code.md` | 4 |

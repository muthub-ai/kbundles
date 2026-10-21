---
type: application-bundle/code-graph-view
title: Dependencies and hotspots — kfsit
description: External dependencies, entry points and fan-in hotspots derived from the code graph.
generated:
  by: process:kfbundle.views@0.1.0
  at: '2026-10-20T19:30:00-05:00'
sources:
- id: g1
  kind: code-graph
  path: code-graph/code-graph.jsonl
  sha256: 7cce3a8bffd531894689010170006598998a6a2289a14595ccd4f2dfbb604d22
x_kf:
  schema: kf-application-bundle/1
  appid: kfsit
  bundle_kind: application
  view: dependencies
  derived: true
---
# Dependencies and hotspots — kfsit

Derived from `code-graph/code-graph.jsonl` and `code-graph/metrics.json`. Hotspots are fan-in counts only (calls, renders, imports and links into a node); the bundle pins one commit, so there is no churn signal.

## External dependencies

| Package | Files that import or declare it |
|---|---:|
| `pathlib` | 13 |
| `json` | 7 |
| `re` | 7 |
| `sys` | 7 |
| `shutil` | 6 |
| `yaml` | 6 |
| `@playwright/test` | 4 |
| `os` | 4 |
| `tempfile` | 3 |
| `typing` | 3 |
| `unittest` | 3 |
| `urllib` | 3 |
| `argparse` | 2 |
| `esbuild` | 2 |
| `fs` | 2 |
| `graphology` | 2 |
| `markdown` | 2 |
| `path` | 2 |
| `sigma` | 2 |
| `tarfile` | 2 |
| `dataclasses` | 1 |
| `datetime` | 1 |
| `events` | 1 |
| `functools` | 1 |
| `http` | 1 |
| `io` | 1 |
| `jsonschema` | 1 |
| `node:path` | 1 |
| `node:url` | 1 |
| `posixpath` | 1 |

## Entry points

- `.github/ci-run.sh (cli-main)`
- `kfsite/__main__.py (cli-main)`
- `scripts/build.sh (cli-main)`
- `scripts/fetch_release.py (cli-main)`
- `scripts/make_quartz_config.py (cli-main)`
- `scripts/pip_install.sh (cli-main)`
- `scripts/vercel_build.sh (cli-main)`
- `tests/serve.py (cli-main)`
- `tests/test_fetch_release.py (cli-main)`
- `tests/test_post.py (cli-main)`
- `tests/test_stage.py (cli-main)`

## Fan-in hotspots

```mermaid
flowchart LR
  n0["explorer/src"]
  n1(["$"])
  n2(["T"])
  n3(["applyFilters"])
  n4(["applyFocus"])
  n5(["esc"])
  n6(["focusNode"])
  n7(["humanDay"])
  n8(["linkCount"])
  n9(["updateStatus"])
  n10["kfsite"]
  n11(["kfsite/bundle.py"])
  n12(["kfsite/stage.py"])
  n13["tests"]
  n14["tests/e2e"]
  n15(["ready"])
  n0 -->|27| n1
  n0 -->|6| n2
  n0 -->|6| n3
  n0 -->|9| n4
  n0 -->|53| n5
  n0 -->|7| n6
  n0 -->|7| n7
  n0 -->|11| n8
  n0 -->|9| n9
  n10 -->|4| n11
  n13 -->|3| n11
  n13 -->|7| n12
  n10 -->|1| n12
  n14 -->|14| n15
```

| Node | Fan-in |
|---|---:|
| `explorer/src/explorer.ts::esc` | 53 |
| `explorer/src/explorer.ts::$` | 27 |
| `tests/e2e/explorer.spec.ts::ready` | 14 |
| `explorer/src/explorer.ts::linkCount` | 11 |
| `explorer/src/explorer.ts::applyFocus` | 9 |
| `explorer/src/explorer.ts::updateStatus` | 9 |
| `kfsite/stage.py` | 8 |
| `explorer/src/explorer.ts::focusNode` | 7 |
| `explorer/src/explorer.ts::humanDay` | 7 |
| `kfsite/bundle.py` | 7 |
| `explorer/src/explorer.ts::T` | 6 |
| `explorer/src/explorer.ts::applyFilters` | 6 |

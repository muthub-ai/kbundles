---
type: application-bundle/code-graph-view
title: Dependencies and hotspots — kfcor
description: External dependencies, entry points and fan-in hotspots derived from the code graph.
generated:
  by: process:kfbundle.views@0.1.0
  at: '2026-10-20T19:30:00-05:00'
sources:
- id: g1
  kind: code-graph
  path: code-graph/code-graph.jsonl
  sha256: 881e9bd0100d27591d42a861bc0797c5ae5cb88f764837f511242482b5d82a7d
x_kf:
  schema: kf-application-bundle/1
  appid: kfcor
  bundle_kind: application
  view: dependencies
  derived: true
---
# Dependencies and hotspots — kfcor

Derived from `code-graph/code-graph.jsonl` and `code-graph/metrics.json`. Hotspots are fan-in counts only (calls, renders, imports and links into a node); the bundle pins one commit, so there is no churn signal.

## External dependencies

| Package | Files that import or declare it |
|---|---:|
| `pathlib` | 17 |
| `typing` | 11 |
| `json` | 7 |
| `sys` | 7 |
| `datetime` | 6 |
| `kb` | 6 |
| `re` | 6 |
| `os` | 5 |
| `unittest` | 5 |
| `dataclasses` | 4 |
| `jsonschema` | 4 |
| `tempfile` | 4 |
| `argparse` | 3 |
| `llmw2` | 3 |
| `shutil` | 3 |
| `yaml` | 3 |
| `collections` | 2 |
| `ingest` | 2 |
| `networkx` | 2 |
| `semantica` | 2 |
| `subprocess` | 2 |
| `types` | 2 |
| `calendar` | 1 |
| `fs` | 1 |
| `functools` | 1 |
| `hashlib` | 1 |
| `llmwiki2` | 1 |
| `logging` | 1 |
| `module` | 1 |
| `numpy` | 1 |

## Entry points

- `.github/ci-run.sh (cli-main)`
- `tests/test_flow.py (cli-main)`
- `tests/test_governance_graph.py (cli-main)`
- `tests/test_ingest.py (cli-main)`
- `tests/test_rules.py (cli-main)`
- `tests/test_semantic_layer.py (cli-main)`
- `tools/kb/__main__.py (cli-main)`
- `tools/librarian/ingest.py (cli-main)`
- `tools/librarian/seed_from_site.py (cli-main)`

## Fan-in hotspots

```mermaid
flowchart LR
  n0["tests"]
  n1(["note_fm"])
  n2(["EndToEnd.kb"])
  n3(["rules"])
  n4(["E"])
  n5["tools/kb"]
  n6(["tools/kb/__init__.py"])
  n7(["tools/kb/extractors/__init__.py"])
  n8(["_norm"])
  n9(["Problem"])
  n10["tools/librarian"]
  n11(["c"])
  n12["wiki/ai-native-sdlc"]
  n13(["wiki/ai-native-sdlc/the-ai-native-sdlc-when-typing-code-stops-being-the.md"])
  n14["wiki/data-ai-platforms"]
  n15["wiki/governed-ai"]
  n16(["wiki/governed-ai/architecture-that-runs-why-ai-era-governance-must-be-code.md"])
  n17(["wiki/governed-ai/model-is-a-tool-harness-is-the-strategy.md"])
  n18["wiki/leading-ai-change"]
  n0 -->|16| n1
  n0 -->|12| n2
  n0 -->|9| n3
  n0 -->|18| n4
  n5 -->|5| n6
  n10 -->|2| n6
  n5 -->|9| n7
  n5 -->|8| n8
  n5 -->|23| n9
  n10 -->|9| n11
  n12 -->|4| n13
  n14 -->|2| n13
  n15 -->|1| n13
  n18 -->|1| n13
  n15 -->|5| n16
  n12 -->|2| n16
  n18 -->|1| n16
  n15 -->|6| n17
  n12 -->|2| n17
```

| Node | Fan-in |
|---|---:|
| `tools/kb/validate.py::Problem` | 23 |
| `tests/test_semantic_layer.py::E` | 18 |
| `tests/helpers.py::note_fm` | 16 |
| `tests/test_flow.py::EndToEnd.kb` | 12 |
| `tests/test_rules.py::rules` | 9 |
| `tools/kb/extractors/__init__.py` | 9 |
| `tools/librarian/dump-site-content.js::c` | 9 |
| `tools/kb/extractors/resolution.py::_norm` | 8 |
| `wiki/ai-native-sdlc/the-ai-native-sdlc-when-typing-code-stops-being-the.md` | 8 |
| `wiki/governed-ai/architecture-that-runs-why-ai-era-governance-must-be-code.md` | 8 |
| `wiki/governed-ai/model-is-a-tool-harness-is-the-strategy.md` | 8 |
| `tools/kb/__init__.py` | 7 |

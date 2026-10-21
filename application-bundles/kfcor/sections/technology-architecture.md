---
type: application-bundle/technology-architecture
title: Technology architecture — Knowledge Foundation core
description: Languages, pinned dependencies, models, build commands, CI/CD workflows and hosting that
  Knowledge Foundation core runs on.
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
  section: technology-architecture
  bootstrap: true
---
# Technology architecture — Knowledge Foundation core

## Runtime and build

The tooling is Python run with `PYTHONPATH=tools`; the Makefile wraps the everyday commands (`ingest`, `curate`, `check`, `test`, `graph`, `stale`, `evals`, `ask`), and every workflow job sets up Python 3.12.[^make] [^py312]

Runtime dependencies are exact pins (`llmwiki2==0.5.0`, `jsonschema`, `PyYAML`, `networkx`, `numpy` for the spring layout), and the optional semantic layer adds `semantica[llm-anthropic]==0.7.0` from a separate requirements file.[^req] [^req-graph]

## Models

The librarian writes with `claude-sonnet-5-5` through Anthropic's OpenAI-compatible endpoint and routes with `tev1-8k` on a local Ollama server at `localhost:11434`; the semantic layer calls `claude-haiku-5-5` through Semantica's provider, with the extraction method chosen by `SEMANTICA_NER_METHOD` and an adapter default of `ml`.[^models] [^adapter-env]

## CI/CD

| Workflow | Trigger | Effect |
|---|---|---|
| `tests.yml` | every pull request and push to `main` | required `unit tests` and `bundle rules` jobs plus a non-required Semantica canary matrix (`pattern`, `ml`, `llm`) [^wf-tests-req] [^wf-tests] |
| `approve.yml` | pull request review submitted | stamps `verified` on changed notes when the owner approves [^wf-approve] |
| `publish.yml` | push to `main` touching `wiki/`, `ontology/`, `schemas/`, `tools/kb/` or `wiki.config.yaml` | builds the graph, creates release `kf-YYYY.MM.DD-N`, calls the site deploy hook; Semantica with `llm` extraction and typed relations is the default [^wf-publish] [^wf-publish-env] [^wf-release] |
| `weekly.yml` | Mondays 11:07 UTC | deterministic report, then a Claude Code lint pass capped at $5 [^wf-weekly] [^wf-weekly-cap] |

`.github/ci-run.sh` wraps each CI step and, on failure, re-emits the last 120 lines of output as numbered error annotations of at most 3,500 bytes so failures are readable from the Checks API.[^ci-run] [^g-cirun]

The wiki site (Quartz 5 with a Sigma.js 4 explorer) lives in a separate repository that reads only the release bundle and `graph.json`; this repository only posts to the Vercel deploy hook after the release exists.[^adr014] [^pub-hook]

*Assessment:* The extractor's own default NER method is `ml`, while `publish.yml` defaults releases to `llm` with typed relations on; the effective production behaviour is therefore set by repository variables, not by code defaults, and a reader of the adapter alone would mispredict it.[^wf-publish-env] [^adapter-env]

*Assessment:* Pinning Semantica exactly and running it as a non-required canary on every pull request isolates the least stable dependency: a breaking release shows up as canary annotations instead of a failed required check or a broken release.[^req-graph] [^wf-tests]

[^make]: src · Makefile#L1-L33 · sha256:a58e905b908a0ceb58998dc5c13b06047ffe89c8162ccd81f032ebbdc61d452d
[^py312]: src · .github/workflows/tests.yml#L16-L25 · sha256:c42e30142e9cb99252bd86fe4bd5be7385c23ee5497a56761111aee18c719e9d
[^req]: src · requirements.txt#L1-L6 · sha256:07b7c171239da5b738b21f2be7c9086d8b76905f41e3f7f670563c9b5a4c3ff3
[^req-graph]: src · requirements-graph.txt#L1-L4 · sha256:fb09e52a74442075620e0319231af312409e13957a37a89e13d8757f22e733dc
[^adapter-env]: src · tools/kb/extractors/semantica_adapter.py#L1-L16 · sha256:7683ec5a853fca09e7a7b90db7f59368ed02df5ae558ee346043983697700a0b
[^models]: src · wiki.config.yaml#L65-L76 · sha256:77deda4aed9666646071680089d07c399a5ebd54c7e8375af1e3d053d3e8348c
[^wf-tests-req]: src · .github/workflows/tests.yml#L1-L3 · sha256:c8805b63fab4a6f2b4198b2c489dbda389fa1d15ee84b539ba38d81b52e6b727
[^wf-tests]: src · .github/workflows/tests.yml#L73-L80 · sha256:a12357bf287d527e7b814567ef8707cd96f5e277a6dd01876f6cad197a93d296
[^wf-approve]: src · .github/workflows/approve.yml#L1-L14 · sha256:25114e845ba235ab7e0fc3b6cdfe38317fd8ec8108f0db452dabb8c19d184892
[^wf-publish]: src · .github/workflows/publish.yml#L1-L8 · sha256:17e8ce4054554a973a0863189f0c783f93f78e16f248bfc8c964f0a5bc7ace36
[^wf-publish-env]: src · .github/workflows/publish.yml#L28-L38 · sha256:47b4c03cbf5b718f542b4b830d30d89481ce8a83e9b63d53169a815068575db7
[^wf-release]: src · .github/workflows/publish.yml#L41-L45 · sha256:0fb2a7871cfd0a3be31d8771205ca928b725b451081015de9be4ff6f1fdfd0b1
[^wf-weekly]: src · .github/workflows/weekly.yml#L1-L6 · sha256:27daddbd2fedc490dd8896facac527d620be69d66bb508f19fe0535ec396de12
[^wf-weekly-cap]: src · .github/workflows/weekly.yml#L51-L54 · sha256:9320f63ce6b386395a294a3b2e420862075d140203eb06392b64f6a13b089719
[^ci-run]: src · .github/ci-run.sh#L1-L21 · sha256:f6be3830ad1207c7cf3ce950539d2071f410b653fe5d6823ef619bab227429c8
[^g-cirun]: graph · .github/ci-run.sh
[^adr014]: src · decisions/014-quartz-5-and-sigmajs-4-as-designed.md#L12-L22 · sha256:f4c0793d0943587d7a74e4f6af3070aa3ec91b0d4c428207ec7158ad88bfa66d
[^pub-hook]: src · .github/workflows/publish.yml#L47-L50 · sha256:9b5d4031d0c2198c4533017f40ad4a2059ac9206fdb6bd38ddce7a311ed65c9c

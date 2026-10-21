---
type: application-bundle/executive-summary
title: Executive summary — Architecture as Code
description: What Architecture as Code is, who uses it, why it matters, and its overall shape in one screen.
generated:
  by: process:building-application-bundles@0.1.0
  at: '2026-10-20T19:30:00-05:00'
sources:
- id: repo
  kind: source-repo
  repo: muthub-ai/aac
  commit_sha: fcc5db4d74b50a8a95a1017cd688ce73ac689633
- id: graph
  kind: code-graph
  path: code-graph/code-graph.jsonl
  sha256: 067e6f351a868e049ee59a6ca2db1eb52ea80346a36b47220ba1fefca2774773
x_kf:
  schema: kf-application-bundle/1
  appid: aacod
  bundle_kind: application
  section: executive-summary
  bootstrap: true
---
# Executive summary — Architecture as Code

## What it is

Architecture as Code keeps system architecture as version-controlled YAML in the repository and treats it like source code: each file is checked against a schema, linted against policy, rendered as diagrams and published by a CI pipeline.[^readme-why]

The repository holds four kinds of governed artifact in top-level folders: C4 system models (`model/`), reusable patterns (`patterns/`), enterprise standards (`standards/`) and time-boxed exceptions (`waivers/`). Each kind has a JSON Schema in `schema/`.[^agents-structure][^cli-init-dirs]

## Who uses it and how

There are four ways in, all reading the same YAML. Architects and engineers use a Next.js web app with a landing scorecard, a catalog dashboard and an in-browser diagram editor. CI jobs and developers use the `aac` CLI. AI coding agents use the `aac-mcp` stdio server. Governance owners use OPA/Rego policies.[^readme-capabilities][^g-mcp-main][^g-cli-entry]

| Surface | Entry point | Purpose |
|---|---|---|
| Web app | `src/app/systems/[id]/page.tsx` | Loads a system model into the diagram editor [^g-system-page] |
| CLI `aac` | `cli/bin/aac.ts` | `init`, `create` and `validate` commands [^g-cli-entry] |
| MCP server `aac-mcp` | `mcp-server/bin/aac-mcp.ts` | Resources, tools and prompts for agents over stdio [^g-mcp-main] |
| Governance pipeline | `.github/workflows/aac-pipeline.yml` | Validates, lints, builds diagrams and publishes the docs site [^wf-header] |

## Shape in numbers

The code graph classifies these files as entry points: the Next.js routes (`/`, `/dashboard`, `/systems/[id]`), the MCP binary and its three tool modules, and the OPA bundle build script.[^g-home][^g-dashboard][^g-system-page][^g-tool-validate][^g-tool-lint][^g-tool-waiver][^g-bundle-sh]

At this commit the repository holds four example system models. The README lists six patterns, nine standards and ten waivers.[^readme-system-models][^readme-capabilities] Only three of the six patterns have a `patterns/<id>/pattern.yaml`. The landing page counts patterns from the in-code `MOCK_PATTERNS` array, not from that folder.[^g-pat-bq][^g-pat-api][^g-pat-ml][^home-mock]

*Assessment:* Value depends on the YAML staying the single source. The web app, CLI, MCP server and pipeline each parse the same folders without a shared service in between. That keeps the system simple, but rules are duplicated across surfaces (see the application and security sections).[^agents-structure][^readme-capabilities]

*Assessment:* Governance is only partly automated at this commit. The five structural lint rules block merges, but the three OPA policies are only unit-tested in CI and never evaluated against the model files.[^wf-header]

[^readme-why]: src · README.md#L26-L28 · sha256:a3402e95fc2eda197105e9ab189a4882b005997ac227d260ba3273d27810df69
[^agents-structure]: src · AGENTS.md#L14-L28 · sha256:3538a5b36f72135d4cd4726b583ddb9f6b77bf988da470b53b4ec2b9fba51de8
[^cli-init-dirs]: src · cli/src/commands/init.ts#L9-L9 · sha256:d63159cd1e5349cf07f8be8e6bbeddbdf796610492e07f7dc08014ce68dd3c03
[^readme-capabilities]: src · README.md#L51-L61 · sha256:4b6bf78639bf1c51b29bd576bd52299cd2fe8941b85704e4d00bd437d7e3178b
[^g-mcp-main]: graph · mcp-server/bin/aac-mcp.ts::main
[^g-cli-entry]: graph · cli/bin/aac.ts
[^g-system-page]: graph · src/app/systems/[id]/page.tsx
[^wf-header]: src · .github/workflows/aac-pipeline.yml#L4-L18 · sha256:ef45d75a0eacff2aaff385c6b69676377f2d6fcf1274abdfe64562bfdf74338b
[^g-home]: graph · src/app/page.tsx
[^g-dashboard]: graph · src/app/dashboard/page.tsx
[^g-tool-validate]: graph · mcp-server/src/tools/validate-architecture.ts
[^g-tool-lint]: graph · mcp-server/src/tools/lint-compliance.ts
[^g-tool-waiver]: graph · mcp-server/src/tools/scaffold-waiver.ts
[^g-bundle-sh]: graph · packages/policies/scripts/build-bundle.sh
[^readme-system-models]: src · README.md#L441-L450 · sha256:41cb25b33bcc50650a89fcf42ae7506e1389cd82d711d95c44cfc32946328e84
[^g-pat-bq]: graph · patterns/data-platform-bq/pattern.yaml
[^g-pat-api]: graph · patterns/internal-api-multiregional/pattern.yaml
[^g-pat-ml]: graph · patterns/aiml-model-inference/pattern.yaml
[^home-mock]: src · src/app/page.tsx#L17-L24 · sha256:6c63746fc7f585263f41b0abbcae230b4ccb846d60ba2e402c732d1b85485344

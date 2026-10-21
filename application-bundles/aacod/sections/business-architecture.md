---
type: application-bundle/business-architecture
title: Business architecture — Architecture as Code
description: Capabilities Architecture as Code provides, its actors, the governance value stream and the
  business rules it encodes.
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
  section: business-architecture
  bootstrap: true
---
# Business architecture — Architecture as Code

## Problem and purpose

The project targets architecture knowledge that lives in slide decks and wiki pages and drifts from the systems it describes. Its answer is to make declarative YAML the single, reviewable record of each system's design.[^readme-why]

## Capabilities

| Capability | How it is delivered |
|---|---|
| Model systems in C4 terms | `model/<system>/system.yaml` with people, software systems, containers, deployment nodes and views [^app-schema-model] |
| Publish reusable patterns | `patterns/<id>/pattern.yaml` plus PlantUML context/container diagrams and catalog metadata [^pattern-yaml-head][^g-pat-puml] |
| Govern with standards | `standards/*.yaml` with RFC 2119 severities (`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`) per requirement [^std-severity][^std-req] |
| Grant time-boxed exceptions | `waivers/*.yaml` with risk severity, compensating controls, financial impact and a remediation plan [^waiver-sample-risk] |
| Report to executives | Landing-page scorecard computed from systems, standards, waivers and trend history [^exec-metrics-sig] |
| Serve AI agents | MCP resources, tools and prompts, including a guided exception request [^req-exception-prompt] |

## Actors

The repository's artifacts name governance roles, not individuals. Standards carry a `standardOwner` and an `assignedArchitect`. Waivers record `requestedBy`, `approvedBy` and an assigned remediation team.[^std-owner][^waiver-sample-approval]

Inside the models, the C4 `people` entries are the business actors of each modeled system. For example, the e-commerce model declares Customer, Administrator and Content Manager.[^model-people]

## Value stream: exception lifecycle

A waiver moves through five states: `PENDING_REVIEW`, `APPROVED`, `REJECTED`, `EXPIRED` and `REMEDIATED`. The schema requires an ID matching `EXC-<CATEGORY>-NNN`.[^waiver-schema-status][^waiver-schema-id]

Agents start the stream through the `request_architecture_exception` prompt. It tells the model to read the standard and the system, gather justification, cost and controls from the user, and call `scaffold_waiver`.[^req-exception-prompt]

`scaffold_waiver` always files the request as `PENDING_REVIEW` with `MEDIUM` risk. It defaults to six months and puts placeholder text in any field the agent did not supply.[^waiver-defaults][^waiver-object]

*Assessment:* Approval stays a human act recorded in YAML (`approvedBy`, `approvalDate`) and merged by pull request. The tooling drafts requests but never moves a waiver past `PENDING_REVIEW`.[^waiver-object][^waiver-sample-approval]

## Business rules enforced in the pipeline

Five structural rules block a merge: no frontend-to-database relationship, no internal system without containers, no orphaned external system, deployment references must resolve, and every container must declare a technology.[^readme-rules][^lint-orchestration]

The scorecard's compliance score is the share of standards with no `APPROVED` or `PENDING_REVIEW` waiver against them. It counts a waiver as active purely by status, ignoring `expirationDate`.[^metrics-active][^metrics-compliance]

For example, `waivers/api-gateway-bypass.yaml` is still `APPROVED` but has an `expirationDate` of 2025-12-31.[^waiver-head][^waiver-sample-approval]

*Assessment:* The headline compliance figure therefore depends on someone updating waiver status by hand, not on the calendar. Waivers that have lapsed but are still marked approved keep counting as sanctioned exceptions.[^metrics-active][^waiver-sample-approval]

The pattern-reuse KPI is hard-coded. It divides the system count by itself, so it always reports 100% when any system exists.[^metrics-pattern-reuse]

[^readme-why]: src · README.md#L26-L28 · sha256:a3402e95fc2eda197105e9ab189a4882b005997ac227d260ba3273d27810df69
[^app-schema-model]: src · schema/application-schema.json#L28-L56 · sha256:49b66c78d418382db156417272b8509ecfa2a3a7982783a129b6318c53bfa064
[^pattern-yaml-head]: src · patterns/data-platform-bq/pattern.yaml#L1-L11 · sha256:46417e115dc3cd4c1e41cc4380ec56b9719fb16dcf9fc3e15fa2b98b15ac3747
[^g-pat-puml]: graph · patterns/data-platform-bq/container.puml
[^std-severity]: src · schema/standards.json#L213-L221 · sha256:437dcd3587b1b999dccc6ea7ecd8624767d5a297f94d7c10ff9e7028caf43b45
[^std-req]: src · standards/cryptography-key-management.yaml#L57-L62 · sha256:5fffb9abcb7c6291799e412e80d331363305a646e3c8a9a17052522ed306e29d
[^waiver-sample-risk]: src · waivers/api-gateway-bypass.yaml#L15-L38 · sha256:fd3f23b48f775c5debcc4ae8e7f688507e3dc4b97eccea049e8c4200d5eeaeb5
[^exec-metrics-sig]: src · src/lib/metrics/compute-metrics.ts#L138-L144 · sha256:93f0498f494a3e02c6a77970940464fccd59d07ed51c0a974fe3cd0602e3c272
[^req-exception-prompt]: src · mcp-server/src/prompts/request-exception.ts#L12-L59 · sha256:2fc82b698af2afd8dc74379ad0e6dd427a15c6ec5404fa7b06fc2f213a7b4ac9
[^std-owner]: src · standards/cryptography-key-management.yaml#L1-L14 · sha256:39c38da9f858b01502ae953ccd38869e7e78b03ff98b763c93bd9d79084ea46c
[^waiver-head]: src · waivers/api-gateway-bypass.yaml#L1-L10 · sha256:273be92aaebadd25b1e7568b7be4eb95be82bed7f1def7f744f5aa738762e33f
[^waiver-sample-approval]: src · waivers/api-gateway-bypass.yaml#L39-L51 · sha256:6a10fdf2406ae1467da367f403b8d735773a082867bdcdf113e0414cf947417f
[^model-people]: src · model/ecommerce-platform/system.yaml#L5-L31 · sha256:efeaf256dfd73bae7ae56d4e3ccaf867317f165c11b974fc72e8bf3343b96184
[^waiver-schema-status]: src · schema/waivers.json#L60-L64 · sha256:9a8a45829de8c6a40d81c522eed428eca69a98006089a97fda8846eb88c46a65
[^waiver-schema-id]: src · schema/waivers.json#L24-L28 · sha256:fe948b86dbf155df2cb91267c4589103ad5443e0ee785811ea214133cc54d195
[^waiver-defaults]: src · mcp-server/src/tools/scaffold-waiver.ts#L101-L128 · sha256:35cc968c849d891d50bc53dcd0c306cc55b4591dcab100acfd5af52428a034d3
[^waiver-object]: src · mcp-server/src/tools/scaffold-waiver.ts#L130-L148 · sha256:bad8d15c199203c65a2972bfe9deb77568bea636e3aad3a5efef97fc8fa235ad
[^readme-rules]: src · README.md#L332-L338 · sha256:4d9f2ce6b9528d0a15499f514c98caff26ae32415a968e6493e4acb6494578dc
[^lint-orchestration]: src · scripts/lint-architecture.ts#L415-L429 · sha256:c7fbe6b9ca12408ea6f925c743562d90a8195f033b06cf6ed8a8a4a90256bbcd
[^metrics-active]: src · src/lib/metrics/compute-metrics.ts#L161-L166 · sha256:4b908a2411f0041431a963c86e66af0721552192935afeb6fe838caed86e0b5f
[^metrics-compliance]: src · src/lib/metrics/compute-metrics.ts#L181-L189 · sha256:91768d23f3d34089b11a8fd19c7926601dc450b663b6ab238bf501ca77c8a06b
[^metrics-pattern-reuse]: src · src/lib/metrics/compute-metrics.ts#L191-L192 · sha256:d2752d3edb08418322426c7ed1009c7da3376172ae10136149233af8be5fca4e

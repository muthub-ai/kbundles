---
type: application-bundle/data-architecture
title: Data architecture — Architecture as Code
description: The YAML and JSON artifacts Architecture as Code stores, their schemas and validators, derived
  outputs, caches and data lineage.
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
  section: data-architecture
  bootstrap: true
---
# Data architecture — Architecture as Code

## Store

The app has no database. The git repository is the only store: architecture records are plain files read straight from disk by the web app, the MCP server and the pipeline scripts.[^load-systems][^repo-resolver-io][^validate-models-paths]

## Entities and schemas

| Entity | Location | Schema | Draft |
|---|---|---|---|
| System model | `model/<id>/system.yaml` | `schema/application-schema.json` (`name`, `model` required) [^app-schema-head] | draft-07 [^app-schema-head] |
| System metadata | `model/<id>/metadata.json` | Zod `SystemMetadataSchema` (repo count, LoC, scan time, branch) [^meta-zod] | Zod [^meta-zod] |
| Pattern | `patterns/<id>/pattern.yaml` | `schema/pattern-schema.json` (root key `pattern`) [^pattern-schema-head] | draft-07 [^pattern-schema-head] |
| Standard | `standards/*.yaml` | `schema/standards.json` (`metadata`, `scope`, `requirements`) [^std-schema-head] | 2020-12 [^std-schema-head] |
| Waiver | `waivers/*.yaml` | `schema/waivers.json` (13 required fields, no extra properties) [^waiver-schema-head] | 2020-12 [^waiver-schema-head] |
| Trend history | `data/trend-history.json` | TypeScript `TrendPoint` only [^trend-load] | none [^trend-load] |

The system model follows the C4 hierarchy. `model` holds `softwareSystems`, `people` and `deploymentNodes`, and the top-level `views` section declares system-context, container and deployment views.[^app-schema-model][^model-views]

Element IDs are restricted to `^[A-Za-z0-9_-]+$`. Relationships refer to targets by `destinationId`, either as a bare ID or as a dotted `System.Container` path.[^app-schema-container][^model-rel-sample]

Container `properties` are an open map (`additionalProperties: true`) with a typed `type` archetype. Systems carry `disposition` and `dataClassification` enums (Public, Internal Use, Confidential, Restricted).[^app-schema-props][^app-schema-classification]

The schema does not declare any property the OPA policies read (`encryption`, `autoscaling_enabled`). They can only appear through the open `properties` map, unchecked.[^app-schema-props][^kms-deny][^rightsizing-deny]

## Validation pipeline

`validate-models.ts` runs three checks on each model folder: AJV on `system.yaml`, a cross-reference check that every `destinationId` resolves, and Zod on `metadata.json`. Any failure fails the job.[^validate-models-checks]

The cross-reference resolver accepts an exact ID match or any known ID that ends with `.<ref>`.[^resolve-ref]

*Assessment:* Suffix matching is lenient. A bare `destinationId: Database` passes whenever any system has a container called `Database`, so references that are ambiguous across systems are not flagged.[^resolve-ref]

Standards and waivers are validated with the AJV 2020-12 build, and system models with the default draft-07 AJV. Every validator runs with `strict: false`.[^validate-waivers-ajv][^validate-models-ajv]

## Derived data and lineage

The pipeline turns models into PlantUML and Draw.io files under `src/docs/diagrams/<system>/`. It turns models, patterns, standards and waivers into static HTML under `build/`, which is gitignored and shipped only as workflow artifacts.[^build-diagrams-out][^gitignore-build][^wf-artifacts]

`snapshot-trends.ts` describes itself as appending a metrics point to `data/trend-history.json` on each merge to main, but no workflow step runs it. The committed history starts at 2025-10-01.[^snapshot-header][^wf-app-arch-steps][^trend-file]

## Caches and retention

The CLI caches downloaded schemas with their ETag under `~/.aac/cache/schemas/`. If the network or the remote fails, it falls back to the cached copy.[^schema-cache]

Workflow artifacts (docs, diagrams, catalog pages, assembled site) are kept for seven days. The published `gh-pages` branch is force-orphaned on every publish, so it holds no history.[^wf-artifacts][^wf-publish]

[^load-systems]: src · src/lib/model/load-systems.ts#L14-L40 · sha256:887d317457c55a7c2cf9f9d2c9a54e3b9f5e00709b3d7a998ed55633dc965e18
[^repo-resolver-io]: src · mcp-server/src/lib/repo-resolver.ts#L67-L86 · sha256:f1a859db555da880e3d41575f9c51c201a666e62aaf46c3596437a0a50034096
[^validate-models-paths]: src · scripts/validate-models.ts#L24-L27 · sha256:f2f74fd1cfa4cefb159f4d56305962ce02e260125a7e074b45ddd0e72323dc75
[^app-schema-head]: src · schema/application-schema.json#L1-L27 · sha256:18673960eaa1e78fdc8ba64fd208acc9329d45892fd76dd7fab146d2c7dfc8bd
[^meta-zod]: src · src/lib/validation/system-schema.ts#L151-L165 · sha256:711cd4c0edfb4b90eb9adbc81d601d53e09fde490680b3d21b9f3a3716f2b5c1
[^pattern-schema-head]: src · schema/pattern-schema.json#L1-L15 · sha256:190d8a5fb684411df7887ea535672623fd6fdab2d10003d1cc020b4ff01316f8
[^std-schema-head]: src · schema/standards.json#L1-L11 · sha256:69163c5057e191ba3ad81e3fa9580c80e3f43af5e6e9e6c55c4f444143bca36b
[^waiver-schema-head]: src · schema/waivers.json#L1-L22 · sha256:104156c43c28db3f0724b23cf5d53342f3ea26f36614e4b3614e019b62e1ffde
[^trend-load]: src · src/app/page.tsx#L11-L15 · sha256:e888c082584108f59158f6af95fdf8b9f6ec1de7d4d29a7f86b51801f360e82f
[^app-schema-model]: src · schema/application-schema.json#L28-L56 · sha256:49b66c78d418382db156417272b8509ecfa2a3a7982783a129b6318c53bfa064
[^model-views]: src · model/ecommerce-platform/system.yaml#L540-L575 · sha256:ebc6074771f254ccf867a16fb3c1e2a2d7924ffb36c79ddcd68b5a3eef290c83
[^app-schema-container]: src · schema/application-schema.json#L149-L189 · sha256:5ac78ad1672792072cb7ea20fe3813b2bf6df6a2a636453a6a5e1e2bc66c811c
[^model-rel-sample]: src · model/ecommerce-platform/system.yaml#L6-L17 · sha256:3e010e03f85d2a3c1ebb63a7d7cc6ec05799445a8e54886d019f835e225d8c89
[^app-schema-props]: src · schema/application-schema.json#L191-L203 · sha256:9461e601c26aaa1eb03c88cb8f5f62bbe5ccfc8bb233b9575796c0102863d30e
[^app-schema-classification]: src · schema/application-schema.json#L104-L123 · sha256:0434d4866ec99051bbe2cc39f7ff713293e2e0fdfba4a521a82b9a62e6fc9ac6
[^kms-deny]: src · packages/policies/rules/security/kms.rego#L30-L52 · sha256:07a75e0663c1700895e3fc447e9c6fa72ba4af923eed8af1b606e3c153a7c2ab
[^rightsizing-deny]: src · packages/policies/rules/finops/rightsizing.rego#L19-L28 · sha256:bcf48d7b4203611be75ed0b03c71f4359e2c6d33b38e491340d0b531341cce5a
[^validate-models-checks]: src · scripts/validate-models.ts#L102-L142 · sha256:b4bcbfd61d4b4d12e58086a0164e46dc3a551da18bae8f7b9a2deedc55e2f493
[^resolve-ref]: src · src/lib/validation/system-schema.ts#L313-L320 · sha256:5704ecae9de1bc0250797de0844cb043dd18a2690938250aae2d0e6f81f08e80
[^validate-waivers-ajv]: src · scripts/validate-waivers.ts#L40-L44 · sha256:65c2cba56ac15163a2cdc6cbeda0350b406c632b5511fc0f4f96372666bdcd42
[^validate-models-ajv]: src · scripts/validate-models.ts#L54-L56 · sha256:965b75d1ee5347b00506becc15479e7f7afc09df62ed2b477825031d64355f9a
[^build-diagrams-out]: src · scripts/build-diagrams.ts#L1-L8 · sha256:d4c22452e4bd733673c3d9a7d648b0c23cedc10e716980994af7ff70f79f3986
[^gitignore-build]: src · .gitignore#L21-L21 · sha256:5b46eb48d96e8571e8c93e4ef4f6ffbe6807b6d7350664a36a064e1167a32718
[^wf-artifacts]: src · .github/workflows/aac-pipeline.yml#L142-L155 · sha256:4141ce7cc898b05c009f989dbba3b8ac3c0e407f367e942fc47f00e9def3e8b3
[^snapshot-header]: src · scripts/snapshot-trends.ts#L1-L7 · sha256:ac796b9004db691d0b84cbc4325c995f5486dc91c7e57850342dec7543f305ff
[^wf-app-arch-steps]: src · .github/workflows/aac-pipeline.yml#L111-L140 · sha256:6fff98170b3a057f322d9962efcfbcbb99425784c6e9769a1f7b0f998da8a8cb
[^trend-file]: src · data/trend-history.json#L1-L5 · sha256:ed64c11fbc610b64fa32cf197e9d917a86b1a10815c1927465318fb74e74e04c
[^schema-cache]: src · cli/src/schema-manager.ts#L40-L79 · sha256:b3d4458d822d6bf28681e3605093efbf898ce2ff0ecdaf74c2d881e446786cd0
[^wf-publish]: src · .github/workflows/aac-pipeline.yml#L517-L529 · sha256:e7d6fc7540e939f983b54abd14db5852b40bc16ea3547d66f039b33e27237379

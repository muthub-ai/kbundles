---
type: application-bundle/domain-map
title: Domain map — C4 modeling
description: Vocabulary of the C4 system-model domain in Architecture as Code (systems, containers, deployment,
  views, sync) and where each term lives in code.
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
  domain: c4-modeling
  bootstrap: true
---
# Domain map — C4 modeling

System models follow the C4 hierarchy, laid out by `schema/application-schema.json`.[^app-schema-head]

| Term | Meaning | Where it lives |
|---|---|---|
| System model | One `system.yaml` per folder, with `name`, `model` and optional `views` | `model/<id>/system.yaml`, application schema [^app-schema-head] |
| Software system | Primary or external system; has `tags`, `disposition`, `dataClassification` | `SoftwareSystem` definition [^app-schema-classification] |
| Container | Deployable unit inside a system; `id`, `technology`, comma-separated `tags`, open `properties` | `Container` definition [^app-schema-container] |
| Container archetype | `properties.type`, such as `UI`, `API`, `database`, `batch` | `ContainerProperties` [^app-schema-props] |
| Person | Human actor with outbound relationships | `model.people[]` [^model-people] |
| Relationship | Outbound edge with `destinationId`, description and technology | `Relationship` definition [^model-people] |
| Deployment node | Environment-scoped infrastructure that hosts container instances | `model.deploymentNodes[]` [^app-schema-model] |
| View | System-context, container or deployment view used to filter the canvas | `views` and `extractViews` [^model-views][^extract-views] |
| Metadata | Portfolio facts (repos, LoC, deployable units, last scan) beside each model | `metadata.json`, `SystemMetadataSchema` [^meta-zod] |
| New vs legacy format | `model:`-rooted documents vs map-keyed `actors`/`softwareSystems` | `isNewFormat`, `transformNewToOld` [^is-new-format][^new-to-old] |
| Sync source | Store flag (`yaml` or `canvas`) that blocks re-entrant updates | `useGraphStore` [^store-sync] |
| Layout | Dagre auto-layout applied to React Flow nodes | `applyDagreLayout` [^g-dagre] |
| Export | PlantUML and Draw.io serializations of the graph | `exportToPlantUml`, `exportToDrawioXml` [^g-puml][^g-drawio] |

[^app-schema-head]: src · schema/application-schema.json#L1-L27 · sha256:18673960eaa1e78fdc8ba64fd208acc9329d45892fd76dd7fab146d2c7dfc8bd
[^app-schema-classification]: src · schema/application-schema.json#L104-L123 · sha256:0434d4866ec99051bbe2cc39f7ff713293e2e0fdfba4a521a82b9a62e6fc9ac6
[^app-schema-container]: src · schema/application-schema.json#L149-L189 · sha256:5ac78ad1672792072cb7ea20fe3813b2bf6df6a2a636453a6a5e1e2bc66c811c
[^app-schema-props]: src · schema/application-schema.json#L191-L203 · sha256:9461e601c26aaa1eb03c88cb8f5f62bbe5ccfc8bb233b9575796c0102863d30e
[^model-people]: src · model/ecommerce-platform/system.yaml#L5-L17 · sha256:9b9368c56b3698d553b90ae25a038b4d1d34f4c9696113994153d32bdc965090
[^app-schema-model]: src · schema/application-schema.json#L28-L56 · sha256:49b66c78d418382db156417272b8509ecfa2a3a7982783a129b6318c53bfa064
[^model-views]: src · model/ecommerce-platform/system.yaml#L540-L575 · sha256:ebc6074771f254ccf867a16fb3c1e2a2d7924ffb36c79ddcd68b5a3eef290c83
[^extract-views]: src · src/lib/parser/new-to-old-transform.ts#L24-L40 · sha256:e1c26f5884f6f2c09a12588950aaeef25f23b54a6c105ecebd82ef3b4475fffb
[^meta-zod]: src · src/lib/validation/system-schema.ts#L151-L165 · sha256:711cd4c0edfb4b90eb9adbc81d601d53e09fde490680b3d21b9f3a3716f2b5c1
[^is-new-format]: src · src/lib/parser/new-to-old-transform.ts#L11-L22 · sha256:f155cc640f67c8a6847e0cbd6517a30e57256f3cc5c987dde2fd710c680cb09a
[^new-to-old]: src · src/lib/parser/new-to-old-transform.ts#L75-L79 · sha256:2e4b42febe86b5ffc873433d5585901d085ecb31a3965874be66dd852a1c74ec
[^store-sync]: src · src/store/use-graph-store.ts#L14-L30 · sha256:3b67cb7eb507f04558ac7c0402a489cd3b0f7dad528a755f87868f227c99528c
[^g-dagre]: graph · src/lib/layout/dagre-layout.ts::applyDagreLayout
[^g-puml]: graph · src/lib/export/plantuml-export.ts::exportToPlantUml
[^g-drawio]: graph · src/lib/export/drawio-export.ts::exportToDrawioXml

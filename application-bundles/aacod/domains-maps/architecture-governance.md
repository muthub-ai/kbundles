---
type: application-bundle/domain-map
title: Domain map — architecture governance
description: Vocabulary of the governance domain in Architecture as Code (standards, waivers, policies,
  compliance rules, scorecard) and where each term lives in code.
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
  domain: architecture-governance
  bootstrap: true
---
# Domain map — architecture governance

This map covers the terms used to state, check and excuse architecture rules. Each row points to where the term is defined or implemented.[^std-schema-head][^waiver-schema-head]

| Term | Meaning | Where it lives |
|---|---|---|
| Standard | A versioned enterprise rule set with `metadata`, `scope` and `requirements` | `standards/*.yaml`, `schema/standards.json` [^std-schema-head] |
| `standardId` | Standard identifier such as `STD-SEC-001`, nested under `metadata` | `standards/cryptography-key-management.yaml` [^std-yaml-meta] |
| Requirement | One numbered statement with RFC 2119 `severity`, rationale and verification method | `requirements[]` in a standard [^std-req][^std-severity] |
| `publicationStatus` / `lifecycleCategory` | Approval and lifecycle state of a standard | standard `metadata` [^std-yaml-meta] |
| Waiver (exception) | Time-boxed deviation from a standard for one application | `waivers/*.yaml`, `schema/waivers.json` [^waiver-schema-head] |
| `exceptionId` | Waiver ID matching `^EXC-[A-Z]+-[0-9]{3}$` | `schema/waivers.json` [^waiver-schema-id] |
| Waiver status | `PENDING_REVIEW`, `APPROVED`, `REJECTED`, `EXPIRED`, `REMEDIATED` | `schema/waivers.json` [^waiver-schema-status] |
| Compensating control | Mitigation with an effectiveness rating and verification method | waiver `compensatingControls[]` [^waiver-controls] |
| Financial impact | Compliance, delay and risk-exposure cost estimates | waiver `financialImpact` [^waiver-financial] |
| Remediation plan | Target date, backlog link, owning team and percent progress | waiver `remediationPlan` [^waiver-remediation] |
| Compliance rule | One of the five structural lint checks (e.g. `no-frontend-db-bypass`) | `scripts/lint-architecture.ts` [^lint-orchestration] |
| Frontend / database detection | Keyword match on container type, tags and technology | `FRONTEND_*` and `DATABASE_*` keyword lists [^lint-keywords] |
| External system | System tagged `external`, or one with no containers and no `internal` tag | `isExternalSystem` [^lint-external] |
| Policy package | Rego package that produces `deny` messages (`architecture.security`, `.integration`, `.finops`) | `packages/policies/rules/` [^policies-domains] |
| Sensitive tag | `sensitive`, `pii`, `phi`, `pci`, which trigger the KMS encryption rule | `kms.rego` [^kms-sets] |
| Gateway | Container whose technology is a known gateway product or that is tagged `gateway` | `gateway.rego` [^gw-is-gateway] |
| Compliance score | Percent of standards with no approved or pending waiver | `computeExecutiveMetrics` [^metrics-compliance] |
| Active waiver | A waiver with status `APPROVED` (scorecard) or `'approved'` (MCP resource) | compute-metrics and MCP waiver resource [^metrics-active][^mcp-waivers-active] |

*Assessment:* "Active waiver" is defined inconsistently. The scorecard uses the schema's upper-case status, but the MCP resource compares against lower case, so the two surfaces disagree on the same data.[^metrics-active][^mcp-waivers-active]

[^std-schema-head]: src · schema/standards.json#L1-L11 · sha256:69163c5057e191ba3ad81e3fa9580c80e3f43af5e6e9e6c55c4f444143bca36b
[^waiver-schema-head]: src · schema/waivers.json#L1-L22 · sha256:104156c43c28db3f0724b23cf5d53342f3ea26f36614e4b3614e019b62e1ffde
[^std-yaml-meta]: src · standards/cryptography-key-management.yaml#L1-L16 · sha256:76a37faa01ef7593e5108721c7b750b3d1c3119c6df394d808796e9ef2fa8a40
[^std-req]: src · standards/cryptography-key-management.yaml#L57-L62 · sha256:5fffb9abcb7c6291799e412e80d331363305a646e3c8a9a17052522ed306e29d
[^std-severity]: src · schema/standards.json#L213-L221 · sha256:437dcd3587b1b999dccc6ea7ecd8624767d5a297f94d7c10ff9e7028caf43b45
[^waiver-schema-id]: src · schema/waivers.json#L24-L28 · sha256:fe948b86dbf155df2cb91267c4589103ad5443e0ee785811ea214133cc54d195
[^waiver-schema-status]: src · schema/waivers.json#L60-L64 · sha256:9a8a45829de8c6a40d81c522eed428eca69a98006089a97fda8846eb88c46a65
[^waiver-controls]: src · waivers/api-gateway-bypass.yaml#L29-L38 · sha256:c2bc009ea3020312c55be40b036e3b39b37313c2183da2c1768577e0c0bb5487
[^waiver-financial]: src · waivers/api-gateway-bypass.yaml#L15-L23 · sha256:458c3ec3d78eec95dc3e7828fd623b7668e00c384b27dc5a5b2ac114a4fc1812
[^waiver-remediation]: src · waivers/api-gateway-bypass.yaml#L44-L51 · sha256:b47ee6627279b9f03ad344ef0bb3d05662b22b6fb80c469ae2382e1d4b79bbe9
[^lint-orchestration]: src · scripts/lint-architecture.ts#L415-L429 · sha256:c7fbe6b9ca12408ea6f925c743562d90a8195f033b06cf6ed8a8a4a90256bbcd
[^lint-keywords]: src · scripts/lint-architecture.ts#L47-L74 · sha256:a2fbd08d3bf86694486861e4d733e9aa9d2f29730126c1f82d6df1cb6f9b5d88
[^lint-external]: src · scripts/lint-architecture.ts#L148-L163 · sha256:b997b278bb4b5d9a4a983e6c34be1b76bb799a8eb5fca88874a40bbe96611544
[^policies-domains]: src · packages/policies/README.md#L48-L60 · sha256:a8e74072f5c9c687bd1e8b7b82de92d9547436e2ed1ad95c4bdcd3d9e7526717
[^kms-sets]: src · packages/policies/rules/security/kms.rego#L17-L28 · sha256:e5e5f65461d30ec26497d6122254ffaccea14ccf2e016e44ecaae460d65959b5
[^gw-is-gateway]: src · packages/policies/rules/integration/gateway.rego#L17-L29 · sha256:12825ce410d9c23f1233a105b31497871f34da919c2271d42708b7028e839e49
[^metrics-compliance]: src · src/lib/metrics/compute-metrics.ts#L181-L189 · sha256:91768d23f3d34089b11a8fd19c7926601dc450b663b6ab238bf501ca77c8a06b
[^metrics-active]: src · src/lib/metrics/compute-metrics.ts#L161-L166 · sha256:4b908a2411f0041431a963c86e66af0721552192935afeb6fe838caed86e0b5f
[^mcp-waivers-active]: src · mcp-server/src/resources/waivers.ts#L74-L82 · sha256:df8da703c275b42cc1bffffe0bde973e4dd59aa572618452dc75555827b994bf

---
type: application-bundle/security-architecture
title: Security architecture — Architecture as Code
description: Trust boundaries, policy enforcement (lint rules, OPA/Rego, waivers), the MCP and CLI attack
  surface, secrets handling and supply chain for Architecture as Code.
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
  section: security-architecture
  bootstrap: true
---
# Security architecture — Architecture as Code

## Trust boundaries

| Boundary | Crossing | Control in code |
|---|---|---|
| Agent to MCP server | stdio subprocess launched by the IDE with `--root` [^mcp-main][^vscode-mcp] | Root must contain `schema/` and `model/` [^repo-root] |
| CLI to schema host | HTTPS `GET`/`HEAD` to `schemaBaseUrl`, default `raw.githubusercontent.com/.../main/schema` [^cli-config-default] | ETag cache; optional bearer token [^cli-fetch] |
| Pull request to `main` | GitHub Actions pipeline on PR and push [^wf-triggers] | Schema, lint and OPA test jobs gate `assemble` [^wf-assemble-needs] |
| Pipeline to public web | `gh-pages` publish on push to `main` only [^wf-publish] | Runs only when `ref == main` and event is `push` [^wf-publish] |

The web app has no authentication and no write route. Its three pages only read repository files at render time.[^readme-routes][^dashboard-page]

## Policy enforcement layers

Merge-blocking checks are JSON Schema validation (`validate-models`, `validate-standards`, `validate-waivers`) plus the five-rule structural linter. The linter exits 1 when it finds any violation.[^wf-app-arch-steps][^lint-exit]

The linter logs YAML parse errors and skips that file without counting it as a violation.[^lint-loop]

*Assessment:* That gap is covered only because `validate-models` runs first in the same job and fails on unparseable YAML. Run on its own, for example through `npm run lint:architecture`, the linter can report a clean result for a broken model.[^lint-loop][^wf-app-arch-steps]

The three OPA packages encode security, integration and FinOps standards, each with a `_test.rego` companion:[^policies-tree]

- `architecture.security` rejects containers tagged `sensitive`, `pii`, `phi` or `pci` unless `properties.encryption` is `kms`, `envelope` or `hsm`.[^kms-sets][^kms-deny]
- `architecture.integration` rejects containers tagged `external-facing` unless they are a gateway or are the target of a relationship from one. A gateway is identified by its technology keyword or a `gateway` tag.[^gw-is-gateway][^gw-deny]
- `architecture.finops` rejects production `Compute` deployment nodes whose `autoscaling_enabled` is not the string `"true"`.[^rightsizing-deny]

The policies read `input.softwareSystems` and `input.deploymentNodes` at the top level, with tags as one comma-separated string. System YAML nests these under `model:`.[^kms-deny][^rightsizing-deny][^model-root]

In CI the policies job only formats, compiles, unit-tests and measures coverage of the Rego. No step passes a model file to `opa eval`.[^wf-policies]

*Assessment:* At this commit the OPA layer is a tested policy library, not an enforced gate. To enforce it, a step would need to reshape each `system.yaml` into the input the policies expect and fail on a non-empty `deny`.[^wf-policies][^kms-deny][^model-root]

`packages/policies/data/approved-unmanaged-dbs.json` lists approved exceptions for unmanaged databases, but no rule under `rules/` imports it.[^unmanaged-dbs][^policies-tree]

## Waiver handling

The MCP resource `aac://waivers/active` keeps waivers whose `status` is exactly `'approved'`. The waiver schema allows only upper-case values such as `APPROVED`.[^waivers-active][^waiver-status-enum]

The waiver summary reads `exception_id`, but waiver files use `exceptionId`. The README says the active list is "approved, non-expired", yet the code never checks `expirationDate`.[^waivers-read][^waiver-head][^readme-active]

*Assessment:* An agent asking which exceptions are currently sanctioned gets an empty list, and every summary falls back to the file name as its ID. This is a governance-correctness defect on the interface built for AI agents.[^waivers-active][^waivers-read]

`scaffold_waiver` validates its output and then writes `waivers/<app>-<standard>.yaml` whatever the result, reporting schema errors only as "warnings". The write overwrites any existing file at that path.[^waiver-write][^write-text]

Scaffolded waivers always get `exceptionId` `EXC-<CATEGORY>-001`. The committed waivers already use IDs in that series, such as `EXC-INT-001`.[^waiver-id][^waiver-head]

## MCP and CLI input handling

`lint_compliance` puts the caller's `systemId` straight into `path.join(model, systemId, "system.yaml")`. Resource templates do the same with `{id}` and `{filename}`, and none of them normalizes or checks the path.[^lint-systemid][^systems-detail][^waivers-detail]

*Assessment:* A crafted ID such as `../../x` can make the server read any `system.yaml`, or any `*.yaml` for waivers and standards, outside the repository. The process's own file permissions are the only limit. The server is a local stdio process, so exposure is limited to whatever drives the agent, such as prompt-injected content.[^lint-systemid][^waivers-detail][^mcp-main]

The CLI reads `GITHUB_TOKEN` from the environment and sends it as `Authorization: Bearer` on every schema request. The request goes to `schemaBaseUrl`, which a `.aacrc` file in the working directory can override.[^cli-token][^cli-fetch][^cli-read-config]

*Assessment:* Running `aac validate` in a CI job that exports `GITHUB_TOKEN`, inside a repository whose `.aacrc` points at another host, sends the token to that host. Sending the header only to GitHub hosts would close this.[^cli-token][^cli-read-config]

## Supply chain and pipeline permissions

The policies job installs the OPA binary with `curl` from the `latest` URL and does not verify a checksum. The release workflow installs Bun at `latest`.[^wf-opa-install][^rel-bun]

Actions are pinned by major tag (`actions/checkout@v4`, `peaceiris/actions-gh-pages@v4`), not commit SHA. The pipeline grants `contents`, `pull-requests` and `pages` write plus `id-token: write` at workflow level, so every job gets them, PR jobs included.[^wf-checkout][^wf-publish][^wf-permissions]

npm publishing uses a long-lived `NPM_TOKEN` secret.[^rel-npm]

## Data exposure

Models carry a `dataClassification`; the e-commerce system is `Confidential`. The docs builder encodes each diagram's PlantUML source into a `www.plantuml.com` URL, which readers' browsers then request.[^model-classification][^docs-plantuml]

*Assessment:* System names, container technologies and relationships from confidential models are sent to a third-party rendering service each time a page is viewed. A self-hosted PlantUML server, or committing rendered SVGs, would keep that data in-house.[^docs-plantuml][^model-classification]

[^mcp-main]: src · mcp-server/bin/aac-mcp.ts#L7-L23 · sha256:d701f7215b5b5349d5e4a8f99169b8c171e74e8dc1f0a5aa409ffff30e7581ff
[^vscode-mcp]: src · .vscode/mcp.json#L1-L13 · sha256:9539e136fa400875be8a6f4e755e2b61a6fa9ddcc2bc84993c2d472a3bf4627c
[^repo-root]: src · mcp-server/src/lib/repo-resolver.ts#L12-L38 · sha256:65a2e7a49c5c91e7d7c7ae641b394f0e7fdf63c9d43030b8452f7b4a97acd5d0
[^cli-config-default]: src · cli/src/utils/config.ts#L12-L16 · sha256:431086e322c2288cd8814cf0a61c2bdfba1fcd7386c80e6be5d2c776676d1d00
[^cli-fetch]: src · cli/src/schema-manager.ts#L107-L116 · sha256:b57db3ab06c49bb96eb88f0f27b469d281df58397befeccf345975e0e4ca56ae
[^wf-triggers]: src · .github/workflows/aac-pipeline.yml#L27-L31 · sha256:d031dab58b2a5ad96cdea1f00447e50ad5403844ae6f388514bec3832b239cf3
[^wf-assemble-needs]: src · .github/workflows/aac-pipeline.yml#L349-L352 · sha256:f8e133b29623283263f0d2c6bff2a6c55117c9166d925842894dfd8a73189cb0
[^wf-publish]: src · .github/workflows/aac-pipeline.yml#L505-L529 · sha256:b6109c83d9924842458f66a49f433bbf11612e535ec5db2d6131e04b19b6826e
[^readme-routes]: src · README.md#L516-L526 · sha256:2adc0b33a579c9e0faf5eaa3ec94c3e678c6560e122f53d942206a0296d03695
[^dashboard-page]: src · src/app/dashboard/page.tsx#L18-L27 · sha256:967399e5f096a0bb7f8ee42ba78c11fb9e14cc9509f8b1f3d812a9dd6a585077
[^wf-app-arch-steps]: src · .github/workflows/aac-pipeline.yml#L111-L125 · sha256:b9c766b902dad6f456ec501e27e7eb932c9e77860ee99e5d98ccdf46ab861319
[^lint-exit]: src · scripts/lint-architecture.ts#L474-L484 · sha256:92964ef65b8d0efef950366bb3ce769dbf808980c200f75f4074aebecdb84988
[^lint-loop]: src · scripts/lint-architecture.ts#L451-L465 · sha256:25b27fd05b92e31c839ea458a027ffc9314e1e3360ab8dc41f16f18b61614a4f
[^kms-sets]: src · packages/policies/rules/security/kms.rego#L17-L28 · sha256:e5e5f65461d30ec26497d6122254ffaccea14ccf2e016e44ecaae460d65959b5
[^kms-deny]: src · packages/policies/rules/security/kms.rego#L30-L52 · sha256:07a75e0663c1700895e3fc447e9c6fa72ba4af923eed8af1b606e3c153a7c2ab
[^gw-is-gateway]: src · packages/policies/rules/integration/gateway.rego#L17-L36 · sha256:d13ce524bbf4bd06a58ca696e383a892a8507c87852b1799ef1ed7e82e4aa1ca
[^gw-deny]: src · packages/policies/rules/integration/gateway.rego#L45-L68 · sha256:4d43d5a8f320fa97bcc10b625deadd9c1a647c99e50181dbfd5607a13510c11b
[^rightsizing-deny]: src · packages/policies/rules/finops/rightsizing.rego#L16-L28 · sha256:5b9c28e14d4363bd00ac1b84822f32d88e37008e7238f660e5c3e23ed9056846
[^model-root]: src · model/ecommerce-platform/system.yaml#L1-L6 · sha256:e1edb77037250f1744dbf8ebc5741fdca2ee1b3392a77167133bd66a7773dd83
[^wf-policies]: src · .github/workflows/aac-pipeline.yml#L316-L340 · sha256:529b3ac00eda9d61889bddf657dc103029d29b6a26cbf17c9b8625029370a09d
[^unmanaged-dbs]: src · packages/policies/data/approved-unmanaged-dbs.json#L1-L14 · sha256:d0e3693452d192b8c930cd44b7a505352580cdd3f790ac39d7ebfa0163d306d9
[^policies-tree]: src · packages/policies/README.md#L20-L36 · sha256:3f6403378b27455368f139e294caf49172d166549781b046e466388810f765f1
[^waivers-active]: src · mcp-server/src/resources/waivers.ts#L74-L82 · sha256:df8da703c275b42cc1bffffe0bde973e4dd59aa572618452dc75555827b994bf
[^waiver-status-enum]: src · schema/waivers.json#L60-L64 · sha256:9a8a45829de8c6a40d81c522eed428eca69a98006089a97fda8846eb88c46a65
[^waivers-read]: src · mcp-server/src/resources/waivers.ts#L24-L40 · sha256:94a18b3f8e371edc798c5aaafbf85646188cb4117caa86d59d58efc68db72e9a
[^waiver-head]: src · waivers/api-gateway-bypass.yaml#L1-L10 · sha256:273be92aaebadd25b1e7568b7be4eb95be82bed7f1def7f744f5aa738762e33f
[^readme-active]: src · README.md#L171-L171 · sha256:d359ccb0af47dd14a7a720648c96ae9b7828d14a7f1df7b7e1ae5b91619a1285
[^waiver-write]: src · mcp-server/src/tools/scaffold-waiver.ts#L158-L178 · sha256:80a260054a87184a1d04e1cec75c428b726165480f6d17c661b2a08f51f631d8
[^write-text]: src · mcp-server/src/lib/repo-resolver.ts#L80-L86 · sha256:7354f24e3d0792e508d4de8497e14e36154756109baeb482c547fd148c844977
[^waiver-id]: src · mcp-server/src/tools/scaffold-waiver.ts#L101-L106 · sha256:bdc88fd790ed5851eee20ae2e359e552d987e16d8027dc2f1847b8ea3ee7dd78
[^lint-systemid]: src · mcp-server/src/tools/lint-compliance.ts#L443-L459 · sha256:e937fc8c6406eeff9d80f3e821d314f7272b0c8acf1635c1914e9a26dcf00152
[^systems-detail]: src · mcp-server/src/resources/systems.ts#L68-L76 · sha256:176c3f58547d5facb8385db32d07e88970a068711242700d828c1a3f64a4b66d
[^waivers-detail]: src · mcp-server/src/resources/waivers.ts#L107-L116 · sha256:3ab95e6705b5dfc82cdfabb9b0a8dc0e4f58dc5f2f71fdfff313419084ed54c3
[^cli-token]: src · cli/src/schema-manager.ts#L28-L32 · sha256:9392963f847de08a56289613cbc88651288141401fec175de142d29f40c1ac4f
[^cli-read-config]: src · cli/src/utils/config.ts#L18-L30 · sha256:4916f23cf8ff764e5e3606b7776d5fd949146d7724d807d6c551ba00dcc6ee5f
[^wf-opa-install]: src · .github/workflows/aac-pipeline.yml#L310-L314 · sha256:24d3bfb970016545d0ae07cfd4a03039d2430b568f4a89a1a1dafa3a64277397
[^rel-bun]: src · .github/workflows/release-cli.yml#L78-L80 · sha256:f280cd9e3d50332df6b8b008e48c1e4641f24ded55b0c750a97a06fa441f61a5
[^wf-checkout]: src · .github/workflows/aac-pipeline.yml#L65-L67 · sha256:73a9bc0466d404ab1379345b8f3c8e4b617b11b5bf6ab2b348b1a1b6e6a4931c
[^wf-permissions]: src · .github/workflows/aac-pipeline.yml#L41-L52 · sha256:c6c7277453655cbe61c4e9aa7b38dce3f5a75d3c22592ca6f3cdf95d6dc398e8
[^rel-npm]: src · .github/workflows/release-cli.yml#L43-L47 · sha256:bfce03484312eb6c37fa0edccf944222e6066ec806dec8f59d60451e63d60690
[^model-classification]: src · model/ecommerce-platform/system.yaml#L33-L40 · sha256:9bf5cef403997909b6f1744536d3978fb9053167eb811ed8a0f8cd7ba838ab18
[^docs-plantuml]: src · scripts/build-docs.ts#L116-L119 · sha256:4887904199849df0edcf7498319205580b3e4b694426ed96f72ae1f58bd18756

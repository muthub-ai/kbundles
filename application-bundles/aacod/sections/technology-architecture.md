---
type: application-bundle/technology-architecture
title: Technology architecture — Architecture as Code
description: Languages, frameworks, runtimes, build tooling, CI/CD workflows, hosting and dependencies
  of Architecture as Code.
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
  section: technology-architecture
  bootstrap: true
---
# Technology architecture — Architecture as Code

## Languages and runtime

The code is TypeScript compiled with `strict: true` and runs on Node.js 22, pinned in `.nvmrc`. The published CLI and MCP packages declare `node >=18`.[^tsconfig-strict][^nvmrc][^cli-engines][^mcp-engines]

Policies are written in Rego v1 (`import rego.v1`) and run by the OPA CLI, not by Node.[^kms-pkg][^wf-opa-install]

## Frameworks and libraries

| Concern | Library (declared version) |
|---|---|
| Web framework | Next.js 16.1.6, React 19.2.3 [^pkg-deps] |
| Canvas, layout, editor | `@xyflow/react` ^12.10.1, `@dagrejs/dagre` ^2.0.4, `@monaco-editor/react` ^4.7.0 [^pkg-deps] |
| State and validation | Zustand ^5.0.11, Zod ^4.3.6, AJV ^8.18.0 with `ajv-formats` [^pkg-deps][^pkg-devdeps] |
| CLI | Commander ^14, Chalk ^5 (root dev deps); tsup build [^pkg-devdeps][^cli-pkg] |
| MCP | `@modelcontextprotocol/sdk` ^1.12.0, Zod ^3.24.0 [^mcp-deps] |
| Docs and diagrams | `plantuml-encoder`, `@asciidoctor/core`, jsdom (for Draw.io export in Node) [^pkg-devdeps][^build-diagrams-jsdom] |
| Tests | Vitest ^3.2.4 across `src/`, `cli/` and `mcp-server/` [^vitest-config] |

*Assessment:* The root app is on Zod 4, while the MCP server pins Zod 3 for its tool input schemas. That works because the packages install separately, but schema code cannot be shared between them without a migration.[^pkg-deps][^mcp-deps]

## Build and packaging

The root `package.json` scripts call `tsx` for every pipeline step (`validate:models`, `lint:architecture`, `build:diagrams`, `build:docs`, page builders) and shell into `packages/policies` for OPA tests.[^pkg-scripts]

The CLI is built with tsup and its templates are copied to `cli/dist/`. A Bun script produces standalone binaries. The MCP server is built with plain `tsc`, and `prepublishOnly` runs the build.[^cli-pkg][^agents-cli-dist][^mcp-pkg-scripts]

The policy bundle script runs `opa fmt`, `opa check` and `opa test`, then `opa build` into `dist/policies.tar.gz` for an OPA server or sidecar.[^bundle-sh]

## CI/CD workflows

`aac-pipeline.yml` runs on pull requests and pushes to `main`. A new PR run cancels the previous one for the same PR, but runs on `main` are never cancelled.[^wf-triggers][^wf-concurrency]

| Job | Needs | What runs |
|---|---|---|
| `lint-and-test` | none | `npm run lint`, `npm run test:run` [^wf-lint-test] |
| `app-architecture` | lint-and-test | validate-models, lint-architecture, build-diagrams, build-docs [^wf-app-arch] |
| `patterns` | lint-and-test | build-pattern-pages [^wf-patterns] |
| `standards` | lint-and-test | validate-standards, build-standard-pages [^wf-standards] |
| `waivers` | lint-and-test | validate-waivers, build-waiver-pages [^wf-waivers] |
| `policies` | lint-and-test | `opa fmt --fail`, `opa check`, `opa test -v`, coverage [^wf-policies] |
| `assemble` | all five stage-2 jobs | merges artifacts into one `site/` [^wf-assemble] |
| `pr-feedback` | assemble, PR only | upserts a PR comment with PlantUML sources [^wf-pr-feedback][^wf-pr-upsert] |
| `publish` | assemble, push to main | deploys `site/` to `gh-pages` [^wf-publish] |

No job runs `next build`, even though AGENTS.md lists a successful production build as a pre-merge requirement.[^wf-lint-test][^agents-verify]

*Assessment:* A change that breaks the Next.js build can still pass the governance pipeline. The deployed site is a separately generated static microsite, not the Next.js app.[^wf-lint-test][^wf-assemble]

`release-cli.yml` runs on `cli-v*` tags. It tests `cli/`, publishes `@muthub-ai/aac` to npm, builds five Bun binaries (Linux x64/arm64, macOS arm64/x64, Windows x64) and attaches them to a GitHub release.[^rel-trigger][^rel-npm][^rel-matrix][^rel-release]

The MCP server has no release workflow. Its package is publishable only through `prepublishOnly` from a developer machine.[^mcp-pkg-scripts][^rel-trigger]

## Hosting and external services

The workflow publishes the assembled static site to GitHub Pages with `peaceiris/actions-gh-pages`. The README names `aac.muthub.org` as the live site.[^wf-publish][^readme-live]

Generated HTML embeds diagrams as `https://www.plantuml.com/plantuml/svg/<encoded>` URLs, so readers' browsers fetch diagram rendering from the public PlantUML server.[^docs-plantuml]

[^tsconfig-strict]: src · tsconfig.json#L7-L7 · sha256:5b5b3bcc1ac14604cb229098e9105bdb9736a0214cda9d14209e75a36a56b1c0
[^nvmrc]: src · .nvmrc#L1-L1 · sha256:f14b4987904bcb5814e4459a057ed4d20f58a633152288a761214dcd28780b56
[^cli-engines]: src · cli/package.json#L36-L38 · sha256:be7dff9d626533c1469968ae5493a766ddbc1d4cd132f23e3d48bb20e5daa2d8
[^mcp-engines]: src · mcp-server/package.json#L36-L38 · sha256:be7dff9d626533c1469968ae5493a766ddbc1d4cd132f23e3d48bb20e5daa2d8
[^kms-pkg]: src · packages/policies/rules/security/kms.rego#L13-L15 · sha256:fe26bef2159a18308e76e9dacfbee72b3ce15e2fb16522c20328da3ce969a39f
[^wf-opa-install]: src · .github/workflows/aac-pipeline.yml#L310-L314 · sha256:24d3bfb970016545d0ae07cfd4a03039d2430b568f4a89a1a1dafa3a64277397
[^pkg-deps]: src · package.json#L27-L47 · sha256:c93f8db2f63d31b1f7f72855e2b910057ff96964bc371f521339bc7266f494bd
[^pkg-devdeps]: src · package.json#L48-L71 · sha256:60b07a8fd044bdb601985e7d0bad6dde1ee723d956b92cc9836e4b488da9e3b0
[^cli-pkg]: src · cli/package.json#L13-L18 · sha256:0cc60d63966004724e07e8b81d4a281eaad8d7ba17d0f161d328331e5edfd9db
[^mcp-deps]: src · mcp-server/package.json#L39-L45 · sha256:da4e0363f4ecf2067611e17d3e641d2a3dc3091e3b74d988fc3cb0a4733c16a4
[^build-diagrams-jsdom]: src · scripts/build-diagrams.ts#L10-L16 · sha256:f62f8b6b8dc987eb4b7dbbc91d75b6b4803d066e4e8612205a19357a543149a2
[^vitest-config]: src · vitest.config.ts#L5-L12 · sha256:c60a82c80023f4e575c4a23d8c5a25453a9a422b5768bda6e42ec7789f7f3fa2
[^pkg-scripts]: src · package.json#L5-L26 · sha256:d5481d203a48c97723ff6b99314a5eb7f967422fb04bd1e5c691fa4bcc240348
[^agents-cli-dist]: src · AGENTS.md#L73-L85 · sha256:2907c9c060f2c384670c27994d8fae163dab340f7f3bafd0f2492926af4da751
[^mcp-pkg-scripts]: src · mcp-server/package.json#L13-L18 · sha256:9933c6609a9b09dec381fe2c0dc03fd5e5bd3a912ef09f0326ee807d395dbb87
[^bundle-sh]: src · packages/policies/scripts/build-bundle.sh#L18-L35 · sha256:525ffba0853d9b9d91cfbfce8eb8cc5900f52f1e4c52f94e312d5ce251d0d081
[^wf-triggers]: src · .github/workflows/aac-pipeline.yml#L27-L31 · sha256:d031dab58b2a5ad96cdea1f00447e50ad5403844ae6f388514bec3832b239cf3
[^wf-concurrency]: src · .github/workflows/aac-pipeline.yml#L37-L39 · sha256:4a8354d78fad73297255882009bcf1e24ae1422c08bbdd754e565dcdbc44060d
[^wf-lint-test]: src · .github/workflows/aac-pipeline.yml#L61-L84 · sha256:0d621f41beabf1d47564be41ce5efa0d352baabe37b437f339bed13f2862523f
[^wf-app-arch]: src · .github/workflows/aac-pipeline.yml#L93-L140 · sha256:096a49b158c848d4b3f5a3ae378de9ae5d5421da6219a706acffc0529ece39ec
[^wf-patterns]: src · .github/workflows/aac-pipeline.yml#L164-L188 · sha256:80ffaecadbb3210b43bd0785e80f70e4938f35cdc6259bb892209ebae5d70a19
[^wf-standards]: src · .github/workflows/aac-pipeline.yml#L205-L236 · sha256:092adc9099860f6a76c497dbd2e932c04fa21cc6e4658b240a0c9a6c0d594df1
[^wf-waivers]: src · .github/workflows/aac-pipeline.yml#L253-L285 · sha256:a09f0666f6160e89e39a00364eac0fc6f390b8bc7d78f2ef1095efcbfea8e454
[^wf-policies]: src · .github/workflows/aac-pipeline.yml#L301-L340 · sha256:03b1d7dbfd2421e09fecf1a98d2a9f78d40255505f24c1d1290ade6179c83eeb
[^wf-assemble]: src · .github/workflows/aac-pipeline.yml#L349-L387 · sha256:a44db1f1b1b81142670a56a940ff914b958e588816437d36cd05b0ef4a7ef5cc
[^wf-pr-feedback]: src · .github/workflows/aac-pipeline.yml#L404-L408 · sha256:2065db95a21393be5a1780896518c2d525f540996c585790b3c804a02de2d749
[^wf-pr-upsert]: src · .github/workflows/aac-pipeline.yml#L473-L497 · sha256:2fd46dac4a435ab002c03e79487fb10fe02a9a4c1a3537b83876f33d781bb602
[^wf-publish]: src · .github/workflows/aac-pipeline.yml#L505-L529 · sha256:b6109c83d9924842458f66a49f433bbf11612e535ec5db2d6131e04b19b6826e
[^agents-verify]: src · AGENTS.md#L91-L98 · sha256:bc7ace037788fd23d9965de7ec58ab352f392efbd45386108fe8cd44df0f33d8
[^rel-trigger]: src · .github/workflows/release-cli.yml#L1-L9 · sha256:aae0f4489096f523c38b7fcc7a50be59230296bb7a3383f17640144d97a96558
[^rel-npm]: src · .github/workflows/release-cli.yml#L28-L47 · sha256:0462355af5001b805074362f6aaea2a7703cd306292cef1187926119ecbe7900
[^rel-matrix]: src · .github/workflows/release-cli.yml#L52-L89 · sha256:8c479950fb6f1528862768706abb7729954b01c108a2ef6a49cf4f399d4bfc6d
[^rel-release]: src · .github/workflows/release-cli.yml#L99-L114 · sha256:793b0350c983e1a4b2b8aab12e6017a9c8009a70ec8f0f82171a7904de730afe
[^readme-live]: src · README.md#L66-L70 · sha256:b372ac7ae3a3de3365b5121488d45ea3ff9c00bd274fb6280b811106c00384c3
[^docs-plantuml]: src · scripts/build-docs.ts#L116-L119 · sha256:4887904199849df0edcf7498319205580b3e4b694426ed96f72ae1f58bd18756

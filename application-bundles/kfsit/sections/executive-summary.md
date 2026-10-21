---
type: application-bundle/executive-summary
title: Executive summary — Knowledge Foundation site
description: What the Knowledge Foundation site is, who it serves, and its shape in one screen.
generated:
  by: process:building-application-bundles@0.1.0
  at: '2026-10-20T19:30:00-05:00'
sources:
- id: repo
  kind: source-repo
  repo: muthub-ai/knowledge-foundation-site
  commit_sha: 3afac247ec2848aa9d8844a83f1fc982eb6a6dc0
- id: graph
  kind: code-graph
  path: code-graph/code-graph.jsonl
  sha256: 7cce3a8bffd531894689010170006598998a6a2289a14595ccd4f2dfbb604d22
x_kf:
  schema: kf-application-bundle/1
  appid: kfsit
  bundle_kind: application
  section: executive-summary
  bootstrap: true
---
# Executive summary — Knowledge Foundation site

## What it is

The Knowledge Foundation site is the static build that produces wiki.muthub.org: note pages rendered by Quartz 5 and a home page that is a Sigma.js 4 (WebGL) explorer over the knowledge graph.[^readme-what]

It reads exactly one input, a release of the `muthub-ai/knowledge-foundation` repository made of `bundle.tgz` and `graph.json`, and imports no code from that repository.[^readme-what][^s01]

## Shape

The build is a three-step pipeline driven by `scripts/build.sh`: `kfsite stage` turns the OKF bundle into Quartz content, `quartz build` renders it at a pinned Quartz commit, and `kfsite post` finishes `public/` with JSON-LD, Markdown twins, `llms.txt` and the explorer.[^build-steps][^main-doc]

| Part | Language | Role |
|---|---|---|
| `kfsite/` (`stage.py`, `post.py`, `bundle.py`) | Python | bundle reading, staging and post-processing [^g-stage][^g-post][^g-bundle] |
| `explorer/src/explorer.ts` | TypeScript | the graph explorer, bundled by esbuild into a committed `explorer/dist/explorer.js` [^g-explorer][^esbuild] |
| `scripts/` | Bash, Python, Node | build orchestration, release download, Quartz config generation [^build-steps] |
| `vercel.json` | JSON | hosting: build command, clean URLs, security headers and CSP [^vercel-build] |

## Why it matters

Every note page opens with a provenance callout that states its review state, last verification date, drafting process, re-check date and number of sources, so readers see how far to trust a note before reading it.[^callout]

Machine-extracted entities from the semantic layer are kept apart in the explorer: they are typed `Entity`, hidden by default, and excluded from note counts.[^s06]

*Assessment:* The release-only coupling makes the site a pure renderer of governed content: it can be rebuilt from any release tag, and it never becomes a second place where knowledge is edited.[^s01]

*Assessment:* The design leans on deterministic, inspectable artifacts (a pinned Quartz commit, a committed explorer bundle, a generated Quartz config) rather than live dependencies, which favours reproducibility over convenience.[^build-steps][^esbuild]

[^readme-what]: src · README.md#L12-L14 · sha256:6eeb2af4f8facc90e47278d19da0adb8a47c5c26244fbf2ee9438ac06e169ff4
[^s01]: src · docs/decisions/S01-release-assets-are-the-only-coupling.md#L10-L13 · sha256:0e8fd2a221f97eaad2dd1e5a5a6ff321998c1523c726d826dee35255a31852a2
[^build-steps]: src · scripts/build.sh#L40-L58 · sha256:e5513efc35e0354623bf6f1d77537052e36614444519c654e2edc25ed8c0e6f3
[^main-doc]: src · kfsite/__main__.py#L1-L7 · sha256:ce0bd894c98c01d3829373f07649cda51013c6072df231022f62fa11f7ffdfc7
[^g-stage]: graph · kfsite/stage.py
[^g-post]: graph · kfsite/post.py
[^g-bundle]: graph · kfsite/bundle.py
[^g-explorer]: graph · explorer/src/explorer.ts
[^esbuild]: src · scripts/build_explorer.mjs#L29-L43 · sha256:4fe5a93d7de5e66479bc043a01d6d3815b51ea7ea6e0b4d1ae06582dc2ac9e45
[^vercel-build]: src · vercel.json#L3-L9 · sha256:a47a64bb6c111c4a276fd49bcf07a50d4217a9ea2f2d254bd89a1000e5f87953
[^callout]: src · kfsite/stage.py#L73-L94 · sha256:ea91b135f6f6b9dbad39b603bb3318515ac580765a60c1abf502397859270dda
[^s06]: src · docs/decisions/S06-machine-structure-is-labelled-hidden-and-counted-apart.md#L10-L15 · sha256:e92a449098b10deef1ce6ee84fdf8c19865c4b1ee752e12188b976ed29148247

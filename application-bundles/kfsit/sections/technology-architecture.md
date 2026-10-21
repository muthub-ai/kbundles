---
type: application-bundle/technology-architecture
title: Technology architecture — Knowledge Foundation site
description: Languages, frameworks, pinned dependencies, build tooling, CI and Vercel hosting of the Knowledge
  Foundation site.
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
  section: technology-architecture
  bootstrap: true
---
# Technology architecture — Knowledge Foundation site

## Languages and runtimes

The build needs Python 3.12 and Node 22; the README states both, and `package.json` declares `node >=22`.[^readme-qs][^pkg]

The only Python runtime dependency is PyYAML 6.0.3; Markdown 3.10.3 is a development dependency used only by the Quartz stand-in in tests.[^req][^req-dev]

## Pinned dependencies

| Dependency | Pin | Used for |
|---|---|---|
| Quartz 5 | commit in `quartz.ref` | rendering note pages [^quartz-ref][^build-quartz] |
| `sigma` | 4.0.3 | WebGL graph rendering in the explorer [^pkg] |
| `graphology` | 0.26.0 | in-memory graph model for the explorer [^pkg] |
| `esbuild` | 0.28.2 | bundling `explorer.ts` into an IIFE for ES2020 [^pkg][^esbuild] |
| `@playwright/test` | 1.56.1 | browser tests on desktop Chrome and a Pixel 7 profile [^pkg][^pw-config] |

The explorer bundle can also be built offline from source checkouts of the same Sigma, graphology and events versions using `--from-source`.[^esbuild-src]

## Quartz configuration

`scripts/make_quartz_config.py` starts from Quartz's own `quartz.config.default.yaml`, disables a fixed set of community plugins (Quartz's graph among them), enables tag lists, sets plugin options, and validates the result against Quartz's JSON Schema.[^qcfg-off][^qcfg-make]

The generated config sets `markdownLinkResolution: absolute` for crawl links, which matches the site paths that `kfsite stage` writes.[^qcfg-opts][^stage-doc]

## Build and hosting

Vercel runs `bash scripts/vercel_build.sh` with no framework preset, publishes `public/` and serves clean URLs without trailing slashes.[^vercel-build]

`vercel_build.sh` picks the newest Python at or above 3.11.4 (installing 3.12 with `dnf` if none is found), creates a virtual environment, installs requirements and runs `build.sh`, teeing output to `.build/vercel.log`.[^vbuild-py][^vbuild-run]

On a failed preview build the script replaces `public/` with a `noindex` page showing the last 200 log lines and exits 0; production and non-Vercel runs fail normally.[^vbuild-fail]

Vercel's `ignoreCommand` skips builds for `ci/*` branches and for production builds from any ref other than `main`.[^vercel-build]

`pip_install.sh` retries a failed install with `--break-system-packages`, then with `--user`, to cope with externally managed Python images.[^pip]

## Continuous integration

The `ci` workflow runs on every pull request and on pushes to `main`, with read-only `contents` permission at workflow level.[^ci-trigger]

Its `build and test` job clones the knowledge repository's `main`, builds its graph, runs the unit tests, runs the full Quartz build, checks the explorer bundle and lockfile for drift, and runs Playwright tests.[^ci-kf][^ci-unit][^ci-drift][^ci-pw]

`.github/ci-run.sh` wraps each step and, on failure, repeats the last 120 output lines as GitHub error annotations split into parts of at most 3,500 bytes.[^ci-run]

`tests/serve.py` serves `public/` with Vercel-like clean URLs and replays the response headers declared in `vercel.json`, so browser tests run under the production CSP.[^serve]

*Assessment:* Pinning by commit (Quartz), exact version (npm and pip) and a committed bundle with a CI drift check gives three independent guards against "works on my machine" builds; the cost is a manual commit every time the explorer changes.[^quartz-ref][^pkg][^ci-drift]

*Assessment:* The preview-failure page is an operational workaround for missing Vercel logs; because it exits 0, a failed preview looks like a successful deployment, so the GitHub check rather than the Vercel status must stay the merge gate.[^vbuild-fail][^ci-trigger]

*Assessment:* Replaying `vercel.json` headers in the local test server turns a hosting configuration into something the test suite exercises, a cheap way to catch CSP regressions before deploy.[^serve]

[^readme-qs]: src · README.md#L49-L51 · sha256:530eff24579426580940d1d3951942c637201c179c42c0e39209e85b0a015291
[^pkg]: src · package.json#L11-L18 · sha256:04a20739e34ab9dd4c7f86052505bd5b00da9df2f27374f1d6a26c21e5f31d20
[^req]: src · requirements.txt#L1-L1 · sha256:0969da99a0bc2a1b71ed50584560f4588a37567ac63af3ddbaf3c4617ca5621a
[^req-dev]: src · requirements-dev.txt#L1-L1 · sha256:762961495ec9d91ec9bda2c0e0561232b8891c64f8b7c93423ea69ab4213549c
[^quartz-ref]: src · quartz.ref#L1-L1 · sha256:80995c357c6bcafa3081b0bbb5a0be1aff20e507dec748424f0d9eb6d64b9784
[^build-quartz]: src · scripts/build.sh#L40-L56 · sha256:08e871141b6d66d4931125602fa06acc8a3db9243cad066d475c75eb4cbf7cb2
[^esbuild]: src · scripts/build_explorer.mjs#L29-L43 · sha256:4fe5a93d7de5e66479bc043a01d6d3815b51ea7ea6e0b4d1ae06582dc2ac9e45
[^pw-config]: src · playwright.config.ts#L17-L20 · sha256:c89c4b39294b3e7fb888a962664bd6078d94c3ac1a4ccd6091ceb31633aa1eae
[^esbuild-src]: src · scripts/build_explorer.mjs#L1-L27 · sha256:9307e6532302e8a355a2b68aea9138040911fc1177080a535c15b74ae16c2470
[^qcfg-off]: src · scripts/make_quartz_config.py#L20-L27 · sha256:b88ee2a32a995a26032ffba08c6caad225e484e1c6dbb5bd682a5561153ab106
[^qcfg-make]: src · scripts/make_quartz_config.py#L57-L78 · sha256:dab121346a440c54ca11a3c61c049a19480595f40648f39153bda6a30fd590d8
[^qcfg-opts]: src · scripts/make_quartz_config.py#L28-L35 · sha256:0e375bbadb022d9311e42576b492c36369fbbca0534387b4add853f07749aa22
[^stage-doc]: src · kfsite/stage.py#L9-L11 · sha256:bffc6b2774f7056781fa2be65f5676b38ab1a54a5cbfd35c189ee29b7b299e5c
[^vercel-build]: src · vercel.json#L3-L9 · sha256:a47a64bb6c111c4a276fd49bcf07a50d4217a9ea2f2d254bd89a1000e5f87953
[^vbuild-py]: src · scripts/vercel_build.sh#L11-L30 · sha256:c5c6684863b3c2f402eee3de8d162c92e2f30d0f8f8a538a77b54c3efc824a16
[^vbuild-run]: src · scripts/vercel_build.sh#L31-L38 · sha256:24aac186e024be95e18747a691432db5f081466668f831d47b24e732eb0e3bc9
[^vbuild-fail]: src · scripts/vercel_build.sh#L39-L48 · sha256:b744e5cb59c78e85cc94babbb7893a22e532f8f4dd68a45ca56bfcdc61686952
[^pip]: src · scripts/pip_install.sh#L1-L10 · sha256:e7ec26d8bda1c345dd8990144cb49aad8cdfc0970335e656ff0a36769ee8882e
[^ci-trigger]: src · .github/workflows/ci.yml#L3-L12 · sha256:1b1bb4c3144e3a0ad6f28b6727c4cc9c89d90d7696afd1f120e785b6bb4a5a16
[^ci-kf]: src · .github/workflows/ci.yml#L22-L33 · sha256:f8bc765e9dcf82a1e884a17298a8587e920e9527f79edff7603d1c8fb57a1858
[^ci-unit]: src · .github/workflows/ci.yml#L37-L45 · sha256:c9b52af82024310b2c2700483084fe07ed2dc7ae4661a8b9f89ea883ac4b00f4
[^ci-drift]: src · .github/workflows/ci.yml#L48-L58 · sha256:9d7c04d3316036f5ad8c7663640965649b249470cd5f93cf9db5ae8496f9304f
[^ci-pw]: src · .github/workflows/ci.yml#L63-L68 · sha256:0e71fd3008dd3ffc8c6da027e1f11f017ae89e13d8de615eaa91bdea6ac83732
[^ci-run]: src · .github/ci-run.sh#L1-L21 · sha256:f6be3830ad1207c7cf3ce950539d2071f410b653fe5d6823ef619bab227429c8
[^serve]: src · tests/serve.py#L1-L34 · sha256:c12e8b8e40e12e7c82345053ebbeb1d358dab8eced18f8ac80fc9837723d9742

---
type: application-bundle/executive-summary
title: Executive summary — Portfolio website (muthub.org)
description: What the muthub.org portfolio site is, who reads it, and its shape on one screen.
generated:
  by: process:building-application-bundles@0.1.0
  at: '2026-10-20T19:30:00-05:00'
sources:
- id: repo
  kind: source-repo
  repo: muthub-ai/muthu-v0-portfolio-website
  commit_sha: 8bca37ea8df4e3f6365c20a323bcd680c986a568
- id: graph
  kind: code-graph
  path: code-graph/code-graph.jsonl
  sha256: c30e501c460d37c9779b2d401e1e376a2e5c0290377d4b5c5d3a5ba92fbfe70d
x_kf:
  schema: kf-application-bundle/1
  appid: folio
  bundle_kind: application
  section: executive-summary
  bootstrap: true
---
# Executive summary — Portfolio website (muthub.org)

## What it is

The application is the site owner's personal publication at muthub.org: essays and shorter notes in five themes, initiatives written as case studies, playbooks with a browser-only self-assessment, site search and dark mode.[^readme-readers][^site-themes]

It is written for two audiences at once. Human readers get HTML pages; agents get a Markdown twin of every page, `/llms.txt`, RSS, a sitemap and schema.org JSON-LD.[^readme-agents][^adr-m02]

## Shape on one screen

| Concern | How the code handles it |
|---|---|
| Content | Typed TypeScript objects in `content/*.ts`; no CMS, publishing is a pull request [^adr-m01] |
| Rendering | Next.js 14 App Router pages and route handlers under `app/`, statically generated [^pkg-next][^md-route] |
| Agent readability | `app/md/[[...path]]` renders Markdown twins; `next.config.mjs` rewrites `/<page>.md` to it and marks it `noindex` [^next-headers][^next-rewrites] |
| Confidentiality | `scripts/check-public-content.mjs` runs before `next build` against a private term list [^pkg-build][^guard-header] |
| Integrity | Playwright content rules check dates, forward citations, links and house style on every pull request [^ci-checks] |
| Hosting | Vercel deploys `main`; CI plus branch protection decide what reaches it [^ci-header] |

## Why it matters

The site is the public front of the site owner's writing and links to the Knowledge Foundation graph at wiki.muthub.org through a header link and a home-page band that degrades to fixed counts when the wiki is unreachable.[^nav-graph][^kf-band]

*Assessment:* The architecture is deliberately small: one content source feeds HTML pages, Markdown twins, the search index, RSS and the sitemap, so the agent-facing and human-facing views cannot drift apart without a code change.[^adr-m01][^adr-m02][^md-route]

*Assessment:* Its distinctive engineering lies less in rendering than in governance of what may be published: a confidentiality guardrail and date-integrity rules both run before a deploy can happen.[^guard-header][^ci-checks]

[^readme-readers]: src · README.md#L15-L17 · sha256:d8f2ea58790a9805fb0380d3390504806b559d1c22b0e79b98bbd323c9f8088a
[^site-themes]: src · content/site.ts#L58-L66 · sha256:afa66191bd57f6476683cac40ca86823fac3a1aeb6dd95b5bbc2cf4d77b5107a
[^readme-agents]: src · README.md#L18-L18 · sha256:4ad578374c14c4e0e03760de8aeb1b770d90e20ce664756f9b9ff8b997446253
[^adr-m02]: src · docs/decisions/M02-readable-by-agents.md#L9-L16 · sha256:b9f0b14677710725b6225ff081bc321c180dd6e53b39df07b920ce846984740e
[^adr-m01]: src · docs/decisions/M01-content-as-typed-code.md#L9-L18 · sha256:9063d7c08b0faef26389b65437e25af95d401c412800b02de8635288ef02a9e9
[^pkg-next]: src · package.json#L54-L58 · sha256:cef0d404475ec2c3e3a03af1a70c7fc0db462c07fa5f19ed45a84a9b8d3a250a
[^md-route]: graph · app/md/[[...path]]/route.ts::render
[^next-headers]: src · next.config.mjs#L43-L51 · sha256:813e0c99488cfbc39957024bfa366d13a13acf0a9c275c2a224c08ab52d02f0d
[^next-rewrites]: src · next.config.mjs#L83-L91 · sha256:e14b0962fca5e53857e284927adcdbd39c08635028c4a7d68399bc9ebdfa359f
[^pkg-build]: src · package.json#L5-L7 · sha256:9088f3d59948ce55edb114d05ecf9afa4339031cb68c49e289bb3ae5de7c49a9
[^guard-header]: src · scripts/check-public-content.mjs#L2-L15 · sha256:8e7b7b915d8b81856e294f323a0fbe9ef82a6af37f8df68530f5a4c44a0971f6
[^ci-checks]: src · .github/workflows/ci.yml#L30-L42 · sha256:c0091b74ab5b85091a8a2238306ff40216bba6ec56f302d2fc8135022af495f4
[^ci-header]: src · .github/workflows/ci.yml#L1-L9 · sha256:a0f4c45d2f2562dc9fa8ad2987ffc667d92f9ef37ce4c5da5ec0c4bbe83cb18d
[^nav-graph]: src · content/site.ts#L49-L56 · sha256:15dadbe17752ca6d0273a1ace3bb59b1b77bff50e496495302b2fe69c21fdc04
[^kf-band]: src · components/knowledge-foundation-band.tsx#L3-L27 · sha256:da1df272bb7d6eb282f8478295fd07a6354538ecc6cf82ca32c686bdce603873

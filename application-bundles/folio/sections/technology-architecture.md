---
type: application-bundle/technology-architecture
title: Technology architecture — Portfolio website (muthub.org)
description: Languages, frameworks, dependencies, build, CI/CD and hosting of the muthub.org site.
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
  section: technology-architecture
  bootstrap: true
---
# Technology architecture — Portfolio website (muthub.org)

## Stack

| Layer | Technology |
|---|---|
| Framework | Next.js 14.2.16 App Router with React 18 [^pkg-next] |
| Language | TypeScript in strict mode with the `@/*` path alias [^tsconfig] |
| Styling | Tailwind CSS 3 with colours mapped from CSS variables so light and dark themes share one palette [^tailwind][^pkg-dev] |
| Theming | `next-themes` class-based provider with system default [^layout-theme] |
| Fonts | Newsreader and Instrument Sans through `next/font/google` [^layout-fonts] |
| Analytics | Vercel Analytics, Speed Insights and Microsoft Clarity loaded lazily [^layout-analytics] |
| Tests | Playwright for content rules and end-to-end tests [^pkg-dev][^pw-config] |
| Tooling scripts | Node ESM scripts for the guardrail and link checks; a Python script (Pillow, fontTools) for social cards [^og-header] |

## Dependencies

`package.json` declares 27 Radix UI packages and other UI libraries such as `cmdk`, `recharts`, `vaul`, `zod` and `react-hook-form`, several pinned only to `latest`, under the package name `my-v0-project`.[^pkg-name][^pkg-radix][^pkg-libs]

The small helper layer that is in use includes `lib/utils.ts::cn`, which merges class names with `clsx` and `tailwind-merge`.[^g-utils][^utils]

*Assessment:* The code graph records the Radix and other UI packages only as declarations in `package.json`, with no importing source file, so they look like scaffold carry-over from the project's v0 origin; pruning them and replacing `latest` with fixed versions would shrink the install and make builds more reproducible.[^pkg-name][^pkg-radix][^pkg-libs]

The repository carries both `pnpm-lock.yaml` and `package-lock.json`; CI installs with pnpm 10 and `--frozen-lockfile`, and the replication plan notes that pnpm 9 refuses the workspace file.[^ci-setup][^plan-pnpm]

*Assessment:* Only the pnpm lockfile is enforced by CI, so the npm lockfile can drift without anyone noticing.[^ci-setup]

## Build

`pnpm build` runs the public-content guardrail and then `next build`.[^pkg-scripts]

`next.config.mjs` sets `typescript.ignoreBuildErrors` and `eslint.ignoreDuringBuilds`, and CI compensates with a separate `tsc --noEmit` step.[^next-ignore][^ci-tsc]

Images are served as AVIF or WebP, and the `X-Powered-By` header is disabled.[^next-images][^next-powered]

Every content route is statically generated; the only periodic regeneration is the home page's Knowledge Foundation band, which revalidates its `graph.json` fetch hourly.[^md-static][^kf-fetch]

## CI/CD

| Workflow / job | Trigger | Steps |
|---|---|---|
| `ci.yml` · types and content rules | pull request, push to `main`, manual | blocklist secret present, guardrail, `tsc --noEmit`, Playwright content rules [^ci-checks] |
| `ci.yml` · build, end-to-end tests, links | after the first job | `pnpm build`, Playwright site and feature tests against the production build, internal link check [^ci-build] |
| `weekly-links.yml` | Mondays 12:17 UTC, manual | external link check against the live site; opens or comments on one issue [^weekly] |

`.github/ci-run.sh` wraps test steps and re-emits the last 120 lines of a failure as GitHub error annotations split into parts of at most 3,500 bytes.[^ci-run]

In CI, Playwright runs Chromium only, with one worker and two retries; locally it runs Chromium, Firefox and WebKit.[^pw-config]

`ci.yml` cancels superseded runs per ref and grants only `contents: read`.[^ci-header]

## Hosting

Vercel builds the repository with `main` as the production branch, serves the apex domain and manages its DNS.[^plan-vercel]

A host-matched redirect sends the old `muthu-m9.vercel.app` production host to muthub.org with a 301, leaving preview deployments untouched.[^next-redirect]

Rollback is by promoting the previous Vercel production deployment or reverting the merge.[^ops]

*Assessment:* Hosting is fully managed: there is no server, database or container to operate, and the operational surface is the CI pipeline plus Vercel's deployment history.[^plan-vercel][^ops]

[^pkg-next]: src · package.json#L54-L58 · sha256:cef0d404475ec2c3e3a03af1a70c7fc0db462c07fa5f19ed45a84a9b8d3a250a
[^tsconfig]: src · tsconfig.json#L2-L24 · sha256:a945d510b0765aa903f33c96a25eb876814824d6f42aeb204a56b482c872f7f8
[^tailwind]: src · tailwind.config.ts#L1-L12 · sha256:11795b0135ed8b6c745831c606557577616124365de1c2bf0800a7cf8dfedd51
[^pkg-dev]: src · package.json#L69-L82 · sha256:f5b39f188aab6917a6dbb799940eabe398e4c5d150c5096b8939a13e75d22f72
[^layout-theme]: src · app/layout.tsx#L46-L50 · sha256:68563fb8c2d2e45a9d9ae2abead43e1a2af7b147dfe390900f231bfde5f4f827
[^layout-fonts]: src · app/layout.tsx#L15-L16 · sha256:4bf9545c201081cd1674950a6df9a5d48172ecf0796a54ceff7cbd1d07e47abd
[^layout-analytics]: src · app/layout.tsx#L63-L68 · sha256:8ff1e027e323b254804a6a240ac4d64c5d53f203b1c60e319b10a27e88156b69
[^pw-config]: src · playwright.config.ts#L1-L39 · sha256:43689f14c43cac8d22cf309533423ce4f543f618514d72a8a3f987f8509a75f0
[^og-header]: src · scripts/og/make-images.py#L1-L11 · sha256:fab688c8387a986f41cc53f4801c853f10fbbfdcc02656b35af347d776829166
[^pkg-name]: src · package.json#L2-L2 · sha256:d1a3e1f7f3eb724a7393476ab9792d174892ff1ecec610dc78c06f113d9ecc35
[^pkg-radix]: src · package.json#L14-L42 · sha256:9c25114ed0a528135bbdebc7375fdb758cd851c49925e9e055d01e58690f4cc2
[^pkg-libs]: src · package.json#L43-L67 · sha256:1309e4265429c4ea64951ce06f7c4f67cbe1217321f18d84ba9a9da45be1c0ca
[^g-utils]: graph · lib/utils.ts::cn
[^utils]: src · lib/utils.ts#L1-L6 · sha256:7c8c3dfc0cdd370d44932828eb067ef771c8fe7996693221d5d4b90af6d54f2d
[^ci-setup]: src · .github/workflows/ci.yml#L24-L29 · sha256:b2674b08d244a318805cca2e0066861885bc527fdf4a48078757ed4208e33856
[^plan-pnpm]: src · docs/plan/04-quality-gates.md#L15-L16 · sha256:8b3f3c73a56520512339e5a95853dd93f55d9e19713ed34a6178b93f1e7272eb
[^pkg-scripts]: src · package.json#L5-L13 · sha256:12819f83b5bd13ba2716649c39bd9377a9ab1cbdefefed92e874230c6c04980b
[^next-ignore]: src · next.config.mjs#L52-L57 · sha256:02599837a22893c661632bc364d9de8f2997927bcafe2339f7c1d22c2661274a
[^ci-tsc]: src · .github/workflows/ci.yml#L36-L39 · sha256:a86771abac6218b053236aee83adcac2959382fdd9d7085f0883d554133a272a
[^next-images]: src · next.config.mjs#L58-L61 · sha256:3297d3ff2a98a15f3137c66cc0a0d9a500ea686c6afc0f8f775e0261fe371938
[^next-powered]: src · next.config.mjs#L39-L42 · sha256:f455b7aa266ac4057bc20d64e51f26dce16be062039abb7852d9068a0ef4d289
[^md-static]: src · app/md/[[...path]]/route.ts#L20-L22 · sha256:15e771c8889e5e825977686a75351b7f65aead146cda53898cd7a6baf7528bfd
[^kf-fetch]: src · components/knowledge-foundation-band.tsx#L12-L16 · sha256:79e8cbbf28e09e6b80d4150c4a9ffb86bc2d1d46ae69f2187ab8e4b95015386c
[^ci-checks]: src · .github/workflows/ci.yml#L18-L42 · sha256:6e4451205d29455e7f8f10e53c9227e03dff1678de06dcbf072a2aa0cefdaeb5
[^ci-build]: src · .github/workflows/ci.yml#L44-L71 · sha256:f6b84f372ca7f6ddb0ff92917ec345e75cd8a9a702c301164f657b23976ef0fb
[^weekly]: src · .github/workflows/weekly-links.yml#L1-L37 · sha256:b3169a09e7e5a33f5c8345eb996e3d944f0d9502b05845b75993312d9eeba6c9
[^ci-run]: src · .github/ci-run.sh#L1-L21 · sha256:f6be3830ad1207c7cf3ce950539d2071f410b653fe5d6823ef619bab227429c8
[^ci-header]: src · .github/workflows/ci.yml#L1-L16 · sha256:4cb62548d2885d47e33a9f5262221c4ad3afd2a53273b0396137dd928fe52a11
[^plan-vercel]: src · docs/plan/03-vercel-dns-security.md#L5-L9 · sha256:a715f54bed9d8a470772b958be0c2812daa4174ed3a1c0fda3b1357e40712ad0
[^next-redirect]: src · next.config.mjs#L62-L71 · sha256:e8be03682cc981a3639b3b81704b1f74fc410078e5de175c2559c105dc108501
[^ops]: src · docs/plan/05-operations.md#L9-L9 · sha256:0646da69ce6c902a699e84fb523e691de48fc20fdfffa3eb8753e3d93768c0d0

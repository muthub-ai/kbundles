---
type: application-bundle/security-architecture
title: Security architecture — Portfolio website (muthub.org)
description: Browser security headers, the confidentiality guardrail and change control of the muthub.org
  site.
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
  section: security-architecture
  bootstrap: true
---
# Security architecture — Portfolio website (muthub.org)

## Browser boundary

The site is static, with no accounts or stored personal data; `next.config.mjs` applies a Content-Security-Policy limited to the site, Microsoft Clarity and Vercel analytics, plus HSTS, `nosniff`, `X-Frame-Options: DENY`, a restrictive Permissions-Policy and a same-origin opener policy to every path; structured data is serialized with `<` escaped.[^security-md][^csp][^headers][^jsonld-escape]

*Assessment:* `script-src` keeps `'unsafe-inline'` for the theme switcher, JSON-LD and hydration, so the CSP limits where scripts load from but does not stop injected inline script; the JSON-LD helper escapes `<` to keep its own output from breaking out of the script tag.[^csp][^jsonld-escape]

## Confidentiality guardrail

`scripts/check-public-content.mjs` scans `app`, `components`, `content`, `lib` and `public` for built-in patterns and for terms from a private list read from a git-ignored file or the `PUBLIC_CONTENT_BLOCKLIST` secret, reporting only file, line and term index, never the term; CI fails before any other check when the secret is not configured.[^guard-scan][^guard-terms][^guard-report][^guard-out][^ci-secret]

Decision record M03 describes the built-in checks as covering stale phrases and email addresses; separately, a Playwright test checks that the Reach page has no `mailto:` link.[^adr-m03][^reach-test]

*Assessment:* The script's built-in list has a phone-number pattern but no email pattern, so the documented email check does not exist; email exposure is caught only by a Playwright test of the Reach page.[^guard-scan][^reach-test]

## Change control

Every path is owned by the repository owner through CODEOWNERS, the CI workflow runs with read-only contents permission, and vulnerabilities are reported through GitHub private vulnerability reporting.[^codeowners][^ci-perms][^security-md]

[^security-md]: src · SECURITY.md#L1-L8 · sha256:58baec5803d68569189541b6fff8c44269e15c437e6fa4b94d25b2c56935a2fe
[^csp]: src · next.config.mjs#L1-L17 · sha256:ea53c344a3599663b254e30150799a9edb993c45d85f3940257ceeef191fea9e
[^headers]: src · next.config.mjs#L19-L27 · sha256:2ef4b0f7436bd2d21b2a2def112c3d135c2bd6c33d2db4363d212eb274a3ea86
[^jsonld-escape]: src · components/json-ld.tsx#L4-L12 · sha256:08aa3df0df65e2d49a651c8dede0d7422883c41143cc3308611cdb2b3a5cedbc
[^guard-scan]: src · scripts/check-public-content.mjs#L19-L32 · sha256:5341a931a219a170c6fe869038366b25bad47727ee3e492fef124df2ad47d090
[^guard-terms]: src · scripts/check-public-content.mjs#L34-L43 · sha256:e1accfc41a9ce6b30973986f1b5a8070805caa805e07b3da6dc9437191bcfb74
[^guard-report]: src · scripts/check-public-content.mjs#L61-L72 · sha256:20a0b4b58c589f54c2096876c83326578b4c4ebf2895656bf3e1c8a77130a515
[^guard-out]: src · scripts/check-public-content.mjs#L92-L96 · sha256:e0badf3f798ea21bcf13c78be609b39ca9e9b3e2ad1da7da15bf8ead0abf40b0
[^adr-m03]: src · docs/decisions/M03-public-content-guardrail.md#L9-L15 · sha256:3b3f96fa01797f85a59f2b89dd5091b30b27f6050d397dff07ed6eb660c54a33
[^ci-secret]: src · .github/workflows/ci.yml#L30-L32 · sha256:aebabe49f3f1601a9e5ebf43f3fccb199ba7d6ea6741a2994c4a219135a48af1
[^reach-test]: src · playwright/tests/features.spec.ts#L161-L170 · sha256:1647b397a7816cd0f165396e37eb11769045ac9aeabaf1acd458f309e1f81d43
[^codeowners]: src · .github/CODEOWNERS#L1-L2 · sha256:82e9aaf9a4325e91ced7c7ecd8561e8299df3df00603790e3a4de1362a484b87
[^ci-perms]: src · .github/workflows/ci.yml#L15-L16 · sha256:e8f2263b0413f25128aa11d16dd3ae0ef6b0c660fb5b1dc08fe71e0a7daabb4b

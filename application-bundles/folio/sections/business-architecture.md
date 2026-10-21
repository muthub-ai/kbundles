---
type: application-bundle/business-architecture
title: Business architecture — Portfolio website (muthub.org)
description: Capabilities, audiences and the editorial rules the muthub.org site enforces.
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
  section: business-architecture
  bootstrap: true
---
# Business architecture — Portfolio website (muthub.org)

## Capabilities and actors

| Capability | Actor | Where it lives |
|---|---|---|
| Publish essays and notes by theme and tag, and initiatives as case studies | Reader, peer | `content/essays*.ts`, `content/initiatives.ts`, `app/writing/`, `app/initiatives/` [^readme-readers][^initiative-type] |
| Offer playbooks with a self-assessment that scores answers into four bands | Practitioner | `content/playbooks.ts`, `components/assessment.tsx` [^assess-bands] |
| Serve machine-readable copies for assistants and agents | AI agent | `/llms.txt`, Markdown twins, JSON-LD [^readme-agents] |

## Business rules

Every public number must trace to the site owner's private master profile, and nothing on the private blocklist may be added to site facts; the pull-request template repeats the first rule as a checklist item.[^site-rule][^pr-template]

Dated writing must not cite a known source published after the piece, internal links must never point to a later piece, and `updated` may never precede `published`; essays also keep a house structure (bold opener, closing "bottom line") with no em or en dashes.[^adr-m04][^house-style]

*Assessment:* The rules treat credibility as the product: dates and confidentiality are checked mechanically and numbers by a review checklist, so that a reader, or an agent quoting the site, can rely on what it says at the time it says it.[^adr-m04][^site-rule]

[^readme-readers]: src · README.md#L17-L17 · sha256:d3fb2327f2eb8e226ea93a1784b80b744e6bfa3725628fec40b0681384d2ecac
[^initiative-type]: src · content/initiatives.ts#L6-L27 · sha256:d77ee565c03446bcb5451adea0f7bf9803738b90f811110c3120daa46141b617
[^assess-bands]: src · components/assessment.tsx#L15-L20 · sha256:ba36e756898277cdb019ea1079d677dffd82b796517b03b07cca798070c49ba7
[^readme-agents]: src · README.md#L18-L18 · sha256:4ad578374c14c4e0e03760de8aeb1b770d90e20ce664756f9b9ff8b997446253
[^site-rule]: src · content/site.ts#L3-L4 · sha256:19958115e84c6b8715092b3e3ce7818d9e87ab7e9a2a997eac2aec1736a364b2
[^pr-template]: src · .github/pull_request_template.md#L5-L12 · sha256:8fb095cb5d510dcd45949f99b5d5d724040559d8490df5b2fd7effd54599f0af
[^adr-m04]: src · docs/decisions/M04-integrity-rules-for-dated-writing.md#L9-L18 · sha256:9dbc4ff6bfea36cd1156a5938bce532c1b1d02bde51bd2691aa0d6fdd5d2272f
[^house-style]: src · playwright/tests/content.spec.ts#L74-L84 · sha256:b9017b1564efc90e57a0860879dcf32515cbda4d6d68e2f197c1b4e507baa098

---
type: application-bundle/domain-map
title: Domain map — editorial content
description: Vocabulary of the site's editorial model — pieces, themes, tags, blocks and publishing states
  — and where each lives in code.
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
  domain: editorial-content
  bootstrap: true
---
# Domain map — editorial content

The editorial model is defined as TypeScript types in `content/` and read through `lib/content.ts`.[^g-essay][^g-getessays]

## Glossary

| Term | Meaning | Where in code |
|---|---|---|
| Essay | Long-form piece with a theme, dates, sources line, related slugs, optional series and a block body | `content/essays.ts::Essay` [^essay-type] |
| Note | Shorter piece with no theme or related list; rendered as a `BlogPosting` | `content/essays.ts::Note` [^note-type][^article-ld] |
| Initiative | Case study with problem, approach, governance, outcome, lesson and optional C4 architecture levels | `content/initiatives.ts::Initiative` [^initiative-type] |
| Playbook | Checklist whose items each carry a `check` question, with a `reviewed` date | `content/playbooks.ts::Playbook` [^playbook-type] |
| Theme | One of five fixed subject areas, each with a slug and a blurb | `content/site.ts` `themes` [^themes] |
| Tag | Finer topic label; curated per slug, else up to three regex matches | `content/tags.ts::tagsFor` [^tags-for] |
| Block | Typed unit of rich text: `p`, `h2`, `ul`, `ol`, `quote`, `bottomLine`, `code`, `figure`, `monday` | `content/site.ts::Block` [^block] |
| Bottom line / What to do Monday | Closing summary block, and an action list rendered under a "What to do Monday" heading | `lib/content.ts::blocksToMarkdown` [^blocks-md] |
| Draft / published | `status` value; drafts are visible only in development or with `NEXT_PUBLIC_SHOW_DRAFTS=true` | `lib/content.ts` `showDrafts` [^visible] |
| `plannedFor` | Free-text target shown as "Draft · …" in place of a date until a piece is published | `lib/content.ts::dateLabel` [^date-label] |
| Series | Named, numbered sequence of essays, ordered by part | `lib/content.ts::getSeries` [^series] |
| Reading time | Word count of text blocks divided by 230, minimum one minute | `lib/content.ts::readingMinutes` [^reading] |
| Archive | Earlier writing on Medium, listed by link only | `content/archive.ts` [^archive] |
| Now | Current-focus list with its own `updated` date | `content/about.ts` `now` [^now] |

*Assessment:* Visibility is the only workflow state; there is no review or scheduled state in the model, so editorial review happens entirely in pull requests.[^visible][^essay-type]

[^g-essay]: graph · content/essays.ts::Essay
[^g-getessays]: graph · lib/content.ts::getEssays
[^essay-type]: src · content/essays.ts#L7-L20 · sha256:46df21f7ea9db4dd40138b44a137ba9038ee15f08d32c50b76c01287007157b7
[^note-type]: src · content/essays.ts#L1132-L1141 · sha256:91a8e50c64dc3f15f6ab2ad22baed70207c1bc8de89952ab7c758c2fa9d8326f
[^article-ld]: src · app/writing/[slug]/page.tsx#L89-L91 · sha256:a5fddf9620802eb333729ab72c851567a879f38c627e95f02038a1aa175d42dd
[^initiative-type]: src · content/initiatives.ts#L6-L27 · sha256:d77ee565c03446bcb5451adea0f7bf9803738b90f811110c3120daa46141b617
[^playbook-type]: src · content/playbooks.ts#L4-L19 · sha256:c868caaf3888750d474188a6310bae75739708e410acef0577b90baa3c0a3d48
[^themes]: src · content/site.ts#L58-L66 · sha256:afa66191bd57f6476683cac40ca86823fac3a1aeb6dd95b5bbc2cf4d77b5107a
[^tags-for]: src · content/tags.ts#L70-L75 · sha256:b1bad7f73805d46aaf0637d550f547978d80127bf528be188d99940026e345f8
[^block]: src · content/site.ts#L72-L83 · sha256:05d32f180611b04d059ca8d4b545b406fa6fe040db7a39a7753242b07f1967f8
[^blocks-md]: src · lib/content.ts#L79-L84 · sha256:42f0dd59815564a1c9f5da1ecda9b5af50839325719e96e40b9ec1312ca4d10d
[^visible]: src · lib/content.ts#L9-L17 · sha256:0e24ad2a461e9e85dcc67f1162055e4e60a5b3242557bd82ba42541afe9e2b3c
[^date-label]: src · lib/content.ts#L46-L51 · sha256:5319b86fd22cdaed688e5bc1a5dad5b4a4b94cb1fb661d29c19016bfff5889df
[^series]: src · lib/content.ts#L92-L96 · sha256:03bbe7ad7d59582f7901b960a636cafaae33696de707a5edafcafa2afd4186fd
[^reading]: src · lib/content.ts#L53-L62 · sha256:7fe0efc56d33b5ed105478bd9fd9906dbc447b8d7f13a0dafbbf0d9428608c5e
[^archive]: src · content/archive.ts#L1-L2 · sha256:bb339936314b300eb77d68b5fc56fe41b99bee755877dd2639ab38ea85522fdb
[^now]: src · content/about.ts#L72-L75 · sha256:589eb6c9e0fad396851a55b37d2f3f06e7f0fc8deb1c24d21790d0f2fc2f999a

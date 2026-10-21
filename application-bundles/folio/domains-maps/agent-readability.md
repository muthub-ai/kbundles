---
type: application-bundle/domain-map
title: Domain map — agent readability
description: Vocabulary of the machine-readable surfaces of muthub.org — Markdown twins, llms.txt, structured
  data, feeds and crawler policy — and where each lives in code.
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
  domain: agent-readability
  bootstrap: true
---
# Domain map — agent readability

Decision record M02 makes every page readable by agents, with search engines indexing only the HTML.[^adr-m02]

## Glossary

| Term | Meaning | Where in code |
|---|---|---|
| Markdown twin | Plain-Markdown copy of a page at `/<page>.md`, ending with a name, URL and disclosure footer | `lib/markdown.ts`, `app/md/[[...path]]/route.ts` [^md-footer][^g-render] |
| Twin rewrite | Mapping of `.md` URLs onto the `/md/...` catch-all route | `next.config.mjs` `rewrites` [^rewrites] |
| `noindex` twin header | `X-Robots-Tag: noindex, follow` on `.md` and `/md/` paths so twins never compete with HTML in search | `next.config.mjs` `headers` [^noindex] |
| Markdown alternate | `alternates.types["text/markdown"]` link from each HTML page to its twin, next to the canonical URL | `lib/seo.ts::pageMetadata` [^seo-alt] |
| `llms.txt` | Site summary plus links to core pages, initiatives, essays, playbooks and archive, all pointing at twins | `lib/markdown.ts::llmsTxt` [^llms] |
| Person / ProfilePage / WebSite | Site-wide schema.org graph; the WebSite node carries a `SearchAction` on `/search?q=` | `components/json-ld.tsx` [^profile-ld] |
| Article / BlogPosting | Per-piece structured data for essays and notes, authored by the shared Person | `app/writing/[slug]/page.tsx` [^article-ld] |
| Search index | Static JSON of every essay, note, initiative, C4 level, playbook and fixed page | `app/search-index.json/route.ts`, `lib/search.ts::buildSearchIndex` [^g-index] |
| RSS feed | RSS 2.0 list of published essays and notes with theme or "Note" as category | `app/rss.xml/route.ts` [^rss] |
| Crawler policy | `robots.txt` that names search and AI answer crawlers explicitly and allows all others, with a training opt-out marked as pending | `public/robots.txt` [^robots] |
| Social card | 1200×630 PNG per piece from `scripts/og/make-images.py`, falling back to the site card | `lib/seo.ts::writingImage` [^og] |

*Assessment:* Agent readability is treated as a first-class output rather than a by-product: the twins, `llms.txt` and the index are generated from the same content as the HTML and are covered by the end-to-end tests.[^adr-m02][^llms]

[^adr-m02]: src · docs/decisions/M02-readable-by-agents.md#L9-L16 · sha256:b9f0b14677710725b6225ff081bc321c180dd6e53b39df07b920ce846984740e
[^md-footer]: src · lib/markdown.ts#L9-L10 · sha256:a8ed2c595e431ab57520aa025f4178fd6b93fdf319946275789b343d8f83a6f6
[^g-render]: graph · app/md/[[...path]]/route.ts::render
[^rewrites]: src · next.config.mjs#L83-L91 · sha256:e14b0962fca5e53857e284927adcdbd39c08635028c4a7d68399bc9ebdfa359f
[^noindex]: src · next.config.mjs#L44-L50 · sha256:91ef95149e147d28bad0c4dcc4f81becb2116020b7828f64cf17f5ef4d6f71a5
[^seo-alt]: src · lib/seo.ts#L35-L42 · sha256:1f524e6becefaf47addefc393d056128f79faf1dce4142864daf0dab7d3e6fcf
[^llms]: src · lib/markdown.ts#L154-L173 · sha256:d63184dedf4c954c84214a370c0644db1ec3116c942b523e301c6c79216ab2ba
[^profile-ld]: src · components/json-ld.tsx#L44-L73 · sha256:8f597a03bf1bad58e7167bdc3b92771d468cc63e78bed3bf775ca793987fb9c7
[^article-ld]: src · app/writing/[slug]/page.tsx#L89-L104 · sha256:8c8275dfe4e39338bfe36f21083f52aa0da9e96ad92c93cfd391a89347820907
[^g-index]: graph · lib/search.ts::buildSearchIndex
[^rss]: src · app/rss.xml/route.ts#L8-L24 · sha256:edb6f8f54ed1414e2acb9ee6a6bd524c6ccedca3b32630c68e31110214460d01
[^robots]: src · public/robots.txt#L1-L22 · sha256:8379a63caf026e4694bc3968a770ffac29f5de737df3533d53e14749f4008cf1
[^og]: src · lib/seo.ts#L25-L29 · sha256:34b9ba58f47766332454421ffa5a2c408aa4efa2ff497b1620c6acbbfcb36d12

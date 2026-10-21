---
type: application-bundle/data-architecture
title: Data architecture — Knowledge Foundation site
description: Inputs, intermediate formats and published outputs of the site build, and the browser-side
  state it keeps.
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
  section: data-architecture
  bootstrap: true
---
# Data architecture — Knowledge Foundation site

## Inputs

| Input | Format | Read by |
|---|---|---|
| `bundle.tgz` | tarball of the OKF `wiki/` folder, extracted with the `data` filter | `scripts/fetch_release.py` [^fetch] |
| `graph.json` | nodes (id, type, label, url, trust, dates, aliases) and edges (source, target, type, origin, evidence) | `explorer/src/explorer.ts` [^gnode][^gedge] |
| `wiki.config.yaml` | site name, URL, themes, author; defaults apply when absent | `kfsite/bundle.py::load_config` [^config] |

## Outputs

Each staged Quartz page carries reduced frontmatter: title, description, tags, created and modified dates, and `kf_kind`, `kf_trust` and `kf_status`; after Quartz runs, the post step publishes the original OKF file of every note as a Markdown twin at the note's path, alongside `llms.txt`, `robots.txt` and a copy of `graph.json`.[^stage-fm][^post-jsonld][^post-llms][^post-explorer]

The only browser-side state is the reader's theme choice in `localStorage.theme`, shared by the explorer and the Quartz pages.[^theme-js]

*Assessment:* The site is stateless between builds: every output is a pure function of one release plus the pinned toolchain, so there is nothing to back up or migrate on the site side.[^fetch][^post-explorer]

[^fetch]: src · scripts/fetch_release.py#L36-L49 · sha256:c2f7c345b5a17c39ef0ebeda3d323067bf4e5fd9104640ccf38a5626cbf8c217
[^gnode]: src · explorer/src/explorer.ts#L18-L22 · sha256:515c7697340f356b0d4d5b6f85490813caa11c77e94fcbc8cc64f839d77e4ca1
[^gedge]: src · explorer/src/explorer.ts#L31-L31 · sha256:ff8221991dcb0f8fe0945ae6b1b821fc937f8fba27460a2650459e5fdf11b5e6
[^config]: src · kfsite/bundle.py#L205-L217 · sha256:7c757c7adf08302663fcdfac62942484503c49899539723e39ab8020602b7f22
[^stage-fm]: src · kfsite/stage.py#L114-L119 · sha256:bddb1488ac57b299f518151c8e5a95821892d1347193aba3c2ae72b63fcbb66d
[^post-jsonld]: src · kfsite/post.py#L69-L77 · sha256:af4e33d73aca7f4ebb6a0803f0fbdf5363730ca3644d62669b6f3a879c8b3ecb
[^post-llms]: src · kfsite/post.py#L87-L96 · sha256:4a3f5f187a4602e8a8f33c081c357db74635b018d62c6488779cedb72fbec36b
[^post-explorer]: src · kfsite/post.py#L98-L110 · sha256:d017d031d05121f3d76b76a9d1aaaeb12a7fd2e7e983bed78bfa144d739656d2
[^theme-js]: src · explorer/theme.js#L3-L23 · sha256:354bfbae54336c71fc0f3e64e569cefa0783e889eccd65951e9da7ff0cb7b4eb

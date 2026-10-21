---
type: application-bundle/security-architecture
title: Security architecture — Knowledge Foundation site
description: Trust boundaries, browser hardening, CI permissions, supply-chain controls and content scanning
  for the site.
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
  section: security-architecture
  bootstrap: true
---
# Security architecture — Knowledge Foundation site

## Browser boundary

The explorer pages (`/`, `/graph` and `/graph/*`) are served with a Content-Security-Policy that allows scripts and connections only from the site itself and styles only from the site and Google Fonts; every path also gets HSTS, `nosniff`, frame denial, a strict referrer policy and a restrictive permissions policy.[^headers][^csp]

Data from `graph.json` is escaped before it reaches HTML, only `https://` URLs and same-site paths become links, and dynamic colours are set through the CSSOM rather than inline `style` attributes so the CSP needs no `unsafe-inline`.[^esc][^safeurl][^colours]

## Build and CI boundary

The CI workflow runs with read-only repository permission; only the `bundle-handback` job, which runs no npm code and is limited to same-repository pull requests, gets `contents: write` to push a rebuilt bundle to a `ci/` scratch branch.[^ci-perm][^handback]

Release downloads use a fixed GitHub host, an optional `GITHUB_TOKEN`, and tar extraction with the `data` filter, which is why the Vercel build insists on Python 3.11.4 or later.[^fetch-get][^fetch-tar][^vbuild-py]

A private blocklist from the `CONFIDENTIAL_TERMS` secret is scanned against the built site and the repository's public prose, and the test fails in CI if the secret is missing.[^ci-terms][^terms-test]

*Assessment:* Downloaded release assets are not checked against a digest or signature, so the integrity of the published site rests on GitHub's release hosting and the knowledge repository's own controls.[^fetch-tar]

[^headers]: src · vercel.json#L10-L35 · sha256:b5844971b7552d3b2a5befed9baf10450e3fd1c2439205e46771e0ed4d6fdc93
[^csp]: src · vercel.json#L36-L62 · sha256:a0162f377248e1a44492a5ac72deb31324d58d12413b1502e760d9caedb35629
[^esc]: src · explorer/src/explorer.ts#L57-L58 · sha256:dfb86977fde9ae6b3c2b1ff49b6db52dddba5e313628f932707c7d2b97bfb01b
[^safeurl]: src · explorer/src/explorer.ts#L775-L781 · sha256:5dea39c3b9a6960abdaf189390c78dd4b99cd4e020e33ce9115cf659f654be17
[^colours]: src · explorer/src/explorer.ts#L294-L298 · sha256:2f820799a9b3b8d052ff975bb75fe0ac4725cfddd3f959afa2d6734342b9a0d8
[^ci-perm]: src · .github/workflows/ci.yml#L11-L12 · sha256:e8f2263b0413f25128aa11d16dd3ae0ef6b0c660fb5b1dc08fe71e0a7daabb4b
[^handback]: src · .github/workflows/ci.yml#L73-L84 · sha256:009ff8722123df8d2eef51a45e736bc76072de14db675167a9a03714f8ec628c
[^fetch-get]: src · scripts/fetch_release.py#L17-L33 · sha256:d4ddd7e1f466d835728d6d8294d90ebbc016a09357c7d27424d189cf9ab0e76d
[^fetch-tar]: src · scripts/fetch_release.py#L36-L49 · sha256:c2f7c345b5a17c39ef0ebeda3d323067bf4e5fd9104640ccf38a5626cbf8c217
[^vbuild-py]: src · scripts/vercel_build.sh#L11-L13 · sha256:d6876d47589c83cdbbdec3d8ca6406615ab25c676a6e6a571fb3e76daff36427
[^ci-terms]: src · .github/workflows/ci.yml#L34-L42 · sha256:09576aa0efeeb02daca8314d09feb0ea6a737b166bb0acad1bd9c463a57fda2c
[^terms-test]: src · tests/test_post.py#L143-L160 · sha256:42ac1e4d36495e4e3e2b6f2ed593d6a40d8f93a0718457ece84eacc8501ba89a

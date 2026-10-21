---
okf_version: "0.2"
---

# Portfolio website (muthub.org) — application bundle (`folio`)

Application bundle for [`muthub-ai/muthu-v0-portfolio-website`](https://github.com/muthub-ai/muthu-v0-portfolio-website) at commit [`8bca37ea8df4`](https://github.com/muthub-ai/muthu-v0-portfolio-website/tree/8bca37ea8df4e3f6365c20a323bcd680c986a568). This index links to sections and directories only, so it never goes stale when ceremony knowledge lands.

## Sections

- [Executive summary](sections/executive-summary.md) — What the muthub.org portfolio site is, who reads it, and its shape on one screen.
- [Business architecture](sections/business-architecture.md) — Capabilities, audiences and the editorial rules the muthub.org site enforces.
- [Application architecture](sections/application-architecture.md) — Modules of the muthub.org site, their responsibilities, entry points and the main build-time and request-time flows.
- [Data architecture](sections/data-architecture.md) — Content entities, their storage as typed source files, and the derived outputs built from them.
- [Technology architecture](sections/technology-architecture.md) — Languages, frameworks, dependencies, build, CI/CD and hosting of the muthub.org site.
- [Security architecture](sections/security-architecture.md) — Browser security headers, the confidentiality guardrail and change control of the muthub.org site.
- [Operating model](sections/operating-model.md) *(illustrative)* — Illustrative, fabricated operating model for the muthub.org site — teams, ownership, ceremony cadence and decision rights for this prototype.

## Domain maps

- [Domain map — agent readability](domains-maps/agent-readability.md) — Vocabulary of the machine-readable surfaces of muthub.org — Markdown twins, llms.txt, structured data, feeds and crawler policy — and where each lives in code.
- [Domain map — editorial content](domains-maps/editorial-content.md) — Vocabulary of the site's editorial model — pieces, themes, tags, blocks and publishing states — and where each lives in code.

## Code graph

- [Module view](code-graph/views/modules.md) — directory-level dependency view
- [Dependencies and hotspots](code-graph/views/dependencies.md) — external packages, entry points, fan-in
- [Metrics](code-graph/metrics.json) · [Graph records (JSONL)](code-graph/code-graph.jsonl)

## Knowledge sources

- [Agile ceremonies](knowledge-sources/agile-ceremonies/) — candidate knowledge from scrum ceremonies, one directory per ceremony and team

## Control files

- [Source pin](knowledge-source.json) · [Manifest](bundle-manifest.json) · [Bundle log](log.md)

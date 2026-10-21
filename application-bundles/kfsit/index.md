---
okf_version: "0.2"
---

# Knowledge Foundation site — application bundle (`kfsit`)

Application bundle for [`muthub-ai/knowledge-foundation-site`](https://github.com/muthub-ai/knowledge-foundation-site) at commit [`3afac247ec28`](https://github.com/muthub-ai/knowledge-foundation-site/tree/3afac247ec2848aa9d8844a83f1fc982eb6a6dc0). This index links to sections and directories only, so it never goes stale when ceremony knowledge lands.

## Sections

- [Executive summary](sections/executive-summary.md) — What the Knowledge Foundation site is, who it serves, and its shape in one screen.
- [Business architecture](sections/business-architecture.md) — Capabilities the site provides, the actors it serves and the publishing rules it enforces.
- [Application architecture](sections/application-architecture.md) — Components of the site build, their responsibilities, entry points and the stage, render, post and explore flows.
- [Data architecture](sections/data-architecture.md) — Inputs, intermediate formats and published outputs of the site build, and the browser-side state it keeps.
- [Technology architecture](sections/technology-architecture.md) — Languages, frameworks, pinned dependencies, build tooling, CI and Vercel hosting of the Knowledge Foundation site.
- [Security architecture](sections/security-architecture.md) — Trust boundaries, browser hardening, CI permissions, supply-chain controls and content scanning for the site.
- [Operating model](sections/operating-model.md) *(illustrative)* — An illustrative, fabricated operating model for the site's two teams, their ownership, ceremonies and bundle-update decision rights.

## Domain maps

- [Domain map — provenance and graph vocabulary](domains-maps/provenance-and-graph.md) — Terms the site uses for note provenance and for the knowledge graph, with their meaning and where they live in code.

## Code graph

- [Module view](code-graph/views/modules.md) — directory-level dependency view
- [Dependencies and hotspots](code-graph/views/dependencies.md) — external packages, entry points, fan-in
- [Metrics](code-graph/metrics.json) · [Graph records (JSONL)](code-graph/code-graph.jsonl)

## Knowledge sources

- [Agile ceremonies](knowledge-sources/agile-ceremonies/) — candidate knowledge from scrum ceremonies, one directory per ceremony and team

## Control files

- [Source pin](knowledge-source.json) · [Manifest](bundle-manifest.json) · [Bundle log](log.md)

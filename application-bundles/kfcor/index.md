---
okf_version: "0.2"
---

# Knowledge Foundation core — application bundle (`kfcor`)

Application bundle for [`muthub-ai/knowledge-foundation`](https://github.com/muthub-ai/knowledge-foundation) at commit [`78d41952391c`](https://github.com/muthub-ai/knowledge-foundation/tree/78d41952391c91356afbebfaee129b8b40a12561). This index links to sections and directories only, so it never goes stale when ceremony knowledge lands.

## Sections

- [Executive summary](sections/executive-summary.md) — What the Knowledge Foundation core repository is, who works in it, and the shape of its governed knowledge pipeline on one screen.
- [Business architecture](sections/business-architecture.md) — The capabilities Knowledge Foundation core provides, the actors involved, the capture-to-publication value stream and the business rules the repository enforces.
- [Application architecture](sections/application-architecture.md) — The modules of the Knowledge Foundation core repository, their responsibilities, entry points and the capture-to-release flow that connects them.
- [Data architecture](sections/data-architecture.md) — The data entities of Knowledge Foundation core (notes, raw source copies, captures, the published graph and release assets), their schemas and the lineage between them.
- [Technology architecture](sections/technology-architecture.md) — Languages, pinned dependencies, models, build commands, CI/CD workflows and hosting that Knowledge Foundation core runs on.
- [Security architecture](sections/security-architecture.md) — Trust boundaries, approval binding, token and secret handling, the confidential-terms guardrail and supply-chain controls in Knowledge Foundation core.
- [Operating model](sections/operating-model.md) *(illustrative)* — An illustrative, fabricated operating model for Knowledge Foundation core (teams, ownership, ceremonies and decision rights); it is not drawn from the source repository.

## Domain maps

- [Domain map — graph and semantic-layer vocabulary](domains-maps/graph-semantic-layer.md) — The vocabulary of the published graph and its Semantica-based semantic layer in Knowledge Foundation core, what each term means and where it lives in code.
- [Domain map — notes and governance vocabulary](domains-maps/note-governance.md) — The vocabulary of notes, sources and governance in Knowledge Foundation core, what each term means and where it lives in code.

## Code graph

- [Module view](code-graph/views/modules.md) — directory-level dependency view
- [Dependencies and hotspots](code-graph/views/dependencies.md) — external packages, entry points, fan-in
- [Metrics](code-graph/metrics.json) · [Graph records (JSONL)](code-graph/code-graph.jsonl)

## Knowledge sources

- [Agile ceremonies](knowledge-sources/agile-ceremonies/) — candidate knowledge from scrum ceremonies, one directory per ceremony and team

## Control files

- [Source pin](knowledge-source.json) · [Manifest](bundle-manifest.json) · [Bundle log](log.md)

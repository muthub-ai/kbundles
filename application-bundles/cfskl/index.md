---
okf_version: "0.2"
---

# C4 skills — application bundle (`cfskl`)

Application bundle for [`muthub-ai/c4-skills`](https://github.com/muthub-ai/c4-skills) at commit [`670fdcd9a8bc`](https://github.com/muthub-ai/c4-skills/tree/670fdcd9a8bc6bc9583a56390877ec742fee50ac). This index links to sections and directories only, so it never goes stale when ceremony knowledge lands.

## Sections

- [Executive summary](sections/executive-summary.md) — What the C4 skills package is, who uses it, and its overall shape at the pinned commit.
- [Business architecture](sections/business-architecture.md) — Capabilities, actors and the architectural rules that the C4 skills package teaches agents to enforce.
- [Application architecture](sections/application-architecture.md) — The skills architecture of C4 skills — skill folders, SKILL.md router structure, bundled references, cross-skill links, install mechanics, registry and test suite.
- [Data architecture](sections/data-architecture.md) — The artifacts C4 skills reads and produces — skill metadata, registry, output document layouts, ADR template and test fixtures.
- [Technology architecture](sections/technology-architecture.md) — Languages, file formats, build and test tooling, CI/CD workflows, documentation hosting and dependencies of C4 skills.
- [Security architecture](sections/security-architecture.md) — Trust boundaries, data handling claims, supply chain and vulnerability reporting for the C4 skills package.
- [Operating model](sections/operating-model.md) *(illustrative)* — An illustrative, fabricated operating model for C4 skills — teams, ownership, ceremony cadence and decision rights for bundle updates.

## Domain maps

- [Domain map — C4 and ADR vocabulary](domains-maps/c4-adr-vocabulary.md) — The C4 model and Architecture Decision Record vocabulary that the C4 skills teach, with where each term is defined in the skill files and enforced by the validators.

## Code graph

- [Module view](code-graph/views/modules.md) — directory-level dependency view
- [Dependencies and hotspots](code-graph/views/dependencies.md) — external packages, entry points, fan-in
- [Metrics](code-graph/metrics.json) · [Graph records (JSONL)](code-graph/code-graph.jsonl)

## Knowledge sources

- [Agile ceremonies](knowledge-sources/agile-ceremonies/) — candidate knowledge from scrum ceremonies, one directory per ceremony and team

## Control files

- [Source pin](knowledge-source.json) · [Manifest](bundle-manifest.json) · [Bundle log](log.md)

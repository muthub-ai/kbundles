---
okf_version: "0.2"
---

# Architecture as Code — application bundle (`aacod`)

Application bundle for [`muthub-ai/aac`](https://github.com/muthub-ai/aac) at commit [`fcc5db4d74b5`](https://github.com/muthub-ai/aac/tree/fcc5db4d74b50a8a95a1017cd688ce73ac689633). This index links to sections and directories only, so it never goes stale when ceremony knowledge lands.

## Sections

- [Executive summary](sections/executive-summary.md) — What Architecture as Code is, who uses it, why it matters, and its overall shape in one screen.
- [Business architecture](sections/business-architecture.md) — Capabilities Architecture as Code provides, its actors, the governance value stream and the business rules it encodes.
- [Application architecture](sections/application-architecture.md) — The four runtime surfaces (web app, CLI, MCP server, pipeline scripts), their modules, interactions, entry points and key flows.
- [Data architecture](sections/data-architecture.md) — The YAML and JSON artifacts Architecture as Code stores, their schemas and validators, derived outputs, caches and data lineage.
- [Technology architecture](sections/technology-architecture.md) — Languages, frameworks, runtimes, build tooling, CI/CD workflows, hosting and dependencies of Architecture as Code.
- [Security architecture](sections/security-architecture.md) — Trust boundaries, policy enforcement (lint rules, OPA/Rego, waivers), the MCP and CLI attack surface, secrets handling and supply chain for Architecture as Code.
- [Operating model](sections/operating-model.md) *(illustrative)* — Illustrative (fabricated) operating model for Architecture as Code — teams, ownership, ceremonies, cadence and decision rights for bundle updates.

## Domain maps

- [Domain map — architecture governance](domains-maps/architecture-governance.md) — Vocabulary of the governance domain in Architecture as Code (standards, waivers, policies, compliance rules, scorecard) and where each term lives in code.
- [Domain map — C4 modeling](domains-maps/c4-modeling.md) — Vocabulary of the C4 system-model domain in Architecture as Code (systems, containers, deployment, views, sync) and where each term lives in code.

## Code graph

- [Module view](code-graph/views/modules.md) — directory-level dependency view
- [Dependencies and hotspots](code-graph/views/dependencies.md) — external packages, entry points, fan-in
- [Metrics](code-graph/metrics.json) · [Graph records (JSONL)](code-graph/code-graph.jsonl)

## Knowledge sources

- [Agile ceremonies](knowledge-sources/agile-ceremonies/) — candidate knowledge from scrum ceremonies, one directory per ceremony and team

## Control files

- [Source pin](knowledge-source.json) · [Manifest](bundle-manifest.json) · [Bundle log](log.md)

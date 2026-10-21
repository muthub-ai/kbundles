---
type: application-bundle/business-architecture
title: Business architecture — C4 skills
description: Capabilities, actors and the architectural rules that the C4 skills package teaches agents
  to enforce.
generated:
  by: process:building-application-bundles@0.1.0
  at: '2026-10-20T19:30:00-05:00'
sources:
- id: repo
  kind: source-repo
  repo: muthub-ai/c4-skills
  commit_sha: 670fdcd9a8bc6bc9583a56390877ec742fee50ac
- id: graph
  kind: code-graph
  path: code-graph/code-graph.jsonl
  sha256: 2d93dd527a4f4487fb0c2f46ec9a8333874f5fab7fc841dda265894565e2e8db
x_kf:
  schema: kf-application-bundle/1
  appid: cfskl
  bundle_kind: application
  section: business-architecture
  bootstrap: true
---
# Business architecture — C4 skills

## Capabilities

| Capability | Skill and modes |
|---|---|
| Design a new architecture as C4 diagrams | `c4designer` design mode [^registry] |
| Retro-document an existing system from code or prose | `c4designer` document-code and document-prose modes [^registry] |
| Review or update existing C4 diagrams | `c4designer` review and update modes [^registry] |
| Draft, infer and review Architecture Decision Records | `adr-scribe` interview, retro-document and review modes [^registry] |

The two capabilities are positioned as complementary: C4 diagrams record *what* the system is and ADRs record *why* it was built that way.[^readme-skills]

## Actors

The actors are the developer or architect who prompts the agent, and the AI coding agent that loads the skill; the skills address the agent and require the user's explicit validation before delivery.[^c4-dialogue][^adr-dialogue]

## Business rules taught to agents

The C4 notation rules are labelled non-negotiable: every diagram has a title and legend, every element has an explicit type and responsibility, containers and components state their technology, and every relationship is unidirectional and labelled with a concrete intent and protocol.[^c4-notation]

Simon Brown's guidance is adopted as a scoping rule: Context and Container diagrams are produced by default, and Component or Code levels only when asked for or clearly valuable.[^c4-levels]

For ADRs, a decision with only one option is treated as a constraint, and an ADR without negative consequences is treated as incomplete.[^adr-pitfalls]

*Assessment:* The rules are encoded twice — as prose instructions for the agent and as grep checks in the validators — and only the second copy is enforced mechanically, and only on example and fixture files.[^c4-notation][^adr-pitfalls]

[^registry]: src · registry.json#L5-L36 · sha256:363eb074f0dcd535ed2be5aad9d606cc258eefd50ba8623efa504687e7df1127
[^readme-skills]: src · README.md#L73-L93 · sha256:1d623f3338ed8569f95b97cb867ce5c1c1858a093d62250890b53127ba19cdf5
[^c4-dialogue]: src · c4designer/SKILL.md#L134-L142 · sha256:9d707b2a53b75ebca2827a231b617523a7519c332de68a2b19c7309faa3d5caa
[^adr-dialogue]: src · adr-scribe/SKILL.md#L56-L62 · sha256:53d52e3bc1fea98695afe145d3ac62b4a5366cd2e881043da99ccde7ecdb8194
[^c4-notation]: src · c4designer/SKILL.md#L83-L100 · sha256:17f8fde374dbaf4ce209eec93d2c96307b6e22e22f9d2c219760e6e39ef97c9e
[^c4-levels]: src · c4designer/SKILL.md#L13-L22 · sha256:86db029eeb13ed6ba95be17bb7c06d9daf5673cde25014acbb2cc826ac050843
[^adr-pitfalls]: src · adr-scribe/SKILL.md#L64-L69 · sha256:6e632cdde5fa1027e6386872064bef44303d48d379d0b63119f26add5949da05

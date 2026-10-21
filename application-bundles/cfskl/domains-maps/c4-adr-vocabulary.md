---
type: application-bundle/domain-map
title: Domain map — C4 and ADR vocabulary
description: The C4 model and Architecture Decision Record vocabulary that the C4 skills teach, with where
  each term is defined in the skill files and enforced by the validators.
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
  domain: c4-adr-vocabulary
  bootstrap: true
---
# Domain map — C4 and ADR vocabulary

## C4 levels and diagram types

| Term | Meaning in the skills | Where it lives |
|---|---|---|
| Context (level 1) | The system with its actors and external systems; audience is everyone; Mermaid `C4Context` | `c4designer/SKILL.md` [^c4-levels] |
| Container (level 2) | Applications, services and data stores of the system; Mermaid `C4Container` | `c4designer/SKILL.md` [^c4-levels] |
| Component (level 3) | Internal parts of one container; Mermaid `C4Component` | `c4designer/SKILL.md` [^c4-levels] |
| Code (level 4) | Classes and functions of a component, drawn as UML `classDiagram` | `c4designer/SKILL.md` [^c4-levels] |
| Golden rule | Context plus Container diagrams suffice for most teams; deeper levels only on request or clear value | `c4designer/SKILL.md` [^c4-levels] |
| Supporting diagrams | System Landscape, Deployment (`C4Deployment`) and Dynamic (`C4Dynamic`) views that add to, never replace, the core levels | `c4designer/supporting-diagrams.md` [^supporting] |

## C4 notation elements

| Term | Meaning in the skills | Where it lives |
|---|---|---|
| `Person`, `System`, `System_Ext`, `SystemDb`, `SystemQueue` | Actors and software systems, `_Ext` for out-of-scope systems | `c4designer/SKILL.md` cheatsheet [^cheatsheet] |
| `Container`, `ContainerDb`, `ContainerQueue`, `Component` | Elements that take a mandatory technology argument | `c4designer/SKILL.md` cheatsheet [^cheatsheet] |
| Boundary | `Enterprise_Boundary`, `System_Boundary` or `Container_Boundary` used to group elements; `{` must never follow `System()` or `Container()` | `c4designer/SKILL.md`, `tests/validate-c4-diagram.sh` [^cheatsheet][^c4-val-boundary] |
| `Rel` | A unidirectional relationship with an intent label and a protocol; `BiRel` is split into two `Rel`s | `c4designer/SKILL.md` notation rules [^notation] |
| Intent label | A concrete verb phrase on a relationship; bare "Uses", "Calls" and "Reads" are banned and rejected by the validator | `c4designer/SKILL.md`, `tests/validate-c4-diagram.sh` [^notation][^c4-val-intent] |
| Undefined alias | A `Rel` endpoint that no element defines, which crashes Mermaid; the validator rejects it | `c4designer/SKILL.md` pitfalls, `tests/validate-c4-diagram.sh` [^pitfalls][^c4-val-elements] |
| Unsupported features | `sprite`, tags, `$link`, `Legend`, layout statements and custom shapes that exist in C4-PlantUML but not in Mermaid | `c4designer/mermaid-c4-syntax.md` [^unsupported] |

## Skill workflow terms

| Term | Meaning in the skills | Where it lives |
|---|---|---|
| Mode | The workflow selected first from user signals: design, document-code, document-prose, review or update for C4; interview, retro-document or review for ADRs | `c4designer/SKILL.md`, `adr-scribe/SKILL.md` [^c4-router][^adr-router] |
| Common contract | Output format, destination, notation rules, per-level deliverable, checklist and dialogue rules shared by every C4 mode | `c4designer/SKILL.md` [^contract] |
| Level document | The Markdown file accompanying each diagram: Overview, Diagram, Legend, Elements, Key relationships, Notable architectural decisions, Assumptions, Links to other levels | `c4designer/level-template.md` [^level-template] |
| Assumptions | Anything inferred rather than confirmed, listed in its own section instead of being baked into the diagram | `c4designer/SKILL.md` [^dialogue] |
| Review checklist | Simon Brown's checklist plus skill-specific additions, run before every delivery | `c4designer/review-checklist.md` [^c4-checklist][^g-c4check] |

## ADR terms

| Term | Meaning in the skills | Where it lives |
|---|---|---|
| ADR | A record of *why* an architecture was built a certain way, complementing C4's *what* | `adr-scribe/SKILL.md` [^adr-intro] |
| Status | One of Proposed, Accepted, Deprecated or Superseded; validator requires a `* Status:` line | `adr-scribe/adr-template.md`, `tests/validate-adr.sh` [^adr-template][^adr-val] |
| Considered Options | The alternatives weighed; a single option is a constraint, not a decision | `adr-scribe/adr-template.md`, `adr-scribe/SKILL.md` [^adr-template][^adr-pitfalls] |
| Decision Outcome | The chosen option with its justification | `adr-scribe/adr-template.md` [^adr-template] |
| Negative Consequences | The trade-offs of the decision; the skill and validator treat an ADR without them as incomplete | `adr-scribe/SKILL.md`, `tests/validate-adr.sh` [^adr-pitfalls][^adr-val] |

## Package and test terms

| Term | Meaning in the skills | Where it lives |
|---|---|---|
| `requires` / `compatible_agents` | Frontmatter metadata naming skill dependencies and supported agents; enforced by the test runner | `registry.json`, `tests/test-skill-format.sh` [^registry][^suite1] |
| Behavioral fixture | A `tests/behavioral/` directory pairing a prompt with acceptance criteria and a golden expected output | `tests/test-skill-format.sh` [^suite3] |
| Negative fixture | A fixture whose name starts with `negative-` and whose expected output must fail validation | `tests/test-skill-format.sh` [^suite3] |
| Golden diagram | Reference output for the sandbox under `tests/example-codebase/diagrams/` | `tests/test-skill-format.sh` [^suite2] |

[^c4-levels]: src · c4designer/SKILL.md#L13-L22 · sha256:86db029eeb13ed6ba95be17bb7c06d9daf5673cde25014acbb2cc826ac050843
[^supporting]: src · c4designer/supporting-diagrams.md#L1-L12 · sha256:37d42190c1152516ffc6b968ee1c2f661ce17fb66d3290b934af656535eeab56
[^cheatsheet]: src · c4designer/SKILL.md#L150-L177 · sha256:510ebda8de6de7a2ab89b49d055f7d5656027ec55c32b4e6a90463be1daee079
[^c4-val-boundary]: src · tests/validate-c4-diagram.sh#L43-L47 · sha256:62424a0bc0d77e4ee02b60f01ee540aeddf62bf812320d8832e7ef54e413f896
[^notation]: src · c4designer/SKILL.md#L83-L100 · sha256:17f8fde374dbaf4ce209eec93d2c96307b6e22e22f9d2c219760e6e39ef97c9e
[^c4-val-intent]: src · tests/validate-c4-diagram.sh#L37-L41 · sha256:0770d342b56bb8e484a37c5c2a1301e77a90de8ce5a74c068cf27a0333cf84ea
[^pitfalls]: src · c4designer/SKILL.md#L223-L235 · sha256:c69f6d9d9ef8502b75d9bb7ee1d09227b2bb1b5b08989bf19629a1575bc51419
[^c4-val-elements]: src · tests/validate-c4-diagram.sh#L66-L77 · sha256:8d965286e2c53a7e94a234cf6cfd2c7ef0830bb925557530f3733c9158915a60
[^unsupported]: src · c4designer/mermaid-c4-syntax.md#L176-L188 · sha256:e4ea3cc9b9bc69447d7440f0205f28c382893e718a0b55eb62423e565c130a54
[^c4-router]: src · c4designer/SKILL.md#L26-L53 · sha256:80d624f668dad59dca4f5e732eed42df270a376ac32d1a2842495618dfb8a41f
[^adr-router]: src · adr-scribe/SKILL.md#L13-L36 · sha256:80de2ac0c59d99413d3043eb0b877c43c8cfcf445fc40fb81c11e074c929da5f
[^contract]: src · c4designer/SKILL.md#L55-L142 · sha256:ab7b101695b5a772d27e9b3effb3e4c67f3d53616902b78da89ffa7e1cb47555
[^level-template]: src · c4designer/level-template.md#L1-L59 · sha256:aee9bce3cb97a5cd243df313296a88897a11dc40ac906b8b4396a265e5ed9574
[^dialogue]: src · c4designer/SKILL.md#L134-L142 · sha256:9d707b2a53b75ebca2827a231b617523a7519c332de68a2b19c7309faa3d5caa
[^c4-checklist]: src · c4designer/review-checklist.md#L1-L48 · sha256:884cf133b533c333336ac5ce8379a6a1f6831dcd8173f69f27731be63b23d4a5
[^g-c4check]: graph · c4designer/review-checklist.md
[^adr-intro]: src · adr-scribe/SKILL.md#L9-L11 · sha256:0f4c0453d3b74d29ebf1428425ca03855f64bb7b3c88e736578b9c03258a4df8
[^adr-template]: src · adr-scribe/adr-template.md#L1-L35 · sha256:713103aa46a3167c464a803bd40e6b24628a3eb958618d345867a10e634be1ec
[^adr-val]: src · tests/validate-adr.sh#L19-L47 · sha256:5a8bef5e410db5aa9d8c8db9efc34cfcf552702b04d2bdbcd77d99d07fe212c4
[^adr-pitfalls]: src · adr-scribe/SKILL.md#L64-L69 · sha256:6e632cdde5fa1027e6386872064bef44303d48d379d0b63119f26add5949da05
[^registry]: src · registry.json#L5-L36 · sha256:363eb074f0dcd535ed2be5aad9d606cc258eefd50ba8623efa504687e7df1127
[^suite1]: src · tests/test-skill-format.sh#L96-L102 · sha256:04cfd939284c836de274c269f25ee56a2b724dd6fba50112aec871724984c1f7
[^suite3]: src · tests/test-skill-format.sh#L170-L208 · sha256:4260bbe3cd1c8d826a3f85ba9c0c1121c9b27614e8553102bb3d91b21f973660
[^suite2]: src · tests/test-skill-format.sh#L140-L157 · sha256:5a4c5fbea98521a14609e54df93392c40123a135f212370c9a4ce6ce10b40b30

# Section authoring guide

How to write the analytical files of an application bundle — `sections/*.md` and
`domains-maps/*.md` — so they pass the gate's citation regime (G6-bundle) on the
first try.

## Contents

1. [The seven sections](#1-the-seven-sections)
2. [Depth tiers](#2-depth-tiers)
3. [Frontmatter template](#3-frontmatter-template)
4. [Claim blocks: factual or assessment](#4-claim-blocks-factual-or-assessment)
5. [Footnote syntax and choosing evidence](#5-footnote-syntax-and-choosing-evidence)
6. [Operating model (synthetic)](#6-operating-model-synthetic)
7. [Domain maps](#7-domain-maps)
8. [Style](#8-style)
9. [Worked example](#9-worked-example)

## 1. The seven sections

File names are fixed. `executive-summary`, `application-architecture`,
`technology-architecture` and `operating-model` are required; the other three
are expected.

| File | Answers | Typical evidence |
|---|---|---|
| `executive-summary.md` | What is this application, who uses it, why it matters, its shape in one screen | README, top-level config, entry points |
| `business-architecture.md` | Capabilities it provides, actors, value streams, business rules it enforces | README, docs, ADRs, policy files |
| `application-architecture.md` | Components/modules, their responsibilities, interactions, entry points, key flows | code graph nodes, source files, module view |
| `data-architecture.md` | Data entities, formats, schemas, stores, lineage, retention | schemas, models, serializers, config |
| `technology-architecture.md` | Languages, frameworks, runtime, build, CI/CD, hosting, dependencies | package manifests, workflows, Dockerfiles, metrics.json |
| `security-architecture.md` | Trust boundaries, authn/z, secrets handling, supply chain, policy enforcement | SECURITY.md, workflows, policy code, auth code |
| `operating-model.md` | Teams, ownership, ceremonies, cadence — **fabricated in this prototype** | `.github/kf/config.yml` teams (see §6) |

Use H2 headings to organize each file. Headings are not claims and need no citation.

## 2. Depth tiers

| Tier | Apps | What to write |
|---|---|---|
| 1 | `kfcor`, `aacod` | All seven sections in full (executive 5–8 claim blocks; application 10–18; others 6–12) |
| 2 | `kfsit`, `folio` | Executive, application, technology, operating model in full; business, data, security present but short (3–6 blocks) |
| 3 | `cfskl` | All seven present, adapted: "application architecture" is the *skills* architecture (skill folders, prompts, tests); shorter |

Every tier carries complete provenance. Depth changes length, never citation rigor.

## 3. Frontmatter template

Copy exactly; change only the marked values. `controls` re-stamps the two source
pins automatically, but write them correctly anyway.

```yaml
---
type: application-bundle/application-architecture   # application-bundle/<file-name>
title: Application architecture — <App title>
description: One sentence saying what this section covers.
generated:
  by: process:building-application-bundles@0.1.0
  at: '2026-10-20T19:30:00-05:00'                   # = knowledge-source.json generated_at
sources:
- id: repo
  kind: source-repo
  repo: <owner/repo from knowledge-source.json>
  commit_sha: <full commit_sha from knowledge-source.json>
- id: graph
  kind: code-graph
  path: code-graph/code-graph.jsonl
  sha256: <sha256 of code-graph.jsonl>
x_kf:
  schema: kf-application-bundle/1
  appid: <appid>
  bundle_kind: application
  section: application-architecture                 # = file name; domain maps use `domain:`
  bootstrap: true                                   # only for content landed by direct bootstrap
---
```

Never add `verified` — acceptance is defined as presence on `main` after approval.

## 4. Claim blocks: factual or assessment

A **claim block** is a paragraph, a list item, or a table row (not the header
row). Headings, fenced code, Mermaid and footnote definitions are not claims.
Every claim block must be one of:

- **Factual** — carries at least one `src` or `graph` footnote that supports it.
- **Assessment** — starts exactly with `*Assessment:*`, and cites only footnotes
  already used by an **earlier factual block in the same file**. It interprets
  evidence; it never introduces new evidence.

Per file: at least one factual block, and assessments at most 50% of claim blocks.

Good:

```markdown
The librarian files capture notes through a local classifier and Claude.[^ing1]

*Assessment:* Routing and writing are separate models, so either can be swapped
without touching the bundle.[^ing1]
```

Fails the gate (and why):

```markdown
This section describes the architecture.            ← uncited claim block
*Assessment:* It is well tested.[^tests9]           ← new footnote in an assessment
| Component | Role |                                ← header row: fine
| Gate | Checks PRs |                               ← table row with no footnote
```

Introductory sentences are claims too: cite them or delete them. A table row needs
its own footnote (put it in the last cell).

## 5. Footnote syntax and choosing evidence

Two forms only. Write the `src` form **without** the hash; `fill_citations.py`
appends it.

```markdown
[^ing1]: src · tools/librarian/ingest.py#L40-L72
[^g7]: graph · tools/kb/graph.py::build_graph
```

- Paths are repo-relative at the pinned commit. Line numbers are 1-based, inclusive.
- Cite the **smallest range that supports the claim** — usually 3–30 lines. Never
  cite a whole long file to dodge the work; reviewers read the cited lines.
- Use `graph · <node-id>` for structural facts (a module or function exists, it is
  an entry point, it has high fan-in). Node ids are file paths or `path::Qual.name`;
  look them up in `code-graph/code-graph.jsonl`.
- Use `src` for behavioral facts (what the code does, what a config sets, what a
  doc states).
- One footnote may support several blocks; reuse ids freely.
- Footnote ids: letters, digits, `_`, `-`. Make them readable: `[^wf-publish]`.

After `fill_citations.py`, a hash changes only if the cited lines change at the
pinned commit — which is exactly when the claim must be re-checked.

## 6. Operating model (synthetic)

The operating model is **fabricated** for this prototype and must say so:

- Frontmatter: `x_kf.synthetic: true`, and the `description` must contain the word
  "illustrative". Synthetic files are exempt from the citation regime.
- `sources:` holds one entry: `{id: fixture, kind: synthetic-fixture, path: .github/kf/config.yml}`.
- Teams **must** be exactly the slugs registered for the appid in
  `.github/kf/config.yml` (with their time zones) — the gate binds team → appid.
- Include: a team table (slug, mission, owned components — name real components
  from the other sections), ceremony cadence per team (standup daily; sprint
  planning, backlog refinement, retro per two-week sprint), decision rights / RACI
  for bundle-update approvals, and how ceremony knowledge flows into
  `knowledge-sources/agile-ceremonies/<ceremony>/<team>/`.
- No real people's names, emails or phone numbers. Use roles ("product owner").

## 7. Domain maps

One or two files in `domains-maps/<domain>.md`: the application's domain
vocabulary — terms, their meaning, and where they live in code. Same frontmatter
with `type: application-bundle/domain-map` and `x_kf.domain: <file name>`
instead of `section`. Same citation regime: a glossary table row is a claim block.

## 8. Style

Plain, specific, present tense. Name real files, modules and commands. No
marketing adjectives. Say what the code does, not what it aspires to. Prefer a
table when comparing; prefer a sentence when explaining. Do not paste code —
cite it. Do not copy prose verbatim from the repo.

## 9. Worked example

```markdown
## Governance pipeline

Every change reaches `main` through a pull request; CI runs schema, date and
blocklist checks first.[^tests-wf]

Approval by the owner triggers a workflow that stamps `verified` on changed notes
using a GitHub App token.[^approve-wf]

*Assessment:* Verification is bound to a human approval event rather than to any
model output, which keeps machine writing and human attestation separate.[^approve-wf]

| Workflow | Trigger | Effect |
|---|---|---|
| `tests.yml` | pull request | runs the rule checks [^tests-wf] |
| `approve.yml` | review approved | stamps `verified` [^approve-wf] |

[^tests-wf]: src · .github/workflows/tests.yml#L1-L40
[^approve-wf]: src · .github/workflows/approve.yml#L1-L35
```

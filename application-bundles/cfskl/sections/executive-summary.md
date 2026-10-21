---
type: application-bundle/executive-summary
title: Executive summary — C4 skills
description: What the C4 skills package is, who uses it, and its overall shape at the pinned commit.
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
  section: executive-summary
  bootstrap: true
---
# Executive summary — C4 skills

## What it is

C4 skills is a package of agent-agnostic instruction files that teach an AI coding agent to work as a software architect, producing C4 model diagrams and Architecture Decision Records (ADRs).[^readme-what]

The package ships two skills: `c4designer`, which produces Mermaid C4 diagrams in five modes (design, document-code, document-prose, review, update), and `adr-scribe`, which drafts and reviews ADRs in three modes (interview, retro-document, review).[^readme-skills][^registry-skills]

The product is Markdown, not a running service: each skill is a folder holding a `SKILL.md` entry file plus mode files, templates, checklists and examples that the agent reads at run time.[^security-safe][^g-c4skill]

## Who uses it and how

The users are developers working with agents such as GitHub Copilot, Claude Code, Cursor, Devin and Windsurf; both skills declare these five agents in `compatible_agents`.[^registry-skills][^readme-compat]

Installation means copying a skill folder into the agent's skills directory (for example `.github/skills/` for Copilot or `.claude/skills/` for Claude Code), or running `install.sh`, which copies both skills into one detected target.[^readme-install][^install-loop]

A mock Internet Banking System under `tests/example-codebase` lets users try the skills on non-proprietary code, with golden diagrams to compare against.[^readme-sandbox]

## Shape in one screen

| Part | What it holds |
|---|---|
| `c4designer/` | Router `SKILL.md`, five mode files, Mermaid C4 syntax reference, level template, review checklist, supporting diagrams, two examples [^g-c4skill] |
| `adr-scribe/` | Router `SKILL.md`, three mode files, ADR template, review checklist, one example ADR [^g-adrskill] |
| `registry.json` | Machine-readable list of the skills with versions, dependencies, agents and modes [^registry-skills] |
| `tests/` | Shell test runner, two domain validators, behavioral fixtures, sandbox codebase [^readme-tests] |
| `docs/` | Docusaurus user guide deployed to GitHub Pages [^docs-wf] |

*Assessment:* Because the deliverable is plain text, the main quality risks are drift between instructions, templates and validators rather than runtime failures; the other sections record several such drifts at this commit.[^security-safe][^readme-tests]

[^readme-what]: src · README.md#L22-L26 · sha256:1ceb5d0d13ef95f1227ecb81c092a2d1403d8f2a9804c679a7245b1f09ef7d71
[^readme-skills]: src · README.md#L73-L93 · sha256:1d623f3338ed8569f95b97cb867ce5c1c1858a093d62250890b53127ba19cdf5
[^registry-skills]: src · registry.json#L1-L37 · sha256:697fc30e823a4b2ecf2e454d2a9440e2fe572dcddc9470570721b8cf32b24981
[^security-safe]: src · SECURITY.md#L11-L17 · sha256:42ec0f46c9903d5f97069c5bc367e4bb2cdc2396d55412e174c0ed9fb252d1f5
[^g-c4skill]: graph · c4designer/SKILL.md
[^g-adrskill]: graph · adr-scribe/SKILL.md
[^readme-compat]: src · README.md#L60-L69 · sha256:ea795be6fea569c6819c8e46da8e00971f821f09adf6939ee17b4dbf13372a88
[^readme-install]: src · README.md#L97-L133 · sha256:cafd8aecd539fefc5658303e8653bf204c243043c0059f46fd9199c0d31b4296
[^install-loop]: src · install.sh#L30-L36 · sha256:519f2cc94f1c054156473570cd8f80b67f124c2d0ce16cfd8f3aa17dd93feed2
[^readme-sandbox]: src · README.md#L137-L146 · sha256:6c3173f51b69fdcc234f103fb8d60ef23b162ed4869c375eef3d2be6db9a5364
[^readme-tests]: src · README.md#L150-L164 · sha256:06c3a21e4c3fee6ea3d70aeb62a3c51aee42a98a835667f061e0900bd4e63734
[^docs-wf]: src · .github/workflows/docs.yml#L1-L42 · sha256:fb15760460a99475002fd7b9d1efb3d2e0aab2a707da103b973a026f31507b74

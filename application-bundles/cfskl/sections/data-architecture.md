---
type: application-bundle/data-architecture
title: Data architecture — C4 skills
description: The artifacts C4 skills reads and produces — skill metadata, registry, output document layouts,
  ADR template and test fixtures.
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
  section: data-architecture
  bootstrap: true
---
# Data architecture — C4 skills

The package has no database; its data is files: metadata about the skills, and Markdown documents the agent writes into the user's repository.[^security-safe]

## Skill metadata

| Artifact | Fields | Evidence |
|---|---|---|
| `SKILL.md` frontmatter | `name`, `version`, `requires`, `compatible_agents`, `description` | [^c4-fm] |
| `registry.json` | Package `name`, `version`, `description`; per skill `id`, `name`, `version`, `description`, `requires`, `compatible_agents`, `path`, `modes` | [^registry] |

The `c4designer/SKILL.md` frontmatter is not valid YAML: its unquoted `description` contains `: ` sequences, and the code graph marks the file with `parse_error`; the test runner reads fields with `grep`, so it does not detect this.[^c4-fm][^g-c4skill][^suite1]

The only version consistency check compares the registry's first `version` with the `c4designer` frontmatter version; the per-skill versions and the `adr-scribe` frontmatter version are not compared.[^suite4]

## Output documents

`c4designer` writes one Markdown file per C4 level under `docs/architecture/` (`01-context.md`, `02-container.md`, `03-component-<container>.md`, `04-code-<component>.md`), each structured by `level-template.md`.[^c4-deliverable][^level-template]

`adr-scribe` writes ADRs to `docs/adr/` with a numbered file name such as `0001-use-redis-for-caching.md`.[^adr-destination]

The ADR template has a title, `* Status:` and `* Date:` lines, then Context and Problem Statement, optional Decision Drivers, Considered Options, Decision Outcome, and Positive and Negative Consequences, the last two marked optional.[^adr-template]

`adr-scribe/SKILL.md` calls this the Michael Nygard MADR format and summarises it as Title, Status, Context, Decision and Consequences.[^adr-skill-template]

`validate-adr.sh` requires `* Status:`, `## Context`, `## Considered Options`, `## Decision Outcome` and `### Negative Consequences`.[^adr-validator]

*Assessment:* `adr-scribe/SKILL.md` describes the template as a five-part Nygard format (Title, Status, Context, Decision, Consequences), but the template and `validate-adr.sh` follow MADR headings, and the validator requires the Negative Consequences section that the template marks optional.[^adr-template][^adr-skill-template][^adr-validator]

## Test fixtures

Each behavioral fixture is a directory with `prompt.md` (must contain `## Acceptance Criteria`), `expected.md` (the golden output) and `skill.txt` (routes to a validator); a `negative-` prefix inverts the expected result.[^contrib-fixtures][^suite3]

[^security-safe]: src · SECURITY.md#L11-L17 · sha256:42ec0f46c9903d5f97069c5bc367e4bb2cdc2396d55412e174c0ed9fb252d1f5
[^c4-fm]: src · c4designer/SKILL.md#L1-L7 · sha256:f99980a6759e1a47ba85e979e6cf288ba5291785eb83b79a2b06837b19dfe3e1
[^registry]: src · registry.json#L1-L37 · sha256:697fc30e823a4b2ecf2e454d2a9440e2fe572dcddc9470570721b8cf32b24981
[^g-c4skill]: graph · c4designer/SKILL.md
[^suite1]: src · tests/test-skill-format.sh#L78-L102 · sha256:b1840d783ba3ef507ea167f231f160fdcec36974481ea681eadd20b92377b4d5
[^suite4]: src · tests/test-skill-format.sh#L243-L250 · sha256:951b07ad04a8c8a3d234db4df95baed441b96dbc7b8c2a80b00954ad8277d054
[^c4-deliverable]: src · c4designer/SKILL.md#L102-L128 · sha256:1dfa5233f0f6b58471d77748a9644bac5177e4132e4d841bdcbd7d8c877157a1
[^level-template]: src · c4designer/level-template.md#L1-L59 · sha256:aee9bce3cb97a5cd243df313296a88897a11dc40ac906b8b4396a265e5ed9574
[^adr-destination]: src · adr-scribe/SKILL.md#L52-L54 · sha256:3b7d482c3c9c3272b37740a6952ab9028230696bd0ee01a0217ef4d02e4b6a8b
[^adr-template]: src · adr-scribe/adr-template.md#L1-L35 · sha256:713103aa46a3167c464a803bd40e6b24628a3eb958618d345867a10e634be1ec
[^adr-skill-template]: src · adr-scribe/SKILL.md#L38-L45 · sha256:7c012c4ed610b0fb1738ed700e0d8361c6ef28bb1bacc6b5156193760a6a55e8
[^adr-validator]: src · tests/validate-adr.sh#L19-L47 · sha256:5a8bef5e410db5aa9d8c8db9efc34cfcf552702b04d2bdbcd77d99d07fe212c4
[^contrib-fixtures]: src · CONTRIBUTING.md#L34-L43 · sha256:9f03633a2be6b7a71cc40237c8e93a16defbeab773275c2d525894b757f273dd
[^suite3]: src · tests/test-skill-format.sh#L170-L208 · sha256:4260bbe3cd1c8d826a3f85ba9c0c1121c9b27614e8553102bb3d91b21f973660

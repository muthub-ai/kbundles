---
type: application-bundle/security-architecture
title: Security architecture — Knowledge Foundation core
description: Trust boundaries, approval binding, token and secret handling, the confidential-terms guardrail
  and supply-chain controls in Knowledge Foundation core.
generated:
  by: process:building-application-bundles@0.1.0
  at: '2026-10-20T19:30:00-05:00'
sources:
- id: repo
  kind: source-repo
  repo: muthub-ai/knowledge-foundation
  commit_sha: 78d41952391c91356afbebfaee129b8b40a12561
- id: graph
  kind: code-graph
  path: code-graph/code-graph.jsonl
  sha256: 881e9bd0100d27591d42a861bc0797c5ae5cb88f764837f511242482b5d82a7d
x_kf:
  schema: kf-application-bundle/1
  appid: kfcor
  bundle_kind: application
  section: security-architecture
  bootstrap: true
---
# Security architecture — Knowledge Foundation core

## Scope and boundaries

The repository is public and by design holds no credentials or private material; secrets live only in GitHub Actions secrets, the in-scope surface is `.github/`, `tools/` and `wiki/`, and problems are reported through private vulnerability reporting.[^security-md]

## Human approval binding

`approve.yml` runs only for an approved review submitted by the repository owner, checks out the stamping code from the base branch so the pull request's files are treated as data, and refuses to stamp when the approved commit is no longer the branch head.[^approve-if] [^approve-base] [^approve-head]

`governance.stamp` raises unless the actor starts with `human:`, and a repeat approval by the same actor on the same day adds no second event.[^stamp-human] [^g-stamp]

## Tokens and permissions

Every workflow defaults to `contents: read`; only `publish.yml` takes `contents: write`, and its job runs only for `refs/heads/main`, so a manual dispatch from another branch cannot release unmerged notes.[^approve-perm] [^tests-perm] [^weekly-perm] [^ingest-perm] [^publish-perm]

Bot pull requests and stamp commits use a GitHub App token, because events created with the built-in `GITHUB_TOKEN` would not trigger the required checks.[^adr005]

In `tests.yml`, a bot-authored pull request that changes anything outside `wiki/`, `inbox/` and `evals/` fails before the step that receives the confidential-terms secret runs.[^tests-guard]

The Claude Code steps in `weekly.yml` and `ingest.yml` run with an explicit tool allowlist, a turn limit and a dollar budget, and their only push permission is to the current branch head.[^weekly-tools] [^ingest-tools]

User-supplied workflow inputs in `ingest.yml` reach the shell through environment variables rather than expression interpolation.[^ingest-env]

## Confidential-terms guardrail

Terms come from the `CONFIDENTIAL_TERMS` secret or a git-ignored local file, match as whole words, and are reported only by their position in the list, never by the matched text; CI requires a non-empty list except on Dependabot pull requests, which cannot read secrets.[^bl-doc] [^bl-report] [^tests-bl]

## Review ownership and supply chain

`CODEOWNERS` assigns every path to the owning account, with `.github/`, `tools/`, `schemas/`, `ontology/`, `prompts/`, `skills/` and `AGENTS.md` named explicitly; Python packages are exact pins, and Dependabot proposes weekly pip and Actions updates.[^codeowners] [^req-pin] [^dependabot]

*Assessment:* The approval path separates who may attest (the owner, checked on the review event) from what code performs the attestation (always the base branch), which closes the obvious route of a pull request rewriting the stamp tool to verify itself.[^approve-if] [^approve-base]

*Assessment:* Restricting agent pull requests to knowledge paths before secrets are exposed means a compromised or misdirected curator can at worst propose wrong notes, which the owner's review then has to catch.[^tests-guard] [^weekly-tools]

[^security-md]: src · SECURITY.md#L1-L11 · sha256:72a17823b447ee5d9ef785308159113f0f04e3a3e357a001104ef0b97b47c138
[^approve-if]: src · .github/workflows/approve.yml#L12-L14 · sha256:b1c06af15b47ed61c160b4e7b828ecdb0c65424bf7113e74ebd20d38b272e1cf
[^approve-base]: src · .github/workflows/approve.yml#L23-L26 · sha256:f288e78126452730b11a1e63862bd2cdee43c27e491432fc2597d87b82cbc6b5
[^approve-head]: src · .github/workflows/approve.yml#L27-L40 · sha256:ef79394f8de9aecb3c4a59740ce9faba809b599bbb48143c003777675d79fa4b
[^stamp-human]: src · tools/kb/governance.py#L51-L71 · sha256:c1e5a7d83bbc979d65689e62da7f159c7c88a51cc287446bdcf4bc76887c5f2f
[^g-stamp]: graph · tools/kb/governance.py::stamp
[^approve-perm]: src · .github/workflows/approve.yml#L9-L10 · sha256:e8f2263b0413f25128aa11d16dd3ae0ef6b0c660fb5b1dc08fe71e0a7daabb4b
[^tests-perm]: src · .github/workflows/tests.yml#L9-L10 · sha256:e8f2263b0413f25128aa11d16dd3ae0ef6b0c660fb5b1dc08fe71e0a7daabb4b
[^weekly-perm]: src · .github/workflows/weekly.yml#L9-L10 · sha256:e8f2263b0413f25128aa11d16dd3ae0ef6b0c660fb5b1dc08fe71e0a7daabb4b
[^ingest-perm]: src · .github/workflows/ingest.yml#L15-L16 · sha256:e8f2263b0413f25128aa11d16dd3ae0ef6b0c660fb5b1dc08fe71e0a7daabb4b
[^publish-perm]: src · .github/workflows/publish.yml#L11-L21 · sha256:0035dd4a3d2bac6431883fb85480f86f49222653ab1bdff40140dd9ab9ec4a1a
[^adr005]: src · decisions/005-a-github-app-authors-automated-pull-requests-and-stamp-commi.md#L5-L15 · sha256:7b7099d813d33176cac8f4c7266c1222bb91e338b09fbaf357ac1377918baca9
[^tests-guard]: src · .github/workflows/tests.yml#L43-L53 · sha256:e005ac1531091a075250a3640c7839ded5c92517caffa7ca63644e6b5e91c06a
[^weekly-tools]: src · .github/workflows/weekly.yml#L38-L55 · sha256:1dc5fa78b89710c69a2a3da7bb552b83bf61b69fd6d42bb22403794987b45ba3
[^ingest-tools]: src · .github/workflows/ingest.yml#L68-L78 · sha256:efc96aa7a6dc6b9b8e1586436f1d9d9a6bf6689d9621abb3462a4756e1790780
[^ingest-env]: src · .github/workflows/ingest.yml#L45-L67 · sha256:2b0aa3416c235fb9ffe563e48c75ee4c728300cb0840b0881e1a0f160b3ca8ea
[^bl-doc]: src · tools/kb/blocklist.py#L1-L28 · sha256:bc7e6c917a7476dca170c4ce589eafb0ff7c06f68dce477e42ca7c42ad7960cf
[^bl-report]: src · tools/kb/blocklist.py#L41-L46 · sha256:925876b7f3073cc228ddbf6c31c2445a8b99bfbd1be71974109a7fedd8b26723
[^tests-bl]: src · .github/workflows/tests.yml#L57-L64 · sha256:2836f80cbacc20b7a3a61e6130d2a6a1e7b6413687d8ac09ef24c2c5547798a2
[^codeowners]: src · .github/CODEOWNERS#L1-L10 · sha256:d6b1550d41459d5ee537b456073b42ea0af77b0637943aebc5fa2d6ec28b79b9
[^req-pin]: src · requirements.txt#L1-L6 · sha256:07b7c171239da5b738b21f2be7c9086d8b76905f41e3f7f670563c9b5a4c3ff3
[^dependabot]: src · .github/dependabot.yml#L1-L8 · sha256:3cd2485d7be02802072a1177ac8ac9969e554466153d4e701fa3ac41cc09aad7

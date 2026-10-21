---
type: application-bundle/security-architecture
title: Security architecture — C4 skills
description: Trust boundaries, data handling claims, supply chain and vulnerability reporting for the
  C4 skills package.
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
  section: security-architecture
  bootstrap: true
---
# Security architecture — C4 skills

## Trust boundary

`SECURITY.md` states that the package is Markdown instructions with no production code, that the skills never send data outside the agent session, and that the test scripts run only in CI, not inside the agent lifecycle.[^security-safe]

*Assessment:* The effective trust boundary is the host agent: the skills inherit whatever file-system, tool and network permissions that agent already has, and the package itself adds no enforcement.[^security-safe]

The skills limit external destinations by instruction: an agent may offer Notion, Linear, Google Drive or similar only when a matching integration is actually present in the session, and must confirm before writing.[^c4-destination][^adr-destination]

## Vulnerability reporting

The policy names prompt injection that could make an agent act maliciously in the IDE as an in-scope issue, asks reporters to contact the maintainer privately rather than file a public issue, and targets a 48-hour response.[^security-report]

The supported-versions table lists only `1.0.0`, while the skills and registry are at `1.2.0`.[^security-versions][^registry]

## Supply chain and CI permissions

The documentation workflow holds `contents: write` and deploys with the repository token through `peaceiris/actions-gh-pages@v3`, an action referenced by tag rather than by commit SHA; the test workflow declares no explicit permissions.[^docs-wf][^test-wf]

`install.sh` copies files with `cp -r` from its own directory and runs no network calls, so installation trusts the local checkout.[^install-loop]

## Sandbox secrets

The sandbox ships placeholder credentials (`POSTGRES_PASSWORD: secret` in `docker-compose.yml` and `SMTP_PASS=secret` in `.env.example`) for a fictional bank; these are test fixtures, not live secrets.[^sandbox-compose][^sandbox-env]

[^security-safe]: src · SECURITY.md#L11-L17 · sha256:42ec0f46c9903d5f97069c5bc367e4bb2cdc2396d55412e174c0ed9fb252d1f5
[^c4-destination]: src · c4designer/SKILL.md#L72-L81 · sha256:1dc743bcc724d81ae267d738ba541d0c3ecfb1dc8aacf142948f9d32d34a60a7
[^adr-destination]: src · adr-scribe/SKILL.md#L52-L54 · sha256:3b7d482c3c9c3272b37740a6952ab9028230696bd0ee01a0217ef4d02e4b6a8b
[^security-report]: src · SECURITY.md#L19-L23 · sha256:798c6654097b9a5319f8a5c1283e16dc4c7a0bd7dc2805931eb98e0cabfbbe3b
[^security-versions]: src · SECURITY.md#L3-L9 · sha256:1c5bc5515e8f983fb18da5063e95c94d43129cdadacd94f4a9e87f0bf08f93d6
[^registry]: src · registry.json#L1-L9 · sha256:88fe02d086ed5c796db2a44ef67035932f91d99d72f1dc8fe2e149331b70b47e
[^docs-wf]: src · .github/workflows/docs.yml#L11-L42 · sha256:f48fa31fdd78b6af6ecfc64aebc6c9fe9a8aee3f213871d39f206dcaf904d82a
[^test-wf]: src · .github/workflows/test.yml#L1-L23 · sha256:52e23310cba2c9deb985bc542e82b8c26048a3a9b5277abdd69322199df40362
[^install-loop]: src · install.sh#L1-L38 · sha256:5fee51b6e8784aaa083a307e6839c557624469408c9794f496f96cfa12748e44
[^sandbox-compose]: src · tests/example-codebase/docker-compose.yml#L20-L26 · sha256:96278900e3d4719c9bc724fa835f4caba056f0040f210a1432bd82defff78a5e
[^sandbox-env]: src · tests/example-codebase/.env.example#L1-L12 · sha256:d31ed480f438324f8157706e0424f7c5e35bd941aa49051005c93e252e49b370

---
type: application-bundle/technology-architecture
title: Technology architecture — C4 skills
description: Languages, file formats, build and test tooling, CI/CD workflows, documentation hosting and
  dependencies of C4 skills.
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
  section: technology-architecture
  bootstrap: true
---
# Technology architecture — C4 skills

## Languages and formats

The skills themselves are Markdown files with YAML frontmatter; the repository describes itself as text instructions with no code that runs in a production environment.[^security-safe][^c4-fm]

Diagrams are authored in Mermaid C4 (`C4Context`, `C4Container`, `C4Component`, `C4Dynamic`, `C4Deployment`), with UML `classDiagram` for level 4 because Mermaid has no `C4Code` type.[^syntax-types]

The skill instructions treat Mermaid's C4 support as experimental and tell the agent to verify rendering in the target viewer; Structurizr DSL, C4-PlantUML and image export are negotiated alternatives.[^c4-output]

The only executable code is Bash: the installer and three test scripts, all of which the code graph records as command-line entry points.[^g-install][^g-runner]

| Tool | Language | Purpose |
|---|---|---|
| `install.sh` | Bash | Copies both skill folders into one agent discovery directory [^install-loop] |
| `tests/test-skill-format.sh` | Bash | Four-suite test runner [^g-runner] |
| `tests/validate-c4-diagram.sh` | Bash (`grep`, `awk`, `sed`) | Mermaid C4 linter [^c4-validator] |
| `tests/validate-adr.sh` | Bash (`grep`) | ADR section linter [^adr-validator] |
| `Makefile` | Make | `test`, `install`, `lint` targets [^makefile] |

## CI/CD

The `Tests` workflow runs on push and pull request to every branch on `ubuntu-latest`, marks two scripts executable and runs `tests/test-skill-format.sh`.[^test-wf]

*Assessment:* The workflow's `chmod` step omits `validate-adr.sh`, which the runner invokes directly, so ADR validation in CI relies on the checkout preserving the script's executable bit.[^test-wf][^adr-validator]

The `Deploy Documentation` workflow runs on pushes to `main` that touch `docs/**` (or on manual dispatch), builds the site with Node 20 and `npm ci`, and publishes `docs/build` to GitHub Pages with `peaceiris/actions-gh-pages@v3` using the built-in token and `contents: write`.[^docs-wf]

Both workflows pin third-party actions by major version tag (`actions/checkout@v4`, `actions/setup-node@v4`, `peaceiris/actions-gh-pages@v3`), not by commit SHA.[^docs-wf][^test-wf]

## Documentation site

The user guide is a Docusaurus 3.7.0 site with the Mermaid theme, React 18 and Node `>=18`, served at `https://muthub-ai.github.io/c4-skills/`.[^docs-pkg][^docs-config]

The Docusaurus build cache folder `docs/.docusaurus/` is committed to the repository even though its own marker file says it is regenerated on every build; it accounts for most of the JSON files in the repository.[^docusaurus-marker][^g-registryjs]

The site footer links to `/reference/mermaid-c4-syntax`, but `docs/sidebars.js` registers no reference page and the config sets `onBrokenLinks: 'warn'`, so the build does not fail on that link.[^docs-footer][^docs-config][^sidebars]

## Sandbox dependencies

The sandbox under `tests/example-codebase` declares Express 4 and `pg` 8 for its mock API and composes an SPA, the API and a `postgres:15` database; it is fixture material for the skills, not part of the delivered package.[^sandbox-api-pkg][^sandbox-compose]

*Assessment:* The compose file builds `./frontend` and `./api`, but neither directory holds a Dockerfile at this commit, so the sandbox is meant to be read by an agent rather than run.[^sandbox-compose]

[^security-safe]: src · SECURITY.md#L11-L17 · sha256:42ec0f46c9903d5f97069c5bc367e4bb2cdc2396d55412e174c0ed9fb252d1f5
[^c4-fm]: src · c4designer/SKILL.md#L1-L7 · sha256:f99980a6759e1a47ba85e979e6cf288ba5291785eb83b79a2b06837b19dfe3e1
[^syntax-types]: src · c4designer/mermaid-c4-syntax.md#L9-L19 · sha256:a956990fc69fe1f4db712be26744ee690c6f92938647fcb27e51154a24a597b2
[^c4-output]: src · c4designer/SKILL.md#L59-L70 · sha256:75b5a838a8e78e1a8c073ff6b0e4e5d2be4f02de6e6a4b0af32e8a37e0317518
[^g-install]: graph · install.sh
[^g-runner]: graph · tests/test-skill-format.sh
[^install-loop]: src · install.sh#L30-L36 · sha256:519f2cc94f1c054156473570cd8f80b67f124c2d0ce16cfd8f3aa17dd93feed2
[^c4-validator]: src · tests/validate-c4-diagram.sh#L19-L80 · sha256:aee5768164af7267aa71e4606f13e3e17ed8c9734870b52c498db53459bbdc15
[^adr-validator]: src · tests/validate-adr.sh#L19-L47 · sha256:5a8bef5e410db5aa9d8c8db9efc34cfcf552702b04d2bdbcd77d99d07fe212c4
[^makefile]: src · Makefile#L1-L16 · sha256:3e231fb09b7c2a31c102fc9f2b3d051f20f20a325046e1669c963bb27485d198
[^test-wf]: src · .github/workflows/test.yml#L1-L23 · sha256:52e23310cba2c9deb985bc542e82b8c26048a3a9b5277abdd69322199df40362
[^docs-wf]: src · .github/workflows/docs.yml#L1-L42 · sha256:fb15760460a99475002fd7b9d1efb3d2e0aab2a707da103b973a026f31507b74
[^docs-pkg]: src · docs/package.json#L12-L28 · sha256:50fcae90c39bb1cbd9fb8966782bcd049bdebad40a8cd47bb153bfef831bcc1a
[^docs-config]: src · docs/docusaurus.config.js#L5-L17 · sha256:afb22999d6c0212234e9eb9bad3b8a0cad2939361370479bddb0716c9b7dd39a
[^docusaurus-marker]: src · docs/.docusaurus/DONT-EDIT-THIS-FOLDER#L1-L5 · sha256:d06e93133c9a3abf2e331df2886028788a5639258b38348d6d31c27e19a3cf44
[^g-registryjs]: graph · docs/.docusaurus/registry.js
[^docs-footer]: src · docs/docusaurus.config.js#L67-L73 · sha256:b16712f01704bf0ba0af3b4fe38bb110fb5b62f8a427ec21697c48b2a69af1a8
[^sidebars]: src · docs/sidebars.js#L1-L72 · sha256:604f68299d103a2e4bbdf620bd0e1b8b3e939ec98664a7cadef91ba4ca394fec
[^sandbox-api-pkg]: src · tests/example-codebase/api/package.json#L1-L9 · sha256:f01527fdbdb1c73bb05360558ea87f85f1e97808cbb465c36c42f76635e9ac7e
[^sandbox-compose]: src · tests/example-codebase/docker-compose.yml#L1-L26 · sha256:1d456744d616146891348e3ff9f26402ddda2c7392d706e0c19128d9de41763d

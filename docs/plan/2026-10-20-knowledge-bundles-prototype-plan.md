# kbundles — Knowledge Bundles Prototype Plan

| | |
|---|---|
| **Status** | **v0.2 — CONFIRMED by two‑model review** (18 findings + 3‑point confirm round, all resolved — Appendix A); awaiting Muthu's approval (§13) |
| **Date** | 2026‑10‑20 |
| **Target repo** | `muthub-ai/kbundles` — *currently spelled `kbundels` on GitHub; rename pending (§13‑1)* |
| **Source repos (read‑only)** | `muthub-ai/knowledge-foundation` · `knowledge-foundation-site` · `muthu-v0-portfolio-website` · `aac` · `c4-skills` |
| **Parent spec** | KF Grill‑Me Architecture Specification v0.4; this plan implements its gate prototype and adds the application‑bundle layer (spec deltas D17–D19, §6) |

## 1. Objective

`kbundles` is the Knowledge Foundation's **knowledge bundles** repo. A knowledge bundle is the governed unit of knowledge in KF; the **application bundle** — deep, code‑grounded documentation of one application — is the first *kind* of knowledge bundle, and this prototype builds it. Future kinds (domain bundles, process bundles, …) get their own top‑level folder **and their own registered gate class** — an unregistered kind fails closed (§6.1); governance is never implicit.

The prototype: for five real repos, generate a complete, OKF v0.2‑conformant **application bundle** (architecture sections + code graph + operating model), seed them into `kbundles` under `application-bundles/<appid>/`, and protect the repo with the **kf‑knowledge‑gate** from spec v0.4 — demonstrated live with green and red PRs produced by a grill‑me **simulator** (no grill‑me agent). Ship a reusable **skill** that regenerates an application bundle for any future repo.

Naming rule: the generated deep documentation is an **application bundle** everywhere (never "deepwiki"); the repo and the category are **knowledge bundles**.

## 2. Deliverables

1. **Five application bundles** with all OKF control files, architecture sections (per‑claim verifiable citations), a reproducible tree‑sitter code graph, and a fabricated‑but‑labeled operating model (2–3 teams per app).
2. **`kf-knowledge-gate`** (Python) as a required check on every PR: spec v0.4 gates G1–G10 adapted to the `application-bundles/` prefix, a fully specified **bundle‑update PR class**, fail‑closed class dispatch, protected‑content rule, revert class, and content‑bound named‑approver enforcement. Built on the spec's real plumbing (four workflows, `pull_request_target` base‑ref code, Checks‑API check run); only App pinning, the deploy environment, and rulesets are deferred to `PRODUCTION.md`.
3. **`simulate_grill.py`** implementing the spec §7.2 safe‑push protocol exactly (author check, SHA lease, regenerate‑not‑rebase, byte‑splice, date‑ordered logs, `--refresh`, `--now` injection), under its own identity `process:kf-grill-sim`.
4. **Scenario gallery derived from spec §13/§14 criterion ids** — ~15 live PRs plus local‑mode CI fixtures (§8).
5. **`building-application-bundles` skill** — canonical scripts in the skill folder, in‑repo + proposed to Muthu's Claude account (§9).
6. **Docs**: README (runbook + generated scenario matrix), `PRODUCTION.md` (demo→prod delta, incl. the forgery known‑fail), this plan at `docs/plan/`.

## 3. App ids (for approval)

Rule: exactly 5 lowercase letters (`^[a-z]{5}$`), unique, registered in the trust‑root registry with the source repo's full name **and immutable GitHub repo id** (rename‑proof). Reserved appids: `index`, `admin`, `other`, current and future bundle‑kind names (`appbd`, `dombd`, `prcbd`). Soft warning when a new appid is within edit distance 2 of an existing one.

| Source repo | Proposed appid | Rationale | Alternate |
|---|---|---|---|
| knowledge-foundation | `kfcor` | KF core platform | `knfdn` |
| knowledge-foundation-site | `kfsit` | KF site/explorer | `kfweb` |
| muthu-v0-portfolio-website | `folio` | portfolio | `mport` |
| aac | `aacod` | Architecture‑as‑Code | `archc` |
| c4-skills | `cfskl` | C‑four skills | `cskil` |

## 4. Full repository structure (verify this tree)

```text
kbundles/
├── README.md                          # what this is, runbook, GENERATED scenario matrix
├── PRODUCTION.md                      # demo→prod delta: App-pinned check, main-only environment,
│                                      #   .github/workflows/** push ruleset, no-bypass; forgery
│                                      #   test documented as known-fail in demo mode
├── docs/
│   ├── plan/
│   │   └── 2026-10-20-knowledge-bundles-prototype-plan.md    # this document (names spec v0.4)
│   └── bootstrap-verdicts/            # only under the fallback bootstrap (§7B): local-gate
│                                      #   verdict JSON for every bootstrapped knowledge file
├── .github/
│   ├── CODEOWNERS                     # required code-owner review: .github/**, gate/**, tools/**,
│   │                                  #   skills/**  (trust root — review finding P1)
│   ├── kf/
│   │   ├── config.yml                 # TRUST ROOT: appid registry (repo full name + repo id,
│   │   │                              #   owners(appid), teams, timezones, aliases), revert
│   │   │                              #   fallback approvers
│   │   └── toolchain.lock             # pinned py-tree-sitter + grammar wheel versions; the gate
│   │                                  #   compares code-graph.json against the BASE-ref copy
│   └── workflows/                     # all four, per spec Appendix B (finding P2)
│       ├── kf-gate.yml                # pull_request_target → base-ref code; head files read as
│       │                              #   API data; check run created via Checks API (distinct
│       │                              #   name from the job), job-level checks:write
│       ├── kf-gate-review.yml         # on: pull_request_review — unprivileged no-op trigger
│       ├── kf-gate-rerun.yml          # on: workflow_run → re-evaluate approval (default-branch code)
│       └── kf-tripwire.yml            # on: push(main) — semantic lint, alert-only
├── kf_lint/                           # ONE shared rule library (finding P16): OKF schema, G2/G6
│                                      #   logic, control-file checks — imported by gate AND validator
├── gate/
│   ├── run.py                         # entrypoint + local mode: --base <ref> --head <ref> [--now T]
│   ├── classes.py                     # ceremony | bundle-update | revert | other(allowlist:
│   │                                  #   README/PRODUCTION/docs) | UNKNOWN → fail closed
│   ├── gates/
│   │   ├── g01_path_allowlist.py … g10_trailer.py      # spec gates, D17 prefix
│   │   ├── g06b_bundle_provenance.py  # G6-bundle: per-claim src·path#L·span_sha256 verified at
│   │   │                              #   pinned SHA / graph·node-id; Assessment-block rules (§6.3)
│   │   ├── g11_graph_reproducible.py  # bundle-update: toolchain.lock(base) match → shallow fetch
│   │   │                              #   @SHA → extractor re-run → byte equality (§6.4)
│   │   ├── protected_content.py       # EVERY PR: knowledge-sources/** immutable (except revert);
│   │   │                              #   ceremony manifest entries byte-identical; root log insert-only
│   │   ├── revert_class.py            # semantic inverse of one merged squash + Reverted block;
│   │   │                              #   x_kf.bootstrap files excluded as targets
│   │   └── approval.py                # content-bound; ceremony: frontmatter approver; bundle-update:
│   │                                  #   approver ∈ owners(appid); approver ≠ author
│   └── requirements.txt               # pinned
├── tools/
│   ├── bundle_builder/                # thin orchestrator — imports skills/…/scripts (canonical)
│   └── simulate_grill.py              # GrillResult JSON → §7.2 safe-push → PR; --refresh; --now;
│                                      #   identity process:kf-grill-sim@x; trailer KF-Grill-Client:
│                                      #   kf-grill-sim; x_kf.synthetic: true on every output
├── scenarios/
│   ├── matrix.yml                     # criterion-id–keyed source of truth: spec §13/§14 id →
│   │                                  #   scenario file → live-PR | local-fixture → expected verdict;
│   │                                  #   README matrix and CI fixture run are GENERATED from this
│   ├── live/                          # ~15 shown as real PRs (§8 table)
│   └── fixtures/                      # the rest run in CI via gate local mode
├── skills/
│   └── building-application-bundles/
│       ├── SKILL.md                   # <500 lines; gerund name; 3rd-person description w/ triggers;
│       │                              #   Requirements block (python, pinned wheels, network for
│       │                              #   clone); checklist workflow; validation loop = kf_lint +
│       │                              #   G6-bundle citation verifier; degraded inventory-only mode
│       ├── reference/                 # one level deep, ToCs: code-graph-schema.md,
│       │                              #   section-authoring-guide.md (incl. *Assessment:* marker),
│       │                              #   okf-control-files.md
│       ├── scripts/                   # CANONICAL code (finding P15): extract_graph.py,
│       │                              #   scaffold_sections.py, build_controls.py, validate_bundle.py
│       └── evals/                     # ≥3, pinned repo+SHA, + no-skill baseline (§9)
└── application-bundles/
    ├── kfcor/                         # template shape for all five
    │   ├── index.md                   # links to sections + DIRECTORIES only (never ceremony files
    │   │                              #   — stale-proof); regenerated only by bundle-update class
    │   ├── log.md                     # appid-root log: bundle-level events; INSERT-ONLY (gate-
    │   │                              #   checked); ceremony PRs may never touch it (red scenario)
    │   ├── bundle-manifest.json       # spec §5.4 shape; per-entry byte-splice/replace ONLY
    │   ├── knowledge-source.json      # source repo + repo id, pinned commit_sha, builder version,
    │   │                              #   bundle-update approver (∈ owners(appid))
    │   ├── domains-maps/<domain>.md
    │   ├── code-graph/
    │   │   ├── code-graph.jsonl       # sorted JSONL, canonical form, stable ids path::qualname;
    │   │   │                          #   extractor+grammar versions stamped; ≤5 MB/shard, sharded
    │   │   │                          #   by top dir beyond; third_party-flagged vendored subtrees
    │   │   ├── metrics.json           # fan-in/out only (no churn — shallow clone)
    │   │   └── views/                 # Mermaid DERIVED from graph; module/dir aggregation,
    │   │                              #   ≤50 nodes / ≤150 edges per view
    │   ├── sections/                  # x_kf.appid + x_kf.bundle_kind: application on every file
    │   │   ├── executive-summary.md
    │   │   ├── business-architecture.md
    │   │   ├── application-architecture.md
    │   │   ├── data-architecture.md
    │   │   ├── technology-architecture.md
    │   │   ├── security-architecture.md        # where warranted (aacod: OPA/Rego)
    │   │   └── operating-model.md              # fabricated teams; x_kf.synthetic: true
    │   └── knowledge-sources/
    │       └── agile-ceremonies/standup/<team>/   # log.md + standup_<date>.md
    │                                              # seeded for EVERY team (finding P4)
    ├── kfsit/ · folio/ · aacod/ · cfskl/          # same shape
```

## 5. Application‑bundle generation (per repo)

Pipeline (`build_bundle.py` → canonical scripts in the skill; re‑runnable):

1. **Pin**: `git init && git fetch --depth 1 origin <sha>` (not `clone --depth`), record `commit_sha` + GitHub repo id.
2. **Code graph** (py‑tree‑sitter ≥0.22 API, wheels pinned in `toolchain.lock`): extension map `.ts/.mts/.cts/.d.ts→typescript`, `.tsx→tsx`, `.js/.mjs/.cjs/.jsx→javascript`, `.py→python`, `.sh`/shebang→bash. **Honest edges** (finding P10): `defines` and `imports` (tsconfig `paths`/baseUrl aliases and barrel re‑exports resolved) are exact; `calls` carry a mandatory `resolution: local | import-bound | name-only` attribute with unresolved targets as `ref:<name>` placeholder nodes — never guessed; no `references` edge type. Framework entry points (Next.js `app/**/page.tsx`/`route.ts`, CLI mains, MCP tool registrations) flagged `entrypoint`. YAML/Markdown/Rego → **structured‑inventory nodes** (PyYAML; frontmatter+links; Rego package/rule‑head extraction tagged `extractor: regex`). Parse failures become `parse_error` nodes, never silent drops. Vendored subtrees (`quartz/`, `node_modules`, minified) flagged `third_party: true` and excluded from metrics/views. Output is the §4 determinism contract (sorted JSONL, canonical form, no wall‑clock, version stamps) — reproducible byte‑for‑byte, which is what G11 verifies.
3. **Sections**: model‑written analytical prose over the graph + repo, under the **G6‑bundle citation regime** (§6.3): factual blocks cite `src·path#L·span_sha256` (verified) or `graph·node-id`; judgments are explicit `*Assessment:*` blocks inheriting cited evidence. All `sources[].commit_sha` must equal `knowledge-source.json` (mixed‑version bundles rejected).
4. **Operating model**: fabricated teams, labeled `x_kf.synthetic: true`, registered in `config.yml`: `kfcor`: fabric-core, librarian-ops, graph-platform · `kfsit`: site-build, explorer-ux · `folio`: web-experience, content-ops · `aacod`: model-authoring, policy-governance, mcp-integrations · `cfskl`: skill-authoring, adr-practice.
5. **Control files** per §4; **validate** via `kf_lint` (same library the gate runs — no validator/gate drift) + the citation verifier; must pass before landing.

**Depth tiers (concrete)**: tier 1 `kfcor`,`aacod` — all 7 sections; tier 2 `kfsit`,`folio` — executive‑summary, application, technology, operating‑model full; business/data present but short; tier 3 `cfskl` — adapted (skills architecture over skill folders/prompts/tests). Every tier carries complete provenance.

## 6. Gate design (spec deltas D17–D19)

### 6.1 PR classes (fail closed)

| Class | Trigger | Write‑set (one appid) | Key gates |
|---|---|---|---|
| **ceremony** | `knowledge-sources/agile-ceremonies/**` or `grill/` branch | ceremony file + ceremony‑team log + manifest (single‑entry byte‑splice) | spec v0.4 G1–G10 unchanged (+ D17 prefix) |
| **bundle‑update** | `sections/**`, `code-graph/**`, `domains-maps/**`, control files; branch `bundle/<appid>/<sha12>` | those paths only; `knowledge-sources/**` untouched; manifest per‑entry splice/replace, ceremony entries byte‑identical; root log insert‑only; `index.md` regeneration allowed here only | G2/G3 (incl. `x_kf.bundle_kind`), **G6‑bundle** (§6.3), **G11** (§6.4), G9, approver ∈ **owners(appid)**, content‑bound |
| **revert** | verified semantic inverse of one merged squash + `Reverted` block | per spec §8.5; `x_kf.bootstrap: true` files excluded as targets | original approver or fallback team |
| **other** | explicit allowlist only: `README.md`, `PRODUCTION.md`, `docs/**` | — | protected‑content rule |
| **unknown** | anything else — incl. `gate/**`, `tools/**`, `skills/**`, `.github/**`, future bundle kinds | **fails closed** (`class=unknown`); those paths change only via code‑owner‑reviewed tooling PRs (CODEOWNERS + push ruleset in prod) | — |

### 6.2 Wrong‑appid protection (D19 — the "100 apps" answer, completed)

Registry allowlist (unregistered appid → G3 fail) **plus**: **team→appid hard binding** (a team not registered under that appid fails G3 — tightens the spec's soft new‑slug warn; recorded as a spec delta), **approver ∈ owners(appid)** for bundle‑updates (a wrong‑folder PR needs the *wrong app's* owner — the person most likely to notice; D10 preserved: approver still declared in frontmatter, gate only validates), registry entries carry the immutable repo id (rename‑proof), edit‑distance soft warn on similar appids, post‑merge repair = revert class + rerun (README runbook).

### 6.3 G6‑bundle — citation regime for sections (confirmed rule text)

A *claim block* is a paragraph, list item, or table row (headings, code fences, Mermaid, frontmatter excluded). Every claim block is **factual** or an **assessment**: (1) factual blocks carry ≥1 footnote `src·<path>#L<a>-L<b>·span_sha256` verified at the pinned SHA, or `graph·<node-id>` resolving in the code graph; (2) assessment blocks start exactly with `*Assessment:*`, carry no new `src`/`graph` footnote, and cite ≥1 footnote id already used by a factual block earlier in the same section; (3) each section has ≥1 factual block and ≤50% assessment blocks; (4) whether inherited evidence *supports* an assessment is the tool‑less LLM pass's advisory check — everything else is hard. Span hash = sha256 of the cited lines, LF‑terminated, no further normalization. The `*Assessment:*` marker ships in the section templates and the skill's authoring guide.

### 6.4 G11 — graph reproducibility (confirmed mechanics)

Bundle‑update PRs only. Order: (i) `code-graph` version stamps must equal the **base‑ref** `toolchain.lock` (a PR bumping its own lockfile + graph in one step fails; toolchain bumps are separate code‑owner‑reviewed tooling PRs); (ii) one shallow **data‑only** fetch of the source repo at the pinned SHA — no install, no build, no hooks (I6 intact); citations (G6‑bundle) verify against this same checkout, no per‑citation API calls; (iii) extractor re‑run → byte equality with the PR's graph — a derived artifact is verified by reproduction, so no human reviews a 5 MB JSONL; (iv) fetch failure concludes `failure` with a retry note — never a pass.

### 6.5 Demo‑grade vs production

Built now (not deferred): all four workflows; `pull_request_target` executing base‑ref code with head files as API data; the required check created via the **Checks API** under a distinct name (so `action_required` → approval → `success` actually works); local mode. Deferred to `PRODUCTION.md`: KF Gate App identity + pinning, `main`‑only environment, `.github/workflows/**` push ruleset, no‑bypass — with the **forgery scenario documented as a known‑fail in demo mode**. Option open to Muthu: register the App now (~30 min) and remove the caveat from every screenshot (§13‑4).

## 7. Seeding & demo flow

**A — Recommended (gated bootstrap):** direct push only of the chicken‑and‑egg set (`.github/`, `gate/`, `kf_lint/`, `tools/`, `skills/`, `docs/`, registry, empty `application-bundles/`); then branch protection on; then the **five bundles land as five bundle‑update PRs** (exercising D18 for real) and seeded standups (one per **every** team) as ceremony PRs approved by the second identity. Every accepted file has an approval trail; scenario 18 reverts a demo‑merged PR.

**B — Fallback (Muthu's original "bootstrap direct" choice, if he prefers it):** bundles + seeds in the bootstrap commit, with `gate/run.py --base <empty-tree>` verdicts committed to `docs/bootstrap-verdicts/` and `x_kf.bootstrap: true` on every seeded file (excluded from revert targets, labeled never‑approved). Scenario 18 then reverts something merged during the demo.

**Either way** (reviewer's dependency note): demonstrating named‑approver enforcement and a real merge needs the **two extra GitHub identities** (§13‑3); without them those scenarios run as local‑mode fixtures only.

## 8. Scenario gallery — derived, not hand‑listed

`scenarios/matrix.yml` keys every scenario to the spec §13/§14 criterion it proves; the README matrix and the CI fixture run are generated from it. Live PRs (~15): green ceremony happy‑path · rerun‑updates‑same‑PR · established‑teams multiteam same‑day (zero refresh — all teams pre‑seeded) · new‑team first‑entry conflict → `--refresh` → approval survives · retro with ACT/RSK · green bundle‑update · valid revert (of a demo‑merged PR) · reds: second appid · second team · out‑of‑allowlist · wrong‑appid coherence · unregistered appid · span‑hash broken · approver=author · PII email · manifest re‑serialization · fake first‑run team log · bundle‑update touching `knowledge-sources/` · invalid revert. Local fixtures cover the rest of spec §14 (UTC+14 edge, reserved slug, 4‑segment branch, profile violation `RSK-` in standup, clobber abort, symlink, rename, root‑log touched, soft‑warn set, zero‑findings, `--refresh` ≥24 h after approval, approval‑by‑non‑approver stays `action_required`) **plus the confirm‑round fixtures**: all‑Assessment section (50% cap fires), head‑lockfile bump (base‑ref comparison holds), mixed commit SHAs, non‑reproducible graph, `config.yml` edit → class=unknown, `other`‑class PR deleting a ceremony file.

## 9. Skill: `building-application-bundles`

Canonical code lives in `skills/building-application-bundles/scripts/` (versioned `process:building-application-bundles@x.y.z`); `tools/bundle_builder` imports it — both copies identical by construction, so the account‑skill upload is standalone. SKILL.md per best practices: gerund name; third‑person description (<1024 chars) with triggers ("application bundle", "knowledge bundle", "onboard an app into KF", "code graph"); **Requirements** block (Python version, pinned wheels, network needed for clone) + degraded inventory‑only mode when grammars are unavailable; checklist workflow; validation loop = `kf_lint` **+ the G6‑bundle citation verifier**; references one level deep with ToCs; `*Assessment:*` marker taught in the authoring guide. **Evals (written before the docs, with a no‑skill baseline)**: (1) pinned Python repo+SHA → graph node/edge counts in band + validator passes; (2) pinned low‑code repo → non‑trivial inventory graph; (3) negative — a section claim citing a nonexistent line must fail validation and lead to a repair. Tested across model tiers.

## 10. Execution phases — vertical slice first

| Phase | Work | Output |
|---|---|---|
| P0 | Attach repos; pin SHAs; **provision identities** (approver account + non‑approver writer, §13‑3); confirm org plan supports required checks/rulesets | access + accounts |
| P1 | `kf_lint` + extractor + validator; **kfcor graph only** | toolchain proven |
| P2 | **Vertical slice**: kfcor sections → gate classes → kfcor bundle‑update PR → one ceremony PR end‑to‑end (approve, merge, revert) | spec loop proven on one app |
| P3 | Widen: remaining four bundles (tiers), all teams seeded | `application-bundles/` complete |
| P4 | Full gallery: live PRs + CI fixtures from `matrix.yml` | demo ready |
| P5 | Skill finalization + account‑skill proposal | reusable regeneration |
| P6 | README, `PRODUCTION.md`, plan in `docs/plan/`, acceptance pass | shareable repo |

## 11. Acceptance criteria

1. Five bundles pass `kf_lint` + citation verification; every section cites repo+SHA+graph; mixed‑SHA bundle rejected (fixture).
2. Graphs reproduce byte‑for‑byte under G11; views render on GitHub (aggregated); `cfskl` yields a non‑trivial inventory graph; vendored code excluded from `kfsit` metrics.
3. Every `matrix.yml` scenario produces its expected verdict in CI **and** local mode; the README matrix is generated, so it matches by construction.
4. Named‑approver enforcement shown live: non‑approver approval leaves `action_required`; the named approver's approval flips `success`; merge; revert of that merge passes the revert class.
5. Established‑teams multiteam scenario: zero refresh, zero re‑approvals; new‑team scenario: exactly one `--refresh`, approval survives.
6. Unknown‑class fail‑closed shown: a PR editing `gate/config.yml`→ red (`class=unknown`).
7. Skill evals pass incl. the negative case; dry‑run against a sixth pinned repo produces a valid bundle skeleton.

## 12. Risks & open items

- **Manifest schema**: spec §5.4 shape until the real KF schema arrives; one mapping pass later (README‑flagged).
- **Section quality**: model‑written; G6‑bundle verifies evidence structurally, the LLM pass checks entailment advisorily, humans approve — same stance as the spec; truth beyond citations is the approver's judgment.
- **Grammar drift**: pinned in `toolchain.lock`; bumps are code‑owner tooling PRs (G11 enforces).
- **Demo‑mode forgery**: known‑fail, documented; closed by `PRODUCTION.md` steps (or now, per §13‑4).
- **kfsit vendored Quartz**: third‑party flagging keeps graph/sections focused; verified in acceptance #2.

## 13. Decisions needed from Muthu (at plan review)

1. **Repo name**: GitHub repo is currently `muthub-ai/kbundels`; intended `kbundles`. Rename in GitHub Settings (redirects are automatic) — or keep the current spelling and I update this plan.
2. **App ids** (§3 table) — confirm or override the five.
3. **Demo identities**: provide/approve a second GitHub account (named approver) and a third (non‑approver writer / clobber author) as collaborators with write access — required to demo approver enforcement, merge, and revert live; otherwise those become local fixtures only.
4. **Gate App now vs later**: ~30 min of org setup removes the forgery caveat from the demo; otherwise it ships as a documented known‑fail.
5. **Bootstrap path**: recommended gated bootstrap (§7A) vs your original direct bootstrap (§7B fallback).

## Appendix A — Review & confirmation record

Independent reviewer: Claude Opus 5.5 (same reviewer as spec v0.1→v0.4). Round 1: 18 findings (P1 CRITICAL trust‑root unprotected / fail‑open `other` class; P2–P4, P6, P7, P9, P10, P13, P14 HIGH; P5, P8, P11, P12, P15–P17 MEDIUM/LOW; P18 GOOD list) — all adopted. Confirm round: **C1** (factual vs. Assessment blocks) accepted with reviewer's tightened rule (block definition incl. list items/table rows, no-new-footnote rule, ≥1 factual block, ≤50% assessments, advisory entailment); **C2** (G11 mechanics) accepted with base‑ref `toolchain.lock` comparison and single data‑only fetch serving both citation checks and the extractor re‑run; **C3** (bootstrap recommendation vs. owner's original choice) agreed as presented in §7/§13‑5, with the identities dependency stated. Reviewer verdict: **CONFIRMED** at v0.2.

---

## As-built deviations (2026-10-20)

Recorded after implementation. The plan text above is unchanged; these notes record where the build departed from it, and why.

- **Shared library location.** The canonical library is `skills/building-application-bundles/scripts/kfbundle/`, which the gate imports. There is no top-level `kf_lint/`. This keeps the skill self-contained for reuse in other repositories, and leaves one copy of the lint rules.
- **Added a `tooling` PR class.** Changes under `.github/`, `gate/`, `tools/`, `skills/` and `scenarios/` are their own class, and a code owner must approve them. Mixing tooling changes with knowledge changes is still `unknown` and fails closed.
- **Gate layout.** The engine and plumbing live in `gate/kfgate/`, with one module per gate in `gate/gates/`. The entry point is `gate/run.py`, which has a local mode and a GitHub mode.
- **Live PRs are red paths only.** The repository has one real identity. Green, approval, merge, refresh and revert paths are therefore proven in the fixture matrix (`scenarios/run_fixtures.py`, 40 scenarios) with fixture identities. The ten live PRs (`scenarios/open_live_prs.py`) each also show G7.
- **No KF Gate App.** The check run is posted by the GitHub Actions app. The App, the rulesets and the forgery fix are specified in `PRODUCTION.md`.
- **Bootstrap re-verification.** `tools/bootstrap.py --reverify` re-judges every bootstrap commit using the current gate code. All 17 steps are `bootstrap-ok`.

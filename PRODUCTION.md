# PRODUCTION.md — from demo-grade to production-grade

This prototype runs the gate's real plumbing (four workflows,
`pull_request_target` executing base-ref code with the PR head read as data,
a Checks-API check run whose `action_required → success` transition encodes
the named-approver rule). What it deliberately does **not** have is the
identity and repository settings that make the gate unforgeable. This file is
the contract for closing that gap (spec v0.4 §8.3, plan §6.5).

## Known failure in demo mode

**Check forgery.** The required check `kf-knowledge-gate` is posted by the
GitHub Actions app using the workflow's `GITHUB_TOKEN`. Any writer can push a
side branch with an `on: push` workflow that posts a *same-name* `success`
check onto a PR's head SHA, and among same-source checks the latest wins. The
fix is an App identity that side-branch workflows cannot mint (steps 1–3).

## Steps

1. **Register the KF Gate App** (org settings → Developer settings → GitHub Apps):
   permissions `contents: read`, `pull requests: read & write`, `checks: read & write`,
   `issues: read & write`; no webhook; install it on `kbundles` only.
2. **Create a `kf-gate-main` environment** (repo settings → Environments) with a
   deployment-branch policy of `main` only, and store the App's private key as the
   environment secret `KF_GATE_APP_KEY` and its id as the variable `KF_GATE_APP_ID`.
3. **Mint the App token in the gate jobs.** In `kf-gate.yml` and `kf-gate-rerun.yml`, add
   `environment: kf-gate-main` to the job and, before "Run gate":
   ```yaml
   - uses: actions/create-github-app-token@<pinned sha>
     id: app
     with: {app-id: ${{ vars.KF_GATE_APP_ID }}, private-key: ${{ secrets.KF_GATE_APP_KEY }}}
   ```
   then pass `GITHUB_TOKEN: ${{ steps.app.outputs.token }}` to the gate. Side-branch and
   merge-ref workflows cannot enter the environment, so they cannot post as the App.
4. **Branch ruleset on `main`:** require status check `kf-knowledge-gate` **from the KF Gate
   App** (expected source), require 1 approving review, squash merge only, block force pushes
   and deletions, and **no bypass actors** (administrators included).
5. **Push ruleset on all refs:** block changes to `.github/workflows/**`; require code-owner
   review on `.github/**` via `.github/CODEOWNERS` (already present).
6. **Default `GITHUB_TOKEN` read-only** (repo settings → Actions → Workflow permissions).
7. **Real identities.** Give named approvers write access; set `owners` per appid in
   `.github/kf/config.yml`; set `revert_fallback_approvers` to a team. With a second identity
   the green scenarios also run as live PRs.
8. **Make `kf-fixtures` a required check** for tooling PRs so a gate change that breaks a
   scenario cannot merge.
9. **Verify registry repo ids** against the API once (`gh api repos/<owner>/<repo> --jq .id`):
   the prototype's ids were read from the repositories' public pages.
10. **Merge queue (optional, plan O8):** the workflow already declares `merge_group`; enable it
    only after evaluating G3 against the PR head ref instead of the queue ref.

## Already production-shaped

- Fail-closed class dispatch (`unknown` fails; trust root changes need a code owner).
- Head content is never checked out or executed by privileged jobs; the source repo for G11 is
  fetched data-only (no install, build or hooks).
- Content-bound approval (refresh-safe, stale on any content change); bootstrap content can never
  be a revert target.
- Deterministic, pinned toolchain (`.github/kf/toolchain.lock`), compared against the base ref.

---
name: building-application-bundles
description: Builds or regenerates a Knowledge Foundation application bundle for a source repository — an OKF v0.2 knowledge bundle with a tree-sitter code graph, architecture sections (executive summary, business, application, data, technology, security, operating model) whose every factual claim cites hash-verified source lines, domain maps and control files — and validates it with the same rules the kf-knowledge-gate enforces. Use when onboarding an app into KF, creating or refreshing an application bundle or knowledge bundle, generating a code graph for a repo, or preparing a bundle-update PR for the kbundles repository.
---

# Building application bundles

An application bundle is one app's governed knowledge under
`application-bundles/<appid>/`. Deterministic parts (code graph, metrics,
views, manifest, index) come from scripts; analytical sections are written by
you and must pass the citation regime. The gate re-runs the same library, so
a bundle that validates here passes there.

## Requirements

- Python 3.11+ with PyYAML and the pinned tree-sitter toolchain:
  `pip install -r .github/kf/toolchain.lock` (in the kbundles repo).
- Network access to clone the source repository.
- Grammars unavailable? `build_bundle.py graph --inventory-only` produces a
  degraded inventory-only graph; say so in the executive summary.

Scripts live in this skill's `scripts/` (run them; do not re-implement them).
Run every command from the kbundles repo root with
`S=skills/building-application-bundles`.

## Workflow

Copy this checklist and tick it off:

```
Bundle progress:
- [ ] 1. Pick the appid and register it
- [ ] 2. Pin the source commit (init)
- [ ] 3. Build the code graph
- [ ] 4. Write the sections and domain maps
- [ ] 5. Fill citation hashes
- [ ] 6. Build control files
- [ ] 7. Validate until PASS
- [ ] 8. Open the bundle-update PR
```

**1. Appid.** Exactly 5 lowercase letters derived from the repo name, not
reserved, not within edit distance 2 of an existing appid. Add it to
`.github/kf/config.yml` (title, repo, numeric repo id, teams with time zones) in a
separate tooling PR — the trust root is code-owner reviewed. Who may approve the
app's knowledge lives in `application-bundles/<appid>/OWNERS`, claimed with an
owners PR (branch `owners/<appid>`); until then the KF stewards approve.

**2. Pin.** Clone the source repo and check out the commit to document, then:

```bash
python3 $S/scripts/build_bundle.py init --bundle application-bundles/<appid> --appid <appid> \
  --title "<App title>" --repo <owner/repo> --repo-id <id> --source <clone> \
  --approver @<owner-handle> [--third-party 'glob' ...] [--generated 'glob' ...]
```

Flag vendored code with `--third-party` and build output with `--generated`
so they do not dominate metrics.

**3. Graph.**

```bash
python3 $S/scripts/build_bundle.py graph --bundle application-bundles/<appid> --source <clone>
```

Read `code-graph/metrics.json` and `code-graph/views/*.md` before writing:
they show entry points, hotspots and module structure. Schema:
[reference/code-graph-schema.md](reference/code-graph-schema.md).

**4. Sections.** Write `sections/*.md` and 1–2 `domains-maps/*.md` following
[reference/section-authoring-guide.md](reference/section-authoring-guide.md) —
read it fully first. The rules that fail most often:

- Every paragraph, list item and table row is a claim: cite it with
  `src · path#La-Lb` or `graph · <node-id>`, or start it with `*Assessment:*`.
- An assessment may only reuse footnotes from earlier factual blocks; at most
  half the blocks in a file may be assessments.
- `operating-model.md` is fabricated in prototypes: `x_kf.synthetic: true`,
  "illustrative" in the description, exactly the registered team slugs.

**5. Hashes.**

```bash
python3 $S/scripts/fill_citations.py --bundle application-bundles/<appid> --source <clone>
```

**6. Controls.**

```bash
python3 $S/scripts/build_bundle.py controls --bundle application-bundles/<appid> \
  [--log-summary "Application bundle created" --log-bullet "..."]   # log flags only when adding a log block
```

This re-stamps the source pin and graph hash into every section, rebuilds the
manifest (byte-stable; ceremony entries untouched) and the index. Control
files: [reference/okf-control-files.md](reference/okf-control-files.md).

**7. Validate — the loop.**

```bash
python3 $S/scripts/validate_bundle.py --bundle application-bundles/<appid> --source <clone> \
  --registry .github/kf/config.yml --reproduce
```

Fix every error, re-run steps 5–7, and only continue when it prints `PASS`.
`--reproduce` re-runs the extractor and byte-compares graph, metrics and
views; if it fails, re-run step 3 rather than editing derived files.

**8. PR.** Branch `bundle/<appid>/<first 12 chars of commit_sha>`, commit
with the trailer `KF-Bundle-Builder: building-application-bundles@0.1.0`, one
appid per PR, nothing under `knowledge-sources/`. The approver in
`knowledge-source.json` must be listed in the app's `OWNERS` (or be a KF steward
while it has none) and not be the author. Title:
`[KF-BUNDLE] <appid> @ <first 12 of commit_sha> — <summary>`.

## Regenerating an existing bundle

Same workflow from step 2 with the new commit: `init` again (keeps the
appid), re-run `graph`, then re-read every section — any cited line that
changed now fails its hash, which is exactly where the prose must be
re-checked. Update the text, then steps 5–8 with a `--log-summary` block.

## Do not

- Do not edit `code-graph/` files, the manifest or `index.md` by hand.
- Do not cite whole files to dodge precise evidence (ranges over 80 lines warn).
- Do not put emails, phone numbers or personal names in any file.
- Do not call the output a "deepwiki" — it is an application bundle.

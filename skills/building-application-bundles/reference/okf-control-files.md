# OKF control files of an application bundle

| File | Owner | Rule |
|---|---|---|
| `index.md` | `build_bundle.py controls` | OKF reserved. Frontmatter is only `okf_version: "0.2"` (bundle root). Links to sections and **directories only** — never to individual ceremony files — so it never goes stale. Regenerated only by bundle-update PRs. |
| `log.md` | `controls --log-summary` | OKF reserved, newest-first, headings `## YYYY-MM-DD: Summary` using the run date. **Insert-only**: each bundle update adds exactly one block; nothing is ever edited or removed. Ceremony PRs never touch it. |
| `bundle-manifest.json` | `controls` (bundle files), grill client (ceremony files) | Fixed header line, one canonical one-line JSON entry per file sorted by `path` in UTF-8 byte order, fixed footer. Edits are line splices, never re-serialization. Ceremony entries (`knowledge-sources/…`) are byte-identical in bundle-update PRs. Bundle entries carry `sha256` of the file. |
| `knowledge-source.json` | `build_bundle.py init` | `schema`, `appid`, `bundle_kind`, `title`, `source` (`repo`, numeric `repo_id`, `url`, `commit_sha`), `builder`, `generated_at`, `graph_options`, `review.approver` (must be an owner of the appid), `bootstrap`. |
| `knowledge-sources/agile-ceremonies/<ceremony>/<team>/log.md` | grill client | Ceremony-team log: created as an optional title line plus exactly one block; afterwards one block per run at its date-ordered position. |

## Frontmatter of knowledge files

Every `sections/*.md` and `domains-maps/*.md` carries OKF v0.2 frontmatter:
`type` (`application-bundle/<section>` or `application-bundle/domain-map`),
`title`, `description`, `generated` (`by: process:…`, `at:` ISO-8601 with
offset), `sources` (exactly one `source-repo` with `repo` + `commit_sha`, one
`code-graph` with `path` + `sha256`; synthetic files use one
`synthetic-fixture`) and `x_kf` (`schema: kf-application-bundle/1`, `appid`,
`bundle_kind: application`, `section` or `domain`, optional `synthetic`,
`bootstrap`). `verified` is always absent: acceptance is presence on `main`
after the named owner's approval.

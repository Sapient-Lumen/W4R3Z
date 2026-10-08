# CHANGELOG — rev0288

Created: 2026-05-26T03:15:00-04:00

## Theme

Local assurance overlay, dimension/tag alias refactor, data-quality observability, actor/tag primary-key repair, service-floor control-plane coverage repair, and refreshed SQLite/query validation.

## Added cube artifacts

- `cube/actor-alias.csv`
- `cube/tag-alias.csv`
- `cube/file-tag-edge-normalized.csv`
- `cube/dimension-taxonomy.csv`
- `cube/dimension-member-audit.csv`
- `cube/pilot-jurisdiction-fixture.csv`
- `cube/localization-overlay-map.csv`
- `cube/local-assurance-evidence.csv`
- `cube/local-owner-assignment.csv`
- `cube/local-control-test.csv`
- `cube/local-access-test.csv`
- `cube/local-audit-redress.csv`
- `cube/local-contracting-process.csv`
- `cube/local-corrective-action.csv`
- `cube/local-workforce-role.csv`
- `cube/local-observation.csv`
- `cube/local-assurance-gate-evaluation.csv`
- `cube/maturity-cap-execution.csv`
- `cube/service-floor-local-assurance-scorecard.csv`
- `cube/local-evidence-gap-backlog.csv`
- `cube/table-schema-catalog.csv`
- `cube/table-column-catalog.csv`
- `cube/data-quality-rule-catalog.csv`
- `cube/data-quality-result-rev0288.csv`
- `cube/data-quality-issue-ledger.csv`
- `cube/query-views-rev0288.sql`
- `cube/datacube-rev0288.sqlite`
- `cube/validation-report-rev0288.csv`
- `cube/validation-report-rev0288.json`
- `cube/structural-audit-rev0288.md`

## Changed

- Repaired duplicate primary keys in `actor.csv` and `tag.csv`; raw spelling/case variants now live in alias tables.
- Added normalized tag edges so each raw `file-tag-edge.csv` value resolves to a canonical `tag_id`.
- Filled missing template control-plane rows for `border_continuity`, `cross_service_readiness`, `rebuild_authority`, and `water_continuity`.
- Recomputed global service-floor gate evaluations, maturity evaluations, assurance scorecards, and gate coverage summaries.
- Added a synthetic local pilot fixture to exercise jurisdiction-scoped maturity caps without changing global template maturity.
- Added data-quality rule catalogs, results, issue ledger, schema catalogs, refreshed referential-integrity checks, and a current SQLite mirror.
- Removed stale SQLite binaries from earlier revisions so the package contains one current query mirror.

## Not changed

- No new numbered canon files were added; the numbered archive remains `00`–`428`.
- `cube/index.csv` remains the wide compatibility view with 120 schema fields.
- Synthetic local fixture rows are not real-world implementation evidence.

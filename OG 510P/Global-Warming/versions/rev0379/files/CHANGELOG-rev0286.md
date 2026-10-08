# CHANGELOG — rev0286

Created: 2026-05-26T01:35:00-04:00

## Theme

Audit/refactor pass for typed routes, referential integrity, service-floor assurance scorecards, evidence-gap backlog, resource manifesting, publication controls, and a SQLite query mirror.

## Added cube artifacts

- `cube/route-relation-taxonomy.csv`
- `cube/field-normalization-audit.csv`
- `cube/service-floor-assurance-scorecard.csv`
- `cube/evidence-gap-backlog.csv`
- `cube/semantic-refactor-map.csv`
- `cube/referential-integrity-report.csv`
- `cube/resource-manifest.csv`
- `cube/sqlite-resource-map.csv`
- `cube/query-views-rev0286.sql`
- `cube/datacube-rev0286.sqlite`
- `cube/validation-report-rev0286.csv`
- `cube/validation-report-rev0286.json`
- `cube/structural-audit-rev0286.md`

## Changed

- Repaired owner-plane referential drift by adding synthetic service-floor rows for `border_continuity, cross_service_readiness, rebuild_authority, water_continuity` and adding missing owner actors referenced by `cube/owner-assignment.csv`.
- Promoted inferred route relation types into `cube/route-edge-table.csv` and `cube/route-graph.csv`; the compact route tables no longer collapse every relationship to `routes_to`.
- Expanded `cube/publication-control.csv` to resource-level publication classifications and redaction rules for cube artifacts.
- Updated `cube/schema.json` and `cube/validation-rules.json` to `rev0286`.
- Added validation around owner-assignment foreign keys, typed route taxonomy coverage, service-floor scorecard coverage, evidence-gap backlog creation, resource manifests, publication controls, and the SQLite mirror.

## Validation target

- continuous numbered files `00`–`428`;
- schema/index alignment;
- all cube CSVs parse;
- owner-accountability foreign keys resolve;
- all referential-integrity and primary-key checks pass;
- typed route tables use the inferred relation taxonomy;
- service-floor scorecard covers every service floor;
- evidence-gap backlog is generated for high-stakes template-only gates;
- publication control covers cube resources;
- SQLite mirror builds and passes integrity check;
- resource manifest exists with row/column/hash metadata.

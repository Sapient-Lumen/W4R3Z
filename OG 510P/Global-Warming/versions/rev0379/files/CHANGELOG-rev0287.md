# CHANGELOG — rev0287

Created: 2026-05-26T02:25:00-04:00

## Theme

Assurance-gate engine, owner-role template refactor, evidence-role semantic split, route self-reference audit, and refreshed SQLite/query validation.

## Added cube artifacts

- `cube/assurance-gate.csv`
- `cube/service-floor-gate-evaluation.csv`
- `cube/service-floor-maturity-evaluation.csv`
- `cube/assurance-gate-coverage-summary.csv`
- `cube/owner-role-taxonomy.csv`
- `cube/route-edge-audit.csv`
- `cube/route-graph-audit.csv`
- `cube/route-node-metrics.csv`
- `cube/route-component.csv`
- `cube/evidence-class-taxonomy.csv`
- `cube/claim-effect-role-taxonomy.csv`
- `cube/evidence-semantic-audit.csv`
- `cube/query-views-rev0287.sql`
- `cube/datacube-rev0287.sqlite`
- `cube/validation-report-rev0287.csv`
- `cube/validation-report-rev0287.json`
- `cube/structural-audit-rev0287.md`

## Changed

- Reclassified explicit route self-loops as `self_reference`, so traversal can distinguish note-to-self/index anchors from cross-file dependencies.
- Expanded `cube/owner-assignment.csv` from sparse owner examples into a standard owner-role template plane covering every service floor.
- Added `cube/owner-role-taxonomy.csv` with eight standard roles: executive, operational, data, civil-rights, procurement, audit/redress, corrective-action, and workforce competency owners.
- Added an assurance-gate engine that evaluates every service floor against active gates and computes an explainable maturity ceiling.
- Updated `cube/service-floor-assurance-scorecard.csv` so its maturity ceiling and owner counts are synchronized with the rev0287 gate engine.
- Split legacy evidence semantics by adding `evidence_class` and `claim_effect_role` to `cube/evidence-item.csv`, and `claim_effect_role` plus `requirement_link_status` to `cube/claim-evidence-edge.csv`.
- Expanded controlled vocabulary, publication controls, referential-integrity checks, validation rules, query catalog entries, and the SQLite mirror.

## Validation target

- numbered files remain continuous `00`–`428`;
- index/schema alignment is preserved;
- all cube CSVs parse;
- route relation taxonomy covers all typed route edges, including `self_reference`;
- standard owner-role templates cover every service floor;
- gate evaluations cover every service floor and active assurance gate;
- maturity evaluations cover every service floor and synchronize with the scorecard;
- evidence-class and claim-effect taxonomies cover observed values;
- referential integrity passes across the expanded control plane;
- rev0287 SQLite views execute.

# Structural audit — rev0286

Created: 2026-05-26T01:35:00-04:00

## Purpose

Rev0286 turns the rev0285 assurance control plane into a more queryable and auditable cube. It does not add new numbered doctrine files. Instead, it repairs a referential-integrity gap, promotes typed route relations into the compact route tables, and adds service-floor assurance scorecards, evidence gap backlogs, resource manifests, and a SQLite query mirror.

## Changes audited

- Repaired the owner-accountability plane by adding missing synthetic service floors referenced by `cube/owner-assignment.csv`: border_continuity, cross_service_readiness, rebuild_authority, water_continuity.
- Added missing owner actors referenced by `cube/owner-assignment.csv` so owner assignments now resolve to `cube/actor.csv`.
- Promoted inferred route semantics from `cube/route-edge.csv` into `cube/route-edge-table.csv` and `cube/route-graph.csv`; `routes_to` is now only one relation among a typed relation set.
- Added `cube/route-relation-taxonomy.csv` so route relation types are defined and countable.
- Added `cube/field-normalization-audit.csv` to classify all wide-index fields and identify their canonical normalized storage.
- Added `cube/service-floor-assurance-scorecard.csv` to summarize, per service floor, claims, evidence, controls, tests, access gates, owners, audit/redress, contracting, workforce, materiality, gaps, and maturity ceilings.
- Added `cube/evidence-gap-backlog.csv` to turn template-only high-stakes gates into actionable closure tasks.
- Added `cube/semantic-refactor-map.csv` to make the cube's entity boundaries explicit.
- Added `cube/referential-integrity-report.csv` and expanded validation rules for foreign-key and primary-key checks across the control plane.
- Expanded `cube/publication-control.csv` from a short policy stub into resource-level publication classifications for cube resources.
- Added `cube/datacube-rev0286.sqlite`, `cube/sqlite-resource-map.csv`, and `cube/query-views-rev0286.sql` as a queryable mirror of the CSV cube.
- Added `cube/resource-manifest.csv` with bytes, hashes, row/column counts, publication class, and generated-revision metadata.

## Validation summary

- Rules passed: 16/16.
- Numbered files: 429 (`00` through `428`).
- Index rows: 429.
- Schema fields: 120.
- Service floors: 418.
- Synthetic service floors added to repair owner-plane references: 4.
- Actor rows: 445.
- Owner actor rows added: 20.
- Route edges: 3557.
- Route relation types: 16.
- Service-floor scorecard rows: 418.
- Evidence-gap backlog rows: 2354.
- Referential-integrity/PK checks: 53.
- Publication-control rows: 351.
- Resource-manifest rows: 783.
- SQLite-imported cube tables: 89.

## Failed or watch-list rules

- None. All rev0286 validation rules passed.

## Remaining limitations

The new scorecard and backlog intentionally expose that most high-stakes service floors remain template-level rather than locally implemented. Rev0286 should therefore be read as a stronger **audit/refactor layer**, not as proof that all service floors are mature. The next logical revision would populate a small pilot jurisdiction with real owner, control-test, access-test, contracting, corrective-action, and redress evidence and then verify whether the maturity caps behave correctly.

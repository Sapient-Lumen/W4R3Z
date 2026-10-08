# Structural audit — rev0287

Created: 2026-05-26T02:25:00-04:00

## Purpose

Rev0287 turns the assurance layer from a scorecard/backlog summary into an explicit gate-evaluation engine. It also audits/refactors the route graph and evidence semantics so downstream users can see why a service floor is capped, why a route edge is traversable or not, and whether an evidence row is a source class or a claim-effect statement.

## Changes audited

- Reclassified 35 explicit self-loop route edges as `self_reference`.
- Added route graph audit artifacts: `route-edge-audit.csv`, `route-graph-audit.csv`, `route-node-metrics.csv`, and `route-component.csv`.
- Added an owner-role taxonomy with 8 standard roles and expanded `owner-assignment.csv` to 3368 rows so every service floor has a template owner plane.
- Added 13 active assurance gates and 5434 service-floor gate evaluations.
- Added 418 service-floor maturity evaluations and synchronized scorecard maturity ceilings to the gate engine.
- Split legacy evidence semantics across `evidence_class` and `claim_effect_role`; 10698 evidence rows and 2661 claim-evidence edges were updated with explicit semantic columns.
- Added query views and rebuilt the SQLite mirror as `cube/datacube-rev0287.sqlite`.
- Expanded referential-integrity, validation, publication-control, query-catalog, controlled-vocabulary, and control-plane-register coverage.

## Validation summary

- Rules passed: 24/24.
- Numbered files: 429 (`00` through `428`).
- Index rows: 429.
- Schema fields: 120.
- Service floors: 418.
- High-stakes service floors: 393.
- Owner assignments: 3368.
- Assurance gates: 13.
- Gate evaluations: 5434.
- Maturity evaluations: 418.
- Route edges: 3557.
- Route self references: 35.
- Route-edge audit rows: 5905.
- Referential-integrity/PK checks: 71.
- Referential-integrity failures: 0.
- SQLite-imported cube tables: 104.
- SQLite views: 7.

## Gate status distribution

- `fail`: 198
- `not_applicable`: 8
- `pass`: 2906
- `template_only`: 2222

## Maturity ceiling distribution

- `R0_unclaimed`: 4
- `R2_documented_template_only`: 414

## Route relation distribution after self-reference refactor

- `routes_to`: 2935
- `tests_access_to`: 156
- `contracts_for`: 118
- `routes_user_to`: 88
- `evidence_for`: 83
- `validates_or_challenges`: 48
- `self_reference`: 35
- `depends_on`: 30
- `governed_by_internal_control`: 11
- `requires_assurance_case`: 11
- `normalizes_cube`: 9
- `scores_or_caps`: 8
- `feeds_corrective_action`: 7
- `audited_or_challengeable_by`: 6
- `requires_civil_rights_access_test`: 6
- `requires_open_contracting_trace`: 3
- `requires_workforce_competency_depth`: 3


## Watch list

- Most high-stakes service floors remain capped by template-only gates. This is expected: rev0287 adds the explanatory gate engine, not local implementation evidence.
- `routes_to` remains the largest route relation class. The new route-edge audit table treats those generic edges as a refactor backlog rather than a validation failure.
- Many evidence rows still have `claim_effect_role = unknown` because bibliographic/source evidence is not automatically a support/refute/qualify statement. This prevents citation count from being mistaken for assurance proof.

# rev0328 QRF cross-route handoff and route-pressure mirror audit

## Risk repaired

The critical defect was not another missing registry row. It was a cross-route handoff and route-head visibility problem.

First, `EU-0010-QRF-FRAME-TRANSPORT` could see `ED-0020-FAMILYC-SUBREGION-STATE-PORTABILITY-PRESSURE`, even though that empirical-delta row is FamilyC-route-local. The reciprocal handoff looked tidy, but the route sets did not overlap. That lets FamilyC subregion-state pressure leak into QRF evidence-unit context.

Second, route-facing forecasts, empirical deltas, and decision experiments were distributed across three ledgers without being visible on the route-state rows themselves. A route editor could therefore read the route head and miss live pressure, or delete a pressure row without noticing the route consequence.

## Repair

rev0328 adds two executable repairs:

- `tools/evidence_delta_handoff_policy.py` now requires evidence/delta handoffs to share route scope.
- `tools/route_pressure_mirror_policy.py` requires each `CANDIDATE-ROUTE-STATE-LEDGER.json` route row to mirror its route-facing `forecast_ids`, `empirical_delta_ids`, and `decision_experiment_ids` exactly.

`ED-0020-FAMILYC-SUBREGION-STATE-PORTABILITY-PRESSURE` is now FamilyC-only. `ED-0023-QRF-FRAME-TRANSPORT-LARGE-GAUGE-PRESSURE` is the route-local QRF pressure row.

## QRF source-role boundary

The QRF lane remains `S2`. Large-gauge, boundary/corner, crossed-product, frame-transport, and observer-dependent entropy sources are current pressure for witness portability. They are not acquired evidence-unit support and do not turn frame-relativity into candidate identity.

The resulting public-witness burden is sharper: a future positive record must name source/target frames, operational equivalence relation, relational-observable quotient, edge/corner sector, large-gauge handling, algebraic type or crossed-product convention, observer/clock convention, same-record rule, and nonportable or nonlocalizable failure cases.

## Non-promotion rule

The mirrors and QRF pressure rows improve control-plane integrity. They do not promote any route, and they do not let pressure rows be spent as independent evidence.

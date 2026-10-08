# Meta 0467 — Closure gates, receipt floors, and route-demotion pilot

This maintenance note records the rev0787 cloudtainer pass.

## Changes

- Added note `985` for closure-gated affected-person evidence receipts and no closure by receipt row.
- Extended `metadata/evidence_receipts.json` with proof floors, denominator gaps, closure blockers, and `can_close_gap` controls.
- Added UI and housing closure receipts that keep `GAP-029` and `GAP-031` live until field/person outcome evidence exists.
- Demoted note `465` from active route status to `historical_preserved` while preserving the file, manifest entry, index entry, and rollback condition.
- Added lint checks for evidence-receipt closure inflation and historical-preserved route hygiene.

## Guardrail

This revision does not declare the affected-person, source-preservation, or route-retirement gaps repaired. It makes premature closure harder.

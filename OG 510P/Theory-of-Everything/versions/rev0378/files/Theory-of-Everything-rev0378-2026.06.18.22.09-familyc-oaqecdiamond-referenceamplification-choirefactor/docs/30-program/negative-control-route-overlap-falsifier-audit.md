# Negative-control route-overlap falsifier audit (rev0339)

## Risk target

The cube had strong source-role and route-pressure controls, but falsifiers were still easier to misuse than positive evidence. A decision, severity row, evidence unit, defeater, or contrast class could name a negative-control handle whose owning `route_id` belonged to a different route. That lets a falsifier from one lane silently shape another lane without an explicit handoff boundary.

## Repairs

- Added `tools/negative_control_route_overlap_policy.py`.
- Added generated audit `docs/30-program/negative-control-route-overlap-audit.generated.md`.
- Added `NC-FAMILYC-ISLAND-DECODER-DECOY` for finite-N / island / black-hole-interior decoder decoys.
- Added `NC-LEARNED-INVERSE-CODE-SPACE-OVERFIT` so learned-inverse OOD failure no longer borrows the stronger FamilyC EW-code falsifier.
- Route-state rows now mirror route-local `negative_control_ids` derived from `NEGATIVE-CONTROL-LEDGER.json`.
- Cross-route negative-control placements in learned-inverse, finite-N/island, and classical-GR decision rows were replaced with route-local falsifiers.

## Non-promotion rule

Negative controls are falsifiers and denominator tests. Passing them can preserve a bounded route state; failing them caps, rolls back, or quarantines the affected route-local claim path. They do not add positive support and cannot promote a route.

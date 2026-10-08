# Rematch worlds should govern exact uncertainty weakening as a two-axis factor ledger

## Claim
The current exact-uncertainty weakening menu can be governed more cleanly as a two-axis factor ledger than as five separate live exceptions. Every released case is a coefficient vector over just two primitives: middle-band precision relief and relaxed-suffix release.

## Current factor signatures
- suffix-only releases: budget steps `1`, `3`, and `4` all have signature `(precision=0, suffix=1)`
- precision-only release: budget step `2` has signature `(precision=1, suffix=0)`
- composite release: budget step `5` has signature `(precision=1, suffix=1)`

So the cumulative budget path is exactly:

- budget `0`: `(0,0)`
- budget `1`: `(0,1)`
- budget `2`: `(1,1)`
- budget `3`: `(1,2)`
- budget `4`: `(1,3)`
- budget `5`: `(2,4)`

## Why this matters
- It compresses the weakening menu to a tiny audited basis.
- It makes the menu's asymmetry explicit: after budget `2`, governance can buy more relaxed-suffix coverage at budgets `3` and `4`, but cannot buy a second precision-origin release until budget `5`.
- It exposes a new impossibility family: there is no current setting that adds more precision-origin relaxation without also adding more relaxed-floor suffix exposure.

## Operational rule
When future inheritors evaluate a threshold change, they should first ask which factor signature is being added. Any redesign that introduces a pure second precision step, removes the composite nature of step `5`, or changes one of the three current signatures is a substantive change to the weakening algebra.

## Pointers
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_incidence_ledger_snapshot_20260308.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_incidence_ledger.py`

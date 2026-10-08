# Rematch worlds should route floor-driven exact uncertainty retuning through a four-point boundary compass

## Claim
For the **current saved exact uncertainty menu**, floor-driven retuning should start from four boundary compass points:
`{2, 8, 18, 19}`.

## Why this matters
The archive already knows two directional facts:
- stronger floors repair through boundary targets `{18, 2}`,
- weaker floors widen through boundary targets `{8, 19}`.

Putting those together yields a more mechanical first-step rule:
- `2` is the singleton precision landing point,
- `8` is the entry boundary into the strong non-fragile band,
- `18` is the exit boundary from the relaxed suffix into the strongest surviving non-precision support,
- `19` is the entry boundary into the relaxed suffix.

That means the first step of floor-driven retuning no longer needs to search all `26` live dwell points in `{2} ∪ [8,32]`.
It can start from **four exact landmarks** instead.

## Implementor rule
- Use `{18, 2}` when the required exact floor gets stricter.
- Use `{8, 19}` when the required exact floor gets weaker.
- Treat interior dwells only as second-step refinements after the relevant compass target has been evaluated.
- If a request is constrained by fixed dwell, width, or other non-floor requirements, run the oracle after the compass step instead of forcing this shortcut too far.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_retuning_compass_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_retuning_compass_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_floor_retuning_compass.py`

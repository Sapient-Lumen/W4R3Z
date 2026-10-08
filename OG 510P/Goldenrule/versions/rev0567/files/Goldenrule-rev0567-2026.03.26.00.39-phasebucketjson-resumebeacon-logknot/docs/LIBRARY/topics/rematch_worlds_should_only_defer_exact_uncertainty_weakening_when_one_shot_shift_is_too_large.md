# Rematch worlds should only defer exact uncertainty weakening when one-shot shift is too large

## Claim
Once the archive can already classify exact-uncertainty requests and route from all saved states `{2, 8, 13, 18, 19, 25}`, the only movement that should ever be optional is **weakening**; strengthenings stay mandatory, while weakenings can be deferred only when their one-shot dwell shift exceeds an explicit operator threshold.

## Why
- a cheapest-tier weakening is exactly the case where the current stronger tier still satisfies the request, so deferral does not break the declared floor,
- strengthenings are different: they arise only when the current tier is too weak, so delay would knowingly violate the request,
- boundary states `8` and `18` are not steady-ready, so deferred weakening from those states should stabilize back to canonical anchor `13` rather than leave the system parked on a transient boundary.

## Current archive consequence
- the base saved-state resolver has exactly `5` weakening cases in its default `18`-case matrix,
- their exact one-shot weakening shifts are `{7, 11, 12, 17, 23}` unique appends,
- a threshold below `7` defers all weakenings and turns the matrix into `6` holds, `5` stabilizations, `0` weakenings, and `7` strengthenings,
- a threshold of `23` recovers the base cheapest-feasible policy exactly.

## Operational rule
1. run the saved-state resolver first,
2. if the selected action is strengthen or infeasible, do not override it,
3. if the selected action is weaken and its one-shot shift exceeds the declared threshold, defer the weakening,
4. when deferring from canonical anchors, hold the current stronger tier,
5. when deferring from transient boundaries `8` or `18`, stabilize to canonical anchor `13` before waiting.

## Pointers
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_snapshot_20260308.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis.py`

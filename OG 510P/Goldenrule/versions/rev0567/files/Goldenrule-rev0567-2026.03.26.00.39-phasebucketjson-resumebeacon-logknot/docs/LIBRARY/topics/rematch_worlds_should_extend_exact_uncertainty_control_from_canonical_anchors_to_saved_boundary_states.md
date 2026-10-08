# Rematch worlds should extend exact uncertainty control from canonical anchors to saved boundary states

## Claim
When the archive already saves transient feasibility boundaries `{8, 18, 19}` alongside canonical anchors `{2, 13, 25}`, inheritors should resolve requests directly from the full saved-state menu instead of manually composing a boundary repair card and then a separate anchor controller.

## Why
- boundary states are operationally real after floor changes, so excluding them from the controller forces the inheritor to do avoidable glue work at exactly the moment when the system is already off-anchor,
- the saved-state menu remains tiny, so extending the controller from `3` anchors to `6` saved states adds useful directness without reopening full dwell search,
- same-band boundary cases are qualitatively different from both hold and retune: they are cheap stabilization moves with zero cap/checkpoint delta and a bounded extra shift tax.

## Current archive consequence
- the default floor-only saved-state matrix has `18` ordered cases and decomposes into exactly `3` holds, `3` stabilizations, `5` weakenings, and `7` strengthenings,
- the only non-steady saved states are `8`, `18`, and `19`, and their maximum stabilization-only tax is `6` unique appends,
- direct saved-state resolution preserves the request-oracle blockers, so infeasible high-floor positive-slack bundles still fail fast instead of being masked by route logic.

## Operational rule
1. classify the request bundle with the exact uncertainty oracle,
2. choose the cheapest feasible exact tier,
3. resolve directly from the current saved state `{2, 8, 13, 18, 19, 25}` to that tier's canonical anchor,
4. call the move **stabilize** when the selected tier matches the current band but the current state is a transient boundary.

## Pointers
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_saved_state_resolver_snapshot_20260308.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_saved_state_resolver.py`

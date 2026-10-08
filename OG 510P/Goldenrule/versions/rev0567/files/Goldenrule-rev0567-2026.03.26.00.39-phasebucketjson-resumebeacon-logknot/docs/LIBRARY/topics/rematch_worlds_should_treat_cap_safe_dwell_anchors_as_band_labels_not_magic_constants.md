# Rematch worlds should treat cap-safe dwell anchors as band labels, not magic constants

## Claim
When the archive talks about the current near-optimal cap-safe compact repeat-sidecar preset, it should preserve the real invariant as a dwell **band** rather than fetishizing one dwell integer. On the saved frontier, dwell `13` is the representative label for the cap-safe near-optimal lane, but the real focal five-transition plateau is dwell `8`–`18`, and the true structural boundaries are the adjacent cliff rows at dwell `7` and dwell `19`.

## Why
- The focal `0.18` minimum-dwell frontier already shows that dwell `8`–`18` is one plateau: same `5` transitions, same interval summary, same preserved gain share `0.980481`, same regret `217.295277`.
- The current uncertainty-default dwell `9` lies inside that same cap-safe band, so the archive is not switching to a different focal plan when it talks about dwell `13`; it is relabeling the same interior lane for cap-safe use.
- The structural changes happen at the neighbors instead: dwell `7` jumps back to `9` transitions, while dwell `19` drops to `3` transitions but leaves the near-optimal lane and falls to gain share `0.870482`.

## Implementor consequence
- Encode the near-optimal cap-safe preset as “band `8`–`18`, representative label `13`” in notes and control logic.
- Treat dwell `9` and dwell `13` as focal-plan-equivalent on the saved frontier.
- Fail fast when edits cross below `8` or above `18` without an explicit lane change, because those are the boundaries that actually alter the promise.

## Provenance
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_cap_safe_anchor_fungibility_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_cap_safe_anchor_fungibility_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_cap_safe_anchor_fungibility.py`

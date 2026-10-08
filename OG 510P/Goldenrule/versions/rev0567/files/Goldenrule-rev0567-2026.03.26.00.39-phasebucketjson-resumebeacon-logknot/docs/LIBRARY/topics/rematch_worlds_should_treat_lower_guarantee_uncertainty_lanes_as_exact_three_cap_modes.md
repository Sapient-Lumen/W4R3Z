# Rematch worlds should treat lower-guarantee uncertainty lanes as exact three-cap modes

## Claim
Once the archive explicitly relaxes the current repeat-uncertainty guarantee to gain share `0.85`, the lower-guarantee compact repeat-sidecar lane should no longer be described as a conservative four-transition planning hint. On the saved frontier for repeat budgets `0.15`, `0.18`, and `0.25`, dwell `19`–`32` is an **exact** hard-`3` lane, with representative anchor dwell `25`.

## Why
- The old guardrail note already isolated dwell `19`–`32` as the right lower-guarantee band, but it left the cap as a planning inference.
- Recomputing the lane directly from the saved frontier closes that gap: every dwell in `19`–`32` preserves at least `0.85` of full dynamic savings across the current repeat reference band while never exceeding `3` transitions.
- Cap `2` is impossible at this guarantee on the current frontier. The focal `0.18` planner only reaches cap `2` at dwell `49`, where preserved gain share has already fallen to `0.510201`.
- Cap `4` buys nothing extra for this lane: its feasible dwell band is identical to the exact cap-`3` band.

## Implementor consequence
- Promote the lower-guarantee lane to: “dwell band `19`–`32`, representative anchor `25`, exact hard cap `3`.”
- Do not keep repeating the stale “conservative hard cap `4`” phrasing in inheritor notes.
- If a future session wants fewer than `3` transitions under repeat uncertainty, it must either relax the guarantee below `0.85` or reopen the repeat band itself.

## Provenance
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_lower_guarantee_three_cap_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_lower_guarantee_three_cap_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_lower_guarantee_three_cap.py`

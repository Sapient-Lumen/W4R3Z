# Rematch worlds should fail fast on exact uncertainty requests that the current menu cannot satisfy

## Claim
The current exact compact repeat-sidecar uncertainty menu now has enough exact structure that future inheritors should treat several request bundles as **immediate no-go screens**, not as retuning invitations.

In particular, the archive can now reject these cases without reopening the frontier:
- hard-cap budget below `3`,
- pre-amortization checkpoint budget below `5`,
- required worst-case preserved-gain floor above `0.999822`,
- minimum anchor slack at least `7`,
- minimum dwell-band width at least `15`,
- any requirement above floor `0.980481` that also demands positive slack or band width above `1`,
- any requested exact dwell inside the internal gap `3–7`,
- and any requested exact dwell below `2` or above `32`.

## Why this matters
The archive already had all of these boundaries, but they were scattered across tier selectors, topology notes, and the near-exact escalation gate.
That made the research program good at saying which tier to choose **when a tier exists**, but weaker at saying when the request bundle itself is impossible under the saved exact menu.

This matters because impossible bundles waste time in exactly the wrong places:
- people keep trying to compress hard cap below `3` without acknowledging that even the relaxed exact `0.85` lane already needs cap `3`,
- people ask for “near-exact but still forgiving” even though the current `0.99` tier is a single-point zero-slack mode,
- and people are tempted to sweep dwell `3–7` even though the exact menu really does skip that region.

The archive can now say something sharper:
- the relaxed exact `0.85` lane is the boundary witness that keeps the menu alive at minimum cap, minimum checkpoints, maximum slack, and maximum width,
- the exact `0.95` lane is the largest live **non-fragile** guarantee,
- and the exact `0.99` tier is only the ceiling witness for absolute floor, not a generic rescue tier when other constraints break.

So this note turns the current exact menu into a real fail-fast screen rather than just a selection table.

## Implementor rule
- Reject the request immediately if hard cap is below `3`.
- Reject the request immediately if pre-amortization checkpoint budget is below `5`.
- Reject the request immediately if the required certified floor is above `0.999822`.
- Reject the request immediately if minimum slack is `7+` or minimum band width is `15+`.
- If the required floor is above `0.980481`, only keep the request alive when zero slack, band width `1`, hard cap `11`, and dwell `2` are all acceptable.
- Skip dwell `3–7` entirely when searching inside the current exact menu.
- Treat dwell below `2` or above `32` as outside the current exact uncertainty-certified menu unless new frontier evidence is generated.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_infeasibility_screen_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_infeasibility_screen_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_infeasibility_screen.py`

# Rematch worlds should repair impossible exact uncertainty requests by the smallest current-menu relaxation

## Claim
The current exact compact repeat-sidecar uncertainty menu is now structured enough that impossible request bundles should usually be repaired by the **smallest exact relaxation**, not by reopening the frontier search immediately.

The repair rules are now explicit:
- hard-cap budget `2` repairs to the relaxed exact lane by raising cap to `3`,
- pre-amortization checkpoint budget `4` repairs locally by raising budget to `5`, or globally by pre-registering the master calendar,
- minimum slack `7` repairs to `6`,
- minimum band width `15` repairs to `14`,
- high-floor requests above `0.980481` with positive slack or width above `1` have two distinct repairs: clip the floor back to `0.980481` to keep a non-fragile band, or collapse the fragility budget to zero slack / width `1` and accept the exact `0.99` precision point,
- dwell inside the dead zone `3–7` repairs by jumping directly to dwell `8` for non-fragile operation or dwell `2` for precision,
- dwell below `2` clamps upward to `2` (or `8` if fragility is unacceptable),
- dwell above `32` clamps downward to `32`,
- and required floors above `0.999822` have no menu-internal structural repair except weakening the requirement itself.

## Why this matters
The fail-fast screen added the previous step is useful, but it still leaves the implementor with a second question: **what is the cheapest exact move that gets me back into the live menu?**

That question matters because many of the current no-go bundles are only one notch away from feasibility.
The relaxed exact `0.85` lane is the boundary witness for minimum cap, minimum checkpoints, maximum slack, and maximum width, so several impossible bundles repair with a single integer step.

The more subtle cases are the high-floor conflicts.
Above floor `0.980481`, the archive no longer has a forgiving exact band.
So the repair choice becomes structural:
- either keep the request non-fragile and clip the floor back into the exact `0.95` lane,
- or keep the stronger floor and accept the zero-slack, width-`1` exact `0.99` precision point.

That distinction is valuable because it prevents a common category error: people ask for “still forgiving, but stricter than `0.95`,” when the current exact menu simply does not contain such a tier.

## Implementor rule
- After a fail-fast result, try the smallest single-constraint repair before doing any heavy recomputation.
- Use one-step cap/checkpoint/slack/width repairs first.
- Use direct dwell jumps to the live support `{2} ∪ [8, 32]` instead of searching inside the dead region `3–7`.
- Treat floor overflow above `0.999822` as a true frontier limit: either weaken the requirement or generate new frontier evidence.
- Treat high-floor conflicts above `0.980481` as a fork between the non-fragile exact `0.95` band and the fragile exact `0.99` precision point.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_repair_guide_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_repair_guide_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_repair_guide.py`

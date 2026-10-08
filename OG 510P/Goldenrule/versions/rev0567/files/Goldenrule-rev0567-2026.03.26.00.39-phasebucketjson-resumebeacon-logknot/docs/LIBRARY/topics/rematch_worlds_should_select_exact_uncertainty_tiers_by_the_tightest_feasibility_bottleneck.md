# Rematch worlds should select exact uncertainty tiers by the tightest feasibility bottleneck

## Claim
Future inheritors should treat the saved exact compact repeat-sidecar uncertainty tiers as a **feasibility selector**. The right question is not “which tier sounds nicest,” but “what is the strongest exact tier that still survives the tightest real operating bottleneck?”

## Why this matters
The archive already had:
- an exact cap staircase,
- an exact checkpoint staircase,
- an exact tariff card,
- and an exact dwell-tolerance staircase.

What it still lacked was the small selector that turns those facts into a direct operating choice.

The saved exact tiers now imply exact cut points:
- hard-cap budget below `3` leaves **no** current exact uncertainty tier,
- hard-cap budget `3`–`4` forces the relaxed exact `0.85` tier,
- hard-cap budget `5`–`10` allows the near-optimal exact `0.95` tier,
- hard-cap budget `11+` is needed before near-exact `0.99` becomes feasible.

The same structure appears in maintenance burden:
- checkpoint budget below `5` leaves no current exact tier,
- checkpoint budget `5`–`7` forces `0.85`,
- checkpoint budget `8`–`13` allows `0.95`,
- checkpoint budget `14+` is needed before `0.99` becomes feasible.

And the tolerance card adds the critical selector warning:
- **any positive minimum anchor-slack requirement already rules out `0.99`**,
- minimum slack requirement `1`–`5` still allows `0.95`,
- minimum slack requirement `6` forces `0.85`,
- minimum slack requirement `7+` leaves no current exact tier.

So the archive can now state the operational rule cleanly: choose by the **tightest bottleneck**.

## Implementor rule
- If your bottleneck is hard-cap budget, use the exact `11 / 5 / 3 / none` selector.
- If your bottleneck is checkpoint calendar size, use the exact `14 / 8 / 5 / none` selector.
- If your bottleneck is tuning forgiveness, remember that any nonzero minimum slack requirement immediately demotes the choice from `0.99` to at most `0.95`.
- When multiple constraints apply, pick the strongest tier that survives **all** of them simultaneously.
- Treat exact `0.95` as the strongest current **non-fragile** selector outcome: it survives positive slack, moderate hard-cap budgets, and moderate checkpoint budgets.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_constraint_selector_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_constraint_selector_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_constraint_selector.py`

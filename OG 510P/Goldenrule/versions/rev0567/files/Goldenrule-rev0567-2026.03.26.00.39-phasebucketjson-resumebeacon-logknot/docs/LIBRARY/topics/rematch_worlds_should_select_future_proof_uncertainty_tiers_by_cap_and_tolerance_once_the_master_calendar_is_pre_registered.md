# Rematch worlds should select future-proof uncertainty tiers by cap and tolerance once the master calendar is pre-registered

## Claim
Once the compact repeat-sidecar program has already pre-registered the full `17`-point master audit calendar, future inheritors should stop treating per-tier checkpoint counts as an active selector for the current exact uncertainty-safe modes.

From that point onward, the exact tier choice collapses to the remaining live bottlenecks:
- hard-cap budget,
- minimum anchor slack,
- and minimum tolerated dwell-band width.

## Why this matters
The archive already knew two facts separately:
- the exact uncertainty selector mapped cap, checkpoint, and tolerance requirements to the strongest feasible tier,
- and the master-calendar amortization card showed that once the sparse `17`-point schedule is pre-registered, every current mode switch becomes calendar-free.

What was missing was the operational consequence of combining those facts.

The new post-amortization selector makes that consequence explicit:
- after the master calendar is sunk cost, checkpoint counts `14`, `8`, and `5` no longer choose among the current exact tiers,
- exact `0.99` stays available only for precision deployments with hard cap `11`, zero minimum slack, and band width requirement `1`,
- exact `0.95` becomes the strongest **future-proof non-fragile** tier because it survives hard-cap budgets `5`–`11`, positive minimum slack up to `5`, and band-width requirements up to `11`,
- exact `0.85` is the remaining future-proof fallback when cap is only `3`–`4` or when tolerance requirements rise to slack `6` / band width `12`–`14`,
- and no current exact tier survives once minimum slack reaches `7` or minimum band width reaches `15`.

So the archive now has a clean implementation rule for programs that expect policy churn and have already paid the calendar cost once.

## Implementor rule
- If the full master calendar has **not** been pre-registered, checkpoint burden is still a live selector and the older constraint selector remains the right tool.
- If the full master calendar **has** been pre-registered, ignore per-tier checkpoint counts for the current exact uncertainty-safe modes and choose only by cap and tolerance.
- Treat exact `0.95` as the strongest current future-proof default whenever any positive slack or any band width above `1` is required.
- Reserve exact `0.99` for true precision deployments.
- Use exact `0.85` only when cap is tight or the deployment insists on more tuning slack than the `0.95` lane can certify.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_post_amortization_selector_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_post_amortization_selector_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_post_amortization_selector.py`

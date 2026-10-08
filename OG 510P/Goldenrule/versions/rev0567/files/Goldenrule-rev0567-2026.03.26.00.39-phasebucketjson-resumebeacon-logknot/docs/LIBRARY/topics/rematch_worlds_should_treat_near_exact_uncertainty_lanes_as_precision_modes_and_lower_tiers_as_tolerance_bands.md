# Rematch worlds should treat near-exact uncertainty lanes as precision modes and lower tiers as tolerance bands

## Claim
Future inheritors should treat the exact compact repeat-sidecar uncertainty tiers not only as cap and checkpoint tradeoffs, but also as a **dwell-tolerance staircase**.

## Why this matters
The archive already knew the exact uncertainty tiers, their rewrite caps, and their checkpoint unions. The missing implementor fact was how much **tuning slack** each tier leaves once a dwell anchor is chosen.

The saved exact tiers now make that explicit:
- near-exact `0.99` is a **single-point precision mode** at dwell `2`, with no left slack, no right slack, and no retuning error budget,
- near-optimal `0.95` is a true tolerance band on dwell `8`–`18`, with anchor `13` and `5` dwell steps of slack on each side,
- relaxed `0.85` is the widest certified band on dwell `19`–`32`, with anchor `25`, `6` dwell steps of left slack, and `7` of right slack.

So tightening from `0.95` to `0.99` is not merely a higher-cap or larger-checkpoint move. It is also a **tolerance collapse**: the certified dwell width falls from `11` to `1`, and minimum anchor slack falls from `5` to `0`.

## Implementor rule
- Use the exact `0.95` lane when the archive wants strong uncertainty safety without fragile retuning.
- Use the exact `0.85` lane when a weaker guarantee is acceptable and extra dwell forgiveness is operationally valuable.
- Reserve the exact `0.99` lane for deliberate precision deployments only, because any dwell drift leaves the certified band immediately.
- When someone proposes “just tightening the guarantee a little,” remember that the `0.95 -> 0.99` step also deletes essentially all dwell slack.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_tolerance_staircase_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_tolerance_staircase_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_dwell_tolerance_staircase.py`

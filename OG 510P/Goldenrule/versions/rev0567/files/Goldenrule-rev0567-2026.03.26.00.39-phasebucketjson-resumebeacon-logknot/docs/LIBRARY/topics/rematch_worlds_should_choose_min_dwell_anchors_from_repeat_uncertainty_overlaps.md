# Rematch worlds should choose minimum-dwell anchors from repeat-uncertainty overlaps

## Claim
When compact repeat-sidecar repeat volume is only known approximately, the archive should choose the midpoint of the minimum-dwell overlap that remains admissible across the whole repeat-budget band rather than anchoring on a plateau computed at one guessed repeat rate.

## Why this matters
Single-budget dwell anchors can look robust while still collapsing if the real repeat volume drifts. The overlap rule keeps one preset safe across every repeat budget in the uncertainty band, so the inheritor can carry a small preset table instead of retuning dwell thresholds every time repeat forecasts move.

## Current measured result
On the current compact repeat-state horizon:
- over repeat budgets `0.15`–`0.25`, the `0.99`-safe overlap shrinks to dwell `1`–`2`, so near-exact tuning is fragile,
- the robust near-optimal preset is dwell `9`, which keeps at least `0.980481` of full dynamic savings while staying within `2`–`5` transitions across the band,
- the broader simplicity-first preset is dwell `16`, which keeps the same worst-case `0.980481` share while allowing the low-repeat edge to collapse all the way to zero transitions.

## Implementor rule
- estimate a plausible repeat-budget band instead of one scalar,
- compute the minimum-dwell overlap that survives the whole band at the gain share you care about,
- anchor at the midpoint of that overlap,
- and only use single-budget dwell plateaus when repeat uncertainty is genuinely negligible.

## Pointers
- `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot_20260307.md`

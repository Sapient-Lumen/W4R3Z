# Rematch worlds should treat equal-value exact uncertainty weakening releases as cheapest-shift-first

## Claim
Once the archive already exposes weakening budgets as one-at-a-time live action flips, future inheritors should group those releases by recovered steady-state savings vector and treat repeated vectors as cheapest-shift-first coverage extensions rather than as increasingly valuable policy steps.

## Why
- the current five-step weakening budget ladder collapses to exactly `3` recovered savings bundles,
- one bundle repeats across budget steps `1`, `3`, and `4`, always recovering the same relaxed-suffix steady-state gains `{cap:2, checkpoints:3, slack:1, width:3}` while the one-shot route shift rises `7 < 12 < 17`,
- so later steps in that repeated class do not buy a richer steady state; they extend the same value to harder-to-move live states,
- and the breakpoint order is therefore an efficiency order within that value class, not just arbitrary threshold numerology.

## Current archive consequence
- budget step `1` releases the cheapest relaxed-suffix case first (`18 @ 0.84`),
- budget step `3` releases the same savings bundle for the neutral anchor (`13 @ 0.84`),
- budget step `4` releases that same bundle again for the remaining harder entry boundary (`8 @ 0.84`),
- while budget steps `2` and `5` are unique because they recover genuinely different precision-origin savings bundles.

## Operational rule
1. price each budget increment by both its released live case and its recovered steady-state savings vector,
2. when two increments recover the same savings vector, interpret the later one as extra state coverage with a larger one-shot move cost,
3. reserve unique value-class steps for genuinely new savings bundles,
4. treat any future policy change that alters a release-step savings vector or breaks cheapest-shift-first ordering inside a repeated class as a substantive redesign.

## Pointers
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_release_value_classes_snapshot_20260308.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_release_value_classes.py`

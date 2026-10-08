# Rematch worlds should ship compact repeat-sidecar operating modes

## Claim
The archive should ship one small compact repeat-sidecar operating ladder instead of forcing each future inheritor to reopen every staging, transition-budget, minimum-dwell, and repeat-uncertainty frontier before they can choose a deployment mode.

## Why this matters
The compact repeat-state line has already produced multiple exact frontiers, but the inheritor usually needs a decision rule, not another frontier walk. A small operating ladder keeps the archive compact and actionable:

- exact dynamic staging remains available when rewrites are cheap and repeat volume is trusted,
- a four-transition staged plan captures most of the measured value when rewrite count is the real bottleneck,
- dwell `9` is the current uncertainty-robust default across repeat budgets `0.15`–`0.25`,
- dwell `16` is the broader simplicity-first uncertainty preset,
- and fixed route blocks become the right freeze policy once rewrite cost or repeat volume makes transitions not worth replaying.

## Current measured result
On the current frontier:
- the full exact dynamic plan still uses `12` transitions at the focal `0.18` repeat horizon,
- the practical rewrite-budget ceiling is `4` transitions, which preserves `0.968419` of full dynamic savings,
- the uncertainty-robust default is dwell `9`, which keeps at least `0.980481` of full dynamic savings across repeat budgets `0.15`–`0.25` while staying within `2`–`5` transitions,
- the broader uncertainty-safe simplicity preset is dwell `16`, which keeps the same worst-case `0.980481` share while allowing the low-repeat edge to collapse to `0` transitions,
- and fixed route blocks become the right freeze policy once rewrite cost clears `927.685921` bytes per transition or expected repeats reach `0.7`.

## Implementor rule
- Default to dwell `9` when repeat volume is uncertain.
- Use the `4`-transition staged planner when rewrite count is explicitly budgeted.
- Use dwell `16` when simplicity matters more than a few extra transitions.
- Freeze on route blocks once rewrite cost or repeat volume makes transitions not worth it.
- Reserve the full `12`-transition dynamic schedule for sessions that truly care about the last slice of byte savings.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_operating_modes_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_operating_modes_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_operating_modes.py`

# Rematch worlds should ship compact repeat-sidecar control cards

## Claim
The archive should hand future inheritors a tiny precedence-ordered compact repeat-sidecar control card, not just a menu of frontier reports, so they can choose a deployment mode from a few observable thresholds.

## Why this matters
The operating ladder already says which modes exist, but the inheritor still needs to know which constraint wins when several are present at once. A small control card keeps the archive compact and gives the implementor a clear precedence order:

- freeze first when rewrites are no longer worth it,
- honor an explicit rewrite-count cap before arguing about finer dwell tuning,
- use dwell `9` as the uncertainty-safe default when repeat volume is only approximately known,
- price churn explicitly when rewrite cost is known but not yet high enough to force a full freeze,
- and only replay the full exact planner when the earlier constraints do not bind and the last slice of byte savings still matters.

## Current measured result
On the current compact repeat-sidecar frontier:
- fixed route blocks are the right freeze policy once rewrite cost reaches `927.685921` bytes per transition or expected repeats reach `0.7`,
- the practical rewrite-budget ceiling remains `4` transitions and preserves `0.968419` of full dynamic savings,
- dwell `9` remains the uncertainty-safe default across repeat budgets `0.15`–`0.25`, keeping at least `0.980481` of full dynamic savings while staying within `2`–`5` transitions,
- micro-churn should already be suppressed once rewrite cost reaches `45.40069` bytes per transition,
- and the full exact planner should be treated as the last-resort high-touch mode because it still requires `12` transitions on the focal horizon.

## Implementor rule
Choose the first matching rule in this order:
1. freeze on route blocks if rewrites do not pay,
2. otherwise honor any explicit rewrite-count cap,
3. otherwise default to dwell `9` when repeat volume is uncertain,
4. otherwise price switch churn directly when rewrite cost is known,
5. otherwise replay the exact staged planner only if the archive truly wants the final slice of savings.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_control_card_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_control_card_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_control_card.py`

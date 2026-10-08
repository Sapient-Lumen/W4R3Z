# Rematch worlds should compare sidecar churn against fixed-policy regret

## Claim

When compact repeat sidecars sit near repeat-budget and bitmap-cliff frontiers, the archive should measure the regret of a single fixed sidecar over the next novel-append horizon before replaying every upgrade and downgrade interval.

## Why

The fully staged compact-repeat plan is only strictly better if sidecar transitions are cheap enough.
A fixed sidecar can lose a few measured objective bytes while avoiding many regime changes.
That makes churn a first-class archive cost rather than an invisible implementation detail.

## Current local evidence

- On the current deterministic `274`-fingerprint frontier, the exact dynamic planner at `0.18` expected repeats uses `12` sidecar transitions across the next `256` novel appends.
- Over that same horizon, the best fixed policy is `paged_catalog_with_route_blocks`.
- Its regret versus the fully dynamic schedule is `11132.231038` objective bytes, only `0.002305` of the dynamic cumulative objective.
- That means the dynamic schedule buys only `927.68592` bytes per transition on average before a fixed policy becomes cheaper overall.
- By `0.7` expected repeats, always-on route blocks already match the dynamic schedule exactly across the whole measured horizon.

## Implementor guidance

- Treat compact repeat-sidecar churn as a budgeted choice, not a free optimization.
- Before replaying every exact staging interval, compare the expected per-switch rewrite or coordination cost against the measured fixed-policy regret.
- When switch cost clears the break-even per-transition threshold, keep the best fixed sidecar for the whole horizon.
- Recompute the threshold whenever page size, fingerprint population, expected repeat volume, or horizon length changes materially.

## Pointers

- `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_fixed_policy_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_fixed_policy_snapshot_20260307.json`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_fixed_policy_snapshot_20260307.md`

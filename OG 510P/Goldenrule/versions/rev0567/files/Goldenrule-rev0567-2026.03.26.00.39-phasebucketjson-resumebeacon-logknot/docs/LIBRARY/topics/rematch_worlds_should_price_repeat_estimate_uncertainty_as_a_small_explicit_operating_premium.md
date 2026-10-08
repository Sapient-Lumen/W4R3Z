# Rematch worlds should price repeat-estimate uncertainty as a small explicit operating premium

## Claim
Future inheritors should treat **repeat-estimate uncertainty** as a priced operating premium over the trusted-repeat rewrite-budgeted plan, not as a vague reason to overbuild the sidecar schedule.

## Why this matters
The archive already had both sides of the comparison, but not in one place:
- the trusted-repeat fallback preserves `0.968419` of full dynamic savings at the focal `0.18` repeat point with `4` rewrites and checkpoints `56, 111, 159, 239`,
- the exact uncertainty-safe tiers preserve different guarantees across the full `0.15`–`0.25` band.

The new exact comparison makes the premium concrete:
- the exact `0.95` lane buys repeat-band robustness for only `+1` hard-cap step and net `+4` checkpoints, while also improving focal `0.18` preservation by `0.012062`,
- the exact `0.85` lane is **not** a monotone uncertainty tax at all: it is cheaper than the trusted-repeat fallback on transition cap (`3` instead of `4`) and only `+1` checkpoint wider, but it gives back `0.097937` focal gain share,
- the exact `0.99` lane is the expensive precision upgrade: `+7` cap steps and net `+10` checkpoints over the trusted-repeat fallback.

So the implementor should stop thinking “uncertainty-safe” means “dramatically more expensive.” The real current premium is small at the `0.95` tier and only becomes structurally large at the near-exact `0.99` tier.

## Implementor rule
- When repeat estimates are truly trusted and rewrites are capped at `4`, keep the trusted-repeat rewrite-budgeted plan.
- When repeat estimates are not trusted across the current `0.15`–`0.25` band, treat the exact `0.95` lane as the default uncertainty upgrade because its premium is only `+1` cap step and net `+4` checkpoints.
- Drop to the exact `0.85` lane only when the archive intentionally wants the cheaper uncertainty-safe cap and accepts the focal-performance loss.
- Upgrade to exact `0.99` only for precision-preservation goals.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_premium_vs_trusted_repeat_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_premium_vs_trusted_repeat_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_premium_vs_trusted_repeat.py`

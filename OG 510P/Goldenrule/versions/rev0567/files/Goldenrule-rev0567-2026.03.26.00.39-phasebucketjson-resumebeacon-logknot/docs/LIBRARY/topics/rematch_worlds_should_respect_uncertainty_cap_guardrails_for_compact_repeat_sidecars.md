# Rematch worlds should respect uncertainty-cap guardrails for compact repeat sidecars

## Claim
The archive should stop treating the current uncertainty-robust compact repeat-sidecar preset and the current four-transition rewrite-budget preset as if they were one merged operating promise.

## Why this matters
The recent operating ladder already says two true things at once:
- the trusted-repeat rewrite-budget lane has a practical ceiling of `4` transitions,
- and the uncertainty-robust default is dwell `9`, whose measured transition range is `2`–`5` across repeat budgets `0.15`–`0.25`.

That means the archive has crossed an important implementation boundary. A future inheritor can no longer casually say “use the uncertainty-safe preset and keep rewrites capped at four” without silently breaking one of the guarantees.

## Current measured guardrail
From the saved frontiers:
- the `0.95` uncertainty-safe dwell overlap is `1`–`18`,
- but on the focal `0.18` repeat frontier those dwells still break into `12`, `11`, `9`, and then `5` transitions,
- so the first cap-safe near-optimal sub-band is only `8`–`18`,
- and the certified hard cap for that lane is therefore `5`, not `4`.

This gives the archive a clean no-go statement:
- a hard cap of `4` is incompatible with the current `0.95` uncertainty-robust guarantee for any single minimum-dwell preset.

The same saved reports also show:
- near-exact `0.99` robustness still needs roughly `11` transitions even after cap minimization,
- while a lower-guarantee lane can plausibly move into dwell `19`–`32`, with dwell `25` as the current conservative planning anchor and `4` as the conservative band-wide cap.

## Implementor rule
- Keep the trusted-repeat `4`-transition planner and the uncertainty-robust preset as separate lanes.
- Reserve `5` transitions when the archive wants one near-optimal preset that stays safe under repeat uncertainty.
- If a hard cap of `4` is non-negotiable, relax the guarantee first instead of pretending dwell `9` still fits.
- Treat the dwell-`19`–`32` region as the next low-churn planning zone, but mark it as a partially certified lane until the exact band-wide minimum cap is replayed and stored.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_guardrails_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_guardrails_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_cap_guardrails.py`

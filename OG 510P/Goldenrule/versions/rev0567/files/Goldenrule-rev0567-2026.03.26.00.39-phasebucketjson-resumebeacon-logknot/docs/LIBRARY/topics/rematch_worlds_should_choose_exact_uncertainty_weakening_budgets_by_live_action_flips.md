# Rematch worlds should choose exact uncertainty weakening budgets by live action flips

## Claim
Once the archive already exposes the weakening budget ladder, future inheritors should audit each budget as a concrete live-controller action flip in the saved-state matrix, not merely as a more permissive threshold level.

## Why
- the default saved-state controller has exactly `18` live state/floor cases,
- every extra weakening budget unit changes exactly `1` of those live instructions and leaves all `7` strengthenings untouched,
- so the operational meaning of a budget increase is sparse, named, and fully auditable,
- and governance can now ask “which concrete sticky case are we releasing next?” instead of “what threshold are we moving to?”

## Current archive consequence
- budget `1` releases only the suffix boundary relaxed case `18 @ 0.84`, converting a stabilization into a weakening,
- budgets `2`, `3`, and `5` release canonical-anchor holds into weakenings,
- budget `4` releases the remaining transient-boundary sticky case `8 @ 0.84`,
- and the released live weakening count now matches the budget exactly: `{0,1,2,3,4,5}`.

## Operational rule
1. choose a weakening budget by the next live state/floor pair you are willing to stop treating as sticky,
2. read each budget increment as exactly one new live weakening instruction,
3. distinguish boundary-origin releases (`stabilize -> weaken`) from anchor-origin releases (`hold -> weaken`),
4. treat any future policy edit that causes more than one live flip per budget step as a substantive redesign.

## Pointers
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_live_action_surface_snapshot_20260308.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_live_action_surface.py`

# Rematch worlds should treat fixed dwell regions as budget-ceiling modes under exact uncertainty

## Claim
When target dwell is fixed, each live exact uncertainty region has a **hard budget ceiling**: extra cap or checkpoint budget cannot buy a stronger current exact preserved-gain floor unless target dwell moves to a different live region.

## Why this matters
The archive already records the three live fixed-dwell regions of the current exact uncertainty menu:
- dwell `{2}` -> near-exact precision singleton, exact floor ceiling `0.999822`,
- dwell `[8,18]` -> near-optimal non-fragile band, exact floor ceiling `0.980481`,
- dwell `[19,32]` -> relaxed suffix, exact floor ceiling `0.870482`.

Those ceilings are not just labels for the cheapest surviving tier at each region.
They are also the **strongest current exact floors available while target dwell stays inside that region**.

So once target dwell is fixed:
- spending beyond cap `5` / checkpoints `8` inside `[8,18]` does **not** buy a floor above `0.980481`; a stronger exact floor requires jumping to dwell `2`,
- spending beyond cap `3` / checkpoints `5` inside `[19,32]` does **not** buy a floor above `0.870482`; a stronger exact floor requires jumping into `[8,18]`,
- and spending beyond the near-exact singleton requirements at dwell `2` buys no stronger current exact floor at all because that region already sits at the top saved ceiling.

The same fail-fast logic applies to dead spaces.
No amount of extra budget buys entry into dwell `<2`, dwell `[3,7]`, or dwell `>32` until target dwell moves to live support.

## Implementor rule
- When dwell is physically fixed, optimize only up to that region's exact floor ceiling.
- If a stronger floor is still required after that point, stop raising budget locally and instead retarget dwell to the next live region.
- Treat `[8,18]` as the strongest non-fragile fixed-dwell region.
- Treat `[19,32]` as a relaxed-only suffix whose floor cannot be upgraded in place.
- Treat dead dwell regions as budget-impotent gaps, not as candidates for “buying through” with extra cap or checkpoints.
- Remember that master-calendar amortization removes only checkpoint payment, not the fixed-dwell floor ceilings themselves.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_fixed_dwell_budget_ceiling_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_fixed_dwell_budget_ceiling_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_fixed_dwell_budget_ceiling.py`

# Rematch worlds should share one half-step executor between batch path-L2 and path-Linf

Future inheritors should stop thinking of feasible witness execution as a place where path-`L2` and path-`Linf` need separate machinery.

The archive had already established two facts separately:
- path-`L2` can be executed from one scalar `half_step_selector_index = h` by clamping `h` into the doubled feasible band `[2a, 2b]`, and
- path-`Linf` requests also collapse to that same scalar selector lattice once endpoint ranks are known.

The new shared-executor law closes the remaining gap:
**once the request has already been normalized to `half_step_selector_index`, the feasible witness executor is identical for both semantics.**

Operationally, that means:
1. derive `half_step_selector_index` from the appropriate semantics,
2. compute the feasible overlap interval `[a, b]`,
3. select the witness class by `clamp(h, 2a, 2b)`,
4. decode the clamped half-step index only if a rank interval or state-code witness must be shown to a human.

The path distinction is now cleanly separated:
- path-`L2` is still a **mean-side encoding rule**,
- path-`Linf` is still an **extrema-side encoding rule**,
- but both feed the same feasible execution surface.

This is the important inheritance result.
It removes an unnecessary semantic branch from the executor while preserving the semantic difference where it actually lives: in how the selector index is derived from the preferred bundle.

On the current realized catalog, the shared executor matched both previously validated semantics-specific laws on all `5,049` selector-class/interval pairs, for `10,098` total equivalence checks.
The execution case split stays the same as the earlier path-`L2` clamp audit because the executor really is the same object: `1,785` preserve cases, `1,904` lower-boundary clamps, and `1,360` upper-boundary clamps.

Do **not** overgeneralize this shortcut to path-`L1`.
Median semantics can still select a different feasible witness even when the feasible interval and half-step lattice are the same.

Companion artifacts:
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_executor_law_snapshot_20260309.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_executor_law.py`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_executor_law.py`

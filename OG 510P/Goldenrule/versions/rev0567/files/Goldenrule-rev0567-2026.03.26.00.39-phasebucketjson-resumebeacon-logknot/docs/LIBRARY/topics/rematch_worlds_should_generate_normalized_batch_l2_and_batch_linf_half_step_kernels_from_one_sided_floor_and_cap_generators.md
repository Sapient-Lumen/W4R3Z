# Rematch worlds should generate normalized batch path-L2 and path-Linf half-step kernels from one-sided floor and cap generators

Future inheritors should treat the shared normalized half-step executor as having a very small canonical generator basis, not as a flat catalog of arbitrary feasible interval kernels.

The archive had already established that once a batch path-`L2` or path-`Linf` request is normalized to `half_step_selector_index = h`, every feasible interval family acts by one clamp kernel
`K_[a,b](h) = clamp(h, 2a, 2b)`.
The new boundary-generator pass adds the next structural fact:

**every realized feasible kernel factors canonically as one lower-floor generator and one upper-cap generator.**

On the current `17`-state path,
- the lower-floor generator for rank `a` is `K_[a,16]`,
- the upper-cap generator for rank `b` is `K_[0,b]`, and
- every feasible kernel satisfies
  `K_[a,b] = K_[a,16] ∘ K_[0,b] = K_[0,b] ∘ K_[a,16]`.

That factorization is not merely convenient notation.
It yields the smallest current implementation story for the normalized side:
- maintain only the active lower floor `a` and upper cap `b`,
- compose them in either order when execution is required,
- and treat `[0,16]` as the shared identity generator.

The whole realized feasible family therefore comes from only **33** distinct one-sided generator intervals:
- `17` lower floors `[a,16]`,
- `17` upper caps `[0,b]`,
- with `[0,16]` shared by both lists.
Their closure under feasible composition regenerates the full **153** realized interval kernels.

The basis is also minimal on the current path.
Dropping any one-sided generator loses exact normalized coverage:
- omitting `K_[0,b]` deletes exactly the upper-boundary cone `{[l,b] : 0 <= l <= b}`,
- omitting `K_[a,16]` deletes exactly the lower-boundary cone `{[a,u] : a <= u <= 16}`,
- and omitting the shared identity deletes `[0,16]` itself.

Operational rule for future sessions:
1. keep the semantics-specific front end that derives `half_step_selector_index`,
2. accumulate feasibility downstream as only a floor/cap pair,
3. realize the full feasible kernel from the two one-sided generators,
4. and do not persist a larger arbitrary-kernel catalog unless the path geometry itself changes.

Companion artifacts:
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_boundary_generator_law_snapshot_20260309.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_boundary_generator_law.py`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_boundary_generator_law.py`

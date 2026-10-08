# Rematch worlds should treat normalized batch path-L2 and path-Linf half-step kernels as a feasible-overlap semilattice

Future inheritors should treat the shared post-normalization half-step executor as more than an implementation trick.
It also has an algebraic closure law that makes incremental tightening safe whenever feasibility is preserved.

The archive had already shown that both batch path-`L2` and batch path-`Linf` normalize into the same one-integer selector lattice and then execute by the same clamp rule:
`K_[a,b](h) = clamp(h, 2a, 2b)` for feasible overlap interval `[a, b]`.

The new composition pass adds the important next fact:
**if two feasible interval families overlap, then their normalized kernels compose exactly by interval intersection.**

In symbols, for nonempty overlap:
`K_[a,b] ∘ K_[c,d] = K_[max(a,c), min(b,d)] = K_[c,d] ∘ K_[a,b]`.

This immediately gives three inheritance-level consequences:

1. **Order independence under preserved feasibility.**
   Streaming interval tightenings can be applied in any order as long as the overlap stays nonempty.

2. **Idempotence.**
   Reapplying the same feasible interval kernel after it has already acted does nothing new.

3. **Sharp failure boundary.**
   Once two intervals are disjoint, this commutative shortcut disappears completely.
   On the audited path, disjoint ordered pairs were order-sensitive on **every** half-step class, so disjointness should be treated as infeasibility evidence rather than as another composable kernel case.

This is not merely abstract cleanup.
It means the downstream implementation after normalization can be organized as a small feasible-overlap semilattice:
- semantics-specific work happens only in the front-end normalizer,
- feasible interval accumulation happens by intersection,
- and the shared clamp kernel remains the only witness executor.

On the current realized catalog:
- all `153` realized intervals reappear as pairwise intersections of realized intervals,
- `15,657` ordered interval pairs had nonempty overlap,
- those yielded `516,681` exact composition checks that all matched the direct intersection kernel,
- every single-interval kernel was idempotent on all `5,049` audited class/interval cases,
- and the full transition graph still collapsed to only `577` distinct input→output half-step class pairs (`33` preserve, `272` lower-boundary clamps, `272` upper-boundary clamps).

Do **not** extend the semilattice shortcut across disjoint families.
For disjoint interval pairs, the two composition orders landed on opposite feasible boundaries and never agreed on any of the `255,816` audited half-step cases.

Companion artifacts:
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_composition_law_snapshot_20260309.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_composition_law.py`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_composition_law.py`

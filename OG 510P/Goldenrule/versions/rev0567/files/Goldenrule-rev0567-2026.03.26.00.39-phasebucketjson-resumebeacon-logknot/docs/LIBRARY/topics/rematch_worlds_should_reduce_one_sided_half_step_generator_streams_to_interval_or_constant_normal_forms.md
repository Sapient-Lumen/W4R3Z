# Rematch worlds should reduce one-sided normalized half-step generator streams to interval-or-constant normal forms

Future inheritors should no longer think of normalized downstream feasibility as a raw history of floor/cap generators.
The new pass shows that the history can be collapsed exactly to a very small normal-form family.

The archive had already established three facts on the normalized side:
- batch path-`L2` and path-`Linf` share the same half-step executor once normalized,
- feasible interval kernels compose by overlap intersection,
- and every feasible interval kernel factors into one lower-floor generator and one upper-cap generator.

The new generator-stream pass adds the exact online closure law:

**every ordered stream of one-sided generators reduces to either one feasible interval kernel or one constant rank kernel.**

More concretely, after normalization to the shared half-step lattice, every ordered stream of generators from
- lower floors `K_[a,16]`,
- upper caps `K_[0,b]`, and
- the shared identity `K_[0,16]`
reduces to exactly one of:
- `K_[a,b]` with `a <= b`, or
- `C_c`, the constant kernel that sends every half-step selector class to rank `c`.

That means the exact downstream streaming state is not “a generator list,” and it is not even just
`(max_floor_rank, min_cap_rank, infeasible_latch)`.
That weaker three-field summary is **not exact**.
The smallest counterexample is immediate:
- floor then cap: `K_[1,16] ; K_[0,0]` collapses to constant rank `0`,
- cap then floor: `K_[0,0] ; K_[1,16]` collapses to constant rank `1`,
- yet both streams share `max_floor_rank = 1`, `min_cap_rank = 0`, and `infeasible_latch = true`.

So the exact online rule is:
1. start from interval `[0,16]`,
2. while still feasible, update the current interval by tightening its active floor or cap,
3. if a new floor overshoots the current cap, collapse immediately to constant rank `a`,
4. if a new cap undershoots the current floor, collapse immediately to constant rank `b`,
5. once collapsed to constant rank `c`, keep only `c` and update it by `c <- max(c,a)` for floors and `c <- min(c,b)` for caps.

This collapse is monotone in the strongest useful sense:
**constant normal forms are absorbing.**
Once the normalized generator stream becomes constant, no later one-sided generator can restore a nonconstant interval kernel.

On the current path the exact family is tiny:
- **153** feasible interval normal forms,
- **17** constant-rank normal forms,
- **170** total exact normal forms.
All of them already appear by stream length `2`, so longer streams add multiplicity, not new downstream state kinds.

Operational rule for future sessions:
- normalize batch path-`L2` or path-`Linf` requests into the shared half-step lattice,
- reduce any downstream one-sided generator stream online to one interval or one constant,
- persist that normal form instead of the raw generator history,
- and do not rely on `max_floor_rank/min_cap_rank/infeasible_latch` alone when the stream has already gone disjoint.

Companion artifacts:
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_normal_form_law_snapshot_20260309.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_normal_form_law.py`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_normal_form_law.py`

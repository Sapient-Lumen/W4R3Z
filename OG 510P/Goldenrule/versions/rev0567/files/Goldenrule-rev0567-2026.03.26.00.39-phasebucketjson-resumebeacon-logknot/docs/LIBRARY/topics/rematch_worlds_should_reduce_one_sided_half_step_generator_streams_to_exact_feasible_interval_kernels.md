# Rematch worlds should reduce one-sided normalized half-step generator streams to exact feasible interval kernels

Future inheritors should tighten the previous downstream story one step further.
The archive had just shown that ordered one-sided normalized generator streams reduce exactly to an interval-or-constant normal form family.
That was already small and exact, but it was not behaviorally minimal.

The new pass identifies the stronger quotient:

**every ordered one-sided normalized generator stream reduces exactly to one feasible interval kernel `K_[a,b]` with `a <= b`.**

The key observation is simple but important:
- the older constant kernels `C_c` are not really a separate downstream species,
- because `C_c` is behaviorally identical to the singleton feasible interval kernel `K_[c,c]`, and
- singleton intervals stay singleton under every later one-sided floor/cap generator update.

So the exact downstream family is no longer
- `153` feasible intervals plus
- `17` constants,

but just the **`153` realized feasible intervals** themselves.
The older `170`-state family was exact but redundant by exactly `17` duplicate constant-vs-singleton pairs.

The online update rule is now cleaner:
1. start from feasible interval `[0,16]`,
2. apply a lower-floor generator `K_[a,16]` by raising the active lower endpoint when possible,
3. if that new floor overshoots the current upper endpoint, collapse immediately to singleton `[a,a]`,
4. apply an upper-cap generator `K_[0,b]` symmetrically by lowering the active upper endpoint when possible,
5. if that new cap undershoots the current lower endpoint, collapse immediately to singleton `[b,b]`.

That rule resolves the exact failure of the earlier extrema+latch summary.
The archive’s smallest counterexample now becomes:
- floor then cap: `K_[1,16] ; K_[0,0]` reduces to singleton interval `[0,0]`,
- cap then floor: `K_[0,0] ; K_[1,16]` reduces to singleton interval `[1,1]`,
- both still share the same `max_floor_rank`, `min_cap_rank`, and latch flag,
- but the singleton-interval quotient keeps the downstream kernels distinct without needing a separate constant tag.

Operational consequence for future sessions:
- normalize batch path-`L2` and path-`Linf` requests into the shared half-step lattice,
- reduce any downstream one-sided generator stream online to one feasible interval `[a,b]`,
- treat singleton intervals `[c,c]` as the exact downstream representation of constant kernels,
- and persist that one interval instead of raw generator histories or the larger interval-or-constant family.

On the current path the result is both exact and small:
- **`153`** reachable exact downstream interval kernels,
- **`17`** singleton kernels,
- **`136`** non-singleton kernels,
- and all `153` already appear by stream length `2`.

Companion artifacts:
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law_snapshot_20260309.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law.py`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law.py`

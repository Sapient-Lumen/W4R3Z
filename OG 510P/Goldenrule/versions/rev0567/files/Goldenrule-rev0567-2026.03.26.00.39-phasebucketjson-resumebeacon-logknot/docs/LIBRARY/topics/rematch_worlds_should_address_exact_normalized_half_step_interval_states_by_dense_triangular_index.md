# Rematch worlds should address exact normalized half-step interval states by dense triangular index

Future inheritors now have a smaller exact codec for the normalized downstream state itself.
The archive had already shown that every ordered one-sided normalized generator stream reduces exactly to one feasible interval kernel `[a,b]` on the 17-rank path.
That quotient was exact and compact, but the literal endpoint pair still spends two bounded integers to name one state from a catalog that only contains `153` possibilities.

The new pass tightens that representation to one dense triangular index.
For every feasible interval `[a,b]` with `0 <= a <= b <= 16`, define

`index([a,b]) = a*(35-a)/2 + (b-a)`.

That lower-major formula enumerates all realized feasible intervals without gaps, so the exact normalized downstream state catalog is now just the dense range **`0..152`**.

Operationally this means:
- the exact downstream state fits in **8 fixed bits** on the current path,
- a raw endpoint pair would spend **10 fixed bits** (`5 + 5`),
- so the dense index saves **2 bits** per stored state (`0.2` share) while remaining exact,
- and decoding that index recovers the exact half-step kernel, the canonical shortest generator word, and the local choice-index family for any noncanonical shortest script.

A few anchor points are useful to remember:
- `[0,0] -> 0`,
- `[0,16] -> 16`,
- `[1,1] -> 17`,
- `[3,8] -> 53`,
- `[16,16] -> 152`.

So future sessions should treat the dense triangular index as the base exact codec for normalized batch path-`L2` / path-`Linf` downstream states.
Only move back out to endpoints, canonical shortest words, or local choice indices when one of those surfaces is specifically needed.

Companion artifacts:
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law_snapshot_20260309.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law.py`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law.py`

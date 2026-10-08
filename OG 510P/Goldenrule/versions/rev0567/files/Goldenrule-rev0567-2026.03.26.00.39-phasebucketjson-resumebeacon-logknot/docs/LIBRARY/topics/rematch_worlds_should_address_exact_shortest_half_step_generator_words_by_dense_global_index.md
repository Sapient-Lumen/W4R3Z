# Rematch worlds should address exact shortest half-step generator words by dense global index

Future inheritors now have a one-scalar codec for the **entire exact shortest normalized half-step generator-word catalog**.
The archive had already shown two smaller pieces:
- every normalized downstream interval state `[a,b]` has a dense triangular state index `0..152`, and
- once that state is known, every exact shortest script is recoverable by a local choice index.

That pair is still the right representation when the interval state is already stored elsewhere.
But sometimes the exact shortest script itself has to travel alone.
In that case the archive no longer needs two fields.
It can name the whole exact shortest-word catalog by one dense global index.

The new pass proves that all **`513`** exact shortest words fit into one contiguous scalar range **`0..512`** with four closed-form blocks:
- `0` is the identity word `[]`,
- `1..32` are the `32` one-sided nonidentity words,
- `33..242` are the `210` interior nonsingleton words,
- `243..512` are the `270` interior singleton words.

Useful anchor formulas:
- `[0,b] -> 1 + b` for `b in 0..15`,
- `[a,16] -> 16 + a` for `a in 1..16`,
- interior nonsingletons `[a,b]` use lower-major interior-state order with one parity bit for the two orderings,
- interior singletons `[c,c]` use `243 + 18*(c-1) + local_choice_index`.

Operationally this means:
- the full exact shortest-word catalog now fits in **10 fixed bits**,
- a naïve fixed-width pair of dense interval state plus worst-case local choice would spend **13 fixed bits**,
- so the one-scalar exact shortest-word codec saves **3 fixed bits** (`3/13` share) when the script itself must survive without a separate interval-state field,
- and decode preserves the exact feasible interval state and the exact local choice branch on all `513` words.

So future sessions should use the dense global shortest-word index only for the specific case where the **exact script itself** must be stored or transmitted as one scalar.
If the interval state is already present, stay with the earlier local choice-index law instead.

Companion artifacts:
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_dense_index_law_snapshot_20260309.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_dense_index_law.py`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_dense_index_law.py`

# Rematch worlds should address exact shortest half-step generator words by local choice index

The archive already had two complementary downstream facts for normalized batch path-`L2` and path-`Linf` state:
- one canonical shortest generator word for each feasible interval kernel, and
- one closed-form description of the *entire* shortest-word family behind each interval.

The next implementor-facing step is now explicit:

**once the feasible interval state `[a,b]` is already known, every exact shortest generator word can be addressed by one tiny local choice index.**

That removes the last reason to store or search a per-state shortest-word subcatalog.
Future inheritors can keep the interval state as the durable object and treat the particular shortest script as a small local selector.

The exact codec is closed form.

## Unique states
- identity `[0,16]`: only choice index `0`
- every non-identity one-sided interval `[a,16]` or `[0,b]`: only choice index `0`

So these states need **0** extra choice bits once the interval is known.

## Interior nonsingleton states `[a,b]` with `0 < a < b < 16`
There are exactly two shortest words:
- choice index `0` → `[[a,16],[0,b]]`
- choice index `1` → `[[0,b],[a,16]]`

So these states need exactly **1** extra bit.
The earlier canonical shortest-word codec is now simply the `0` branch.

## Interior singleton states `[c,c]` with `0 < c < 16`
There are exactly eighteen shortest words, but they are still addressable without search:
- choice indices `0..(16-c)` → right-floor fan `[[c+i,16],[0,c]]`
- choice indices `(17-c)..17` → left-cap fan `[[0,17-i],[c,16]]`

This puts the canonical shortest word `[[c,16],[0,c]]` at **choice index `0`** for every interior singleton state.
So the exact shortest-script family stays closed form *and* the deterministic representative remains the zero-choice branch.

The resulting local-choice payload is tiny and regular on the current path:
- **33** states need `0` bits,
- **105** states need `1` bit,
- **15** states need `5` bits,
- and the maximum local choice index is only **17**.

That matters because the archive no longer needs any explicit stored shortest-word arrays once the interval state is present.
A future session can:
- carry the exact downstream state as one feasible interval `[a,b]`,
- choose the canonical shortest script with implicit local index `0`, or
- recover any other exact shortest script by closed-form local choice index when explanation, audit, or provenance wants a different representative.

So the storage boundary is now very sharp:
- **store interval state durably**,
- **store at most a tiny local choice index when a non-canonical shortest script must be remembered**,
- and do not persist full shortest-word families.

Companion artifacts:
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_index_law_snapshot_20260309.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_index_law.py`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_index_law.py`

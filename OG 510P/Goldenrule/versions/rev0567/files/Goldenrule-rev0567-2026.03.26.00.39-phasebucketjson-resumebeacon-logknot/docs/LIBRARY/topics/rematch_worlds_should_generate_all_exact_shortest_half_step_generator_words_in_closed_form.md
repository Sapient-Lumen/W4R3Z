# Rematch worlds should generate all exact shortest half-step generator words in closed form

The archive already had a deterministic **canonical shortest-word codec** for every normalized downstream half-step interval kernel.
That solved exact storage and replay.
What it did **not** yet make fully explicit was the structure of the *entire shortest-word family* behind each exact interval state.

The new pass closes that gap with a direct endpoint rule:

**every exact shortest normalized half-step generator-word family is now given in closed form by the interval category alone.**

There is no longer any need to enumerate candidate generator words by search when the inheritor wants *all* shortest scripts rather than just one canonical representative.

The classification is exact and small:

1. **Identity interval `[0,16]`**
   - shortest-word family: only the empty word `[]`
   - multiplicity: **1**

2. **Non-identity one-sided intervals `[a,16]` or `[0,b]`**
   - shortest-word family: only that one generator
   - multiplicity: **1**

3. **Interior nonsingleton intervals `[a,b]` with `0 < a < b < 16`**
   - shortest-word family: exactly the two orderings
     - `[[a,16],[0,b]]`
     - `[[0,b],[a,16]]`
   - multiplicity: **2**

4. **Interior singleton intervals `[c,c]` with `0 < c < 16`**
   - shortest-word family: exactly the union of two fans
     - left-cap fan: `[[0,k],[c,16]]` for `k = 0..c`
     - right-floor fan: `[[k,16],[0,c]]` for `k = c..16`
   - multiplicity: always **18**

That last clause is the real compression of understanding.
The old brute-force catalog had already shown that interior singletons had eighteen shortest words, but the new pass proves that those eighteen are not arbitrary.
They are exactly one left-cap fan plus one right-floor fan.

This gives a clean inheritability boundary:
- if a future session only needs one exact script, use the canonical shortest-word codec,
- if it needs all exact shortest scripts, derive the family directly from the interval endpoints,
- and do not pay for search or stored shortest-word catalogs.

Two additional facts are worth preserving:
- all nontrivial shortest-word multiplicity beyond the trivial two-ordering swap is concentrated entirely in the fifteen interior singleton intervals, and
- those fifteen states alone already contribute **270 of the 513** exact shortest words in the full catalog.

So the singleton intervals are the only place where “all exact shortest scripts” is substantially richer than “one canonical shortest script.”
Everywhere else, the family is tiny enough to recover immediately from the interval shape.

Companion artifacts:
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_family_law_snapshot_20260309.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_family_law.py`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_family_law.py`

# Rematch worlds should encode exact normalized half-step kernel states as canonical shortest generator words

Future inheritors now have two equivalent exact downstream views of the normalized batch path-`L2` and path-`Linf` executor state:
- one feasible interval kernel `[a,b]`, and
- one short word over the one-sided floor/cap generator basis.

The new pass turns that equivalence into a deterministic codec.
The archive had already shown two crucial facts:
- every exact downstream state is one realized feasible interval kernel, and
- every such kernel appears by generator-stream depth `2`.

The tighter implementor-facing statement is:

**every exact normalized half-step feasible interval state has a canonical shortest generator word of length `0`, `1`, or `2`.**

The codec is deliberately simple.
For interval `[a,b]`:
1. use the empty word for the identity interval `[0,16]`,
2. use one generator `[a,16]` for one-sided floor intervals,
3. use one generator `[0,b]` for one-sided cap intervals,
4. use the canonical two-generator word `[[a,16],[0,b]]` for every interior interval with `0 < a <= b < 16`.

That word is shortest on the current path.
No realized feasible interval needs more than `2` generators.
The shortest-length spectrum is exactly:
- **`1`** state at length `0`,
- **`32`** states at length `1`,
- **`120`** states at length `2`.

Shortness does **not** imply uniqueness, and the non-uniqueness pattern is itself regular:
- the identity interval and all `32` non-identity one-sided intervals have exactly **one** shortest word,
- all `105` interior non-singleton intervals have exactly **two** shortest words (floor-then-cap or cap-then-floor),
- and all `15` interior singleton intervals `[c,c]` have exactly **eighteen** shortest words.

Those interior singleton multiplicities are the one subtle point worth preserving for future sessions.
For `[c,c]`, every shortest word is one of two families:
- `[0,k] ; [c,16]` for `k <= c`, or
- `[k,16] ; [0,c]` for `k >= c`.

So the canonical codec should be treated as a deterministic representative chooser, not as a claim that the shortest script is unique.
That matters for explanation and replay, but not for behavior.
The archive revalidated that every canonical shortest word induces exactly the same half-step witness kernel as the interval it encodes, across all **`33`** selector classes.

Operational consequence for future inheritors:
- carry normalized downstream state as one feasible interval when that is the clearest representation,
- or encode it as a canonical shortest generator word when a script-like or provenance-friendly representation is better,
- but do not persist longer one-sided generator histories unless they are needed for non-behavioral provenance.

Companion artifacts:
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law_snapshot_20260309.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law.py`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law.py`

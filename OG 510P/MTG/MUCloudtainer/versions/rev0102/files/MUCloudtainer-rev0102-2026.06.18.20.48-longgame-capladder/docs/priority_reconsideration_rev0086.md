# rev0086 priority reconsideration

After rev0085, the riskiest unfinished item was the meaning of ties. With 207 same-score pairs, it would be easy to drift into saying the stabilizer is "mostly equivalent" to the guard. That is only true for score, not for terminal behavior.

## Revised priorities

1. Keep `public_counter_life20_stabilizer` quarantined.
2. Treat transfer-panel score failure as the main statistical score reason for quarantine.
3. Treat same-score mechanism drift as a separate behavioral reason not to call the candidate equivalent.
4. Require future adaptive candidates to report score+mechanism equivalence, not only score ties.
5. Move the next substantive search toward genuinely preregistered counter generation instead of hand-tuning this stabilizer.

## Next useful work

The next high-value step is a preregistered candidate generator or search panel. Any new candidate should be evaluated under the rev0085/rev0086 pair-integrity, exact-sign, and mechanism-drift contracts before it is allowed to enter a broad population frontier.

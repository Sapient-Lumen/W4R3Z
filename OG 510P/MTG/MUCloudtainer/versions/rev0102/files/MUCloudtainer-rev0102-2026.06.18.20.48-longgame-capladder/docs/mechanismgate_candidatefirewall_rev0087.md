# rev0087 — mechanism-aware candidate firewall

## Risk targeted

rev0083 introduced `public_counter_life20_stabilizer` from a selected weak cell. rev0084 and rev0085 showed negative transfer, and rev0086 showed same-score terminal-mechanism drift. The remaining risk was procedural: those results were descriptive artifacts, not an enforceable gate. A later runner could still accidentally place the adaptive candidate into a broad population or candidate pool.

## Change

rev0087 adds `src/muc5/population_candidate_gate.py`, a reusable gate that combines three checks before an adaptive counter candidate can become pool-eligible:

1. paired score transfer must not familywise-hard-fail;
2. same-score terminal-mechanism drift must not familywise-hard-fail;
3. source game rows must not leak into broad or candidate pools.

For the stabilizer, the gate rejects the candidate for both score and mechanism reasons while confirming no pool leak occurred in the rev0084 source rows.

## Result

The candidate remains excluded from both candidate and broad promotion pools. The hard fail reasons are:

- `score_transfer_familywise_negative`
- `score_tie_mechanism_drift_familywise_supported`

This is not a new claim about `public_counter_guard`; it is a guardrail preventing an adaptive, mechanism-shifting repair attempt from contaminating future population evidence.

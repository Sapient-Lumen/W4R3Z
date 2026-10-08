# rev0083 deficient-cell counterprobe

rev0082 identified exactly one fine hierarchy row as current-counter-set deficient even by upper bound: `counter40_vs_threat40`, starting life 20, against `library_aware_threat_closure_targetguarded`.

rev0083 does not broaden the population or claim a rescue. It runs a seed-paired targeted probe over that one cell with three counter policies:

- `legacy_cf34_counter_ranker`
- `public_counter_guard`
- `public_counter_life20_stabilizer`

The new stabilizer is a public-information-only counter profile. It keeps mana up more often in life-20 pressure states, prioritizes Overlord/Jace counters, treats Jace mostly as bounce/fateseal rather than a draw engine, blocks face damage more aggressively, and avoids voluntary library churn.

## Result

The targeted probe ran 192 terminal-clean games: 3 policies × 2 target seats × 2 starting players × 16 reps. The C++ shadow sample checked 12,000 supported transitions with no mismatches.

The result changes the interpretation of the deficient cell but does not certify a repair:

- Existing `public_counter_guard` mean on the new paired seed grid: 0.53125.
- New `public_counter_life20_stabilizer` mean: 0.53125.
- Both have familywise probe LCB 0.3378533112 and UCB 0.7246466888.
- Rescue status becomes `certification_limited_existing_counter_candidate`, not `current_counter_set_deficient_even_by_upper_bound`.
- The new stabilizer does not improve the aggregate result: 58/64 paired guard-vs-candidate seed cells have the same score, 3 favor the candidate, and 3 favor the guard.

The most important read is that the rev0082 “upper-bound impossible” label was too brittle at 32 games in that fine cell. However, the targeted evidence is adaptive and must remain excluded from broad promotion pools.

## Next substantive move

Do not promote `public_counter_guard`. Do not add the stabilizer to the broad population as if it were preregistered. The next high-value work is either:

1. seed-disjoint non-adaptive replication of the cell if this fine stratum matters for certification, or
2. counterfactual deck/policy search for a meaningfully different counter plan, since this heuristic stabilizer tied the current guard rather than expanding the frontier.

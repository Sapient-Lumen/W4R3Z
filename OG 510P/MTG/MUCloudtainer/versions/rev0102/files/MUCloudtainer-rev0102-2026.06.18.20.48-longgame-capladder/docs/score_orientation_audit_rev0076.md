# rev0076 score-orientation audit

Risk addressed: the recent population conclusion is meaningless if target score orientation is wrong when the target policy is seated as player 1. Previous runners wrote the target-perspective score with repeated local logic. rev0076 centralizes that derivation and audits the live raw population game rows against raw player scores, winner, target seat, and terminal loss reason.

Inputs audited:

- `data/rev0069_population_frontier_games.csv`
- `data/rev0070_population_precision_games.csv`
- `data/rev0075_stratum_challenge_games.csv`

Result:

- 720 raw population games audited
- 360 target-seat-0 rows and 360 target-seat-1 rows
- 3 source tables
- 0 focus-score/result/mechanism mismatches
- all rows terminal-clean

This does not promote `public_counter_guard`. It protects the negative result from a high-impact bookkeeping failure: accidentally scoring the left player instead of the target policy after seat flips.

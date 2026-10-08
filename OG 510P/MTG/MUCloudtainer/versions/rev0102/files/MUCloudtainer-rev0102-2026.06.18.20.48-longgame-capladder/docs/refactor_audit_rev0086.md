# rev0086 refactor audit

rev0086 extends `src/muc5/population_pair_forensics.py` rather than adding another one-off notebook-style script.

## Added shared helpers

- `MechanismDriftSummary`
- `mechanism_flip_direction`
- `same_score_mechanism_flip_rows`
- `mechanism_drift_summary`
- `grouped_mechanism_drift_rows`

## Why this matters

Before rev0086, rev0085 could warn that same-score ties sometimes used different terminal mechanisms, but candidate-transfer gates still lacked a reusable contract for that distinction. The new helpers make score-only tie inflation testable.

The new script `scripts/run_rev0086_mechanism_drift_audit.py` consumes the existing rev0084 paired-delta table and emits only compact derivatives:

- primary mechanism-drift rows;
- exploratory context mechanism-drift rows;
- an 18-row same-score flip ledger; and
- a JSON summary.

No raw games, transition traces, or replay logs are introduced.

## Refactor result

The audit confirms that only 189 of 207 score ties are full score+mechanism equivalences. The remaining 18 are mechanism flips, and the direction is not symmetric. This closes a subtle interpretation loophole: a candidate can appear mostly tied on score while changing how the game ends.

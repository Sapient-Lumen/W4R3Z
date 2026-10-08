# rev0084 candidate-transfer audit

rev0083 invented `public_counter_life20_stabilizer` from a selected weak cell. That made the next risk adaptive overfit: a targeted candidate could drift into the broad counter population before proving it transfers.

rev0084 keeps the candidate out of the broad pool and runs a seed-disjoint guard-vs-candidate transfer audit.

## Design

Two paired designs were run:

1. **Selected-cell holdout**: `counter40_vs_threat40`, starting life 20, against `library_aware_threat_closure_targetguarded`, using new seeds and 24 reps per target-seat/start-player condition.
2. **Transfer panel**: guard and stabilizer across 3 size axes × 3 threat axes × 2 life totals × 2 target seats × 2 starting players × 2 reps.

Every pair uses the same seed for `public_counter_guard` and `public_counter_life20_stabilizer` in the same scenario. Rows are explicitly marked:

- `broad_pool_eligible = False`
- `candidate_pool_eligible = False`
- `sampling_design` equal to either `selected_cell_seed_disjoint_holdout` or `adaptive_candidate_transfer_seedpaired`

## Result

The run produced 480 terminal-clean games and 240 complete guard-vs-candidate pairs. The C++ shadow sample checked 14,000 supported transition events with zero mismatches, skips, or Python errors.

Overall paired result:

- candidate better: 10 pairs
- guard better: 23 pairs
- same score: 207 pairs
- candidate mean delta versus guard: -0.0541666667
- status: `candidate_quarantined_negative_transfer`

Selected-cell holdout:

- pairs: 96
- candidate better: 8
- guard better: 10
- same score: 78
- candidate mean delta: -0.0208333333
- status: `candidate_quarantined_negative_transfer`

Transfer panel:

- pairs: 144
- candidate better: 2
- guard better: 13
- same score: 129
- candidate mean delta: -0.0763888889
- status: `candidate_quarantined_negative_transfer`

## Interpretation

The stabilizer is not a repair. It tied the existing guard in the rev0083 target probe, then lost the seed-disjoint holdout/transfer audit on paired mean and pair counts.

The right action is to quarantine it as an adaptive diagnostic artifact. Future broad population work should not add it as a third counter row unless a preregistered, non-adaptive complete panel first shows transfer dominance.

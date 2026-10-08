# rev0099 expanded-matrix refresh and balanced evaluation design

rev0099 focuses on measurement risk rather than adding a new oracle. The riskiest inherited fact after rev0098 was that the first admitted PSRO response had dominated a low-resolution expanded matrix, while later challenger tests were all one-target probes. If the empirical-game matrix itself was under-sampled or seat/start handling drifted between runners, the whole PSRO loop could point at the wrong target.

## Code changes

- `src/muc5/evaluation_design.py` centralizes the canonical focal-pair design: configured life totals, repetitions, both physical seats, and both starting-player roles.
- `src/muc5/psro.py` now consumes `balanced_pair_cells()` inside `EmpiricalGameEvaluator.evaluate_focal_pair()` rather than carrying an inline loop.
- `tests/test_rev0099_evaluation_design.py` verifies design coverage, malformed-row detection, and evaluator emission of complete seat/start rows.
- `scripts/run_rev0099_matrix_refresh.py` refreshes the nine-strategy empirical population matrix with a larger balanced sample.

## Refreshed matrix

The nine-strategy population is the original eight-strategy response ecology plus the rev0092 admitted response:

```text
oracle_map_08_60_mixed_threats_counter_wall
```

The refresh uses:

```text
life totals: 20 and 40
reps per life/seat/start cell: 10
off-diagonal strategy pairs: 36
games per off-diagonal pair: 80
total game rows: 2,880
truncations: 0
```

The refreshed matrix remains exactly constant-sum by construction:

```text
max |M + Mᵀ - 1|: 0.0
max diagonal error from 0.5: 0.0
```

The solved empirical game still places all effective 1e-3 support on the admitted response:

```text
oracle_map_08_60_mixed_threats_counter_wall: 0.9996001799190364
```

Its refreshed pure floor against the nine-strategy population is 0.5, with mean score 0.6944 against the population rows. Against the eight incumbents specifically, its row scores are:

```text
guard_counter_wall40: 0.7000
guard_counter_wall60: 0.7125
pub_threat40_closure: 0.8750
pub_threat40_pressure: 0.7000
pub_threat40_surge: 0.7500
pub_threat60_closure: 0.6625
pub_threat60_pressure: 0.6875
pub_threat60_surge: 0.6625
```

## Interpretation

This strengthens the empirical target used by rev0094-rev0098 challenger work. It is not a strategic promotion and does not promote the admitted response as a general strategic answer. The refreshed matrix is still an empirical sample over a fixed population, and future oracles may find responses outside that population.

The important correction is procedural: every future PSRO or oracle runner now has a shared design/audit helper for balanced focal rows, so seat/start completeness is no longer a copy-pasted convention.

## Produced evidence

- `data/rev0099_expanded_matrix_refresh_summary.json`
- `data/rev0099_expanded_matrix_refresh_audit.json`
- `data/rev0099_expanded_matrix_games.csv`
- `data/rev0099_expanded_matrix_cells.csv`
- `data/rev0099_expanded_matrix_pair_estimates.csv`
- `data/rev0099_expanded_matrix_strategy_summary.csv`
- `data/rev0099_pair_symmetry_summary.csv`

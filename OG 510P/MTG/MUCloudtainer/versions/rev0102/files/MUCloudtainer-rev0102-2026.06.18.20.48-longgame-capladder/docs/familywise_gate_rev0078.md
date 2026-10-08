# rev0078 familywise promotion gate

## Risk addressed

The recent population gate made a promotion decision over a 2×3 empirical game. Previous rows used ordinary per-cell 95% Hoeffding intervals. Those intervals were conservative for a single bounded payoff row, but a promotion gate inspects all matrix cells together. If a future candidate sits near 0.50, unadjusted per-cell intervals can make the decision too optimistic.

## Code change

`population_familywise_interval_rows` recomputes simultaneous matrix intervals from the source mean and game count. For each context matrix it uses:

```text
per_cell_alpha = family_alpha / (row_policy_count * column_policy_count)
```

`population_familywise_gate_rows` then runs the existing fail-closed promotion gate against these recomputed columns:

```text
target_score_lcb_familywise
target_score_ucb_familywise
```

The ordinary gate remains available for continuity and comparison, but familywise rows should be preferred for promotion-sensitive matrix decisions.

## Result on the live broad population pool

Eligible rows are still only rev0069 + rev0070 complete panels. rev0075 remains an adaptive targeted challenge and is excluded from broad promotion evidence.

```text
ordinary eligible global LCB:       0.29827953478001323
familywise eligible global LCB:     0.26324362954759206
LCB delta:                         -0.03503590523242117
ordinary max CI width:              0.3201075971066403
familywise max CI width:            0.39017940757148256
width delta:                        0.07007181046484229
passed cells:                       0
blocking reason:                    conservative_floor_below_threshold
```

The conclusion does not become more exciting; it becomes safer. `public_counter_guard` remains quarantined under the conservative floor.

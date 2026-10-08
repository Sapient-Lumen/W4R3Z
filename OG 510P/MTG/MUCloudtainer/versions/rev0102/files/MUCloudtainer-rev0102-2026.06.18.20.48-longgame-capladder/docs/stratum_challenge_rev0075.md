# rev0075 stratum challenge

rev0075 spends new games on the riskiest remaining population surface from rev0074: fine strata where `public_counter_guard` had high point floors but the evidence was too thin to interpret.

The selection rule was executable, not narrative:

```text
source: data/rev0074_population_raw_fine_gate.csv
status: underpowered_min_games
mean_pure_security_value >= 0.50
mean_best_pure_row_policy == public_counter_guard
```

That selected three unique size/life strata:

```text
counter40_vs_threat40, life 40
counter60_vs_threat40, life 20
counter60_vs_threat40, life 40
```

Primary artifacts:

```text
scripts/run_rev0075_stratum_challenge.py
src/muc5/population_stratum_challenge.py
data/rev0075_stratum_challenge_summary.json
data/rev0075_stratum_challenge_games.csv
data/rev0075_stratum_challenge_arm_summary.csv
data/rev0075_stratum_challenge_pre_gate.csv
data/rev0075_stratum_challenge_post_gate.csv
data/rev0075_stratum_challenge_comparison.csv
```

## Result

The run added 288 seed-disjoint games, 16 new games per targeted population cell arm, and pooled those with the rev0069+rev0070 source evidence.  Each targeted cell now has 28 games per observed arm.

```text
new games:                         288
selected strata:                     3
post-stress gate rows:               3
post-stress gate-passed cells:       0
post-stress statuses:                3 quarantined_low_security_floor
min games per post cell arm:        28
max CI width after stress:           0.5133141236899359
best conservative LCB after stress:  0.38620008101217496
C++ checked transitions:        30,000
C++ mismatches:                      0
truncations:                         0
```

The targeted stress converted the three selected strata from `underpowered_min_games` to `quarantined_low_security_floor`.  This is real forward movement: the best-looking fine cells are no longer merely too small to judge; under the current gate, they remain below the conservative promotion floor after a seed-disjoint challenge.

## Cell comparison

```text
counter40_vs_threat40 life40:  pre 12 games, mean floor 0.5833, LCB 0.1913 -> post 28 games, mean floor 0.6071, LCB 0.3505
counter60_vs_threat40 life20:  pre 12 games, mean floor 0.3333, LCB 0.0000 -> post 28 games, mean floor 0.2857, LCB 0.0291
counter60_vs_threat40 life40:  pre 12 games, mean floor 0.5000, LCB 0.1079 -> post 28 games, mean floor 0.6429, LCB 0.3862
```

The third cell still looks promising on point estimate, but the lower bound is below 0.50.  It is the next natural budget target only if the project wants to test whether a real guarded-counter island exists, not if the goal is to promote now.

## Unexpected refactor finding

The first rev0075 analysis attempt produced six post-stress gate rows instead of three.  The cause was type fragmentation: older CSV summaries carried `starting_life` as strings while new in-memory summaries carried it as integers.  Without context normalization, the pooled gate split one scientific stratum into `"40"` and `40`.

rev0075 now normalizes context-axis values before population grouping and aggregation.  The corrected rerun produces the intended three post-stress gate rows.

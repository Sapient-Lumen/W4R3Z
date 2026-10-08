# rev0048 terminal-gate results

The rev0048 terminal-gate table is stored in:

```text
data/rev0048_truncation_rescue_games.csv
```

Companion artifacts:

```text
data/rev0048_truncation_rescue_aggregate.csv
data/rev0048_truncation_rescue_standings.csv
data/rev0048_truncation_rescue_stat_standings.csv
data/rev0048_truncation_rescue_pairwise.csv
data/rev0048_truncation_rescue_by_strategy.csv
data/rev0048_truncation_rescue_by_pair.csv
```

The most important new columns are:

```text
baseline_is_truncation
final_is_truncation
resolved_from_truncation
truncation_rescue_status
baseline_max_decisions
final_max_decisions
```

The summary:

```text
rev0047 baseline max decisions:   380
rev0048 final max decisions:      900
baseline truncations:             30 / 144
final truncations:                 0 / 144
resolved terminal rate:          100% of baseline truncations
```

Interpretation:

* The rev0047 result was too truncation-heavy for comfortable policy comparison.
* The same schedule at 900 decisions becomes terminal-clean.
* Future payoff panels that exceed the strict truncation gate should either be rescued this way or kept out of promotion/statistical claims.

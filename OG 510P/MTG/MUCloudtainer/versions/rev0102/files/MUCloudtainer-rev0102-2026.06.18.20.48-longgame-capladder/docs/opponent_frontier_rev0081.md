# rev0081 opponent-frontier threat audit

rev0080 resolved the size/fine power blocker and kept `public_counter_guard` quarantined.  The remaining risk was interpretability: one hierarchical security floor says the matrix is weak, but does not identify whether the weakness is broad or isolated to a particular opponent axis.

rev0081 adds a column-resolved frontier audit.  For every hierarchy layer and context, it asks: for this exact threat column, does the current counter-policy population contain any credible familywise answer?

The audit uses the same matrix-familywise Hoeffding correction as the promotion gate:

```text
family alpha:        0.05
matrix cells:        6
per-cell alpha:      0.008333333333333333
min games per cell:  24
max CI width:        0.60
answer threshold:    0.50 LCB
```

Input evidence is restricted to broad complete-panel sources:

```text
rev0069 + rev0070 + rev0080 eligible games: 1152
rev0075 adaptive challenge rows excluded: 18 summary rows
```

Result:

```text
frontier rows:                         36
column answers passed:                 0
status:                                36 no_credible_counter_answer_for_threat_column
weak threat axes:                      3/3
worst best-response LCB:               0.0
best best-response LCB:                0.4886154443213881
max CI width observed:                 0.5852691113572237
min games per observed column cell:    32
```

Layer breakdown:

```text
global:        3 no credible column answers
by_life:       6 no credible column answers
by_size:       9 no credible column answers
by_size_life: 18 no credible column answers
```

The worst resolved cell is the library-aware closure threat at `counter40_vs_threat40`, starting life 20.  The strongest resolved cell still remains below threshold, so the result is not merely “one ugly outlier.”  It says the current two-policy counter population lacks a certified answer across every named threat axis under the current familywise gate.

Primary artifacts:

```text
src/muc5/population_frontier.py
scripts/run_rev0081_opponent_frontier_audit.py
tests/test_rev0081_opponent_frontier.py
data/rev0081_opponent_frontier_summary.json
data/rev0081_opponent_frontier_familywise.csv
data/rev0081_opponent_frontier_layer_summary.csv
data/rev0081_opponent_frontier_hierarchical_gate_reference.csv
```

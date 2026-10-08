# rev0052 life-flip results

rev0052 selected four target/opponent cells from rev0051's target-pair table and retested them at `max_decisions=900`.

Archived result:

```text
games:                     256
selected target matchups:    4
target/life cells:           8
life-flip retest rows:       4
truncations:                 0
promotion gate:              passed
statistical gate:            passed
life-flip gate:              passed
replay samples:              8 / 8 passed
C++ shadow events:           75,767
C++ shadow mismatches:       0
C++ shadow skipped:          0
C++ replay trace events:     2,867
C++ replay mismatches:       0
```

The important result is negative/softening: all four selected rev0051 life splits softened under the focused retest. The largest previous apparent flip, `code_jace60` versus `cf34_counter_wall`, no longer showed the dramatic 20-vs-40 split observed in the lower-sample table.

This does not prove life total is irrelevant. It means the previous low-sample target-pair rows were too noisy for matchup/life claims.

The strongest concrete cell in this run was:

```text
cf34_counter_wall vs pub_threat_overlord
life 20: score 0.78125
life 40: score 0.78125
cell signal: favored at both life totals
```

The next useful life-total work should select specific opponent/life cells for more reps from the retest table, not from the older low-sample table alone.

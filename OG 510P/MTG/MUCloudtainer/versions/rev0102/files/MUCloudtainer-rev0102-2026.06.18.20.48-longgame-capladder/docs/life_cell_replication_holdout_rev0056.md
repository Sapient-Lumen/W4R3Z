# rev0056 — life-cell replication holdout

rev0055 converted the `cf34_counter_wall` vs `pub_threat_overlord` matchup from an all-life story into two life-specific cells. rev0056 asks whether those cells survive an independent seed-disjoint holdout block.

The selected cells are the two rev0055 cumulative `life_cell_claim_candidate` rows:

- `cf34_counter_wall` vs `pub_threat_overlord`, 20 life
- `cf34_counter_wall` vs `pub_threat_overlord`, 40 life

The holdout schedule uses:

```text
life total:       cell-specific, 20 or 40
target seats:     target as p0 and target as p1
starting player:  0 and 1
reps:             24 per life/seat/start
max decisions:    900
```

This yields 96 terminal-clean holdout games per life cell, 192 games total.

The holdout is deliberately evaluated separately from the previous cumulative evidence. Combined evidence is reported, but a failed holdout cannot be rescued by old rows.

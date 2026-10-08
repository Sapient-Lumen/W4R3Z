# rev0055 life-cell claim dossier

rev0054 found that `cf34_counter_wall` versus `pub_threat_overlord` was positive overall but life-sensitive.  Averaging 20-life and 40-life games hid the more useful question:

```text
Does the target have a claim at each life total separately?
```

rev0055 decomposes the dossier into target/opponent/life cells.  It adds fresh terminal-clean repetitions for both life totals, then reports two views:

```text
current-only rev0055 cell evidence
cumulative rev0054 + rev0055 cell evidence
```

The cumulative view is intentionally labeled as cumulative.  It is not allowed to silently replace the current-only table.

## Schedule

```text
target:        cf34_counter_wall
opponent:      pub_threat_overlord
life totals:   20 and 40
target seats:  target as p0 and target as p1
starters:      starting player 0 and 1
reps:          32 per life/seat/starter
max decisions: 900
```

This produces 128 fresh games per life cell and 256 fresh games total.

## Claim hygiene

A cell is labeled `life_cell_claim_candidate` only when the cumulative target-perspective cell has enough games, no truncations, a positive mean, and a lower confidence bound above 0.5.  The current-only cells are still reported separately because they are the cleanest view of this revision's new evidence.

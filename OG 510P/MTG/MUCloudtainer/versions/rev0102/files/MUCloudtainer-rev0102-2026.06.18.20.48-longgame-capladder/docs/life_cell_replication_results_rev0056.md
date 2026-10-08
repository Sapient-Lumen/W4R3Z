# rev0056 results — holdout replication

The rev0056 holdout block replicated both life cells.

```text
games:                 192
truncations:             0
replay samples:      8 / 8 passed
C++ shadow events:  54,475
C++ skipped:             0
C++ mismatches:          0
```

Holdout-only results:

| target | opponent | life | games | holdout score | score LCB 95 | label |
|---|---|---:|---:|---:|---:|---|
| cf34_counter_wall | pub_threat_overlord | 20 | 96 | 0.78125 | 0.64264 | holdout_replicated_candidate |
| cf34_counter_wall | pub_threat_overlord | 40 | 96 | 0.83333 | 0.69472 | holdout_replicated_candidate |

Prior cumulative plus holdout:

| life | combined games | combined score | combined LCB 95 | replication label |
|---:|---:|---:|---:|---|
| 20 | 304 | 0.68092 | 0.60303 | replicated_life_cell_claim_candidate |
| 40 | 304 | 0.79934 | 0.72145 | replicated_life_cell_claim_candidate |

Interpretation: the `cf34_counter_wall` advantage over `pub_threat_overlord` now has independent holdout support at both life totals under the current agents, decks, mulligan policies, terminal-clean settings, and C++ shadow parity gates.

This is still a simulator-local claim, not a general Magic claim.

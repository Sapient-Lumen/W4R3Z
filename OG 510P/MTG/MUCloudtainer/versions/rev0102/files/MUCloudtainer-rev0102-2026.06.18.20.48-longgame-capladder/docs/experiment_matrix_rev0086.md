# rev0086 experiment matrix

| Item | Value |
|---|---:|
| New games | 0 |
| Input paired-delta rows audited | 240 |
| Primary mechanism-drift rows | 3 |
| Exploratory context mechanism-drift rows | 40 |
| Same-score mechanism-flip ledger rows | 18 |
| Overall score ties | 207 |
| Overall score + mechanism equivalents | 189 |
| Overall same-score mechanism flips | 18 |
| Overall life-to-library flips | 16 |
| Overall library-to-life flips | 2 |

## Primary mechanism-drift family

| Row | Score ties | Mechanism flips | Life → library | Library → life | p(candidate library shift) | Familywise supported |
|---|---:|---:|---:|---:|---:|---|
| Overall | 207 | 18 | 16 | 2 | 0.0006561279 | yes |
| Selected-cell holdout | 78 | 10 | 9 | 1 | 0.0107421875 | yes |
| Transfer panel | 129 | 8 | 7 | 1 | 0.0351562500 | no |

## Decision

`public_counter_life20_stabilizer` remains excluded from broad and candidate pools. rev0086 adds a stronger tie contract: score-only ties are not full equivalence when terminal mechanism differs.

# rev0085 experiment matrix

| Item | Value |
|---|---:|
| New games | 0 |
| Input game rows audited | 480 |
| Input paired-delta rows audited | 240 |
| Pair keys reconstructed | 240 |
| Complete pairs | 240 |
| Seed mismatches | 0 |
| Context mismatches | 0 |
| Primary sign-test rows | 3 |
| Exploratory context sign-test rows | 40 |
| Tie-forensics rows | 43 |

## Primary exact sign tests

| Row | Candidate better | Guard better | Ties | One-sided p(candidate worse) | Familywise negative supported |
|---|---:|---:|---:|---:|---|
| Overall | 10 | 23 | 207 | 0.0175410167 | no |
| Selected-cell holdout | 8 | 10 | 78 | 0.4072647095 | no |
| Transfer panel | 2 | 13 | 129 | 0.0036926270 | yes |

## Tie mechanism forensics

| Item | Value |
|---|---:|
| Same-score pairs | 207 |
| Same-score same-mechanism pairs | 189 |
| Same-score mechanism-flip pairs | 18 |
| Life-to-library flips | 16 |
| Library-to-life flips | 2 |

## Decision

`public_counter_life20_stabilizer` remains excluded from broad and candidate pools. The corrected reason is transfer-panel exact-sign failure plus no demonstrated candidate dominance, not a statistically confirmed selected-cell holdout failure.

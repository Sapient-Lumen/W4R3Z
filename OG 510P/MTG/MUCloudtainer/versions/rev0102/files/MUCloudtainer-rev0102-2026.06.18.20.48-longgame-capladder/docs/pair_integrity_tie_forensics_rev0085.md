# rev0085 pair-integrity and tie-forensics audit

rev0084 correctly kept `public_counter_life20_stabilizer` out of the broad counter population, but its wording was too blunt: it called the selected-cell holdout negative-transfer even though the evidence was dominated by ties and had not been passed through an exact paired sign test.

rev0085 does not run another policy panel. It audits the paired evidence already created by rev0084 and answers three risk questions:

1. Are guard/candidate pairs actually matched on seed, seat, life, starting player, size axis, and threat axis?
2. Does the negative-transfer claim survive an exact paired sign test with a primary-family correction?
3. Are score ties mechanistically equivalent, or can they hide different terminal causes?

## Pair exposure integrity

The audit checked all 480 rev0084 game rows and reconstructed 240 pair keys.

| Item | Value |
|---|---:|
| Pair keys | 240 |
| Complete guard/candidate pairs | 240 |
| Incomplete pairs | 0 |
| Duplicate-policy pairs | 0 |
| Seed mismatches | 0 |
| Context mismatches | 0 |
| Broad-pool-eligible rows | 0 |
| Candidate-pool-eligible rows | 0 |

This means the seed-paired design was implemented as intended.

## Exact paired sign tests

The primary test family has three rows: overall, selected-cell holdout, and broad transfer panel. Bonferroni-adjusted alpha is 0.0166666667.

| Primary row | Candidate better | Guard better | Ties | One-sided p(candidate worse) | Familywise supported? |
|---|---:|---:|---:|---:|---|
| Overall | 10 | 23 | 207 | 0.0175410167 | no |
| Selected-cell holdout | 8 | 10 | 78 | 0.4072647095 | no |
| Transfer panel | 2 | 13 | 129 | 0.0036926270 | yes |

The corrected interpretation is therefore narrower and stronger:

- The selected-cell holdout is point-negative, not statistically confirmed.
- The broad transfer panel does support guard superiority by exact paired sign test.
- No primary row supports candidate dominance.

The stabilizer remains quarantined, but the evidence label is now calibrated: quarantine rests on transfer-panel failure and absence of dominance, not on overstating the selected-cell holdout.

## Tie mechanism forensics

Score ties were not always mechanistically identical.

| Item | Value |
|---|---:|
| Total pairs | 240 |
| Same-score pairs | 207 |
| Same-score same-mechanism pairs | 189 |
| Same-score mechanism-flip pairs | 18 |
| Life-to-library flips | 16 |
| Library-to-life flips | 2 |

This prevents a second narrative error: a score tie between guard and candidate should not automatically be treated as identical play. Some tied outcomes reach the same score through different terminal mechanisms.

## Bottom line

rev0085 preserves the policy conclusion from rev0084—do not add `public_counter_life20_stabilizer` to broad pools—but it corrects the evidentiary claim. The candidate is not a rescue, but the holdout component alone was too weak to be used as proof of negative transfer.

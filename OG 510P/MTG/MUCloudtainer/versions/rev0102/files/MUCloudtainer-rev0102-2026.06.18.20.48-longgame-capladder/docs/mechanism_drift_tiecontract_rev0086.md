# rev0086 mechanism-drift tie contract

rev0085 showed that 18 of 207 guard/candidate score ties were not mechanistically identical. rev0086 makes that warning operational: future candidate gates must distinguish **score-only ties** from **score + terminal-mechanism equivalence**.

The input is still the rev0084 seed-paired candidate-transfer panel. No new games were run.

## Primary family

Primary family rows are overall, selected-cell holdout, and transfer panel. Bonferroni-adjusted alpha is 0.0166666667.

| Row | Pairs | Score ties | Score + mechanism equivalent | Same-score mechanism flips | Life → library | Library → life | p(candidate library shift) | Familywise supported? |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Overall | 240 | 207 | 189 | 18 | 16 | 2 | 0.0006561279 | yes |
| Selected-cell holdout | 96 | 78 | 68 | 10 | 9 | 1 | 0.0107421875 | yes |
| Transfer panel | 144 | 129 | 121 | 8 | 7 | 1 | 0.0351562500 | no |

## Interpretation

The stabilizer remains quarantined, but rev0086 tightens the reason again:

- It still does not dominate the guard on score.
- The transfer panel still supports guard superiority by exact paired sign test from rev0085.
- Among score ties, the candidate is not behaviorally equivalent to the guard.
- Same-score flips are strongly directional: 16 of 18 move from life-total termination under the guard to library-out termination under the candidate.

The selected-cell holdout is not statistically negative on score, but it does show familywise-supported mechanism drift toward library-out outcomes among ties. That makes the candidate unsuitable as a clean repair even before broad promotion is considered.

## Resulting contract

For adaptive counter candidates, a score tie is only a true tie for promotion discussion if both conditions hold:

1. candidate score equals baseline score; and
2. terminal mechanism also matches.

Score-only ties with terminal-mechanism flips must remain visible in compact evidence. They are not automatic wins, losses, or proof of dominance, but they are behavioral changes that can invalidate a narrative of equivalence.

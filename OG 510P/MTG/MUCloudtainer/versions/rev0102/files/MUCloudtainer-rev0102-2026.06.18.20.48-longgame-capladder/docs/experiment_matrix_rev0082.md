# rev0082 experiment matrix

| Input | Rows | Purpose | Result |
|---|---:|---|---|
| `rev0081_opponent_frontier_familywise.csv` | 36 | Source threat-column frontier | Complete input |
| `rev0082_counterset_rescue_envelope.csv` | 36 | Rescue status per hierarchy/threat column | 0 certified, 1 upper-bound-deficient |
| `rev0082_counterset_rescue_layer_summary.csv` | 4 | Layer rollup | Global/by-life/by-size are not upper-bound-impossible; one fine cell is |

No new games were generated in rev0082. This was intentional: before running another expensive panel, the cube needed to know whether more sampling or counter-policy invention is the better risk-reducing action.

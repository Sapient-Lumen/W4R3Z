# Field execution risk burndown — rev0331

| Risk | Prior state | rev0331 change | Remaining test |
|---|---|---|---|
| Final-readout free text leaks small cells | `FINAL-READOUT.csv` fields were copied into `MICRO-PILOT-RESULT.json` verbatim | result recorder redacts numeric/small-cell-sensitive final-readout fields and records row/field suppression coordinates | run a real cycle and confirm the receipt carries no exact small cells |
| Narrative readout becomes quoteable fake evidence | the final readout could display tiny `n`, rates, or move counts beside a polished decision | receipt points reviewers to thresholded `session_summary` and keeps final free text local/protected | owner memo must still avoid public-claim language |
| Small refactor turns into more bureaucracy | the leak could have produced a new registry/check family | existing recorder was refactored; no new schema or validator family | keep next change field-facing |
| Decision support overreaches | row 8 decision remains visible and could be overread | boundary text keeps decision local: stop, redesign, repeat narrower, or plan separate review only | real owner review must use local decision only |

## Current unblocker

Hold one real discovery conversation, complete one local owner plan, and run at most one feasibility
cycle. Do not treat a redacted receipt as learning evidence.

# Field execution risk burndown — rev0330

| Risk | Prior state | rev0330 change | Remaining test |
|---|---|---|---|
| Result receipt leaks small cells | exact counts/rates could appear in `MICRO-PILOT-RESULT.*` | result recorder masks counts/rates below the local threshold | run a real cycle and confirm exact small cells stay local |
| Tiny cycle becomes fake effect estimate | descriptive delta was always calculated when counts existed | delta is `null` when baseline/transfer rates are suppressed | owner memo must use stop/redesign language only |
| Paper cycle reaches owner review | numeric rows could be zero and still look structurally complete | required phases must have nonzero aggregate attempts | real packet still needs owner-observed work |
| Safety boilerplate blocks clean result | result recorder scanned all memo text and could flag its own warnings | recorder now scans likely entered payload, matching readiness behavior | keep warnings visible without making operators delete them |
| Control-plane growth displaces field work | each defect could have created another validator family | patched existing hot-path tools only | continue preferring deletion/refactor over new registries |

## Current unblocker

Hold one real discovery conversation. Do not use a synthetic dry run, generated readiness card, or
suppressed local receipt as evidence that the intervention works.

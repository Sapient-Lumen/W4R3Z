# CELL-089 — PTQ Scale Search in KV Wind Tunnel

Priority: **P1**
Status: **candidate**

## Cheap first run

Optimize quantization scales on calibration samples for MSE/logit/output objectives.

## Sources

SRC-0145, SRC-0001

## Baselines

- minmax
- row
- varnorm
- MSE scale
- logit scale
- output scale

## Metrics

- decode drift
- scale transfer
- top-error tail
- task score

## Stop condition

If searched scales overfit seed/regime, mark as calibration trap.

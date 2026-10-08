# CELL-088 — Joint Next-K Safe Decoding Toy

Priority: **P2**
Status: **candidate**

## Cheap first run

Synthetic languages where safe multi-token emission varies by state.

## Sources

SRC-0147, SRC-0148

## Baselines

- one-step AR
- next-K predictor
- run-length predictor
- oracle

## Metrics

- tokens/step
- error rate
- calibration
- safe length

## Stop condition

If entropy baseline predicts safe length, fold.

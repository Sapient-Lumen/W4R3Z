# CELL-083 — One-Bit SSM Scaffold Probe

Priority: **P2**
Status: **candidate**

## Cheap first run

Quantize recurrent state matrices to sign plus low-rank residual and test recall.

## Sources

SRC-0137

## Baselines

- fp32 SSM
- sign-only
- sign+rank1
- sign+rank4
- int8

## Metrics

- recall accuracy
- state error
- memory bytes
- rank needed

## Stop condition

If residual rank approaches full rank, demote.

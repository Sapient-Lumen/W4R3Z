# CELL-062 — Per-Token Mixed Precision KV Policy

Priority: P1

Status: candidate

Source IDs: SRC-0112

## Cheap first run

KV wind tunnel with token-level FP16/INT8/INT4 allocation.

## Baselines

- uniform int4
- uniform int8
- attention-mass protected
- value-norm protected
- semantic-sponsor protected

## Metrics

- decode drift
- output MSE
- bit budget
- catastrophic-loop proxy

## Stop condition

If mixed precision reduces to uniform int8 under all traps, drop policy complexity.

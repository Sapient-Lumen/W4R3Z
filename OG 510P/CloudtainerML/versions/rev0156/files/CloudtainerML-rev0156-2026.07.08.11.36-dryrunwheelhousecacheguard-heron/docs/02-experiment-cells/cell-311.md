# CELL-311 — Copy-Head Phase Transition Screen

Priority: **P0**  
Status: `coded-native-mechanistic-screen`

## Why it exists

Can tiny copy-task phase probes distinguish abrupt softmax emergence from smoother linear/annealed emergence before training a transformer?

## Cheap first run

Run REV0030_COPY_HEAD_PHASE_SMOKE.json; inspect loss, precursor, abruptness, monitor risk across samples/L/V.

## Metrics

- `score`
- `loss`
- `pool_order`
- `copy_order`
- `precursor`
- `abruptness`
- `monitor_risk`
- `compute_frac`

## Required baselines

- `softmax_head`
- `linear_attention`
- `annealed_softmax`
- `linear_then_softmax_switch`
- `entmax_smoother`

## Stop condition

Escalate to trained tiny copy model only if phase screen shows a nontrivial transition tradeoff.

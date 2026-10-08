# CELL-084 — LRKV Head-Diversity Residual Sweep

Priority: **P1**
Status: **candidate**

## Cheap first run

Train/fit shared KV plus low-rank per-head residuals on conflicting head tasks.

## Sources

SRC-0138, SRC-0139

## Baselines

- MHA
- GQA/MQA
- shared KV
- LRKV rank sweep
- Q-K=V

## Metrics

- task accuracy
- head diversity
- cache bytes
- residual rank

## Stop condition

If no conflicting task stresses shared KV, redesign task.

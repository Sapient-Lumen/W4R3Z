# CELL-072 — Token-Precision Budget Frontier

Priority: **P0**
Status: **candidate-with-runnable-probe**

## Cheap first run

Runnable scaffold exists in experiments/token_precision_frontier/token_precision_probe.py; smoke output under artifacts/probe-results/REV0007_TOKEN_PRECISION_FRONTIER_SMOKE.*.

## Sources

SRC-0001, SRC-0060, SRC-0128

## Baselines

- few fp16 tokens
- many int4 tokens
- mixed precision
- attention-protected bits
- value-protected bits

## Metrics

- output relative error
- dropped attention mass
- target retention
- retained token count
- mean bits
- byte budget

## Stop condition

If one corner dominates all tasks, collapse the frontier.

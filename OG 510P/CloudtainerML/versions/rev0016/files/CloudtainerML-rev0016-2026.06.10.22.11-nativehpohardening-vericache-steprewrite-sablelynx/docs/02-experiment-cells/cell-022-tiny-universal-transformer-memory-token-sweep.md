# CELL-022 — Tiny Universal Transformer Memory-Token Sweep

Priority: **P0**
Status: `candidate`

## Cheapest first run

Implement a single-block recurrent transformer with optional ACT later; first sweep fixed recursion depth and memory-token counts.

## Baselines

- random or identity baseline
- strong simple heuristic
- matched-budget architecture baseline

## Metrics

- accuracy/exact match
- loss/error
- memory bytes
- runtime
- failure mode count
- seed variance

## Stop condition

If no task shows memory tokens beating normal extra tokens or extra width, demote.

## Source ids

SRC-0063

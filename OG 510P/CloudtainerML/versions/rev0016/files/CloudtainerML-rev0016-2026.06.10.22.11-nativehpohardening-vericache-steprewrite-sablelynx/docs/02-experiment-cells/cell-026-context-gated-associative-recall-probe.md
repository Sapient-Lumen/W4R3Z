# CELL-026 — Context-Gated Associative Recall Probe

Priority: **P1**
Status: `candidate`

## Cheapest first run

Sweep key collision, gate dimension, memory rank, and noise; compare ungated/gated/ridge memories.

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

If context gates do not help on collision stress tests, merge with CELL-004.

## Source ids

SRC-0025, SRC-0007

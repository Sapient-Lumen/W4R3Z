# CELL-068 — KV-Fold Drift Plateau Probe

Priority: **P1**
Status: `candidate`

## Cheapest first run

Fold chunk summaries through a tiny cache recurrence for 10-500 chunks and track retrieval/drift.

## Baselines

- full context oracle
- sliding window
- running mean memory
- folded KV recurrence

## Metrics

- needle exact match
- drift norm
- cosine plateau
- rare-fact retention
- chunk-depth limit

## Stop condition

If no stable plateau appears in the simplest exact tasks, mark as pretrained-model-dependent.

## Source ids

SRC-0122

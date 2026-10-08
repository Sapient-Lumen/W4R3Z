# CELL-077 — Lookahead Sparse Indexer Probe

Priority: **P1**
Status: **candidate**

## Cheap first run

Create synthetic future-query demands and train/simple-fit a chunk indexer independent of backbone attention.

## Sources

SRC-0132

## Baselines

- reactive attention history
- recency
- lookahead index
- oracle future chunks

## Metrics

- chunk recall
- false negatives
- output error
- cache fraction

## Stop condition

If learned lookahead cannot beat reactive baselines without oracle labels, defer.

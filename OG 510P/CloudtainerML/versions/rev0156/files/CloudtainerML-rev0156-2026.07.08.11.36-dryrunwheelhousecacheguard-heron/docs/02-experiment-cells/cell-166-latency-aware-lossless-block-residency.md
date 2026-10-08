# CELL-166 — Latency-Aware Lossless Block Residency

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0165` — Latency-aware lossless block residency

## Core question

Does a cache block deserve residency because it lowers future kernel/recompute latency, not because it has high semantic score?

## Source anchors

- `SRC-0204` — Multi-Segment Attention: Enabling Efficient KV-Cache Management for Faster Large Language Model Serving (https://arxiv.org/abs/2606.02964)

## Cheap first run

No runnable probe yet; block scheduling/cost model with exact-output constraint.

## Metrics

- estimated latency
- hit rate
- recompute cost
- fragmentation penalty

## Required baselines

- LRU
- frequency
- recency
- oracle future access

## Falsifier / stop condition

If latency-aware policy reduces to hit-rate policy, demote.

## Rev0013 note

This cell was added during the native-frontier pass. C++ is preferred when the inner loop is deterministic, high-volume, and framework-free; Python remains preferred for training, plotting, and orchestration.

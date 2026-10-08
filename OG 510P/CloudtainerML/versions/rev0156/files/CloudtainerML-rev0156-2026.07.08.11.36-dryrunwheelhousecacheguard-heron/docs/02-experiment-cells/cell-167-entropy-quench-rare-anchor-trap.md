# CELL-167 — Entropy Quench Rare-Anchor Trap

Priority: **P2**  
Status: **candidate**  
Idea: `IDEA-0166` — Entropy quench as pre-cache compression

## Core question

Can token-stream compression remove enough redundancy before KV/cache machinery to change the cache problem?

## Source anchors

- `SRC-0205` — Entropy Gate: Entropy Quenching for Near-Lossless Token Compression in LLM Pipelines (https://arxiv.org/abs/2606.03739)

## Cheap first run

No runnable probe yet; token stream compression with redundant blocks and later rare-anchor queries.

## Metrics

- compression ratio
- anchor survival
- downstream answer accuracy
- false deletion rate

## Required baselines

- dedupe
- recency
- random
- oracle anchor retention

## Falsifier / stop condition

If rare anchors are frequently killed, keep only as warning note.

## Rev0013 note

This cell was added during the native-frontier pass. C++ is preferred when the inner loop is deterministic, high-volume, and framework-free; Python remains preferred for training, plotting, and orchestration.

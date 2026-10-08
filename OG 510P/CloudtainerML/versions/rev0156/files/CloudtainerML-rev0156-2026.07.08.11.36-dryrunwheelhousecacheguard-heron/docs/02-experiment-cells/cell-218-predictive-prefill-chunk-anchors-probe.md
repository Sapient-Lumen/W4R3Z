# CELL-218 — Predictive Prefill Chunk Anchors Probe

Priority: **P1**  
Status: **runnable**  
Idea: `IDEA-0217`  
Sources: SRC-0244

## Cheap first run

Run experiments/prefill_chunk_anchors/prefill_chunk_anchor_probe.cpp.

## Metrics

- target recall
- lost-middle miss
- cost
- utility

## Required baselines

- dense all chunks
- top-k no anchors
- top-k with anchors
- random chunks
- oracle chunks

## Stop condition

If anchors act only as leaks, redesign with more adversarial anchors.

# CELL-064 — Adaptive Decay Fenwick Memory

Priority: P1

Status: candidate

Source IDs: SRC-0116

## Cheap first run

Log-bucket memory with fixed, oracle, and lightweight learned decay.

## Baselines

- fixed decay
- oracle per-level decay
- recency decay
- event-boundary decay

## Metrics

- selective-copy accuracy
- associative recall
- state norm
- decay entropy

## Stop condition

If oracle decay barely beats fixed decay, do not implement learned decay.

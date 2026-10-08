# CELL-281 — STAR-KV Soft-Threshold Rank HPO

Priority: **P0**  
Status: **candidate-with-runnable-probe**

## Why this cell exists
Runnable C++ probe at experiments/starkv_soft_threshold_hpo/starkv_soft_threshold_hpo.cpp; smoke output REV0026_STARKV_SOFT_THRESHOLD_HPO_SMOKE.json.

## Metrics
- score
- loss/error
- runtime/FLOPs proxy
- memory/bytes proxy
- failure-mode fields
- winner counts

## Stop condition
If static uniform rank dominates after tail + latency + bytes normalization, demote adaptive-rank enthusiasm.

## Rev0026 focus
Performance-core / tiny architecture-surprise lane. Security/trust material is a bounded side wing, not the project center.

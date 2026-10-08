# CELL-047 — Low-Rank Head-Diversity Sweep

Priority: P1  
Status: candidate

## Cheap first run

Shared full-rank KV + low-rank head residuals on multi-relation recall.

## Metrics

accuracy/exact match, loss/error, memory bytes, runtime, failure mode count, seed variance

## Stop condition

If rank sweep has no boundary, make relation heads more conflicting.

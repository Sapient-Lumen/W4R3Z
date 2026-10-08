# CELL-222 — Trustworthy Memory Search Filter

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0221`  
Sources: SRC-0248, SRC-0199, SRC-0200

## Cheap first run

Extend memory provenance phase with typed memory objects and search-stage trust filters.

## Metrics

- sycophancy rate
- cross-domain leakage
- correction retrieval
- objective answer utility

## Required baselines

- flat vector ranking
- typed object ranking
- provenance filter
- oracle filter

## Stop condition

If typed objects do not reduce failure tails, focus on write-time filters.

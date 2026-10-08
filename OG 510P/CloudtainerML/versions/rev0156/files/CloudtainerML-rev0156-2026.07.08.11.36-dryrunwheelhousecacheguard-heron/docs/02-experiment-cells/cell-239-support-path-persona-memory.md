# CELL-239 — Support-Path Persona Memory

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0238`  
Sources: SRC-0262

## Cheap first run

Simulate leaf evidence, mid-level patterns, root claims, and query-conditioned retrieval depth.

## Metrics

- unsupported_claim_rate
- support_path_recall
- over_retrieval_cost
- conflict_resolution_rate

## Required baselines

- flat_facts
- source_weighted
- three_level_tree
- oracle_support_path

## Stop condition

If hierarchy adds no benefit over provenance scoring, merge with CELL-237.

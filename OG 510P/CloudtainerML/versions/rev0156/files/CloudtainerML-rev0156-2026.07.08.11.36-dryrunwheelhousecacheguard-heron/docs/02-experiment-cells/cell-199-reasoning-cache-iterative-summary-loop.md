# CELL-199 — Reasoning Cache Iterative Summary Loop

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0198`  
Sources: SRC-0232

## Cheap first run

No runnable probe yet; iterative response plus summary on toy search/proof tasks.

## Metrics

- horizon extrapolation
- summary drift
- final success
- token budget

## Required baselines

- plain chain
- periodic summary
- learned summary update
- oracle state

## Stop condition

If summary loops amplify early mistakes, connect to verifier guard before training.

# CELL-203 — FlowTrace Reasoning Credit Probe

Priority: **P0**  
Status: **implemented**  
Idea: `IDEA-0203`  
Sources: SRC-0234

## Cheap first run

Run C++ reasoning-DAG flow credit against local attention and recency under bridge/decoy regimes.

## Metrics

- precision
- recall
- F1
- noise credit

## Required baselines

- uniform
- recency
- local attention mass
- max path
- flowtrace toy
- oracle gold

## Stop condition

If local attention mass wins in all regimes, demote flow to analysis-only.

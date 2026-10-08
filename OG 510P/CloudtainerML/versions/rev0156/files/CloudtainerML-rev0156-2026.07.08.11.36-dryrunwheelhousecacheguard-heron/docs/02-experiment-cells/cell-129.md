# CELL-129 — Head-Aware KV Object Probe

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0128`  
Sources: SRC-0188

## Cheap first run

Simulate heads with local/global/reasoning roles and budgets.

## Metrics

- retained mass
- per-head waste
- quality per byte

## Required baselines

- uniform budget
- head role budget
- oracle head budget

## Stop condition

If uniform budget matches head-aware under heterogeneous roles, demote.

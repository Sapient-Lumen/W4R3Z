# CELL-204 — Hasse Mask Frontier Probe

Priority: **P1**  
Status: **implemented**  
Idea: `IDEA-0204`  
Sources: SRC-0235

## Cheap first run

Run C++ partial-order mask toy across causal/block/butterfly/prefix tasks.

## Metrics

- coverage
- leakage
- redundancy
- train-infer gap
- utility

## Required baselines

- full bidirectional
- causal
- local window
- task exact
- block two-stream toy
- butterfly toy

## Stop condition

If task-exact masks dominate with no reusable insight, keep only as mask-design docs.

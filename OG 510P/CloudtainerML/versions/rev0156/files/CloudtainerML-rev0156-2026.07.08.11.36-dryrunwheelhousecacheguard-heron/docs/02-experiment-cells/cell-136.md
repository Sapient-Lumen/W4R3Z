# CELL-136 — Sparse Reuse vs Shared Routing Compare

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0135`  
Sources: SRC-0210, SRC-0093

## Cheap first run

Compare segment-level correction and shared token routing on same support sets.

## Metrics

- support recall
- correction cost
- reuse error

## Required baselines

- shared token routing
- segment sparse recompute
- oracle support

## Stop condition

If failure modes are disjoint, keep lanes separate.

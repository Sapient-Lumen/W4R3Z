# CELL-287 — MPI Router Alignment Wind Tunnel

Priority: **P0**  
Status: **runnable-native**

## Why this cell exists
Run manifold_power_router.cpp and score assignment, alignment, imbalance, rare-domain miss, and stability loss.

## Question
Linked idea: `IDEA-0285`.

## Sources
- `SRC-0307`
- `SRC-0302`

## Metrics
- top1_assignment
- router_expert_alignment
- imbalance
- tail_miss
- score

## Required baselines
- random router
- centroid router
- load-balanced router
- oracle router

## Stop condition
Demote if MPI wins only dominant-principal-direction regimes and fails load/rare/drift traps.

## Rev0027 note
Performance-first lane. Security/trust side-wing material is not driving this cell.

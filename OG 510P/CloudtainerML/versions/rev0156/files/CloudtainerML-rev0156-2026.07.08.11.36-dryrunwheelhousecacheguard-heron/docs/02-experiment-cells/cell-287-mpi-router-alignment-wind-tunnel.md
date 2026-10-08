# CELL-287 — MPI Router Alignment Wind Tunnel

Priority: **P0**  
Status: **runnable-native**

## Cheap first run
Run manifold_power_router.cpp and score assignment, alignment, imbalance, rare-domain miss, and stability loss.

## Linked idea
`IDEA-0285`

## Sources
- `SRC-0307`
- `SRC-0302`

## Metrics
- top1_assignment
- router_expert_alignment
- imbalance
- tail_miss
- score

## Stop condition
Demote if MPI wins only dominant-principal-direction regimes and fails load/rare/drift traps.

## Rev0027 note
Performance-first cell; security/trust side-wing is not driving this priority.

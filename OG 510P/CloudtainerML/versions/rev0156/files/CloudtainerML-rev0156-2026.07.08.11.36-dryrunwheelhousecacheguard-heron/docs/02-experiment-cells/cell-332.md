# CELL-332 — Boundary Reachability Repair Wind Tunnel

Priority: **P0**  
Status: **native-probe-added**

## Question

Can local sparse masks fail exact-copy tasks because the source is graph-unreachable despite being nearby?

## Cheap first run

Compute exact graph reachability for fixed block, sliding-window, centered bridge, PBB, SE-Bridge, periodic full, and dense oracle masks across boundary offsets and distances.

## Metrics

- `reachable`
- `exact_miss_counts`
- `boundary_cliff`
- `phase_risk`
- `cost`
- `regret`
- `score`

## Required baselines

- `fixed_block`
- `sliding_window`
- `dense_full_oracle`

## Stop condition

Keep as a promotion guard if boundary phase changes winners under equal-cost exact-copy regimes.

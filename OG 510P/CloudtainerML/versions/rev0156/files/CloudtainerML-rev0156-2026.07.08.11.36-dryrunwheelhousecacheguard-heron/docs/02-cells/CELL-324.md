# CELL-324 — Directional Suppression Router Wind Tunnel

Priority: **P0**  
Status: `native-probe-added`  
Idea: `IDEA-0322`  
Sources: SRC-0342

This native wind tunnel scores directional suppression as a coordination mechanism. The useful failure guard is ablation fragility: if disabling the coordinator hurts more than disabling one head, the mechanism may be qualitatively different from ordinary head capacity.

## Cheap first run

Compile/run experiments/directional_suppression_router/directional_suppression_router.cpp; test shared router vs independent heads and fixed pruners.

## Metrics

- `recall`
- `leakage`
- `coordination`
- `ablation_fragility`
- `rare_miss`
- `score`

## Stop condition

Keep only if coordination wins survive rare-direction and low-overhead regimes.

# CELL-276 — PolyHard Routing Optimizer Toy

- priority: P1
- status: implemented-native-rev0025
- idea: IDEA-0275
- sources: SRC-0297

## Cheap first run

Screen forward-only PolyStep-like optimizer against hard routers, surrogate gradients, ES, and hillclimb.

## Metrics

- best_loss
- stability
- query_cost
- score

## Required baselines

- random_search
- evolution_strategy
- straight_through_surrogate
- coordinate_hillclimb
- polystep_like_subspace
- oracle_forward_optimizer

## Stop condition

Keep P1 unless hard/discrete regimes show a clean non-oracle advantage.

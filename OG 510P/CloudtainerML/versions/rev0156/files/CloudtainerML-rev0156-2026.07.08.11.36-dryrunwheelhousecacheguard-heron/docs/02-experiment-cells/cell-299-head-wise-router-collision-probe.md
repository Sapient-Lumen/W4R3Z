# CELL-299 — Head-wise Router Collision Probe

Priority: **P1**  
Status: `native-probe-added`

## Cheap first run
experiments/headwise_router_collision/headwise_router_collision.cpp compares concat, load-aux, head-wise, factorized, and oracle routing under composition collisions.

## Metrics
- score
- route_collision
- old_loss_proxy
- load_violation
- wall_proxy

## Required baselines
- concat_router
- concat_plus_load_aux
- headwise_router
- factorized_product_router

## Stop condition
Promote only if a tiny trained MoE shows collision metrics predict performance debt.

# CELL-336 — Tiny Boundary Reachability Training

Priority: **P0**  
Status: **trained-probe-added**

## Question

Does the boundary reachability cliff survive when a tiny attention model actually learns a copy task instead of only being scored by graph reachability?

## Cheap first run

Run experiments/tiny_boundary_reach_training/tiny_boundary_reach_train.py and compare fixed-block, sliding, bridge, periodic, and full causal masks on boundary-copy accuracy.

## Metrics

- `final_acc`
- `reachable_fraction`
- `source_attention_mass_by_target_pos`
- `acc_by_target_pos`
- `target_miss`

## Required baselines

- `fixed_block`
- `sliding_window`
- `full_causal_oracle`

## Stop condition

Promote only if trained accuracy respects graph reachability and exact-copy guards separate masks clearly.

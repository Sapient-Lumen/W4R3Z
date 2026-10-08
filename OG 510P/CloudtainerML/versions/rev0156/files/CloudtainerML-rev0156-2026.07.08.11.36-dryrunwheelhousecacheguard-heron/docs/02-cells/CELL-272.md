# CELL-272 — DOT-MoE Transport Assignment Phase Probe

- priority: P0
- status: implemented-native-rev0025
- idea: IDEA-0271
- sources: SRC-0294

## Cheap first run

Compare assignment/routing methods under active-parameter and capacity constraints.

## Metrics

- retention
- route_miss
- imbalance
- wall_proxy
- score

## Required baselines

- random_split_moe
- kmeans_neuron_cluster
- dot_sinkhorn_balanced
- dot_plus_joint_router
- oracle_assignment

## Stop condition

Promote if DOT-style methods win outside hand-constructed clean clusters.

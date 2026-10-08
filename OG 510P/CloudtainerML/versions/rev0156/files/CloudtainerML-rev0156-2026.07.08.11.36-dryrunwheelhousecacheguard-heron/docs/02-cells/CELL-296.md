# CELL-296 — ProbMoE Subset Exploration Probe

Priority: **P1**  
Status: `native-probe-added`

## Why this exists
experiments/probmoe_subset_exploration/probmoe_subset_exploration.cpp sweeps k-subsets across rare/complementary/noisy/load regimes.

## Metrics
- score
- expected_loss
- rare_miss
- subset_regret
- load_violation
- exploration_cost

## Required baselines
- deterministic_topk
- load_balanced_topk
- dot_assignment_router
- oracle_subset

## Stop condition
Keep P1 unless it beats deterministic/load-balanced routers under non-rare regimes too.

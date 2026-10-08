# CELL-352 — Annealed Hard Bridge Gate Training

Priority: **P0**  
Status: trained-probe-added

## Question

Can annealed sparse gate training turn a soft bridge ranking into a hard deployable sparse program without relying on post-hoc probability thresholds?

## Cheap first run

Run experiments/tiny_bridge_annealed_hard/tiny_bridge_annealed_hard_train.py. Compare soft gate accuracy, hard top-k deployment, threshold deployment, and optional hard fine-tune after annealed sparse training.

## Metrics

- `promotion_score`
- `soft_final_acc`
- `hard_topk_acc`
- `hard_threshold_0p5_acc`
- `hard_threshold_0p2_acc`
- `deployment_gap_soft_to_hard_topk`
- `deployment_gap_topk_to_threshold_0p5`
- `topk_edge_f1`
- `edge_f1_threshold_0p5`
- `hard_topk_target_miss`
- `active_edge_count_threshold_0p2`

## Required baselines

- `dense_candidate_trained`
- `fixed_block_same_weights`
- `hard_finetune_from_best_annealed_topk`
- `oracle_true_bridge_finetune`

## Stop condition

Promote only if hard top-k or hard threshold deploys exact-copy behavior with high true-edge F1; soft accuracy alone is insufficient.

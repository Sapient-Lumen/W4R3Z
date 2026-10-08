# CELL-349 — Post-Training Sparse Bridge Compilation

Priority: **P0**  
Status: trained-probe-added

## Question

Can a dense candidate-bridge model be sparsified after training into a deployable hard sparse mask without losing exact-copy performance?

## Cheap first run

Run experiments/tiny_bridge_posttrain_sparsify/tiny_bridge_posttrain_sparsify.py. Compare dense candidate training, fixed block same weights, post-trained soft gates, hard top-k, hard threshold, and hard fine-tuned top-k masks.

## Metrics

- `promotion_score`
- `soft_final_acc`
- `hard_topk_acc`
- `hard_threshold_0p5_acc`
- `deployment_gap_soft_to_hard_topk`
- `topk_edge_f1`
- `edge_f1_threshold_0p5`
- `active_edge_count_threshold_0p2`
- `target_miss`

## Stop condition

Promote only if a hard sparse compiler preserves exact copy and recovers true bridge edges; soft gate success by itself remains insufficient.

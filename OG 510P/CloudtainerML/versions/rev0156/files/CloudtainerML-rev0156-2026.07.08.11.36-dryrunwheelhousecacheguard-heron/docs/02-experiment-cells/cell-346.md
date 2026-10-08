# CELL-346 — Learned Boundary Repair Mask

Priority: **P0**  
Status: **trained-probe-added**

## Question

Can a tiny model discover the minimal cross-boundary relay edges from an overcomplete candidate set, rather than being handed the boundary repair program?

## Cheap first run

Run experiments/tiny_learned_boundary_mask/tiny_learned_boundary_mask.py. Compare fixed block, all-candidate edge oracle, and learned candidate gates under sparsity penalties.

## Metrics

- `promotion_score`
- `final_acc`
- `target_miss`
- `topk_edge_f1`
- `topk_depth_reachable_fraction`
- `true_false_prob_gap`
- `active_edge_count`

## Required baselines

- `fixed_block`
- `all_candidate_edges`
- `learned_candidate_gate`

## Stop condition

Promote only if exact copy accuracy coexists with top-k recovery of true boundary bridge edges; soft accuracy without edge recovery is not enough.

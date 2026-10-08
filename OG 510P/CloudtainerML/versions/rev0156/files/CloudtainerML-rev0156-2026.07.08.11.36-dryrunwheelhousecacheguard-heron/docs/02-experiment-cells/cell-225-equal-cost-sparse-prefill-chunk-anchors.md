# CELL-225 — Equal-Cost Sparse Prefill Chunk Anchors

Priority: **P0**  
Status: **implemented-native-rev0019**  
Idea: `IDEA-0224`  
Sources: SRC-0246, SRC-0207

## Cheap first run

Run experiments/prefill_anchor_equalcost/prefill_anchor_equalcost_probe.cpp and require dense/sparse methods to obey the same processed-token budget.

## Metrics

- mean_recall
- mean_false_hit_rate
- mean_cost_tokens
- mean_utility

## Required baselines

- dense_equal_cost
- topk_semantic
- topk_anchor
- anchor_then_expand
- middle_repair
- distractor_aware
- oracle_chunks

## Stop condition

If anchors only help in oracle-friendly regimes, demote sparse chunk anchors below forecast/query routing.

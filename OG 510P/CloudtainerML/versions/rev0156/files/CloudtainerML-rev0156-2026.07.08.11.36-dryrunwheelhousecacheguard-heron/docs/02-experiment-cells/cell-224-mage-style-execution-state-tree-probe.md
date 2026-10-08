# CELL-224 — Mage-Style Execution State Tree Probe

Priority: **P0**  
Status: **implemented-native-rev0019**  
Idea: `IDEA-0223`  
Sources: SRC-0251

## Cheap first run

Run experiments/execution_state_tree/mage_state_tree_probe.cpp and compare active path/tree policies against semantic retrieval under branch error and long-dependency regimes.

## Metrics

- mean_success
- mean_state_integrity
- mean_error_contamination
- mean_cost
- mean_utility

## Required baselines

- full_context
- semantic_retrieval
- flat_summary
- active_path_tree
- tree_maintain_revise
- oracle_active_path

## Stop condition

If semantic retrieval wins under error branching after contamination penalties, revisit the regime design before escalating.

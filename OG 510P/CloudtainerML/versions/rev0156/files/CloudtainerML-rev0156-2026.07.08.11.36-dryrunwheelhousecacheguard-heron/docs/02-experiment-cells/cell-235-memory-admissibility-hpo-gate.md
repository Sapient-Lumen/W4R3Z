# CELL-235 — Memory Admissibility HPO Gate

Priority: **P0**  
Status: **implemented-native-rev0020**  
Idea: `IDEA-0234`  
Sources: SRC-0248, SRC-0249, SRC-0261

## Cheap first run

Run experiments/memory_admissibility_hpo/memory_admissibility_hpo.cpp and inspect attack vs false reject tradeoffs.

## Metrics

- attack_success_rate
- valid_recall_rate
- false_reject_rate
- mean_poisoned_read_fraction
- catastrophic_contract_failure_rate
- mean_utility

## Required baselines

- similarity_only
- static_memgate
- admissibility_contract
- hpo_threshold_gate
- conservative_contract
- oracle_boundary

## Stop condition

If non-oracle gates only win by rejecting useful memories, flag as safety-cost frontier rather than algorithmic win.

# CELL-236 — Execution-State Verification and Revise Boundaries

Priority: **P0**  
Status: **implemented-native-rev0020**  
Idea: `IDEA-0235`  
Sources: SRC-0251, SRC-0266

## Cheap first run

Run experiments/execution_state_verify/execution_state_verify_probe.cpp across branch-error and false-success regimes.

## Metrics

- mean_success
- mean_state_integrity
- mean_error_contamination
- mean_recovery
- catastrophic_state_failure_rate
- mean_utility

## Required baselines

- semantic_retrieval
- full_trace
- active_path_tree
- maintain_verify
- revise_on_failure
- verify_revise_hpo
- oracle_execution_state

## Stop condition

If verify/revise only beats semantic retrieval by excess cost, harden equal-cost variants next.

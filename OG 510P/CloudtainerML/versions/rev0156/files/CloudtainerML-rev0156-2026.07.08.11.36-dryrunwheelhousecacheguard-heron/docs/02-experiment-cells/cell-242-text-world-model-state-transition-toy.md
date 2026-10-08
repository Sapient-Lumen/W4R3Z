# CELL-242 — Text World Model State Transition Toy

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0241`  
Sources: SRC-0268

## Cheap first run

Build a tiny textual state machine and compare reactive, retrieval, and transition-model validators.

## Metrics

- transition_accuracy
- impossible_state_detection
- planning_success
- false_repair_rate

## Required baselines

- reactive
- retrieval_only
- symbolic_transition
- tiny_learned_transition

## Stop condition

If transition models memorize only state IDs, postpone.

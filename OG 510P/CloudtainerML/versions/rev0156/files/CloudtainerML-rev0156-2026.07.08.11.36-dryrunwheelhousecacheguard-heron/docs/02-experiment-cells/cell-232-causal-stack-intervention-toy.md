# CELL-232 — Causal Stack Intervention Toy

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0231`  
Sources: SRC-0259

## Cheap first run

Train or hand-build counter-language models and test causal edits to inferred stack directions.

## Metrics

- intervention_effect
- counter_accuracy
- false_intervention_rate
- hidden_state_separability

## Required baselines

- accuracy_only
- linear_probe
- causal_direction_edit
- oracle_stack_edit

## Stop condition

If edits do not predictably change outputs, keep as diagnostic only.

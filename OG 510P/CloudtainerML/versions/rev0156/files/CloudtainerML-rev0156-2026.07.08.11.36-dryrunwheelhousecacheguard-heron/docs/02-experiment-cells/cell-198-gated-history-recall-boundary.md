# CELL-198 — Gated History Recall Boundary

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0197`  
Sources: SRC-0231

## Cheap first run

No runnable probe yet; mix Markovian and non-Markovian episodes and train/fit a gate.

## Metrics

- success
- history-use rate
- false recall activations
- distribution-shift penalty

## Required baselines

- no_history
- always_history
- heuristic_gate
- learned_gate
- oracle_gate

## Stop condition

If heuristic gate matches learned gate, keep the simpler policy.

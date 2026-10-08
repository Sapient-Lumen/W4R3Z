# CELL-214 — Safety Tail Phase HPO Probe

Priority: **P0**  
Status: **runnable**  
Idea: `IDEA-0212`  
Sources: SRC-0127, SRC-0195

## Cheap first run

Run experiments/safety_tail_phase/safety_tail_phase.cpp.

## Metrics

- risk_found_rate
- best_tail
- hidden_risk
- search cost
- utility

## Required baselines

- grid
- random
- domain_prior
- centaur_state_prior

## Stop condition

If grid dominates at equal cost, use HPO only on more expensive probes.

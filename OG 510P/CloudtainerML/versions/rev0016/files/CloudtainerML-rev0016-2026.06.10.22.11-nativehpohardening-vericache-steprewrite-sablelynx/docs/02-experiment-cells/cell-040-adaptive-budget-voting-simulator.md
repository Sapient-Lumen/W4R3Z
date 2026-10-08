# CELL-040 — Adaptive Budget Voting Simulator

Priority: **P1**  
Status: `candidate`  
Idea: `IDEA-0040`  
Sources: SRC-0088, SRC-0089

## Question

Can a query-sampling/voting policy identify when a request needs more cache or different retention before the final query arrives?

## Cheap first run

Use generated future query samples to choose K/policy on dormant and region-wipeout tasks.

## Baselines

- random or identity baseline
- strong simple heuristic
- matched-budget architecture baseline

## Metrics

- accuracy/exact match
- loss/error
- memory bytes
- runtime
- failure mode count
- seed variance
- budget_cost
- hardcase_recall

## Stop condition

If adaptive policy always chooses max budget, add stronger cost regularization.

# CELL-117: Vertical CoT Compute Frontier

Priority: **P1**
Idea: `IDEA-0116`
Status: **candidate**

## Cheap first run

Tiny graph/logic tasks; sweep recurrence steps, fixed depth, width, and scratchpad length.

## Required baselines

- fixed transformer
- explicit scratchpad
- shared recurrent block
- oracle algorithm

## Metrics

- accuracy vs depth
- compute steps
- generalization gap

## Stop / demote condition

If recurrence steps do not make a clean frontier, demote.

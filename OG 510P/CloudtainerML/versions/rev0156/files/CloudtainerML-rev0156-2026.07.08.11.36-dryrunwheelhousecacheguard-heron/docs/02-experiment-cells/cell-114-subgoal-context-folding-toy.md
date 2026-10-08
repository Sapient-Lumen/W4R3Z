# CELL-114: Subgoal Context Folding Toy

Priority: **P1**
Idea: `IDEA-0113`
Status: **candidate**

## Cheap first run

Generate subgoal trajectories with known hidden state; fold completed subgoals and query later.

## Required baselines

- full history
- last-k
- flat summary
- subgoal fold

## Metrics

- state preservation
- answer accuracy
- tokens retained

## Stop / demote condition

If folding loses critical hidden state across simple subtasks, refine summary schema.

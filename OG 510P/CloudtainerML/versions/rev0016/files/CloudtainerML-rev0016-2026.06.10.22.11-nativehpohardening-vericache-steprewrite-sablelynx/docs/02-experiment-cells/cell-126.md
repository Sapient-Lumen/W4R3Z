# CELL-126 — Pretraining Exposure Grokking Toy

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0125`  
Sources: SRC-0183

## Cheap first run

Synthetic grammar next-token task with critical phrase exposure split.

## Metrics

- delayed generalization step
- proxy train loss
- proxy validation accuracy

## Required baselines

- standard split
- critical exposure split
- random exposure split

## Stop condition

If no delayed transition appears, lower priority.

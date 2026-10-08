# CELL-098 — Low-Rank Decay Grokking

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0098`  
Sources: SRC-0161

## Cheap first run

Run modular arithmetic with L2 vs low-rank decay.

## Baselines

- L2
- none
- low-rank decay
- rank clipping

## Metrics

- grokking_step
- test_acc
- QK_effective_rank
- loss_delay

## Stop condition

If no grokking under CPU budget, use smaller known task.

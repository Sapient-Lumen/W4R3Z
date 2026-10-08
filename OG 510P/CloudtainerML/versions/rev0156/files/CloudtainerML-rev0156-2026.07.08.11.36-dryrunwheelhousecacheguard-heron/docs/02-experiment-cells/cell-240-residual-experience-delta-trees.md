# CELL-240 — Residual Experience Delta Trees

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0239`  
Sources: SRC-0264

## Cheap first run

Compare append-only traces, merge summaries, and residual-delta trees over near-repeat tasks.

## Metrics

- rare_difference_recall
- compression_ratio
- reuse_success
- negative_transfer_rate

## Required baselines

- append_only
- merge_summary
- delta_tree
- oracle_task_cluster

## Stop condition

If rare differences vanish, use this as a red-team regime for experience memory.

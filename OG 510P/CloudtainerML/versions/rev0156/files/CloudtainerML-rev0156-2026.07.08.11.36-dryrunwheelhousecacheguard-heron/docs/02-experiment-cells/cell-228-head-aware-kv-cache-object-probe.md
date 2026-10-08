# CELL-228 — Head-Aware KV Cache Object Probe

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0227`  
Sources: SRC-0254

## Cheap first run

Simulate heads with local, global, sink, safety, and outlier roles; compare monolithic token budgets with head-aware budgets.

## Metrics

- mean_error
- tail_error
- head_starvation_rate
- memory_cost

## Required baselines

- monolithic_topk
- uniform_per_head
- head_class_budget
- oracle_head_budget

## Stop condition

If head-aware wins only with leaked oracle role labels, keep it as systems note.

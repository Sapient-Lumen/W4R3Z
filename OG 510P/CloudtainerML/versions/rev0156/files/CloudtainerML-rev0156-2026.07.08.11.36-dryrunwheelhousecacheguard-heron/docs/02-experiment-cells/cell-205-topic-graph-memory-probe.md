# CELL-205 — Topic-Graph Memory Probe

Priority: **P0**  
Status: **implemented**  
Idea: `IDEA-0205`  
Sources: SRC-0172, SRC-0236

## Cheap first run

Run C++ streaming fact/revision memory toy comparing flat/topic/temporal graph/non-destructive graph.

## Metrics

- accuracy
- stale error
- evidence count
- harmful overwrite
- utility

## Required baselines

- flat recency
- flat confidence
- topic document
- temporal graph
- non-destructive graph
- oracle latest valid

## Stop condition

If topic docs always dominate and graph metadata never helps, simplify agent memory lane.

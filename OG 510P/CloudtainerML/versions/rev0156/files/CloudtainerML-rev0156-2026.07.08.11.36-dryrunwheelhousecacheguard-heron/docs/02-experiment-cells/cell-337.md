# CELL-337 — Sparse Attention Program Schema Wind Tunnel

Priority: **P0**  
Status: **native-probe-added**

## Question

Can block, sliding, bridge, periodic, and anchor sparse masks be compared as small reachability/cost programs with common guard fields?

## Cheap first run

Run experiments/sparse_attention_program_schema/sparse_attention_program_schema.cpp and tools/sparse_program_report.py.

## Metrics

- `direct`
- `depth_reach`
- `target_miss`
- `cost_frac`
- `score`

## Required baselines

- `fixed_block`
- `sliding_window`
- `dense_causal`

## Stop condition

Keep if common program fields explain at least one priority/audit decision.

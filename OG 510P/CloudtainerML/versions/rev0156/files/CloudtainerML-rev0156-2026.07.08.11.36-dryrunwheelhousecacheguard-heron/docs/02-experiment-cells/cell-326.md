# CELL-326 — Contribution Weight Geometry Guard

Priority: **P0**  
Status: `native-probe-added`  
Idea: `IDEA-0324`  
Sources: SRC-0344, SRC-0347

This guard turns attention attribution into value geometry. Attention mass alone can preserve high-score tokens while losing high-magnitude aligned or cancellation-sensitive values. The probe records output_error, tail_miss, and cancel_error.

## Cheap first run

Compile/run experiments/contribution_weight_geometry/contribution_weight_geometry.cpp; compare attention mass against contribution-style geometry.

## Metrics

- `kept_support`
- `output_error`
- `tail_miss`
- `cancel_error`
- `regret`
- `score`

## Stop condition

Make contribution fields mandatory only if they expose errors attention mass misses.

# CELL-233 — Trajectory Geometry Monitor

Priority: **P2**  
Status: **candidate**  
Idea: `IDEA-0232`  
Sources: SRC-0258

## Cheap first run

Add layer/step trajectory metrics to one tiny trained-model run and compare against loss changes.

## Metrics

- trajectory_length
- curvature
- anisotropy
- phase_change_lead_time

## Required baselines

- loss_curve
- accuracy_curve
- trajectory_metrics

## Stop condition

If metrics do not anticipate any regime shift, drop.

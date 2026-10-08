# CELL-194 — Periodic Step-Boundary Cache Rewrite Probe

Priority: **P0**  
Status: **runnable_native_probe**  
Idea: `IDEA-0193`  
Sources: SRC-0227

## Cheap first run

Run experiments/periodic_cache_rewrite/step_rewrite_probe.cpp; native audit emits REV0019_PERIODIC_CACHE_REWRITE_SMOKE.json.

## Metrics

- mean utility
- needed fact retention
- rewrite cost
- chain success

## Required baselines

- continuous_eviction
- fixed_periodic_rewrite
- step_boundary_rewrite
- attention_reconsolidate
- oracle_step_rewrite

## Stop condition

If step boundaries do not improve needed-fact retention under noisy delimiters, move to learned event detectors.

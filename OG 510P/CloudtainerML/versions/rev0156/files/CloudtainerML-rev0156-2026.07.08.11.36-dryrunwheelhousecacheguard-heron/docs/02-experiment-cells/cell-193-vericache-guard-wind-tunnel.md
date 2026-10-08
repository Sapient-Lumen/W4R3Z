# CELL-193 — VeriCache Guard Wind Tunnel

Priority: **P0**  
Status: **runnable_native_probe**  
Idea: `IDEA-0192`  
Sources: SRC-0228

## Cheap first run

Run experiments/vericache_guard/vericache_guard_probe.cpp; native audit emits REV0019_VERICACHE_GUARD_SMOKE.json.

## Metrics

- mean utility
- catastrophic divergence rate
- recompute fraction
- accuracy

## Required baselines

- full_kv
- lossy_no_guard
- periodic_refresh
- margin_guard
- drift_guard
- vericache_toy_guard
- oracle_risk_guard

## Stop condition

If verifier recompute fraction approaches full cache cost or misses catastrophic sites, redesign risk signal.

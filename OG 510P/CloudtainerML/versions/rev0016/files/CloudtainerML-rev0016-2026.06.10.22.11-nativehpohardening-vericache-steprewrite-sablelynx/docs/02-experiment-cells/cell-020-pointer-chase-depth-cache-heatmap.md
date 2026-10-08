# CELL-020 — Pointer-Chase Depth/Cache Heatmap

Priority: **P0**
Status: `candidate`

## Cheapest first run

Runnable side-probe exists in experiments/depth_value_mixing/depth_value_mixing_probe.py; smoke output under artifacts/probe-results/REV0005_DEPTH_VALUE_MIXING_SMOKE.json.

## Baselines

- random or identity baseline
- strong simple heuristic
- matched-budget architecture baseline

## Metrics

- accuracy/exact match
- loss/error
- memory bytes
- runtime
- failure mode count
- seed variance

## Stop condition

If no sharp memory/depth boundary appears, keep only as a diagnostic task.

## Source ids

SRC-0062, SRC-0023, SRC-0064, SRC-0065

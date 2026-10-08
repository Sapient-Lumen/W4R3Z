# CELL-075 — Reasoning Wave Budget Allocation Probe

Priority: **P0**
Status: **candidate-with-runnable-probe**

## Cheap first run

Runnable scaffold exists in experiments/reasoning_wave_budget/reasoning_wave_probe.py; smoke output under artifacts/probe-results/REV0007_REASONING_WAVE_BUDGET_SMOKE.*.

## Sources

SRC-0130

## Baselines

- uniform
- pyramid decreasing
- pyramid increasing
- static wave
- online head
- online layer
- oracle

## Metrics

- success proxy
- critical starvation
- layer starvation
- preserved mass
- allocation entropy

## Stop condition

If online-only or uniform dominates all demand generators, demote static layer-wave calibration.

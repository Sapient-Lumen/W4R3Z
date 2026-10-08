# CELL-247 — Gated Subspace Inference Probe

Priority: **P0**  
Status: **candidate-with-runnable-native-probe**

## Cheap first run

Runnable C++ probe exists at experiments/gated_subspace_inference/gated_subspace_probe.cpp; smoke output REV0022_GATED_SUBSPACE_PROBE_SMOKE.json.

## Metrics

- quality_loss
- top1_flip_rate
- cost_ratio
- score
- residual_corrections

## Required baselines

- full_linear
- subspace_only
- residual_norm_gate
- oracle_error_gate

## Stop condition

If non-oracle gates cannot beat full linear under any bandwidth/cost setting, postpone until a learned gate is available.

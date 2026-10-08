# CELL-248 — Exact/Linear Attention Dilution Probe

Priority: **P0**  
Status: **candidate-with-runnable-native-probe**

## Cheap first run

Runnable C++ probe exists at experiments/exact_linear_attention_dilution/ela_dilution_probe.cpp; smoke output REV0022_ELA_DILUTION_PROBE_SMOKE.json.

## Metrics

- target_mass
- output_error
- cost_ratio
- score

## Required baselines

- softmax_full
- relu_linear_kernel
- positive distance kernel
- sparse_lowrank_mix
- exact_kernel_oracle

## Stop condition

If target-mass dilution is unavoidable for cheap kernels, only escalate kernel variants with a credible anti-dilution repair.

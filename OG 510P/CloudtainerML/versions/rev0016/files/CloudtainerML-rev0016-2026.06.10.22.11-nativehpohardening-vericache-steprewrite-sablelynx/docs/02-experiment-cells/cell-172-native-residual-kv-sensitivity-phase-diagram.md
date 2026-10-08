# CELL-172: Native Residual/KV Sensitivity Phase Diagram

Priority: P0

Status: runnable

Idea: IDEA-0171

Source: SRC-0201

Cheap first run: experiments/native_residual_kv_sensitivity/residual_kv_sensitivity.cpp emits REV0014_RESIDUAL_KV_SENSITIVITY_SMOKE.json.

Metrics:
- winner counts by regime
- score
- memory MB
- error risk

Baselines:
- full KV
- window KV
- residual checkpoints
- hybrid recent KV + far residual

Stop condition: If residual wins all regimes after sensitivity, rebalance constants.

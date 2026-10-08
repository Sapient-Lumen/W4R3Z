# CELL-314 — Confidence-Adaptive SwiGLU MoE Guard

Priority: **P1**  
Status: `coded-native-frontier`

## Why it exists

Does confidence-adaptive activation compute help, or does it fail exactly where router confidence is wrong or rare experts matter?

## Cheap first run

Run REV0030_CONFIDENCE_ADAPTIVE_SWIGLU_SMOKE.json; compare confidence-adaptive activation with rare guard and dense fallback.

## Metrics

- `score`
- `quality`
- `cost_frac`
- `route_flip`
- `rare_miss`
- `load_penalty`
- `regret`

## Required baselines

- `dense_swiglu`
- `standard_top2_moe`
- `confidence_adaptive_swiglu`
- `confidence_plus_rare_guard`
- `always_tiny_linear_experts`
- `hpo_switch_dense_or_adaptive`

## Stop condition

Keep P1 unless confidence adaptation survives overconfident-wrong and rare-expert regimes.

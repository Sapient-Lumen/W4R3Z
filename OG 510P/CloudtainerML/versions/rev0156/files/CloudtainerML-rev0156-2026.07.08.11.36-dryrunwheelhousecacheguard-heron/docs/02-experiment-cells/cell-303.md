# CELL-303 — Spectral Operator Hardening with Actual Transforms

Priority: **P0**  
Status: `runnable-native`

## Why this exists
experiments/spectral_operator_hardening/spectral_operator_hardening.cpp generates synthetic signals, runs DCT/IDCT, top-k attention, local windows, hybrid residuals, and Bayesian operator routing under equal budgets.

## Metrics
- abs_error
- cost_frac
- budget_over
- alias_error
- tail_miss
- regret
- score

## Required baselines
- full_attention
- topk_attention
- local_window
- dct_lowpass
- dct_energy_topk
- dct_attention_residual

## Stop condition
If actual transform outputs remove the symbolic CHIAR-like advantage, demote spectral routing.

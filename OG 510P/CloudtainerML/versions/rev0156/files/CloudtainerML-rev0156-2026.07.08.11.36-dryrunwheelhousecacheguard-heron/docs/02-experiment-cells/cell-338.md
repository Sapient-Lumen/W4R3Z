# CELL-338 — Preconditioned Attention Conditioning Probe

Priority: **P1**  
Status: **native-probe-added**

## Question

Can attention preconditioning improve ill-conditioned attention geometry without erasing rare-axis signals?

## Cheap first run

Run experiments/preconditioned_attention_conditioning/preconditioned_attention_conditioning.cpp over anisotropic and rare-axis regimes.

## Metrics

- `cond_proxy`
- `entropy`
- `tail_risk`
- `score`

## Required baselines

- `raw_dot`
- `per_dim_whiten`
- `ridge_precondition`

## Stop condition

Do not promote unless conditioning improves score without tail-risk collapse.

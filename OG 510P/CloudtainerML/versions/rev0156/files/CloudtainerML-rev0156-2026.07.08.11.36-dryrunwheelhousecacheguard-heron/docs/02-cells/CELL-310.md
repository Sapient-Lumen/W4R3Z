# CELL-310 — Spectral Operator HPO Sweep

Priority: **P0**  
Status: `coded-native-hardening`

## Why it exists

Can DCT/spectral operator routing beat fixed DCT+attention residuals on held-out regimes once alias/tail/cost fields are scored?

## Cheap first run

Run REV0030_SPECTRAL_OPERATOR_HPO_SWEEP_SMOKE.json; compare router_hpo against fixed dct_attention_residual on held-out regimes.

## Metrics

- `score`
- `abs_error`
- `cost_frac`
- `budget_over`
- `alias_error`
- `tail_miss`
- `regret`
- `selected_train_score`

## Required baselines

- `topk_attention`
- `local_window`
- `dct_lowpass`
- `dct_attention_residual`
- `oracle_nonfull`

## Stop condition

Stop if HPO does not improve held-out non-oracle score or if it wins only by ignoring alias/tail misses.

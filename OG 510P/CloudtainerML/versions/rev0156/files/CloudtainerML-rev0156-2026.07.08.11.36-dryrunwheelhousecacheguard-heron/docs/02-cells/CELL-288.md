# CELL-288 — STAR-KV SVD/HPO Rank Hardening

Priority: **P0**  
Status: **runnable-native**

## Why this cell exists
Run starkv_svd_hpo.cpp with mean_error and tail_error under synthetic spectra and budget sweeps.

## Question
Linked idea: `IDEA-0286`.

## Sources
- `SRC-0301`

## Metrics
- mean_error
- tail_error
- latency_proxy
- bytes_fraction
- score

## Required baselines
- uniform rank
- energy threshold
- K/V asymmetric rank
- oracle rank/precision

## Stop condition
Promote only if adaptive methods beat uniform rank outside hand-picked tail regimes.

## Rev0027 note
Performance-first lane. Security/trust side-wing material is not driving this cell.

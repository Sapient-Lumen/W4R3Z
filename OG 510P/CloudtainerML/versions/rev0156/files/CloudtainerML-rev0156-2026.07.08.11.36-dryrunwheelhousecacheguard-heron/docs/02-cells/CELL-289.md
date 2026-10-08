# CELL-289 — VIA-SD Tiered Verifier Frontier

Priority: **P1**  
Status: **runnable-native**

## Why this cell exists
Run via_sd_tiered_verifier.cpp to map direct/slim/full verification thresholds.

## Question
Linked idea: `IDEA-0287`.

## Sources
- `SRC-0309`

## Metrics
- expected_cost
- mismatch_rate
- accept_rate
- speedup_proxy
- score

## Required baselines
- binary accept/full verify
- direct confidence only
- conservative slim tier
- oracle tier

## Stop condition
Demote if slim tier wins only by hiding mismatch cost.

## Rev0027 note
Performance-first lane. Security/trust side-wing material is not driving this cell.

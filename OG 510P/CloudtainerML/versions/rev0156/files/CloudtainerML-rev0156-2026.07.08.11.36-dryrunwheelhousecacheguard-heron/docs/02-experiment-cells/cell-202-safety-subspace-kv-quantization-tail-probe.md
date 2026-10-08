# CELL-202 — Safety-Subspace KV Quantization Tail Probe

Priority: **P0**  
Status: **implemented**  
Idea: `IDEA-0202`  
Sources: SRC-0127

## Cheap first run

Run C++ safety-subspace probe and inspect mean task MSE vs safety flip/p99 divergence.

## Metrics

- mean task MSE
- mean safety MSE
- safety flip rate
- safety p99
- utility

## Required baselines

- fp32
- global_int
- grouped_int
- per_channel_int
- PCR-like protected channels
- oracle projection

## Stop condition

If per-channel/global rankings never diverge from safety-tail ranking, tail contract is less urgent.

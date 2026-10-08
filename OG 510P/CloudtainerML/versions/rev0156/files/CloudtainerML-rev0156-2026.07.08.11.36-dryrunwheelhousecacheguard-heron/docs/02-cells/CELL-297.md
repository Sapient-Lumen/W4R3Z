# CELL-297 — Routing-Consistent Quantization Probe

Priority: **P1**  
Status: `native-probe-added`

## Why this exists
experiments/routing_consistent_quantization/routing_consistent_quantization.cpp separates output MSE from route flip and rare-route miss across bits/regimes.

## Metrics
- score
- output_mse
- route_flip_rate
- rare_route_miss
- bytes_fraction
- mismatch_rate

## Required baselines
- reconstruction_only
- per_channel_quant
- router_align_loss
- mixed_precision_router_protect

## Stop condition
Do not promote without actual tiny-router quantization after symbolic pass.

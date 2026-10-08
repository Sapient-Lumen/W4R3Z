# CELL-307 — Expert-Wise Mixed Precision Routing Sensitivity

Priority: **P2**  
Status: `future-candidate`

## Why this exists
Extend routing-consistent quantization to compare router-norm, expert variance, route frequency, and rare-domain protection policies.

## Metrics
- route_flip_rate
- rare_route_miss
- bytes_fraction
- quality_drop
- score

## Required baselines
- uniform_bits
- reconstruction_only
- mixed_precision_router_protect

## Stop condition
Drop if reconstruction-only remains equal under near-boundary routing.

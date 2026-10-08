# CELL-354 — GVR Exact Top-K Temporal Selector Toy

Priority: **P0**  
Status: native-probe-added

## Question

Can temporal correlation make exact top-k selection cheaper without approximate misses, and where does drift force fallback?

## Cheap first run

Compile/run experiments/gvr_topk_temporal/gvr_topk_temporal.cpp. Test exact GVR, approximate previous-top-k, calibrated threshold, and radix exact baseline over temporally correlated score streams.

## Metrics

- `score`
- `exact`
- `misses`
- `candidate_count`
- `passes`
- `pred_hit_ratio`
- `wall_proxy`
- `regret`

## Required baselines

- `radix_exact_baseline`
- `gvr_guess_verify_refine`
- `gvr_aggressive_no_fallback`
- `threshold_calibrated`
- `approx_prev_topk_only`

## Stop condition

Promote only if GVR wins while preserving exactness; no-fallback approximate wins are treated as speed-only non-promotions.

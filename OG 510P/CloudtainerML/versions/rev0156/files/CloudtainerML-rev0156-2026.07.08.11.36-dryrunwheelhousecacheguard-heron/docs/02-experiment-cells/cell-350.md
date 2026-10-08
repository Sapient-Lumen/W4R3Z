# CELL-350 — Sparse Gate Compiler Frontier

Priority: **P0**  
Status: native-probe-added

## Question

Which hard compiler should turn continuous gate scores into sparse connectivity: threshold, top-k, validation-HPO, uncertainty band, or gap-knee?

## Cheap first run

Run experiments/gate_compiler_frontier/gate_compiler_frontier.cpp. Sweep calibrated, shrunken, noisy, ambiguous and overactive score distributions across threshold, top-k, gap-knee and uncertainty-band compilers.

## Metrics

- `score`
- `reachable`
- `miss`
- `selected`
- `tp`
- `fp`
- `fn`
- `calibration_error`
- `rank_quality`
- `regret`
- `cost`

## Stop condition

Promote compiler strategies only if they survive both shrunken rank-good gates and false-spike regimes with exact reachability and cost guard fields.

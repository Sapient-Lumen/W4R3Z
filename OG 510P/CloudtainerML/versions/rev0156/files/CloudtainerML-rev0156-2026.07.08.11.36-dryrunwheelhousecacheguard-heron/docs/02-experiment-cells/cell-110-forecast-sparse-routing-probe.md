# CELL-110: Forecast Sparse Routing Probe

Priority: **P0**
Idea: `IDEA-0109`
Status: **candidate-with-runnable-probe**

## Cheap first run

Runnable scaffold exists in experiments/forecast_sparse_routing/sparda_forecast_probe.py; smoke output under artifacts/probe-results/.

## Required baselines

- random
- shared once
- previous layer
- current query
- oracle next layer

## Metrics

- support recall
- mass recall
- wasted fraction
- JS divergence proxy

## Stop / demote condition

If forecast never beats current query under support drift/noisy query regimes, demote.

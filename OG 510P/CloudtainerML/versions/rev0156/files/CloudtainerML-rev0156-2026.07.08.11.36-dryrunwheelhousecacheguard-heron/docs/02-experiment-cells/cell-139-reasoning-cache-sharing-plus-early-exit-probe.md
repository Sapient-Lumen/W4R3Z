# CELL-139 — Reasoning cache sharing plus early exit probe

Priority: **P0**  
Status: **candidate-with-runnable-probe**

## Cheap first run

Runnable scaffold exists in experiments/reasoning_cache_share_exit/rksc_probe.py; smoke output in artifacts/probe-results/.

## Metrics

- primary utility
- accuracy/error
- compute fraction
- failure regime count
- seed variance

## Stop condition

If high-confidence wrong branches create too many errors, require calibration/stability gates before any trained follow-up.

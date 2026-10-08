# CELL-018 — Local Linear / Parallax Attention Probe
Priority: `P2`  
Status: `candidate`
## Question
Can covariance-probing local-linear attention improve associative memory under noisy retrieval at tiny scale?
## Sources
- `SRC-0051` Parallax: Parameterized Local Linear Attention for Language Modeling — https://arxiv.org/abs/2605.29157

## Cheap first run
Local constant vs local linear kernel attention on noisy key-value pairs; no language pretraining needed.

## Baselines
- simplest heuristic / random baseline
- matched-memory attention or recurrence baseline
- oracle/full-information baseline where applicable

## Metrics
- exact accuracy or loss
- memory bytes / state size
- runtime
- extrapolation length
- failure-mode taxonomy
- seed variance

## Falsifier / demotion rule
If tuning bandwidth dominates results, this is too fiddly for early project shape.

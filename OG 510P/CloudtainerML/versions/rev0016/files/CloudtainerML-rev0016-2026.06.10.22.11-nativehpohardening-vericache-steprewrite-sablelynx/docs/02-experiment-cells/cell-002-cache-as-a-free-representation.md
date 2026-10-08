# CELL-002 — Cache as a Free Representation
Priority: `P0`  
Status: `candidate`
## Question
Can the KV cache itself serve as a cheap state embedding for deciding whether to sample more, stop, route to a slow path, or predict correctness?
## Sources
- `SRC-0002` Beyond Speedup -- Utilizing KV Cache for Sampling and Reasoning — https://arxiv.org/abs/2601.20326

## Cheap first run
Train a tiny model on generated tasks; freeze it; fit classifiers/regressors on summary features of its KV cache to predict correctness/uncertainty/need-more-compute.

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
If cache features are no better than final hidden states, length, entropy, or random projections, keep as note only.

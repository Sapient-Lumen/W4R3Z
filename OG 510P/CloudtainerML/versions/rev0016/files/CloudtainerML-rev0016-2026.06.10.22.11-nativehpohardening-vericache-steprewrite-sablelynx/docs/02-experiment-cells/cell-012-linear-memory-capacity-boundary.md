# CELL-012 — Linear Memory Capacity Boundary
Priority: `P1`  
Status: `candidate`
## Question
Where exactly do delta-rule, Kaczmarz, variational, and gated linear memories break as keys collide and pairs exceed head dimension?
## Sources
- `SRC-0006` Kaczmarz Linear Attention — https://arxiv.org/abs/2605.08587
- `SRC-0007` Variational Linear Attention: Stable Associative Memory for Long-Context Transformers — https://arxiv.org/abs/2605.11196
- `SRC-0008` Gated DeltaNet-2: Decoupling Erase and Write in Linear Attention — https://arxiv.org/abs/2605.22791
- `SRC-0009` Kimi Linear: An Expressive, Efficient Attention Architecture — https://arxiv.org/abs/2510.26692

## Cheap first run
Pure tensor fast-weight simulations, then tiny trained modules; sweep key dimension, pair count, noise, corrections, and repeated writes.

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
If all variants obey the same capacity curve once normalized for rank/state size, deprioritize architectural variants.

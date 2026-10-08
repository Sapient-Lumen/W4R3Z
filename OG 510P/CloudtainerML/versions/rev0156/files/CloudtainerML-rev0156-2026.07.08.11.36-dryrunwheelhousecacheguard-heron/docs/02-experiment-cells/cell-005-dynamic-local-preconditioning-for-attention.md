# CELL-005 — Dynamic Local Preconditioning for Attention
Priority: `P0`  
Status: `candidate`
## Question
Does an input-dependent short convolution before Q/K/V help tiny Transformers learn retrieval circuits faster than static local convolutions or plain attention?
## Sources
- `SRC-0011` Dynamic Short Convolutions Improve Transformers — https://arxiv.org/abs/2606.03825

## Cheap first run
Tiny model with dynamic 3-7 token filters over Q/K/V on associative recall and induction tasks.

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
If it helps only language loss but not exact recall, keep as lower-priority architecture spice.

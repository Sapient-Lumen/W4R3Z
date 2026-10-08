# CELL-009 — Writable Memory Shootout
Priority: `P0`  
Status: `candidate`
## Question
What is the smallest setting where writable memory beats plain attention under a fixed memory budget, and which write rule actually matters?
## Sources
- `SRC-0027` GradMem: Learning to Write Context into Memory with Test-Time Gradient Descent — https://arxiv.org/abs/2603.13875
- `SRC-0028` Titans: Learning to Memorize at Test Time — https://arxiv.org/abs/2501.00663
- `SRC-0029` ATLAS: Learning to Optimally Memorize the Context at Test Time — https://arxiv.org/abs/2505.23735
- `SRC-0030` Titans Revisited: A Lightweight Reimplementation and Critical Analysis of a Test-Time Memory Model — https://arxiv.org/abs/2510.09551
- `SRC-0031` Trellis: Learning to Compress Key-Value Memory in Attention Models — https://arxiv.org/abs/2512.23852
- `SRC-0032` Key-Value Means: Transformers with Expandable Block-Recurrent Memory — https://arxiv.org/abs/2605.09877
- `SRC-0035` Mela: Test-Time Memory Consolidation based on Transformation Hypothesis — https://arxiv.org/abs/2605.10537
- `SRC-0036` Gated Differentiable Working Memory for Long-Context Test-Time Adaptation — https://arxiv.org/abs/2601.12906

## Cheap first run
Same associative recall task, same memory bytes: full attention oracle, sliding window, Trellis-like fixed slots, KVM-like block means, gradient-written tokens, surprise memory, ATLAS-like batch update.

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
If memory tricks only match well-tuned reservoir/top-k baselines, postpone.

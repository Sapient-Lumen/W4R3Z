# CELL-008 — Sequence-Axis Hybrid Router
Priority: `P0`  
Status: `candidate`
## Question
Can a model or policy learn when to spend full attention and when cheap recurrence is enough within the same sequence?
## Sources
- `SRC-0013` Multi-Mixer Models: Flexible Sequence Modeling with Shared Representations — https://arxiv.org/abs/2605.28769
- `SRC-0014` Expressivity-Efficiency Tradeoffs for Hybrid Sequence Models — https://arxiv.org/abs/2603.08859
- `SRC-0012` Forget Attention: Importance-Aware Attention Is All You Need — https://arxiv.org/abs/2606.02332

## Cheap first run
Generated streams with local filler and sparse retrieval-critical segments; train/evolve a router to choose attention vs recurrence at each chunk.

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
If static interleaving matches adaptive routing across tasks, keep the simpler static hybrid.

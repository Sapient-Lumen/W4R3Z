# CELL-011 — Reasoning Trace Compression Bench
Priority: `P1`  
Status: `candidate`
## Question
Are reasoning traces compressible by token importance, segment importance, answer contribution, or head importance?
## Sources
- `SRC-0039` Crystal-KV: Efficient KV Cache Management for Chain-of-Thought LLMs via Answer-First Principle — https://arxiv.org/abs/2601.16986
- `SRC-0040` Semantic Integrity Matters: Benchmarking and Preserving High-Density Reasoning in KV Cache Compression — https://arxiv.org/abs/2502.01941
- `SRC-0041` LongFlow: Efficient KV Cache Compression for Reasoning Models — https://arxiv.org/abs/2603.11504
- `SRC-0044` SkipKV: Selective Skipping of KV Generation and Storage for Chain-of-Thought Reasoning — https://arxiv.org/abs/2512.07993
- `SRC-0045` Which Heads Matter for Reasoning? RL-Guided KV Cache Compression — https://arxiv.org/abs/2510.08525

## Cheap first run
Generate symbolic proof/scratch traces with known dependency graph; remove tokens/segments/heads and measure final-task damage.

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
If all methods reduce to preserving the exact dependency graph, then the research value becomes graph recovery, not cache compression.

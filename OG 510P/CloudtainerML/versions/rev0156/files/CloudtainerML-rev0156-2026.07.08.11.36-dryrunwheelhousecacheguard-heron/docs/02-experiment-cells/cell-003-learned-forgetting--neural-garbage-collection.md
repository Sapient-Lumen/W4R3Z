# CELL-003 — Learned Forgetting / Neural Garbage Collection
Priority: `P0`  
Status: `candidate`
## Question
Can a small controller learn which tokens/slots/heads to forget from final outcome, and does it discover non-obvious recurrence or semantic-unit behavior?
## Sources
- `SRC-0003` Neural Garbage Collection: Learning to Forget while Learning to Reason — https://arxiv.org/abs/2604.18002
- `SRC-0004` Self-Pruned Key-Value Attention — https://arxiv.org/abs/2605.14037
- `SRC-0042` Cache What Lasts: Token Retention for Memory-Bounded KV Cache in LLMs — https://arxiv.org/abs/2512.03324
- `SRC-0043` LazyEviction: Lagged KV Eviction with Attention Pattern Observation for Efficient Long Reasoning — https://arxiv.org/abs/2506.15969
- `SRC-0045` Which Heads Matter for Reasoning? RL-Guided KV Cache Compression — https://arxiv.org/abs/2510.08525

## Cheap first run
Synthetic reasoning traces with an oracle full-cache solver; learn or evolve a retention policy under a memory budget.

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
If learned policies collapse to recency/attention mass and do not transfer to longer traces, demote.

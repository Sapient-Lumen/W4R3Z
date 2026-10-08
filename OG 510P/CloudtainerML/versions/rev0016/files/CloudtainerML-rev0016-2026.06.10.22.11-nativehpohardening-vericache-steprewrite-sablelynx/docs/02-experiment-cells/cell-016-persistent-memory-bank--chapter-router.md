# CELL-016 — Persistent Memory Bank / Chapter Router
Priority: `P2`  
Status: `candidate`
## Question
Can explicit parametric memory tables or routed memory chapters store editable facts with less interference than dense weights?
## Sources
- `SRC-0052` Mixture of Chapters: Scaling Learnt Memory in Transformers — https://arxiv.org/abs/2603.21096
- `SRC-0053` STEM: Scaling Transformers with Embedding Modules — https://arxiv.org/abs/2601.10639
- `SRC-0026` HoReN: Normalized Hopfield Retrieval for Large-Scale Sequential Model Editing — https://arxiv.org/abs/2605.08143

## Cheap first run
Tiny fact-family tasks with continued training and edits; compare dense model, memory bank, token-indexed table, Hopfield edit wrapper.

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
If memory bank just memorizes IDs and fails paraphrase/generalization in controlled variants, deprioritize.

# CELL-007 — Hidden-State Attractor Margin Probe
Priority: `P0`  
Status: `candidate`
## Question
Can hidden-state geometry distinguish correct recall, conflicting recall, and absent facts better than output entropy in a tiny controlled memory model?
## Sources
- `SRC-0024` Attractor Geometry of Transformer Memory: From Conflict Arbitration to Confident Hallucination — https://arxiv.org/abs/2605.05686
- `SRC-0025` Context-Gated Associative Retrieval: From Theory to Transformers — https://arxiv.org/abs/2605.10970

## Cheap first run
Install synthetic facts via training/adapters; query present, conflicting, and absent facts; compute nearest-basin/margin measures.

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
If entropy and margin are equally predictive in the tiny setting, the large-model claim may not miniaturize.

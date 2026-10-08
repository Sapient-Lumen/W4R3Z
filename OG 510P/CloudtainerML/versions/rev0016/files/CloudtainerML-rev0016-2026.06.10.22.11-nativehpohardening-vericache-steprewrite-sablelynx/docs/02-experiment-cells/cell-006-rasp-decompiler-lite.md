# CELL-006 — RASP Decompiler Lite
Priority: `P0`  
Status: `candidate`
## Question
When a tiny Transformer length-generalizes, did it learn a crisp program we can actually extract, or only a fragile interpolation trick?
## Sources
- `SRC-0019` Discovering Interpretable Algorithms by Decompiling Transformers to RASP — https://arxiv.org/abs/2602.08857
- `SRC-0020` Length Generalization Bounds for Transformers — https://arxiv.org/abs/2603.02238
- `SRC-0021` Softmax Transformers are Turing-Complete — https://arxiv.org/abs/2511.20038
- `SRC-0022` Looped Transformers for Length Generalization — https://arxiv.org/abs/2409.15647

## Cheap first run
Train on simple formal/algorithmic tasks; inspect attention patterns, causal ablations, and threshold-like MLP features; manually recover enough of the program.

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
If many seeds pass validation but no stable sufficient subprogram appears, record that too: useful negative result.

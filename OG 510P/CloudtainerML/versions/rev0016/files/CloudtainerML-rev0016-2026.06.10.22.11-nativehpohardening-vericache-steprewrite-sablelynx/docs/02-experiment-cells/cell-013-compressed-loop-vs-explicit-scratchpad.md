# CELL-013 — Compressed Loop vs Explicit Scratchpad
Priority: `P1`  
Status: `candidate`
## Question
When does hidden recurrent looping replace explicit scratchpad tokens, and when does it fail because the persistent state is too small?
## Sources
- `SRC-0022` Looped Transformers for Length Generalization — https://arxiv.org/abs/2409.15647
- `SRC-0023` Chain-of-Thought and Compressed Looped Transformers — https://arxiv.org/abs/2605.30757

## Cheap first run
Pointer chasing, iterative arithmetic, and associative recall with looped hidden state vs explicit generated scratch sequence.

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
If explicit scratchpad always wins at same compute and memory, focus on scratchpad compression instead.

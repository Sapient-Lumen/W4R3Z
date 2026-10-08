# CELL-010 — Position + Sparse Attention Length Extrapolation
Priority: `P1`  
Status: `candidate`
## Question
Do CoPE-style RoPE clipping and sparse/entmax attention help tiny models extrapolate to longer lengths, or do they just shift failure modes?
## Sources
- `SRC-0017` CoPE: Clipped RoPE as A Scalable Free Lunch for Long Context LLMs — https://arxiv.org/abs/2602.05258
- `SRC-0018` Long-Context Generalization with Sparse Attention — https://arxiv.org/abs/2506.16640

## Cheap first run
Train at length 128/256, evaluate to 4096 on fixed-pattern retrieval and bracket/formal tasks; plot wrong-position and attention-dispersion failures.

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
If gains disappear under adversarial distractors or different seeds, keep as setup-dependent.

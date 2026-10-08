# CELL-014 — Toy State-Tracking World Model
Priority: `P1`  
Status: `candidate`
## Question
Can small models maintain exact latent state over action sequences, and do recurrent/hybrid mixers beat causal attention at tiny scale?
## Sources
- `SRC-0010` Mamba-3: Improved Sequence Modeling using State Space Principles — https://arxiv.org/abs/2603.15569
- `SRC-0054` Chess-World-Model: A 10M-Game Benchmark for Exact State Tracking from Chess Move Sequences — https://arxiv.org/abs/2605.30100
- `SRC-0060` Sequential-Parallel Duality in Prefix Scannable Models — https://arxiv.org/abs/2506.10918

## Cheap first run
Start with stack automata/grid worlds/mini move systems; predict exact state after sequence; include random-action OOD split.

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
If a simple hand-coded recurrent baseline dominates all learned models, the benchmark is too easy or architecture-insensitive.

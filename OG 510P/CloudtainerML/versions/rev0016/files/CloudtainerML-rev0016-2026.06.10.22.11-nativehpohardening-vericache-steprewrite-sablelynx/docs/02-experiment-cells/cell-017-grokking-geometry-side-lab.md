# CELL-017 — Grokking Geometry Side Lab
Priority: `P2`  
Status: `candidate`
## Question
Can architecture/topology change whether tiny models memorize first and generalize later, and can we see algorithmic structure before generalization?
## Sources
- `SRC-0055` Slower Generalization, Faster Memorization: A Sweet Spot in Structured-Output Learning — https://arxiv.org/abs/2605.14659
- `SRC-0056` The Geometric Inductive Bias of Grokking — https://arxiv.org/abs/2603.05228
- `SRC-0057` Latent Algorithmic Structure Precedes Grokking — https://arxiv.org/abs/2603.23784
- `SRC-0059` Geometric Scaling of Bayesian Inference in LLMs — https://arxiv.org/abs/2512.23752

## Cheap first run
Modular arithmetic and structured matrix-output tasks with spherical constraints, uniform attention, Fourier probes, and data-size sweeps.

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
If runs are too seed-sensitive for our CPU budget, preserve as background.

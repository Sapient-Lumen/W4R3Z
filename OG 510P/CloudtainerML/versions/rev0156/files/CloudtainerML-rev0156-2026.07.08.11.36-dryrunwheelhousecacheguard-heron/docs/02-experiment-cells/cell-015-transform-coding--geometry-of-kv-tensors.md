# CELL-015 — Transform Coding / Geometry of KV Tensors
Priority: `P1`  
Status: `candidate`
## Question
Is KV compression mostly about coordinate decorrelation, rotational smoothing, dimension allocation, or entropy coding?
## Sources
- `SRC-0048` OCTOPUS: Optimized KV Cache for Transformers via Joint Coordinate Quantization — https://arxiv.org/abs/2605.21226
- `SRC-0049` KV Cache Transform Coding for Compact Storage in LLM Serving — https://arxiv.org/abs/2511.01815
- `SRC-0050` Offline Spectral Covariance-Aware Rotation for 2-bit KV Cache Quantization — https://arxiv.org/abs/2605.17757
- `SRC-0047` Mixed-Dimension Budget Allocation for Efficient KV Cache Compression — https://arxiv.org/abs/2603.20616

## Cheap first run
Collect K/V tensors from small trained models and compare identity, Hadamard, random orthogonal, PCA, covariance-aware, and grouped-coordinate quantizers.

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
If task accuracy is insensitive to all transforms at small scale, move to larger local pretrained models only if available.

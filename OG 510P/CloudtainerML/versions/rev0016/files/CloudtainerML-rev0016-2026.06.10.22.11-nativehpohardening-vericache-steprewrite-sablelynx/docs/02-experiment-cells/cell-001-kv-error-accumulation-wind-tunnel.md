# CELL-001 — KV Error Accumulation Wind Tunnel
Priority: `P0`  
Status: `candidate`
## Question
Do cache quantization errors that look tolerable in static/prefill probes accumulate catastrophically during autoregressive decode? Which statistic predicts collapse: MSE, inner-product error, token-scale error, or top-tail outliers?
## Sources
- `SRC-0001` KVarN: Variance-Normalized KV-Cache Quantization Mitigates Error Accumulation in Reasoning Tasks — https://arxiv.org/abs/2606.03458
- `SRC-0046` Adaptive KV-Cache Quantization for Lightweight On-Device LLMs — https://arxiv.org/abs/2604.04722
- `SRC-0049` KV Cache Transform Coding for Compact Storage in LLM Serving — https://arxiv.org/abs/2511.01815
- `SRC-0050` Offline Spectral Covariance-Aware Rotation for 2-bit KV Cache Quantization — https://arxiv.org/abs/2605.17757

## Cheap first run
Tensor-only or tiny-transformer pseudo-decode with stored K/V tensors, quantized variants, and decode-length sweeps.

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
If naive int4/int2, rotated, variance-normalized, and covariance-aware methods have identical accuracy-vs-length curves, the idea loses priority.

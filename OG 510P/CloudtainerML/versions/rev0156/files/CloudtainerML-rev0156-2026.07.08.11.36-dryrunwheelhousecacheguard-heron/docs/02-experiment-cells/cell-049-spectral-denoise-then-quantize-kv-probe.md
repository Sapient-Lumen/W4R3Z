# CELL-049 — Spectral Denoise-Then-Quantize KV Probe

Priority: P1  
Status: candidate

## Cheap first run

Spiked matrix KV generator; low-rank shrinkage before residual quantization.

## Metrics

accuracy/exact match, loss/error, memory bytes, runtime, failure mode count, seed variance

## Stop condition

If denoising hurts all cases, inspect generator assumptions.

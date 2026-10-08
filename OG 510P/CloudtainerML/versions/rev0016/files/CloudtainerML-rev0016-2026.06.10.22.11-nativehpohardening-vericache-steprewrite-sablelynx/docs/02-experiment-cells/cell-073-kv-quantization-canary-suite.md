# CELL-073 — KV Quantization Canary Suite

Priority: **P2**
Status: `candidate`

## Cheapest first run

Add rare-class preference/canary labels to quantized decode probes.

## Baselines

- fp32
- int8
- int4
- KVarN-ish normalized
- mixed precision

## Metrics

- canary flip rate
- accuracy
- calibration error
- tail output error

## Stop condition

If canary flips are fully predicted by output MSE, keep as dashboard metric only.

## Source ids

SRC-0127, SRC-0001

# CELL-069 — Cache-Compressibility Training Toy

Priority: **P1**
Status: `candidate`

## Cheapest first run

Train two tiny models on synthetic recall, one with random KV-slot masking/dropout, then compress both.

## Baselines

- standard training
- slot-masked training
- explicit bottleneck model
- post-hoc pruning only

## Metrics

- full-cache accuracy
- compressed accuracy
- cache bytes
- eviction robustness
- quantization robustness

## Stop condition

If slot masking only hurts full and compressed accuracy, drop.

## Source ids

SRC-0123, SRC-0128

# CELL-121 — Parametric/KV Memory Crossover Probe

Priority: **P0**  
Status: **active**  
Idea: `IDEA-0120`  
Sources: SRC-0186

## Cheap first run

Run parametric_kv_probe.py over retention ratios and adapter qualities.

## Metrics

- ROUGE proxy
- answer accuracy
- hallucination rate
- cache hit rate

## Required baselines

- context only
- adapter only
- gated context+adapter
- full cache oracle

## Stop condition

If crossover is absent, adjust or demote.

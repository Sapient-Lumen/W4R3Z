# CELL-122 — Still Single-Pass Latent Compactor Probe

Priority: **P0**  
Status: **active**  
Idea: `IDEA-0121`  
Sources: SRC-0180

## Cheap first run

Run still_compactor_probe.py over clusters, needles, and slots.

## Metrics

- reconstruction error
- cosine to full
- critical hit proxy

## Required baselines

- full attention
- random tokens
- attention top-k
- centroids
- latent slots
- hybrid

## Stop condition

If latent slots only match random, demote; if isolated needles break them, promote hybrid rule.

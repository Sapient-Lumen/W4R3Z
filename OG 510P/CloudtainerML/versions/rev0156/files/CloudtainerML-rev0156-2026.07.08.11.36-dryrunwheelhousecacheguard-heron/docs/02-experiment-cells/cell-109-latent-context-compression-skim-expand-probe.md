# CELL-109: Latent Context Compression Skim-Expand Probe

Priority: **P0**
Idea: `IDEA-0108`
Status: **candidate-with-runnable-probe**

## Cheap first run

Runnable scaffold exists in experiments/latent_context_compression/lclm_probe.py; smoke output under artifacts/probe-results/.

## Required baselines

- compressed-only
- compressed-then-expand
- random expand
- oracle expand
- full raw oracle

## Metrics

- output relative error
- target chunk hit
- effective token budget
- compression ratio

## Stop / demote condition

If compressed-only dominates expand in all regimes, role taxonomy needs revision.

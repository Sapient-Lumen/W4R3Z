# CELL-209 — Multi-Domain Agent Stress Toy

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0209`  
Sources: SRC-0238

## Cheap first run

Interleave multiple tiny domains and track whether memory/routing errors increase with domain switches.

## Metrics

- task success
- state violation
- memory contamination
- false success

## Required baselines

- single-domain
- multi-domain recency
- topic memory
- oracle state

## Stop condition

If failures reduce to single-domain cases, keep benchmark small.

# CELL-132 — Adapter Staleness Trap

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0131`  
Sources: SRC-0186

## Cheap first run

Parametric memory conflict toy with stale adapter confidence.

## Metrics

- fresh-context win rate
- stale override rate
- hallucination rate

## Required baselines

- fresh context
- stale adapter
- gated adapter

## Stop condition

If gating never matters, make confidence adversarial.

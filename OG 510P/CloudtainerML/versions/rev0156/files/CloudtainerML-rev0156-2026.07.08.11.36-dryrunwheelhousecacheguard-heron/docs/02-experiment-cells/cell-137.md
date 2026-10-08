# CELL-137 — Decoding-Time Adapter Prior Probe

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0136`  
Sources: SRC-0186

## Cheap first run

Separate encode-time and decode-time adapter effects in parametric-KV toy.

## Metrics

- decode-prior gain
- encode-memory gain
- conflict harm

## Required baselines

- encode adapter
- decode adapter
- both
- none

## Stop condition

If effects cannot be separated, redesign.

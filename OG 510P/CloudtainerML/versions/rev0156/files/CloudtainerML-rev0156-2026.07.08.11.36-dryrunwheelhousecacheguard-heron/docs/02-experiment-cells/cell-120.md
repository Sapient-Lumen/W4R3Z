# CELL-120 — Evidence-Aligned Query Adaptation Probe

Priority: **P0**  
Status: **active**  
Idea: `IDEA-0119`  
Sources: SRC-0179

## Cheap first run

Run ease_ttt_probe.py with top-k/soft evidence targets and decoy regimes.

## Metrics

- answer accuracy
- evidence mass
- decoy mass
- first evidence rank

## Required baselines

- full context
- retrieval-only
- random qTTT
- oracle evidence target

## Stop condition

If EASE-style update does not beat random/retrieval-only outside oracle, demote.

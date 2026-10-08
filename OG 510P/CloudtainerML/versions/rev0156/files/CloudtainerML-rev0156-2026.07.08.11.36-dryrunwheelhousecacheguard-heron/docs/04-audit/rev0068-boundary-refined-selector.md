# rev0068 — Boundary-refined selector/layout audit

## Question

Can a deployable score-only selector recover the value-layout headroom seen in rev0064 without paying exact Top-p sort cost?

## Change

rev0068 adds a boundary-refined histogram selector. It uses a coarse probability histogram to find the threshold bin, keeps all bins above it, and sorts only the threshold boundary bin. This reduces support over-selection while keeping the selector cheaper than a full exact sort.

## Result

On the local tiny-trained Q/K/V trace:

- coarse histogram selected fraction: about 0.661
- boundary-refined selected fraction: about 0.433
- exact-sort selected fraction: about 0.433
- refined quality rate: 1.0
- refined QK-included speedup versus dense: about 0.413×
- exact-sort QK-included speedup versus dense: about 0.346×

## Decision

Boundary refinement fixes the coarse histogram support-width problem, but it does not make the path promotable. It still computes all QK scores, requires row-local score/probability storage, and is slower than dense on this CPU replay.

## Follow-up

The next useful work is not another support selector over full scores. The remaining hard question is whether any observable score-path pruning or external/public trace can produce support without full QK materialization.

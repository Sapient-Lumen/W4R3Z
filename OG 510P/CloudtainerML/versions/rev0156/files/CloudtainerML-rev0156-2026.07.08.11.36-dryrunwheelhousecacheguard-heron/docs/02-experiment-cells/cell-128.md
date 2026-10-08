# CELL-128 — SparseX Segment Reuse Correction Toy

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0127`  
Sources: SRC-0210

## Cheap first run

Repeated non-prefix segments with context-dependent correction tokens.

## Metrics

- reuse error
- corrected interaction mass
- recompute tokens

## Required baselines

- raw segment reuse
- full recompute
- sparse recompute
- random recompute

## Stop condition

If sparse correction cannot beat raw reuse, inspect selectors.

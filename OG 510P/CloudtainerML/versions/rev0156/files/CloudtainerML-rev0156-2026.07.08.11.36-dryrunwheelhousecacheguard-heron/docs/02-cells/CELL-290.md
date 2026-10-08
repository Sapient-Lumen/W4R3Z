# CELL-290 — nD-RoPE Isotropy Geometry Probe

Priority: **P1**  
Status: **runnable-native**

## Why this cell exists
Run nd_rope_isotropy.cpp over dimensions, rotated grids, and extrapolation radii.

## Question
Linked idea: `IDEA-0288`.

## Sources
- `SRC-0308`

## Metrics
- isotropy_error
- alias_error
- extrap_error
- score

## Required baselines
- axis-separable RoPE
- random wave vectors
- oracle isotropic kernel

## Stop condition
Promote only if non-axis regimes show consistent wins at acceptable cost.

## Rev0027 note
Performance-first lane. Security/trust side-wing material is not driving this cell.

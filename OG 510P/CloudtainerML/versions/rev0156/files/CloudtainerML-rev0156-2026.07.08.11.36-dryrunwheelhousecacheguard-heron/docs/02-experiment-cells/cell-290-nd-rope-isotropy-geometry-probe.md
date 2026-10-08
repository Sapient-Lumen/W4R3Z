# CELL-290 — nD-RoPE Isotropy Geometry Probe

Priority: **P1**  
Status: **runnable-native**

## Cheap first run
Run nd_rope_isotropy.cpp over dimensions, rotated grids, and extrapolation radii.

## Linked idea
`IDEA-0288`

## Sources
- `SRC-0308`

## Metrics
- isotropy_error
- alias_error
- extrap_error
- score

## Stop condition
Promote only if non-axis regimes show consistent wins at acceptable cost.

## Rev0027 note
Performance-first cell; security/trust side-wing is not driving this priority.

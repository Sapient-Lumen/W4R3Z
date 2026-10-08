# CELL-339 — Periodic Skip Off-Phase Trap

Priority: **P1**  
Status: **covered-by-schema**

## Question

Do deterministic periodic skip edges create predictable long-range coverage but fail sharply on off-phase dependencies?

## Cheap first run

Use CELL-337 rows for pi_periodic_skip in periodic_offphase and old_anchor regimes.

## Metrics

- `depth_reach`
- `target_miss`
- `cost_frac`

## Required baselines

- `sliding_window`
- `boundary_bridge`
- `dense_causal`

## Stop condition

Promote only if periodic skip wins under a realistic equal-cost phase, not only easy old-anchor cases.

# CELL-111: Head-Profile Stability for Non-Uniform KV Budgets

Priority: **P1**
Idea: `IDEA-0110`
Status: **candidate**

## Cheap first run

Synthetic head profiles with distance/entropy/value-role; compare static Tangram-like budgets to online routing under shifted prompts.

## Required baselines

- uniform budget
- oracle dynamic
- static profile
- noisy online router

## Metrics

- retained mass
- profile drift
- fragmentation proxy
- budget waste

## Stop / demote condition

If profiles are not stable even in controlled regimes, postpone systems lane.

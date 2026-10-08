# CELL-333 — Exactness Guard Report

Priority: **P0**  
Status: **audit-refactor-added**

## Question

Which performance probes expose exact-copy, needle, reachability, route-flip, target-miss, or rare-token fields before they are promoted?

## Cheap first run

Run tools/exactness_guard_report.py over current artifacts and identify probes missing copy/needle/reachability guard fields.

## Metrics

- `current_candidate_artifacts`
- `exactness_ready`
- `guard_field_count`

## Required baselines

- `routing_family_report`
- `spectral_operator_report`

## Stop condition

Keep if it blocks or reprioritizes at least one attractive but under-guarded performance probe.

# Defect: ad-hoc fork lifecycle sprawl

## Before

Fifteen raw test forks across eight translation units separately owned PID,
wait, timeout, kill, pipe, and cleanup policy. Structural audits sometimes
required the duplicated choreography, making consolidation look like a failure.

## Correction

One test-only move-only owner now contains the only raw fork. Thirteen genuine
inherited-state spawn sites use it, and audits require the centralized topology.

## Residual boundary

The callback remains a reviewed post-fork exception; central ownership is not a
general async-signal-safety proof.

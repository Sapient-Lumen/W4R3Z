# ADR 0371: Keep the 24-hour soak passive on slow cycles

Status: accepted and implemented
Date: 2026-09-10

## Context

The first ADR 0368 retuned 24-hour candidate was much calmer than the original
five-second high-churn profile through cycle 10, but it still tripped the
120-second stalled-cycle recovery path at cycle 19 and again at cycle 20.  The
recovery path restarted lagging daemons, which made sense as a separate
resilience drill, but it muddied the first trust-graduation question.

For a first 24-hour reliability soak, we want to know whether a representative
three-writer namespace can keep converging without emergency intervention.  A
cycle that is merely slow should not cause the harness to restart nodes and
change the experiment.

## Decision

The `soak-24h` profile disables `soakStalledRestartAfter` and raises the hard
cycle timeout to 900 seconds.  The runner still supports
`--soak-stalled-restart-after` for explicit recovery/stress profiles, but the
graduation profile now waits passively for convergence or fails on the hard
timeout.

The runner also prints the soak delay, timeout, and stalled-restart threshold in
the `writable soak started` stage line.  Scheduled daemon restart messages also
include the soak cycle number.  The live status helper parses those fields and
derives a cadence-aware stale window for sparse progress logs while showing the
last scheduled restart cycle/node when available.

## Consequences

An accepted 24-hour soak will now mean the mesh stayed healthy without
emergency daemon restarts.  A rejection will be easier to interpret: either a
cycle exceeded the hard convergence timeout, the VM exited, or the operator
stopped the run.  Recovery-path behavior remains testable, but it no longer
defines the primary trust-graduation run.

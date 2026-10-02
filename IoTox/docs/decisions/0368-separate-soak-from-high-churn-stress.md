# ADR 0368: Separate soak from high-churn stress

Status: accepted and implemented
Date: 2026-09-10

## Context

The first clean rerun after ADR 0367 used the 24-hour profile's original five-second cycle delay. It
reached 68 completed writable cycles in roughly half an hour, but needed emergency stalled-cycle
recovery at cycle 16 and again at cycle 68 before the operator stopped it cleanly with an ACPI power
button. The stopped run retained a rejected receipt with content-free projection shape and two
stalled-cycle recovery events.

That behavior is useful stress evidence, but it is not the shape wanted for a first 24-hour trust
graduation soak. A five-second edit cadence attempts thousands of three-writer revisions in one day,
with scheduled repair and daemon restarts layered on top. That makes it a high-churn stress test.
The graduation question is different: can an ordinary read/write namespace stay healthy for a full
day while all three writers remain authorized, occasionally edit, occasionally repair, and rotate
daemon restarts?

## Decision

The `soak-24h` Sandwurm profile now uses `soakCycleDelaySeconds = 240` while keeping:

- `soakSeconds = 86400`;
- `soakMinimumCycles = 288`;
- `soakRestartEvery = 24`;
- `soakRepairEvery = 12`;
- the same 512 by 16-KiB capacity prelude, 24 shadow cycles, maintenance lifecycle, recovery drill,
  and storage-fault follow-up.

At four minutes between synthetic edits, the minimum cycle floor still represents one converged
three-writer write every five minutes or better across the day. Scheduled daemon restarts rotate
across all three nodes roughly every 96 minutes at the minimum cadence, and repair passes occur
roughly every 48 minutes at the minimum cadence. If convergence is faster, the harness still records
the actual cycle count and timing distribution.

The five-second profile behavior remains an important future stress class, but it must not be
confused with the first 24-hour graduation soak.

## Consequences

The 24-hour gate is now a reliability soak instead of a high-churn throughput campaign. A pass with
few or zero stalled-cycle recoveries will be more meaningful for "can I keep a noncritical working
directory synchronized all day?" than a noisy pass that only proves the harness can repeatedly kick a
busy mesh.

This does not lower the correctness bar: every cycle still requires all three worktrees to converge
to the exact current/toggle state, with no conflict files and all three branches visible. ADR 0371
later keeps the primary 24-hour profile passive on slow cycles by disabling emergency
stalled-cycle restarts and relying on the hard convergence timeout. ADR 0373 later keeps
`soakRestartEvery = 24` and `soakRepairEvery = 12` but defers the repair pass when those intervals
land on the same cycle; the coincident restart-plus-repair shape is retained as explicit stress
science rather than the representative 24-hour gate.

High-churn, many-writer, near-capacity, and bulk-interference campaigns remain separate science.

## Evidence

The stopped high-churn clean rerun is retained at
`.sandwurm/lab/three-writer-soak-24h/run.4Zd0SZy8`. Its rejected receipt reports
`failure="interrupted by SIGTERM"`, 68 completed cycles, scheduled restart targets `["a", "b"]`,
two stalled-cycle recoveries, full capacity projection on all nodes, and content-free projection
shape at the stop point.

The verifier now accepts that rejected receipt shape after treating zero high-water RSS on a stopped
child process as unavailable rather than invalid.

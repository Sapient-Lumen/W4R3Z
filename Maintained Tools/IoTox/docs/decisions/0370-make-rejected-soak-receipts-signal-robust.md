# ADR 0370: Make rejected soak receipts signal-robust

Status: accepted and implemented
Date: 2026-09-10

## Context

The first ADR 0368 24-hour candidate reached cycle 10 cleanly, then entered
stalled-cycle recovery at cycle 19 and again at cycle 20.  The operator stopped
the VM with the Cloud Hypervisor power button because the run was no longer a
clean graduation candidate.

During shutdown, the three-writer service tried to write rejected evidence but
reported `three-writer rejected evidence failed: interrupted by SIGTERM`.
Sandwurm therefore retained the hypervisor/console proof, but no
`iotox/sync-three-writer.json` guest receipt.  The console still proved the
important sequence, but the missing receipt was a harness failure.

## Decision

The three-writer runner now treats rejected-evidence emission as last-gasp
cleanup:

- SIGINT and SIGTERM are ignored before writing the rejected receipt; and
- read-only partial snapshot collectors use content-free safe fallbacks so
  teardown races cannot abort the whole receipt.

## Consequences

Interrupted or intentionally stopped long soaks should now retain the same
machine-verifiable rejected receipt shape as natural qualification failures.
That receipt remains content-free and can still show zero/unavailable counters
when a node process is already gone; the verifier already treats those as
unavailable rather than secret data.

This does not make an interrupted run a pass.  It only makes the failure worth
keeping.

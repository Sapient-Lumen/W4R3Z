# ADR 0377: Use explicit control deadlines for post-soak maintenance

Status: accepted and implemented
Date: 2026-09-14

## Context

The ADR 0376 24-hour replacement candidate
`.sandwurm/lab/three-writer-soak-24h/run.UKn62cvQ` completed the representative
writable soak itself: it crossed the 24-hour wall-clock target, reached the
`soak_minimum_cycles=288` gate, drained the cycle-288 deferred repair on cycle
289, and logged `writable soak completed cycles=289`.

The terminal IoTox receipt was still `status = "rejected"` because the
post-soak maintenance lifecycle then failed:

`b sync-writer-cutoff field-notes ... failed: IoTox control response deadline elapsed`

This failure shape is different from a three-writer data divergence.  The
content-free soak evidence had already converged through the terminal cycle.
The rejection happened while proving the retained writer-cutoff lifecycle after
the soak.  ADR 0373 fixed this class for `sync-repair` by passing an explicit
IoTox `--timeout-ms` control deadline instead of relying only on the Python
subprocess timeout, but the maintenance-lifecycle commands still used the
control client's default deadline.

## Decision

The three-writer harness now applies the explicit long control deadline to all
post-soak maintenance lifecycle control commands:

- `sync-checkpoint`;
- `sync-pin`;
- `sync-unpin`;
- `sync-retention`;
- `sync-gc dry-run`;
- `sync-gc quarantine`;
- `sync-restore`;
- `sync-writer-cutoff`; and
- `sync-automation` evidence reads.

The harness reuses the existing `--sync-repair-control-timeout-ms` value for
these maintenance commands and records `maintenance_control_timeout_ms` in the
receipt evidence.  The subprocess timeout is derived from the same deadline, so
the local-control deadline and the wrapper patience now agree.

## Consequences

The representative 24-hour gate remains strict: the maintenance lifecycle is
still required, including checkpoint, pin/unpin, GC quarantine/restore, writer
cutoff, and retired-writer re-entry refusal.  This ADR does not skip or soften
those checks.  It makes their control-plane patience explicit under the same
late-soak pressure profile already used for bounded `sync-repair`.

The rejected `run.UKn62cvQ` remains valuable evidence: it proves the long soak
reached cycle 289 with exact convergence and identifies the remaining failure
as post-soak local-control deadline pressure during `sync-writer-cutoff`.

## Evidence

The motivating rejected receipt is retained at
`.sandwurm/lab/three-writer-soak-24h/run.UKn62cvQ/live/workspace-export/guest-receipts/iotox/sync-three-writer.json`.
It reports `status = "rejected"`, `soak_cycles = 289`,
`soak_minimum_cycles = 288`, `soak_repair_pending = false`,
`soak_restart_settle_passes = 12`, `soak_repair_deferrals = 12`, and
`soak_stalled_cycle_recoveries = 2`, with the failure text naming
`sync-writer-cutoff` and `IoTox control response deadline elapsed`.

The replacement receipt at
`.sandwurm/lab/three-writer-soak-24h/run.lYtTYT0k/live/workspace-export/guest-receipts/iotox/sync-three-writer.json`
closes the ADR with `status = "passed"`, `soak_cycles = 289`,
`soak_elapsed_ms = 109651807`, `soak_restart_settle_passes = 12`,
`soak_repair_deferrals = 12`, `soak_repair_pending = false`,
`maintenance_lifecycle = true`, and `maintenance_control_timeout_ms = 120000`.
It proves checkpoint propagation, pin/unpin, recoverable GC quarantine/restore,
writer cutoff, and retired-writer re-entry refusal after the 24-hour/288-cycle
soak gate.

One proof-boundary nuance remains deliberately visible: Sandwurm's generic
legacy guest receipt boundary was not emitted for this domain-specific run, so
the live-chain status is `launched-without-guest-evidence` with blocker
`guest-evidence-not-observed`.  The IoTox verifier accepts the run as
`evidence_boundary = "iotox-domain-receipt"` only because the VMM wrapper
exited and the content-free IoTox receipt itself passes the full three-writer
verification.  Moving the IoTox domain receipt into Sandwurm's generic
top-level task boundary is a packaging polish task, not a remaining ADR 0377
maintenance failure.

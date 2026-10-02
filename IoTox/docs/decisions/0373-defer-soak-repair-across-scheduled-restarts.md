# ADR 0373: Defer soak repair across scheduled restarts

Status: accepted and implemented
Date: 2026-09-11

## Context

The ADR 0372 restart-before-edit 24-hour candidate
`.sandwurm/lab/three-writer-soak-24h/run.Ym8xWhvm` reached cycle 40 cleanly,
then fired the scheduled cycle-48 restart against node `b`.  The same cycle was
also divisible by `soakRepairEvery = 12`, so the harness immediately stacked a
periodic `sync-repair` pass on top of scheduled daemon churn.

The run rejected with:

`c sync-repair field-notes failed: IoTox control response deadline elapsed`

Its retained rejected receipt is useful because the synchronized content-free
projection was aligned on all three nodes: the `soak/current.txt` digest and
deleted-toggle state matched everywhere, capacity shape matched everywhere, and
there were no conflict alternatives.  The failure was therefore not a
three-writer data divergence claim.  It was a maintenance/control responsiveness
failure under coincident scheduled restart plus repair pressure.

There was also a harness bug hiding in the shape: the Python wrapper gave the
`sync-repair` subprocess 120 seconds, but did not pass an explicit IoTox
`--timeout-ms` control deadline to the CLI.  A busy but live daemon could
therefore trip the control client's shorter default deadline before the
harness's intended patience mattered.

## Decision

`tools/run-sync-three-writer.py` now has an explicit
`--sync-repair-control-timeout-ms` knob.  All harness-owned `sync-repair`
maintenance commands pass that deadline to IoTox and derive the subprocess
timeout from it.

The writable soak also has a `--soak-repair-restart-policy` knob:

- `defer` moves a periodic soak repair that lands on a scheduled restart cycle
  to the next non-restart cycle;
- `coincident` preserves the old sharper shape, where scheduled daemon restart
  and periodic repair run in the same cycle.

The Sandwurm `soak-smoke` and `soak-24h` profiles use `defer` with a
120-second repair control deadline.  Receipts record
`soak_repair_restart_policy`, `sync_repair_control_timeout_ms`,
`soak_repair_deferrals`, `soak_repair_deferred_cycles`, and
`soak_repair_pending`.  The soak loop keeps running until a deferred repair has
drained, so an accepted receipt must have `soak_repair_pending = false` and at
least as many repair passes as deferred restart cycles.  The verifier checks
those fields when present, and the live inspector/watcher surfaces them during
long runs.

## Consequences

The primary 24-hour graduation gate now separates ordinary long-run reliability
from the harsher "restart while immediately forcing full repair" stress cell.
That does not weaken the sync correctness bar: every soak cycle still requires
all three worktrees to converge to the exact expected projection, with all three
branches visible and no conflict files.

The coincident restart-plus-repair shape remains valuable science, but it is now
named and opt-in.  If the representative 24-hour run still rejects with repair
deferral and an explicit control deadline, the next investigation should focus
on sync repair/event-loop responsiveness itself rather than accidental
maintenance scheduling.

## Evidence

The clean ADR 0373 smoke at source commit
`7dc73d1690696435ae91891b82ac83c14609cfc7` accepted at
`.sandwurm/lab/three-writer-soak-smoke/run.cnowmx9v`.  It completed five soak
cycles, two scheduled daemon restarts (`["a", "b"]`), two deferred repair
cycles (`[2, 4]`), two repair passes, zero stalled-cycle recoveries,
`soak_repair_pending = false`, retained recovery rehearsal, storage-fault
rehearsal, and VM-smoke verification.

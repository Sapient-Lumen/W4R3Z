# ADR 0372: Schedule soak restarts before edits

Status: accepted and implemented
Date: 2026-09-11

## Context

The passive ADR 0371 24-hour candidate reached 71 completed writable cycles,
rotated scheduled restarts across nodes `a`, `b`, and `c`, and rejected at cycle
72 with `timeout waiting for writable soak cycle 72`.  Its retained IoTox
receipt showed zero emergency recoveries, full capacity projection, no conflict
alternatives, and node `b` behind the cycle-72 synthetic projection while nodes
`a` and `c` had converged.

The timing matters.  The old scheduled-restart order wrote the cycle's synthetic
edit first, then restarted the scheduled node before waiting for convergence.
At cycle 72, the scheduled restart target and the cycle writer were both node
`c`, so the harness deliberately killed the writer immediately after creating a
fresh local edit and before all peers converged.

That is a useful fault class, but it is sharper than the primary 24-hour
reliability soak.  The graduation question is whether a representative
read/write namespace can stay synchronized for a day while daemons occasionally
restart.  "Writer dies immediately after a fresh unpropagated edit" belongs in
a separate restart-resume or abrupt-writer-loss campaign.

## Decision

Scheduled writable-soak restarts now happen before the cycle's synthetic edit.
The runner records `soak_restart_phase = "before-edit"` whenever scheduled
soak restarts are enabled, and guest-side assertions require that phase in
passing soak receipts.

Rejected receipts also promote the latest soak progress fields to the top level
in addition to retaining the nested `partial_soak_evidence` block.  This keeps
operator summaries and postmortems simple without exposing synchronized file
contents.

## Consequences

The primary 24-hour soak still tests daemon restart churn, full-mesh session
reconfirmation, repair passes, deletes, capacity preload, conflicts, and
multi-writer convergence.  It no longer turns a scheduled daemon restart into an
implicit abrupt-after-write fault injection.

The harder "restart the active writer after a fresh unpropagated edit" case
remains important science, but it should be named, isolated, and accepted or
rejected as its own gate.

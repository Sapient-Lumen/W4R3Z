# ADR 0163: Bound runnable incoming files per peer

Status: accepted, 2026-08-25; first two-guest latency gate rejected, superseded by ADR 0164 tuning.

## Context

ADR 0160 reserves the semantic event queue and ADR 0162 fairly resumes transfers that have already
reached that pressure signal. The two exact ADR 0162 `bulk-8` runs prove that callback pressure is
not a sufficient carrier-load signal. `pair.xs9phpya` activates thousands of paced batches and
improves the tail without meeting the 50 ms direct p95 target. `pair.dwo77gs0` never reaches the
event trigger, advances only 375,654 aggregate file bytes at about 5% CPU, and still reaches
504.428 ms render p95 while remote Ratox service remains healthy.

Tox file bytes and Ratox packets share one reliable friend carrier. Waiting for an Agent event queue
to fill permits every accepted file to become runnable in toxcore first. At eight streams per
direction that is sixteen independent bulk producers on the same peer connection. The qualified
`bulk-1` cell already proves the useful target shape: one incoming file runnable at each endpoint,
therefore at most one bulk producer in each direction.

## Decision

The safe receiver admits at most one locally resumed incoming file per peer by default. Additional
accepted files retain their private staging descriptors and remain locally paused. The oldest
eligible waiter receives the next slot. If a runnable transfer and a waiter both remain live for a
20 ms quantum, the manager pauses the runnable transfer and resumes the waiter. One service call
performs at most one rotation per peer.

The explicit controls are:

```text
--file-carrier-window N
--file-carrier-quantum-ms N
```

The window is in `1..min(max-active-receives, 256)` and defaults to one. The quantum is in
`5..1000` ms and defaults to 20 ms. The ordinary service cadence runs even when Ratox is disabled,
so sync and file-only agents cannot strand queued receives. When Ratox is active, Ratox service runs
before carrier rotation on each cadence.

Only incoming transfers are scheduled. The receiver already owns safe admission and can stop its
sender without two independent endpoints trying to schedule the same direction. Outgoing transfer
semantics remain unchanged. An explicit local PAUSE takes ownership of a scheduler-waiting transfer;
the scheduler will not resume it. An explicit RESUME returns it to the fair queue and cannot bypass
the per-peer window. Cancellation, disconnect, and terminal completion remove either runnable or
waiting state normally.

Runtime status adds the complete content-free group:

```text
file-carrier-window-per-peer
file-carrier-rotation-quantum-ms
file-carrier-runnable-receives
file-carrier-waiting-receives
file-carrier-admission-count
file-carrier-rotation-count
file-carrier-pause-count
file-carrier-resume-count
file-carrier-control-failure-count
file-carrier-total-wait-us
file-carrier-maximum-wait-us
```

Strict proofs accept complete absence in historical evidence. New proofs require the whole group,
zero final runnable/waiting receives, zero control failures, and internally coherent admission,
rotation, pause, resume, and wait accounting.

## Consequences

- Concurrent files remain admitted, cancellable, durable in their staging destinations, and visible
  as active or paused; the window is not a transfer-count rejection.
- Aggregate bulk throughput may fall. The scientific gate decides whether the interactive latency
  improvement justifies the default and whether window/quantum tuning is needed.
- Per-peer scheduling prevents one peer's files from consuming another peer's receive window.
- Ratox v1 framing, file IDs, file bytes, authority, sync manifests, and Tox wire APIs are unchanged.
- The reactive 64/16 pacer remains a second semantic-queue safety boundary for the transfer that is
  currently runnable.

## Qualification plan

The deterministic provider gate creates three incoming transfers for one peer, admits exactly one,
rotates through the other two in oldest-first order, proves window/quantum and counter invariants,
then cancels all state. Existing two-object sync convergence must also complete when Ratox is
disabled. GCC Debug and ThreadSanitizer remain mandatory.

The scientific gate is another exact clean-commit direct-UDP `ratox-matrix-bulk-8` run. It must prove
all eight transfers present and progressed, at least eight carrier admissions, positive rotation,
zero carrier/pacer/semantic failures, cancel-to-empty, close, resources/status, strict raw and compact
verification, owner p99 below 2 ms, and direct render p95 below 50 ms. A lifecycle pass without
carrier activation is not a treatment result.

## First two-guest result

Clean commit `328f3a3dbf56c45c9f791268fe1a4ead9f96dd0c` produced strict compact proof
`.sandwurm/exports/pairs/pair.qrggya8w`. All eight files progressed by 151,114,362 aggregate bytes;
the receiver recorded 1,456 admissions and 1,454 rotations with zero carrier failures. Render
p50/p95/p99/max was 24.619/56.247/86.550/137.970 ms and owner p99 was 1.488 ms. This is a large
improvement over ADR 0162 but fails the strict direct p95 threshold.

The 20 ms scheduler also collided with the reactive pacer 141 times as undifferentiated pause
failures, and an already-queued chunk after cancellation became a false final diagnostic. ADR 0164
therefore coordinates typed pause ownership, makes late cancellation events harmless, and tests a
50 ms quantum. The framing remains frozen.

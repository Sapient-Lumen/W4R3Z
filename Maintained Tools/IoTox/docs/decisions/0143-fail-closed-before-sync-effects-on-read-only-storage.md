# ADR 0143: Fail closed before synchronization effects on read-only storage

Date: 2026-08-24

Status: accepted

## Context

Every local synchronization mutation is serialized by the namespace transaction lock and may update
signed attempt, accepted-HEAD, activation, rollback-guard, object, or derived-tree state. A namespace
can become read-only between otherwise valid operations because of administrator action, filesystem
error handling, or degraded media. Treating a lock/setup write failure as permission to continue
would let transport work escape the same persistence boundary that makes retries and crash recovery
truthful.

A permissions-only test would not establish this behavior: a privileged process can bypass mode bits.
The genuine gate therefore places the subscriber namespace on a dedicated loop-backed ext4
filesystem and changes the kernel mount state between operations.

## Decision

Read-only local storage is a terminal typed failure for the current synchronization operation, and
IoTox does not silently fall back to an in-memory or partially durable transaction.

- A pull must acquire and secure the persistent namespace transaction directory before requesting
  immutable objects. If that setup reports `EROFS`, the job fails with zero requested, admitted, or
  committed objects and no candidate staging.
- A failed pull preserves the predecessor object inventory, accepted HEAD, activation record,
  `current` link, and visible tree byte-for-byte.
- After storage becomes writable, recovery is an explicit exact pull retry. It may commit the
  candidate objects and accept the signed successor HEAD, but it still does not activate content.
- Activation on read-only storage fails at the same transaction boundary. It preserves the already
  accepted successor while leaving activation and the visible tree at the predecessor.
- After storage becomes writable, an explicit activation retry of that exact HEAD is required to
  switch the derived tree. No background repair or automatic retry is implied.

## Consequences

The direct-UDP and forced-TCP `sync-tree-read-only` cells now prove the same fail-closed and retry
sequence with one production binary on a real ext4 mount. Storage writability is part of mutation
admission, not a best-effort implementation detail. An operator can distinguish a durable accepted
successor from an activated visible successor after an activation-side storage failure.

This does not prove remount races during an individual write, underlying media correctness, journal
replay after power loss, every possible filesystem/errno, automatic recovery, peak resident-memory
limits, multi-source convergence, or target-fleet behavior.

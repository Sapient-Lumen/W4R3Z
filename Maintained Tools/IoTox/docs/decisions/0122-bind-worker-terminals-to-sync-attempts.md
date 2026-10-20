# ADR 0122: bind worker terminal events to immutable sync attempts

Status: accepted

Date: 2026-08-21

## Decision

An auxiliary worker may resume an incoming file only after the supervisor has reserved one bounded,
non-evicting terminal-event slot and installed a provisional record for the exact route key, worker
incarnation, friend, and file number. The event storage itself is allocated before worker transports
start. Completion, cancellation, peer loss, trust replacement, and file-processing failure move the
reserved record into that queue exactly once; new receives fail before effect when the bound is full.

`SyncTransferCoordinator` is the namespace-scoped bridge above those live handles. Before it asks a
worker to resume an offer, it verifies that the scheduler attempt is active with both route and byte
reservations, acquires the namespace transaction, derives the attempt staging path, and retains the
complete attempt/route/file binding. The accepted worker record must preserve direction, file number,
byte count, and destination. A mismatch cancels the live handle, discards staging, and fences only that
attempt.

A completed terminal event is never itself proof of content. The bridge commits the private staged
file through the existing strict size/digest verification and no-clobber object-store boundary. Only
then does it mark the exact scheduler attempt verified and committed. Cancellation, failure, corrupt
bytes, or conflicting terminal metadata discards the staging path and fences the attempt, releasing
its route and aggregate staging reservations. Unknown or replayed terminal events are counted as
stale and cannot target a replacement attempt.

The coordinator exposes an individual event entrance so a future parent dispatcher can drain the
supervisor once and route events among namespaces. Its optional `service` pump is valid only when one
coordinator is the sole consumer of that drain.

## Consequences

Gate 3 now has an end-to-end process-local path from authenticated worker admission through real-byte
object commit and exact attempt release. Terminal events are bounded and lossless while the process
is alive, and allocation pressure closes new receive admission instead of losing completion truth.

This does not freeze the remote object-offer/request wire record, persist scheduler/binding state,
reconstruct crash fences, advance accepted HEAD or activation, enable an Agent feature, or prove a
genuine two-guest transfer. Those remain explicit gates; a process crash must not yet trigger
automatic reassignment.

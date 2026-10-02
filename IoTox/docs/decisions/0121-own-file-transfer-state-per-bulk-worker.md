# ADR 0121: own file-transfer state per bulk worker

Status: accepted

Date: 2026-08-21

## Decision

Every auxiliary route worker owns a `FileTransferManager` beside its `ToxTransport`. Its active send
and receive counts are bounded by the signed route member's `maximum_active_work`; its file-size bound
comes from the parent Agent configuration. The worker service loop delivers all transport events to
that manager, so offers, chunks, controls, disconnects, and removals are no longer silently ignored.

The supervisor exposes only route-scoped operations. Receive and cancel resolve an exact route public
key plus current worker incarnation and then use that worker's sole configured friend number. They
fail before filesystem or transport effects unless the member is a bulk route, its application
session is confirmed, its local binding was sent, and its reciprocal binding is authenticated.
Protected routes, stale incarnations, and merely connected workers are ineligible. Live snapshots
include the route key and worker ID with each transfer record.

The same rule applies inside the event loop. An offer arriving before exact bulk authentication or
on a protected route is explicitly cancelled instead of being retained as a paused offer. Replacing
primary trust cancels every retained worker transfer before reciprocal authentication is cleared.

Worker shutdown stops its transfer manager before its transport, releasing descriptors and removing
unfinished temporary receives. No authority ledger, namespace root, scheduler, or signer is copied
into a worker.

## Consequences

Bulk file numbers are now contained inside the exact authenticated worker that issued them, while the
parent can correlate operational state using stable route and attempt identities. Signed route work
limits also bound each manager's active transfer count.

This slice does not yet queue required terminal completion/failure events to the coordinator, bind an
offer to a scheduler attempt and derived staging path, or prove positive multi-worker transfer. Those
are the next Gate 3 integration and Sandwurm evidence boundaries.

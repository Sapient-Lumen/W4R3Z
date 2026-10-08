# AnonSync rev0882 revision notes

## Mission-level correction

AnonSync treats exact authorized evidence as the owner of identity, causality,
dispatch, retry, receipts, and visible effects. Rev0881 closed the local
post-callback construction race, but a successfully returned
`SyncReplicaOutboundFileDelivery` remained an ordinary C++ value. It could wait
outside the service after its exact outbox claim or authenticated channel ceased
to be current, then be passed to a transport that had no durable-attempt
context.

Rev0882 establishes one reviewed local transition from exact sender-attempt
authority to TLS stream progress. It does not claim distributed atomicity or
remote delivery. It makes the first ambiguous transport frontier explicit and
keeps terminal receiver evidence load-bearing.

## C++ implementation

### Narrow SQLite/TLS composition

New `sync_replica_file_tls_dispatch` APIs compose the existing file-delivery
service with the authenticated TLS channel without merging their policy layers.
For one already-prepared outbound delivery the implementation:

1. freezes the bounded outbound value and channel context outside SQLite;
2. reconstructs the exact evidence request from claim, local actor, peer actor,
   service kind, attempt identity, and TLS exporter binding;
3. validates and canonically re-encodes the file request and digest;
4. acquires the exact outbox claim through
   `SyncReplicaSqliteOutboxDispatchGuard` under `BEGIN IMMEDIATE`;
5. re-proves the live authenticated channel and current claim-derived request;
6. proves direct nonblocking socket BIO readiness;
7. writes the complete encrypted eight-byte AnonSync record prefix;
8. commits and releases the SQLite writer; and
9. writes the immutable body through an exclusive move-only continuation.

The companion claim-and-dispatch API claims the next due File operation and
immediately executes the same path.

### Truthful failure ownership

Before successful prefix return, every exception rolls back the guard first,
poisons any stream that may have partial framing state, and attempts exact claim
release through the sender's positive bounded retry policy. The body has not
been supplied through a reusable channel, so a fresh attempt cannot be confused
with a complete old frame on that discarded stream.

After successful prefix return, the attempt is ambiguous. A SQLite commit
failure or body failure poisons the channel but deliberately leaves the exact
claim live. TLS progress never invokes outbox settlement. Only the existing
validated receipt path, an explicit exact release, or owned-clock expiry can
change durable attempt state.

### Exclusive TLS record continuation

`SyncReplicaTlsRecordWriteContinuation` is noncopyable, no-throw movable, and
privately minted only after the full prefix is accepted by `SSL_write_ex()`. It
binds the exact advertised body length and carries the readiness policy into a
second live proof before body transfer.

The authenticated TLS state now owns `record_write_active_`. While a
continuation is live, another prefix begin, ordinary one-shot write, or record
read fails. Completion releases the reservation. Abandonment, move-assignment
over an active continuation, size mismatch, readiness contradiction, body I/O
failure, or process/thread/session contradiction poisons the stream.

This state-owned reservation is an important audit correction. The first draft
of rev0882 put exclusivity only in wrapper conventions, permitting a same-thread
caller to interleave another framed operation before the first body. Runtime
coverage now proves rejection while preserving the original continuation.

### Enforced nonblocking socket proof

The database composition uses
`SyncReplicaTlsRecordWriteReadinessPolicy::RequireNonblockingSocket`. On Unix it
requires:

- direct read and write BIO methods equal to `BIO_TYPE_SOCKET`;
- nonnegative `SSL_get_rfd()` and `SSL_get_wfd()` observations;
- successful `getsockopt(SOL_SOCKET, SO_TYPE)` for every distinct descriptor;
  and
- `fcntl(F_GETFL)` showing `O_NONBLOCK`.

The checks run before prefix reservation and again before body transfer. This
prevents the sole SQLite writer from entering an opaque or blocking transport
operation. Non-Unix platforms fail closed for this strict composition until an
equivalent observation owner exists. The generic caller-managed record API is
unchanged in policy and delegates to the same framing state machine.

### Shared claim-to-request construction

Generic delivery, file delivery, and immediate TLS dispatch now use one
`make_sync_replica_delivery_request_from_claim_or_throw()` implementation. It
validates destination against the authenticated peer, operation identity,
local actor, optional service kind, active claim ID, and positive attempt
number. This removes divergent security-sensitive constructors.

The file service also centralizes pre-dispatch exact-release and typed guard
failure handling. The service remains transport-neutral; OpenSSL is present only
in the separate composition target.

## Runtime additions

The TLS runtime executable grows from 25 to 74 checks. New coverage includes:

- move-only/no-throw continuation traits and exact successful framing;
- rejected overlapping begin, generic write, and read while the original
  continuation remains usable;
- post-finish reuse rejection;
- mismatch, abandonment, prefix failure, and body failure poisoning;
- blocking socket rejection before bytes, exact release, and untouched-channel
  reuse through caller-managed policy;
- non-socket descriptor rejection despite `O_NONBLOCK`;
- stale-attempt zero-byte behavior;
- due retry with a fresh claim ID, attempt number, and exact canonical frame;
- tampered frame/digest preflight failure with exact release;
- successful transfer leaving the claim live awaiting receipt;
- same-claim bounded lease renewal under guarded re-attestation; and
- forced two-mebibyte nonblocking body backpressure after successful prefix,
  proving that the claim remains live with no retry-release provenance.

## Audit/refactor

`tools/audit_sync_file_tls_dispatch.py` adds 28 deterministic checks over the
composition boundary, dependency direction, canonical builder, continuation
ownership, readiness proof, critical-section ordering, failure split, runtime
matrix, package surface, and explicit nonclaims. Four neighboring audits were
updated to recognize the shared constructor/member helpers without relaxing
their contracts.

The audit is lexical structure/inventory evidence only. It does not prove
OpenSSL partial-progress semantics, SQLite serialization, crash recovery,
exception safety, peer receipt, or remote effect behavior.

## Validation

Fresh cloudtainer evidence for rev0882 records:

- GCC 14.2 Debug full all-target build: 311 fresh Ninja actions;
- complete registered CTest gate: 192/192;
- complete audit-named CTest block: 61/61;
- focused GCC Debug: 13/13 executables, 5,198/5,198 checks;
- focused Clang 17 Release with C++ `-Werror`: 5,198/5,198 checks;
- focused GCC ASan/UBSan with leak detection and bundled SQLite C
  instrumentation: 5,198/5,198 checks;
- repeated mixed authority gate: 20 iterations, 100/100 executions,
  5,920/5,920 checks;
- targeted first-prefix/TLS gate: 100 iterations, 7,400/7,400 checks; and
- selected source audits: 505/505 checks across 17 audits.

Final no-work dependency closure, active-projection binding, evidence indexing,
manifest verification, directory verification, and ZIP verification are
recorded in `REVISION_EVIDENCE/rev0882/` or generated externally after the final
immutable package bytes are sealed.

## Deliberate nonclaims

Rev0882 does not claim:

- atomic SQLite-plus-TLS dispatch or proof of peer receipt from a local write;
- exactly-once network delivery or remote execution;
- a resumable event-loop owner for OpenSSL WANT states;
- durable `dispatch_started`/body-offset state across process crash;
- automatic lease heartbeat, cancellation, transfer-age, chunking, or resume;
- acceptance of filtered, buffered, memory, QUIC, or custom BIOs at the guarded
  prefix frontier;
- portable strict readiness proof outside Unix;
- receiver-loop or shipped-executable integration;
- complete retry/dead-letter/wake or payload-availability policy;
- complete membership, enrollment, key rotation, revocation, recovery, or
  rollback protection;
- anti-entropy, causal stability, compaction, tombstone collection, or rejoin;
- production-scale indexed ownership replacing the O(history) oracle;
- anonymity, unlinkability, endpoint hiding, or traffic-analysis resistance;
- externally trusted signed provenance, full-project Clang/sanitizer coverage,
  ThreadSanitizer, Windows runtime coverage, or formal proof.

## Next engineering sequence

The highest-value next slice is a small production-shaped replica service that
owns one nonblocking event loop, reads and writes exact framed messages, invokes
the existing receiver file-delivery service, and returns exact receipts on the
same authenticated channel. Crash injection should span prefix, arbitrary body
offsets, receiver evidence commit, payload staging, immutable rename,
directory durability, receipt write, and sender settlement. The shipped
executable should then migrate to that path before assurance work expands into
more isolated libraries.

Primary rationale, source research, failure matrix, and speculation are in
`TLS_FIRST_PREFIX_DISPATCH_AUDIT_rev0882.md` and
`REVISION_EVIDENCE/rev0882/RESEARCH.md`.

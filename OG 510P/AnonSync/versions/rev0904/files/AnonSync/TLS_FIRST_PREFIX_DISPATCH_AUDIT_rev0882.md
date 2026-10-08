# TLS First-Prefix Dispatch Audit — rev0882

## Executive finding

AnonSync's newer sender stack had reached a strong local construction cutpoint in
rev0881, but the result still escaped as an ordinary C++ value. A scheduler,
queue, or caller could retain that frame after its exact SQLite claim expired,
was released, was settled, or was replaced. The authenticated TLS channel could
also be moved, poisoned, or replaced while those already-encoded bytes waited.
The next call to the generic record writer knew nothing about the durable claim
that had originally authorized the frame.

That gap is the difference between **historical evidence that a frame was once
constructible** and **live authority to begin this exact attempt on this exact
channel**. Rev0882 adds a deliberately narrow composition owner for the first
production-shaped sender frontier:

1. freeze one bounded file-delivery value and authenticated channel context;
2. reconstruct the canonical request, frame, and digest outside SQLite;
3. acquire the exact current outbox claim under `BEGIN IMMEDIATE`;
4. re-prove the live TLS capability and current request identity while that
   writer guard excludes competing outbox transitions;
5. prove the TLS read and write BIOs are socket-backed and `O_NONBLOCK`, then
   write the complete encrypted eight-byte AnonSync record-length prefix;
6. commit and release SQLite; and
7. re-prove nonblocking readiness and write the potentially large immutable body
   through a move-only exclusive TLS continuation.

The correction does not pretend that SQLite and TLS are one transaction. It
instead makes the remaining ambiguity explicit and keeps receiver idempotency
and terminal effect receipts load-bearing.

## Mission fit

The heart of AnonSync remains exact authority accounting. Canonical evidence
owns identity and causality. A claim owns one sender attempt. A live
authenticated channel owns one transport context. Receiver publication owns a
visible effect. A terminal receipt may retire sender intent only after its exact
remote state is durable. Local copies, summaries, clocks, socket buffers, and
successful API returns are subordinate observations.

Rev0882 applies that hierarchy at the send boundary. The frame is re-derived
from the exact claim instead of trusted as caller bytes. TLS progress does not
settle the outbox. A failed stream is poisoned rather than resynchronized by
wishful parsing. A stale attempt cannot emit a new body merely because a C++
object still exists.

## The prior authority gap

The rev0881 service correctly performed arbitrary payload acquisition before a
scope-bound dispatch guard, re-attested the claim, built the canonical frame,
and returned it only after committing. It explicitly warned that the returned
frame was not send authority. There was nevertheless no production composition
that enforced the warning.

A caller could perform this sequence:

1. receive `SyncReplicaOutboundFileDelivery` for claim A;
2. place it in an ordinary queue;
3. let claim A be exactly released or expire;
4. mint claim B for the same operation; and
5. still call `write_sync_replica_tls_record_or_throw()` with claim A's bytes.

The receiver would reject or deduplicate stale identity, so canonical history
was not necessarily corrupted, but the sender could waste bandwidth, create
spurious receiver work, and confuse settlement bookkeeping. More importantly,
the implementation had no single place that owned the transition from durable
attempt authority to stream progress.

## Corrected composition boundary

### Frozen bounded input

`dispatch_sync_replica_outbound_file_delivery_over_tls_or_throw()` first copies
the outbound value and channel context. File payload and frame limits bound that
copy. It then:

- reconstructs the evidence request from the claim, local actor, peer actor, and
  channel binding;
- requires `SyncReplicaValueKind::File`;
- validates the full file request;
- re-encodes the canonical frame and compares exact bytes; and
- recomputes the canonical request digest and compares it.

All allocations and caller-data contradictions occur before the SQLite writer
is acquired. A failure exact-releases the same claim under sender-owned bounded
retry policy, or reports the combined original/release contradiction.

### Guarded exact re-attestation

The SQLite owner then acquires `SyncReplicaSqliteOutboxDispatchGuard`. Missing,
stale, and expired outcomes are typed. For an acquired guard, the composition
owner re-proves the opaque TLS delivery authority and rebuilds the request from
the guard's current claim. A valid same-claim lease renewal is tolerated because
it does not alter canonical wire identity. Destination, operation, claim ID,
attempt number, actor, and channel binding must remain exact.

`BEGIN IMMEDIATE` is useful here because SQLite documents that it starts a write
transaction immediately and fails when another writer is active. The claim is
therefore serialized against another connection's release, renewal, settlement,
or replacement while the final pre-send proof and fixed-size prefix operation
run.

### Exclusive TLS continuation

The generic TLS writer was refactored into one state machine:

- `begin_sync_replica_tls_record_write_or_throw()` validates the frame size,
  reserves the stream, writes the complete eight-byte prefix, and returns a
  move-only continuation;
- `SyncReplicaTlsRecordWriteContinuation::finish_or_throw()` requires exactly
  the prefixed number of body bytes, re-proves live process/thread/session
  authority, writes the body, and releases the stream reservation; and
- the existing one-shot writer delegates to begin plus finish.

The private continuation constructor, no-throw move operations, and copied
label ensure that a successful prefix write cannot be followed by a local
handoff allocation failure. The composition selects
`RequireNonblockingSocket`; the state first requires direct `BIO_TYPE_SOCKET`
read and write BIOs, then observes both `SSL_get_rfd()` and `SSL_get_wfd()`,
proves each visible descriptor is a kernel socket with
`getsockopt(SOL_SOCKET, SO_TYPE)`, and checks `F_GETFL/O_NONBLOCK` before prefix
reservation. The continuation records that policy and repeats the socket and
nonblocking proofs before body I/O. Abandonment, size mismatch, body I/O
failure, readiness contradiction, or live-session contradiction permanently
poisons the stream.

During implementation, a serious same-thread overlap defect was found in the
first draft. The continuation existed only as a wrapper convention; the same
thread could begin a second record or call the ordinary read/write API before
finishing the first body. The live authenticated TLS state now owns an explicit
exclusive `record_write_active_` reservation. A second begin, generic write, or
record read is rejected while the original continuation remains valid. This is
the audit/refactor correction in rev0882: framing exclusivity is enforced by the
shared SSL owner, not by every caller remembering a rule.

### Writer release before body

After the complete prefix is accepted by OpenSSL, the SQLite guard commits and
is destroyed before body transfer. This avoids holding the sole database writer
across a payload-sized operation. The body remains immutable and bound to the
continuation's exact length.

A failure before successful prefix return rolls back the guard, poisons the
stream, and exact-releases the claim. After prefix return, commit or body failure
leaves the claim live and the stream poisoned. That is conservative ambiguity:
the sender waits for a terminal receipt, an explicit exact transition, or
owned-clock expiry rather than guessing that the peer observed nothing.

## OpenSSL SSL_write semantics

OpenSSL's current `SSL_write_ex()` documentation states that, without
`SSL_MODE_ENABLE_PARTIAL_WRITE`, success means the complete requested
application buffer was written to the SSL connection. A nonblocking BIO may
instead return `SSL_ERROR_WANT_READ` or `SSL_ERROR_WANT_WRITE`. OpenSSL also
documents that an SSL object created over a nonblocking descriptor inherits
nonblocking behavior. The AnonSync composition now verifies both descriptors
immediately before prefix progress and the continuation verifies them again
before body progress. A filtered/custom BIO is rejected even when it can expose
an underlying descriptor. Descriptor visibility and `O_NONBLOCK` are also not
enough: a socket-method descriptor BIO can wrap a pipe, so the implementation
requires a successful `SO_TYPE` query before either frontier.

OpenSSL explicitly warns that the data passed to a write that returns
`SSL_ERROR_WANT_READ` or `SSL_ERROR_WANT_WRITE` might have been partially
processed and must be retried with the same arguments. Rev0882 deliberately
does not attempt such a retry. It poisons the channel. Before successful prefix
return, no body call has occurred, so even a remotely observable prefix cannot
form a complete AnonSync request; the exact claim can be released only because
the stream is thereafter unusable through this capability. After successful
prefix return, any body readiness loss is ambiguous and the claim remains live.

Primary sources:

- OpenSSL SSL_write documentation:
  https://docs.openssl.org/3.5/man3/SSL_write/
- OpenSSL mode documentation:
  https://docs.openssl.org/3.5/man3/SSL_CTX_set_mode/
- OpenSSL descriptor/BIO behavior:
  https://docs.openssl.org/3.5/man3/SSL_set_fd/
- Linux/POSIX descriptor flag observation:
  https://man7.org/linux/man-pages/man2/fcntl.2.html

"Written to the SSL connection" is intentionally weaker than delivered to the
peer. OpenSSL may buffer encrypted data, the kernel may buffer it again, the
connection can fail later, and the remote application may reject the frame.
The complete prefix is therefore a local stream cutpoint only.

## SQLite transaction semantics

SQLite documents that `BEGIN IMMEDIATE` begins a write transaction immediately
and may return `SQLITE_BUSY` when another write transaction is active. SQLite
also serializes writers rather than creating distributed atomicity.

Primary sources:

- https://www.sqlite.org/lang_transaction.html
- https://www.sqlite.org/isolation.html

The exact supported claim is narrow: another SQLite connection cannot commit a
competing sender transition while the guard is alive. SQLite does not know
whether OpenSSL, TCP, a peer process, a receiver database, or a filesystem has
made progress.

## TLS record protection is not application acknowledgement

TLS 1.3 protects application records with traffic keys and sequence-derived
nonces, but it does not turn a successful local write into receiver application
state. RFC 8446 also makes application-layer provisioning necessary where one
party needs to know how the other party classified authentication or state.

Primary source:

- RFC 8446, especially the record layer and security considerations:
  https://www.rfc-editor.org/rfc/rfc8446.html

AnonSync therefore retains its own request identity, durable admission result,
effect receipt, and sender settlement protocol above TLS.

## Failure matrix

| Frontier | Observable local result | Stream authority | Exact outbox action | Remote claim |
| --- | --- | --- | --- | --- |
| frozen copy/allocation fails | exception | untouched | exact retry release attempted | no send claimed |
| channel/canonical preflight fails | exception | untouched | exact retry release | no send claimed |
| guard says missing/stale/expired | typed exception | untouched | owner result remains authoritative | no send claimed |
| direct socket/nonblocking readiness cannot be proved | typed exception | untouched | rollback, then exact retry release | no send claimed |
| guarded channel/request reproof fails | exception | untouched or poisoned by live reproof | rollback, then exact retry release | no body claimed |
| prefix write fails/readiness is lost | exception | poisoned | rollback, then exact retry release | incomplete framing only; no body supplied |
| prefix succeeds, guard commit fails | exception | poisoned on continuation unwind | claim remains live conservatively | peer receipt not known |
| guard commits, body fails | exception | poisoned | claim remains live/ambiguous | partial, full, or no body observation possible |
| body succeeds | return | reusable | claim remains live awaiting receipt | receipt/admission/effect still unknown |
| validated terminal publication receipt | separate service path | independent | exact settlement | durable effect identity bound |

The implementation never uses TLS send completion as `settle_outbox` authority.

## Runtime evidence added

The TLS runtime executable now proves:

- continuation success preserves exact frame bytes;
- the continuation is move-only and transfers, rather than duplicates,
  authority;
- same-thread overlap begin, generic write, and read attempts are rejected;
- rejected overlap does not invalidate the original continuation;
- reuse after finish is rejected;
- size mismatch, abandonment, and body failure poison the stream;
- a stale released attempt emits no new TLS record through the composition API;
- a blocking TLS socket is rejected before prefix I/O, exact-releases the claim,
  and leaves the untouched channel reusable by the generic caller-managed API;
- a nonblocking pipe installed through a descriptor BIO is rejected because
  `O_NONBLOCK` does not prove socket backing;
- a due retry mints a fresh claim/attempt and sends that exact canonical frame;
- successful body transfer leaves the outbox live awaiting a receipt;
- tampered caller frame bytes fail canonical preflight, exact-release the claim,
  and leave the untouched channel reusable;
- a failed prefix write exact-releases with retry provenance and poisons the
  channel;
- forced nonblocking backpressure after a successful prefix leaves the exact
  claim live with no retry-release provenance; and
- a bounded same-claim lease renewal is carried through guarded re-attestation
  without changing frame identity.

The post-prefix case uses a two-mebibyte frame, a nonblocking socket, a small
send buffer, and no receiver read to force body readiness loss after observable
TLS ciphertext. This distinguishes real post-prefix ambiguity from a merely
closed socket before any stream progress.

## Refactor assessment

Rev0882 removes two forms of security-sensitive duplication.

First, generic evidence delivery and file delivery had separate
claim-to-request constructors. They now call one
`make_sync_replica_delivery_request_from_claim_or_throw()` implementation that
checks destination, operation identity, local actor, optional service kind,
claim ID, and attempt number. The dispatch composition also uses that builder
both before and inside the guard.

Second, the generic one-shot TLS record writer now delegates to the same
begin/continuation state machine used by the composed file sender. Framing,
poisoning, live-session reproof, and exclusive ownership no longer have separate
implementations.

The new file/TLS composition remains its own small static library. The
file-effect service does not include OpenSSL and the TLS transport does not gain
SQLite or file-effect policy. That dependency direction preserves auditability.

## Peer receipt is not claimed

A successful prefix or body write does not prove that:

- the peer kernel received ciphertext;
- the peer TLS stack authenticated a complete record;
- the receiver parsed or admitted the request;
- canonical evidence was committed;
- payload bytes were durably staged;
- a namespace effect was atomically published; or
- the terminal receipt reached or settled the sender.

Those remain separate protocol and durability frontiers.

## Deliberate nonclaims and remaining severe gaps

Rev0882 does **not** claim:

- atomic SQLite-plus-TLS dispatch;
- exactly-once network delivery or exactly-once remote execution;
- a durable sender `dispatch_started` state across process crash;
- an event-loop continuation that resumes `WANT_READ`/`WANT_WRITE` safely;
- acceptance of custom, buffered, memory, QUIC, or otherwise non-socket BIOs at
  the SQLite first-prefix frontier;
- portable nonblocking-descriptor observation outside the Unix implementation;
- automatic lease heartbeat while a large body is in flight;
- prevention of duplicate transfer when the body can cross lease expiry;
- receiver process integration with this sender seam;
- a production executable using the newer owner/service stack;
- payload chunking, resume, congestion policy, dead-letter scheduling, or retry
  jitter;
- membership enrollment, key rotation/revocation/recovery, compaction, rejoin,
  anonymity, unlinkability, endpoint hiding, or traffic-analysis resistance; or
- externally trusted signed build provenance.

The blocking-I/O caveat is now enforced rather than documented. A bounded
prefix can still wait indefinitely on a blocking BIO, so the composition rejects
any channel whose read and write socket flags cannot be observed as
`O_NONBLOCK`. This gives the SQLite critical section a fail-fast readiness
boundary. It is still not a complete event-loop design: `WANT_READ` or
`WANT_WRITE` poisons the channel and schedules a fresh exact attempt instead of
retaining immutable buffers and resuming on readiness. That is conservative and
safe, but can waste handshakes and bandwidth under sustained backpressure.

The body can cross lease expiry because the writer is intentionally released
before payload transfer. A second worker may eventually mint a fresh attempt
while the first stream is still draining. Receiver idempotency protects
correctness, but duplicate bandwidth and scheduling pressure remain. A later
state machine should define heartbeat ownership, cancellation, body age, and
connection teardown without trusting wall time as causal authority.

## Recommended next sequence

1. Put the new composition behind a small replica service executable rather
   than leaving it test-only.
2. Replace fail-on-readiness-loss with an event-loop-owned immutable
   continuation that resumes only the same OpenSSL write operation under a
   monotonic transfer-age policy, without retaining a SQLite writer.
3. Connect a real receiver loop that reads the frame, invokes the existing
   file-delivery service, and writes the exact receipt on the same authenticated
   channel.
4. Inject process crashes after prefix, after arbitrary body offsets, after
   receiver evidence commit, after payload staging, after rename, after
   directory durability, after receipt write, and after sender settlement.
5. Define durable in-flight/ambiguous attempt state only where restart evidence
   demonstrates that the current live-lease model is insufficient.
6. Add lease-heartbeat and transfer-age policy, then chunking/resume, while
   differentially checking canonical results against the existing full-history
   oracle.
7. Keep the shipped executable migration as the milestone: assurance around an
   unused library is not product capability.

## Audit status

`tools/audit_sync_file_tls_dispatch.py` inventories dependency direction,
shared builders, continuation ownership, source ordering, test vocabulary,
package requirements, and explicit nonclaims. It is lexical hygiene only. It
does not prove OpenSSL progress, SQLite exclusion, exception safety, crash
recovery, peer receipt, or terminal effect semantics. Those require compiled
runtime, sanitizer, stress, and multi-process crash evidence.

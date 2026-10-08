# TLS file-dispatch continuation audit — rev0887

## Mission boundary

AnonSync is an evidence-authorized convergence system. Exact durable history and
live owned capabilities govern operation identity, causal admission, dispatch,
retry, receiver effect, receipt, and sender settlement. A TLS return code,
readiness notification, file-descriptor integer, locally completed write, or
source-level audit is only subordinate evidence. None of those observations may
silently become peer admission or visible-effect authority.

The file-delivery path crosses four independently owned boundaries:

1. a SQLite outbox claim identifies one exact destination and attempt;
2. an authenticated TLS channel owns one exact live SSL/BIO/socket lifetime;
3. the receiver evidence/effect owners decide causal admission and visible
   publication; and
4. an authenticated terminal effect receipt alone may retire the sender intent.

Rev0887 repairs the composition between the first two boundaries and exercises
all four in one runtime scenario.

## Severe composition defect in the parent

Rev0886 correctly introduced a heap-stable, move-only TLS record writer. It can
retain the exact `SSL_write_ex` pointer, length, offset, WANT direction, socket
lifetime, and exclusive stream reservation across nonblocking backpressure. It
also introduced a bounded `poll(2)` owner that spends one absolute monotonic
deadline and advances at most one TLS operation per wakeup.

The durable file dispatcher did not expose that capability. After accepting the
complete eight-byte TLS record prefix under the exact SQLite outbox guard, it
committed and released SQLite and immediately called
`SyncReplicaTlsRecordWriteContinuation::finish_or_throw()`.

For a strict nonblocking socket, an ordinary `SSL_ERROR_WANT_READ` or
`SSL_ERROR_WANT_WRITE` therefore caused the compatibility helper to abandon the
accepted-prefix record and poison an otherwise healthy channel. The durable
claim correctly remained ambiguous, so safety was fail-closed, but liveness and
resource use were severely wrong:

- a normal event-loop condition destroyed the channel;
- the sender had to wait for claim expiry or an explicit policy decision;
- the receiver could retain a partial frame until connection teardown;
- authentication and handshake work were discarded;
- the raw resumable writer was a correctness island not reachable through the
  durable file-delivery API; and
- the convenient `claim_and_dispatch...` entry point continued steering callers
  toward the collapsing path.

This is the kind of defect that can survive extensive component tests: each
component is locally correct, but the composition erases the stronger contract.

## Corrected authority model

Rev0887 adds `SyncReplicaFileTlsDispatchContinuation`. It is non-default-
constructible, move-only, and no-throw movable. One instance jointly owns:

- the exact frozen `SyncReplicaOutboundFileDelivery` (claim, canonical request,
  canonical frame, and digest);
- the underlying exact TLS record-write continuation;
- the committed body cutpoint; and
- one explicit terminal state: Writing, Complete, or Failed.

The object is minted only by
`begin_sync_replica_outbound_file_delivery_over_tls_or_throw()` after:

1. bounded caller-owned data is copied and canonically revalidated outside
   SQLite;
2. the live authenticated channel is preflighted;
3. the exact outbox claim is reacquired under the SQLite dispatch guard;
4. the channel and claim-to-request mapping are re-attested inside that guard;
5. the complete encrypted record prefix is accepted on a strict direct
   nonblocking socket;
6. the guard's owned-clock observation is committed; and
7. the SQLite writer is released.

Only no-throw ownership moves remain after prefix acceptance. The returned
continuation exclusively owns every body step. It exposes:

- `advance_or_throw()` for one bounded TLS body operation;
- `pending_readiness_or_throw()` for the exact re-proved WANT target;
- `poll_and_advance_or_throw(deadline)` for one bounded wait/step;
- exact body/frame cutpoints;
- completion state; and
- the exact frozen outbound evidence for later receipt validation.

`claim_and_begin_next_file_delivery_over_tls_or_throw()` makes this the direct
nonblocking convenience path. The old synchronous dispatch and claim/dispatch
functions remain compatibility adapters and are explicitly documented as
inappropriate when ordinary WANT is possible.

## State machine

| State | Durable claim | TLS stream | Permitted transition |
|---|---|---|---|
| Preflight | claimed | idle | exact release on local/channel/canonical failure; otherwise acquire guard |
| Guarded prefix | exact guard held | Write reservation; prefix not or fully accepted | pre-prefix failure rolls back then exact-releases; full prefix commits ambiguity |
| Writing body | live and ambiguous | exclusive continuation with exact pending operation | bounded advance, bounded poll, move, local completion, or terminal poison |
| Local complete | still live | record reservation released; stream reusable | wait for authenticated receipt; local completion cannot settle |
| Receiver published | still live until receipt applied | independent receiver cutpoint | emit terminal effect receipt bound to request/channel/effect cutpoint |
| Settled | retired | independent | only exact authenticated Published/AlreadyPublished receipt |

A process crash cannot preserve an OpenSSL continuation or byte-stream session.
The durable recovery unit remains the outbox claim. A crash after prefix
acceptance leaves ambiguity; retry occurs through expiry/new claim/new channel,
and receiver idempotency reconciles duplicate canonical evidence/effect.

## OpenSSL and poll requirements

The implementation follows the current primary contracts:

- OpenSSL documents that nonblocking `SSL_write_ex` can require read or write
  readiness, and that a retry must repeat the same write arguments until the
  operation completes. Rev0887 delegates exact pointer/length retention to the
  rev0886 heap-stable transport continuation.
  <https://docs.openssl.org/3.5/man3/SSL_write/>
- OpenSSL requires `SSL_get_error` to be called in the same thread immediately
  after the failed I/O operation, with no intervening OpenSSL call and an empty
  thread error queue before I/O. That remains inside the transport leaf rather
  than the file-dispatch wrapper.
  <https://docs.openssl.org/3.5/man3/SSL_get_error/>
- `poll(2)` error and hangup bits are readiness observations, not TLS protocol
  truth. The poll owner wakes one exact continuation step and lets channel
  re-attestation plus OpenSSL classify retry, clean close, truncation, or fatal
  failure.
  <https://man7.org/linux/man-pages/man2/poll.2.html>
- TLS shutdown only concerns closure of the TLS connection. It is not evidence
  that an application request was durably admitted or published.
  <https://docs.openssl.org/3.5/man3/SSL_shutdown/>

## Failure matrix

| Frontier | Observation | Stream consequence | Durable claim consequence |
|---|---|---|---|
| before frozen copy/canonical preflight | allocation, malformed frame, digest mismatch, stale channel | untouched or channel-classified preflight failure | exact release through service-owned clock policy |
| guard acquisition | missing/stale/expired/replaced claim | no TLS bytes | owner disposition; no fabricated release |
| guarded re-attestation | channel changed or claim no longer maps to frozen request | no prefix | rollback then exact release when still exact |
| prefix write before full prefix acceptance | socket/TLS failure | poison because framing may be uncertain | rollback then exact release |
| after full prefix, before guard commit | SQLite commit failure | continuation destruction poisons stream | claim remains live/ambiguous |
| body returns WANT | normal nonterminal backpressure | exact pending operation retained | unchanged and live |
| poll deadline expires | scheduling policy cutpoint only | exact target/pointer/length/cutpoint retained | unchanged and live |
| continuation move | ownership transfer | same heap-stable TLS operation | same exact frozen claim/request |
| body terminal failure or abandonment | cannot resynchronize framed stream | poison | live/ambiguous; no immediate retry fabrication |
| local body complete | local TLS progress | stream reservation released | live; not settled |
| receiver Published/AlreadyPublished receipt validates | terminal remote effect evidence | independent | exact sender intent retires |

## Runtime evidence added

The focused TLS test now constructs two independent replica SQLite owners, a
separate receiver effect SQLite owner, a real mutually authenticated TLS 1.3
socket pair, and a maximum-policy two-megabyte payload.

The sender uses `claim_and_begin...` on a deliberately constrained nonblocking
socket. The test proves:

1. the returned outer continuation retains the exact operation, claim, payload,
   canonical frame, and digest;
2. polling before WANT rejects without consuming the active continuation;
3. body progress reaches real kernel backpressure;
4. moving the continuation preserves the exact WANT target and body cutpoint;
5. an already-expired poll returns `DeadlineExpired` without changing TLS state
   or the complete sender SQLite snapshot;
6. a nonblocking receiver and bounded cooperative poll loop transfer the exact
   canonical frame;
7. every successful writer poll step remains at or below 64 KiB;
8. local TLS completion leaves the exact outbox claim live;
9. the receiver stages evidence/payload and atomically publishes exact visible
   bytes;
10. the terminal receipt binds the receiver effect cutpoint;
11. the receipt crosses authenticated TLS in the reverse direction; and
12. only applying that exact receipt settles the sender and converges canonical
    evidence digests.

The older synchronous body-backpressure test remains. It proves the legacy
adapter still fails closed and preserves ambiguity rather than pretending a
failed synchronous send is retry-safe.

## Audit/refactor outcome

The file-dispatch source now has one authoritative guarded-prefix constructor.
The synchronous function delegates to it, and the nonblocking claim convenience
function delegates to the same constructor. SQLite/TLS composition logic is no
longer duplicated between blocking and event-loop paths.

The structural audit is revised to inspect the actual begin function rather
than the now-trivial synchronous wrapper. It also inventories move-only outer
ownership, poll delegation, pre-WANT nonterminal behavior, exact deadline
retention, terminal effect coverage, and the rev0887 release surface. The audit
continues to disclaim semantic authority: lexical order cannot prove socket,
SQLite, crash, or remote effect behavior.

## Remaining waste and next corrections

### Frame memory amplification

At this stage the caller-prepared outbound value and the outer continuation both
retain a canonical request frame, while the underlying TLS continuation owns a
separate heap-stable copy required for exact WANT retry. During handoff, a large
frame can therefore exist in several copies. This is bounded by protocol limits
and safer than borrowing mutable caller memory, but it is not a scalable payload
architecture.

A future refactor should introduce one immutable canonical-frame allocation with
an explicit stable-lifetime owner shared by transport and receipt metadata, or
move to chunked content-addressed payload transfer where the small request frame
commits to independently bounded chunks. Any sharing design must preserve:

- pointer stability across WANT;
- no caller mutation;
- destruction order (transport poison before metadata release);
- aggregate memory quotas; and
- exact receipt binding.

### No production session owner yet

The runtime now demonstrates the desired end-to-end sequence, but the shipped
executable still does not instantiate a process/thread-affine session owner that
manages read/write continuation queues, readiness registration, claim leases,
receiver requests, terminal receipt writes, shutdown, and reconnect.

The next narrow production milestone should be one `SyncReplicaFileTlsSession`
(or equivalent) that exclusively owns one authenticated channel on one thread,
has bounded inbound/outbound queues and memory budgets, and drives both request
and receipt continuations without changing their exact deadlines or retry
arguments. A session close after any uncertain frame must discard the stream;
durable recovery must re-enter through outbox identity and receiver idempotency,
not through serialized OpenSSL state.

### Receipt path still uses the synchronous adapter in this test

The large request exercises nonblocking continuation ownership. The terminal
receipt is small and is sent with the existing caller-managed blocking adapter.
A production session needs a symmetric queued write continuation for receipts,
including prioritization so a saturated request queue cannot starve effect
acknowledgments and hold remote claims unnecessarily.

### No anonymity claim

TLS authentication, payload confidentiality, and exact evidence settlement do
not by themselves hide device identities, traffic timing, endpoint addresses,
message sizes, or communication graphs. Rev0887 adds no anonymity,
unlinkability, relay, discovery, membership, revocation, or traffic-analysis
resistance property.

## Nonclaims

Rev0887 does not claim:

- production event-loop integration or use by `anonsync_core`;
- crash-resumable TLS records;
- durable partial-record continuation across process restart;
- exactly-once network delivery or execution;
- safe concurrent raw `SSL*`, BIO, descriptor, or socket-mode mutation;
- thread/process migration of a continuation;
- bounded OpenSSL internal CPU work or wall-clock completion;
- complete retry, dead-letter, membership, key rotation, or revocation policy;
- scalable indexed replica/effect ownership;
- anti-entropy, compaction, tombstone collection, or offline rejoin;
- anonymity, unlinkability, endpoint hiding, or traffic-analysis resistance;
- ThreadSanitizer coverage, formal proof, or externally signed provenance.

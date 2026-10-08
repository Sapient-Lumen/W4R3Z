# TLS receiver exchange cutpoint audit — rev0887

## Mission connection

AnonSync is an authority-accounting system. Exact authenticated evidence and
owned capabilities decide whether an operation may enter causal history, create
one visible file effect, emit a terminal receipt, retire sender intent, or be
retried. A socket descriptor, a complete local TLS write, a timeout, or a
summary cannot manufacture any of those transitions.

The sender path already had a production composition owner for:

> exact SQLite claim → live TLS re-attestation → complete encrypted record
> prefix → resumable request body

The receiver path did not have its counterpart. Tests and future callers had to
manually compose record read, `receive_request_or_throw`, record write, and
receipt read. That manual choreography was a serious integration gap because
its most important ordering rule existed only by convention:

> A complete bounded request must precede the durable idempotent effect
> decision, and that decision must precede a newly re-attested exact receipt.

Rev0887 adds one narrow C++ owner for that sequence.

## Authority invariant

`receive_one_sync_replica_file_delivery_over_tls_or_throw` owns exactly one
application conversation on one authenticated TLS stream:

1. require the service's exact canonical request ceiling;
2. reserve the strict nonblocking TLS read direction;
3. consume one complete encrypted record through bounded 64 KiB operations;
4. invoke the receiver file service exactly once only after the complete frame;
5. preserve the returned durable idempotent decision as exact result evidence;
6. independently test the receipt deadline;
7. reacquire and re-attest the same live TLS channel at the response-prefix
   frontier;
8. write the exact receipt through bounded WANT-aware operations; and
9. report local receipt completion without calling it peer receipt or sender
   settlement.

The request and receipt deadlines are independent absolute `steady_clock`
cutpoints. Neither deadline is renewed after progress or interruption.

## Why two deadlines matter

A single exchange deadline conflates two different authority questions:

- **Request authority:** Is the receiver still willing to begin or continue
  acquiring the peer's complete request?
- **Response policy:** After a durable effect decision exists, is the receiver
  still willing to begin or continue emitting the receipt?

Request expiry is pre-authority: it invokes no durable service callback.
Receipt expiry is post-authority: it cannot roll back publication and cannot
pretend the sender learned the result. The exact sender claim therefore remains
live until its owned-clock expiry or an authenticated terminal receipt.

## Stream discard is application sequencing, not delivery evidence

TLS record framing can remain byte-synchronized after a complete malformed
application frame or after the receiver has committed an effect but abandoned
its receipt. The application conversation cannot.

Reusing that stream would make the next peer record ambiguous: is it a retry, a
new request, or bytes associated with the response that never completed?
Rev0887 therefore adds
`discard_sync_replica_tls_authenticated_channel_noexcept`. It permanently
poisons the local authenticated capability without claiming TLS shutdown,
remote observation, or socket closure.

The helper is intentionally destructive and no-throw. It is used when:

- the request deadline is already exhausted before the first read;
- one complete application frame is malformed or denied by an exception;
- the receipt deadline is exhausted before prefix acceptance;
- receipt construction/transport fails after a durable effect decision; or
- an active continuation unwinds after partial progress.

A pending read/write continuation remains fail-closed: its destructor also
poisons if an exact OpenSSL operation or accepted prefix cannot be completed.

## Exact cutpoint result

`SyncReplicaFileTlsReceiveResult` distinguishes:

- `PeerClosed`: authenticated clean close before any request frame;
- `RequestDeadlineExpired`: no complete request and no durable callback;
- `ReceiptDeadlineExpired`: a durable inbound decision exists, but the exact
  receipt did not complete locally; and
- `ReceiptSent`: OpenSSL accepted the complete application receipt record.

The result records request prefix/body progress and receipt prefix/body
progress. These are local diagnostic cutpoints. They are not remote receipt,
remote effect, durable network delivery, or sender settlement.

`inbound` is present only after the receiver service returns its exact durable
idempotent decision. The type is statically required to be no-throw movable so
returning a deadline result does not introduce a new allocation after the
durable callback.

## Refactor and waste correction

The new module is a semantic dependency leaf:

- `src/sync_replica_file_tls_exchange.hpp`
- `src/sync_replica_file_tls_exchange.cpp`
- `anonsync_sync_replica_file_tls_exchange`

It depends only on the file delivery service and shared TLS poll owner. This
removes repeated request/effect/receipt choreography from application callers
without moving durable policy into the generic TLS transport.

The runtime fixture also exposed a stale helper that accepted only the raw TLS
write continuation even though rev0887's file-dispatch continuation has the
same bounded `advance_or_throw` vocabulary. The helper is now a constrained-by-
use template over one stable lvalue continuation. This removes duplicate drive
loops and fixes a compile-time disconnect in the recovered pre-seal rev0887
source.

## Failure matrix

| Frontier | Required result |
|---|---|
| Request deadline expired before first operation | No OpenSSL call, no durable mutation, stream discarded |
| WANT then request deadline | Exact retry frontier retained until unwind; no durable callback; stream poisoned |
| Clean `close_notify` before frame | Typed `PeerClosed`; no durable mutation |
| Partial frame then close/error | Throw and poison; no frame resynchronization claim |
| Complete malformed frame | Durable snapshots unchanged; stream discarded; no receipt |
| Complete valid frame | Invoke receiver service once |
| Durable publication, receipt deadline already expired | Return exact inbound decision; emit no receipt prefix; stream discarded |
| Receipt prefix/body timeout | Durable decision remains; local progress reported; active writer poisons on unwind |
| Fresh exact retry after ambiguous response | Receiver returns `AlreadyPublished`; no second effect |
| Complete receipt write | Local `ReceiptSent`; sender still settles only after reading and validating the exact receipt |

## Runtime evidence

The real TLS 1.3 integration test now proves:

1. one complete request reaches durable evidence admission and exact visible
   file publication before the receipt;
2. the emitted terminal receipt settles the exact sender claim and converges
   canonical replica digests;
3. an already-expired receipt budget returns the durable `Published` decision
   while emitting zero receipt-prefix bytes;
4. the old channel becomes poisoned and the sender intent remains live;
5. owner-clock expiry mints one fresh claim and channel binding;
6. the receiver reconciles that retry as `AlreadyPublished` with one retained
   effect row and unchanged file bytes;
7. a partial advertised frame reaches genuine WANT, retains exact prefix/body
   progress to the absolute deadline, and changes neither durable owner;
8. an already-expired request budget changes neither evidence nor effect state;
   and
9. a complete malformed record changes neither durable owner and leaves no
   reusable application stream.

## Online protocol review

The transport profile continues to disable TLS early data and reject resumed
sessions. That remains the correct prerequisite for a non-idempotent application
request path: TLS 1.3 explicitly treats 0-RTT data as replayable and requires
applications to own replay safety. The receiver's durable idempotency is useful
defense, but it is not a reason to silently enable early data.

Primary references reviewed for rev0887:

- RFC 8446, section 8, “0-RTT and Anti-Replay”:
  <https://www.rfc-editor.org/rfc/rfc8446#section-8>
- OpenSSL 3.5 early-data API and replay cautions:
  <https://docs.openssl.org/3.5/man3/SSL_read_early_data/>
- OpenSSL `SSL_read_ex` / `SSL_write_ex` retry rules:
  <https://docs.openssl.org/3.5/man3/SSL_read/>
  <https://docs.openssl.org/3.5/man3/SSL_write/>

Those specifications constrain the design. They do not prove this C++ code,
thread safety, crash recovery, package integrity, or anonymity.

## Nonclaims and remaining gaps

Rev0887 does **not** claim:

- peer receipt merely because OpenSSL accepted the local receipt bytes;
- exactly-once network delivery;
- atomicity across sender and receiver SQLite databases;
- a production listener, connection acceptor, membership service, or key
  lifecycle;
- peer/folder quotas, fairness, dead-letter ownership, or staged-payload garbage
  collection;
- filesystem watch, deletion, rename, or conflict-effect protocols;
- traffic-analysis resistance, anonymity, unlinkability, or metadata privacy;
- complete crash injection at every kernel/OpenSSL/SQLite/publication frontier;
  or
- that the lexical audit proves semantic ordering.

The next useful production step is a small replica service that owns connection
acceptance, authenticates membership epochs, invokes this one-exchange seam,
closes/discards terminal channels, and persists bounded retry/dead-letter
policy. The full-history SQLite owner should remain the correctness oracle while
an indexed production owner is developed and differentially tested.

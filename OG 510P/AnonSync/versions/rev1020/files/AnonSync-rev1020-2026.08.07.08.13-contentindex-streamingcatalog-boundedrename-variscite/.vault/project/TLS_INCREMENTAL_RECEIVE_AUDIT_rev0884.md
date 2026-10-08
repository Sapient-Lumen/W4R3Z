# TLS Incremental Receive Continuation Audit — rev0884

## Executive finding

AnonSync's newest evidence-authorized delivery path could create authenticated
TLS records, bind them to exact durable outbox claims, and retain an exclusive
write continuation after the encrypted length prefix crossed the first-byte
frontier. The receive direction was still a blocking convenience function. On a
nonblocking descriptor, `SSL_ERROR_WANT_READ` or `SSL_ERROR_WANT_WRITE` caused
that function to fail and poison the stream. There was no application-owned
object that could preserve the exact pending read operation across readiness
notifications.

A tempting implementation is a movable value containing an inline eight-byte
prefix array and inline body string. That design is unsafe at the OpenSSL retry
boundary: moving the value can relocate its prefix storage, and later string
moves are not an API-level guarantee that a previously supplied application
buffer address remains the same. OpenSSL SSL_read documentation requires a
retryable read to be repeated with the same arguments. A continuation whose
C++ move changes the supplied pointer can violate that contract without a
compiler error and without necessarily failing deterministically.

Rev0884 introduces a heap-stable, move-only read continuation. One private
allocation owns the prefix, body, offsets, pending-operation state, exact
channel owner, limits, policy, and cleanup behavior. Moving the public wrapper
moves only a `std::unique_ptr`; it does not move the buffers supplied to
`SSL_read_ex`. Each `advance_or_throw()` performs at most one OpenSSL read and
returns a typed event-loop result: progress, WANT_READ, WANT_WRITE, complete
frame, or clean pre-frame peer close.

The work also refactors the authenticated channel's write-only active flag into
one duplex reservation enum. A read continuation, write continuation, generic
record operation, or delivery-authority live verifier cannot re-enter the same
`SSL*` while another record operation owns it. This is conservative by design:
OpenSSL permits full-duplex patterns under carefully separated execution, but
AnonSync currently binds an SSL owner to one process/thread incarnation and has
no lock or two-owner scheduler that could make concurrent calls authoritative.

This revision closes one transport-state gap. It does not claim a production
receiver service, durable partial-body resume, remote effect completion,
exactly-once execution, or anonymity.

## Mission fit

The heart of AnonSync is exact authority accounting:

> Exact authorized history owns identity, causality, projection, dispatch,
> retry, receipt, and visible effect. A readiness bit, buffer address, TLS
> session, C++ wrapper, or source audit is subordinate evidence and cannot mint
> authority by convenience.

A pending `SSL_read_ex` operation therefore has identity-bearing state:

- the exact authenticated TLS owner;
- the exact creating process and thread incarnation;
- the record reservation held on that stream;
- the exact output pointer and requested length supplied to OpenSSL;
- whether any call has entered OpenSSL;
- the accepted prefix bytes and decoded body ceiling;
- the body bytes already returned to the application; and
- whether the only truthful terminal result is complete, cleanly closed, or
  poisoned/ambiguous.

Treating that state as a loop-local collection of variables loses its owner at
`WANT_READ` or `WANT_WRITE`. Treating it as an ordinary movable aggregate risks
changing the pending operation's identity. Rev0884 makes the continuation the
exclusive owner of this cutpoint and makes its buffer addresses stable for the
allocation's lifetime.

## Primary-source constraints

The implementation was reviewed against the OpenSSL 3.5 documentation used by
this cloudtainer (the observed library is OpenSSL 3.5.5):

- OpenSSL SSL_read / SSL_read_ex:
  <https://docs.openssl.org/3.5/man3/SSL_read/>
- SSL_get_error:
  <https://docs.openssl.org/3.5/man3/SSL_get_error/>
- SSL_pending:
  <https://docs.openssl.org/3.5/man3/SSL_pending/>
- OpenSSL thread safety:
  <https://docs.openssl.org/3.5/man7/openssl-threads/>

The load-bearing observations are:

1. A nonblocking SSL read can require either read or write readiness.
2. After a retryable WANT result, the operation must be repeated with the same
   arguments; the output pointer and requested byte count are therefore part of
   the continuation identity.
3. `SSL_get_error` must classify the exact preceding call on the same thread,
   with no intervening OpenSSL call that changes the thread-local error queue.
4. `SSL_pending` reports already processed application bytes buffered inside
   the SSL object. It is not a complete socket-readiness oracle and may report
   zero while an unprocessed TLS record is available. It cannot replace the
   typed WANT result or the event loop.
5. OpenSSL's general thread-safety guarantees do not authorize simultaneous use
   of one mutable `SSL*` from arbitrary threads.

The code consequently calls `ERR_clear_error()` immediately before one
`SSL_read_ex`, then calls `SSL_get_error()` immediately after a failed result.
It does not perform certificate, exporter, or other SSL operations between a
WANT result and retry of that exact read. Strict mode may re-observe the direct
socket descriptors and `O_NONBLOCK`; that is an operating-system capability
check rather than an application-data SSL operation.

These sources constrain the design. They do not prove this implementation or
its scheduling correct. Compiled tests, sanitizer runs, repeated executions,
and manual review remain necessary.

## Heap-stable state

`SyncReplicaTlsRecordReadContinuation` is a small public capability containing:

```cpp
std::unique_ptr<detail::SyncReplicaTlsRecordReadState> state_;
```

The private state allocation owns:

- `std::array<unsigned char, 8>` prefix storage;
- `prefix_offset`;
- the decoded `frame_bytes`;
- the exact-sized `std::string frame` body storage;
- `body_offset`;
- the maximum allowed frame size;
- strict/caller-managed readiness policy;
- the diagnostic label;
- the shared authenticated TLS owner;
- reservation-active and I/O-started facts; and
- a terminal state of Reading, Complete, or PeerClosed.

The public type is noncopyable and not default-constructible. Its move
constructor and move assignment are `noexcept`. A wrapper move transfers one
heap allocation rather than relocating the prefix or body. If move assignment
replaces an already active target, destruction of the target's allocation first
runs the same owner-fenced abandonment policy as ordinary destruction.

The private destructor is explicitly `noexcept` and calls exactly one
`abandon_noexcept()` path. Cleanup is not a side channel around authority: the
authenticated owner verifies the exact process and thread before changing its
reservation, poison, closed, or SSL lifetime state.

## Incremental state machine

### Begin

`begin_sync_replica_tls_record_read_or_throw()` performs all local operations
that can throw before reserving the stream:

1. validate the nonzero bounded maximum frame size;
2. validate the readiness policy;
3. require a live, non-moved authenticated channel;
4. allocate the heap state, retain shared ownership, and copy diagnostics;
5. re-attest the idle live TLS session;
6. in strict mode, prove direct socket BIOs and `O_NONBLOCK`; and
7. atomically within the single-thread owner, change the reservation from Idle
   to Read.

After reservation, setting the local boolean and moving a `unique_ptr` into the
return value are nonthrowing. This mirrors the write continuation's rule that a
stream cutpoint must never be accepted and then lost to a local allocation or
copy failure.

### Advance

One `advance_or_throw()` call:

1. verifies that the continuation still owns a Reading reservation;
2. reconstructs the exact pointer and remaining length from stable storage and
   unchanged offsets;
3. verifies process/thread ownership and channel usability;
4. on the first attempted read, re-attests the exact authenticated session;
5. in strict mode, re-proves direct nonblocking socket capability;
6. marks I/O started before entering OpenSSL;
7. clears the thread-local OpenSSL error queue;
8. performs exactly one `SSL_read_ex` call;
9. immediately classifies a failure with `SSL_get_error`; and
10. either returns a typed progress result or transitions terminally.

WANT_READ and WANT_WRITE do not change prefix or body offsets. The next advance
therefore supplies the same arguments. A successful read is a completed OpenSSL
operation; its returned bytes advance the appropriate offset. Prefix completion
is decoded and validated before body allocation. Empty, over-limit, or
unrepresentable lengths fail closed before a body byte is read.

The first successful body completion releases the channel reservation and drops
the private state's shared TLS reference before reporting Complete. The caller
can then move the completed frame out through `take_frame_or_throw()`. A
completed continuation no longer carries live SSL authority.

### Why the full session is not re-attested after WANT

The authenticated channel normally revalidates protocol, verification mode,
peer key pin, and exporter binding at each new operation boundary. A WANT result
means the existing `SSL_read_ex` operation is incomplete. Calling exporter or
certificate APIs before retry would interpose unrelated SSL work between that
call and its required same-argument retry. Rev0884 performs full live-session
re-attestation at the first read frontier, then relies on the exclusive
reservation and exact owner until that framed read terminates. Strict descriptor
capability is still checked on every advance because a caller can change file
status flags without changing the SSL session.

This is a deliberately narrow trust interval: one bounded record read under one
process/thread owner. A future service that allows channel mutation, TLS
renegotiation-like control, or cross-thread scheduling must introduce a stronger
serialized owner rather than weakening this interval by convention.

## Duplex reservation refactor

Rev0883 represented unfinished application data with a `record_write_active_`
boolean. Adding reads as a second boolean would admit invalid states such as
both true, and every verifier would need to remember both fields.

Rev0884 replaces it with:

```cpp
enum class SyncReplicaTlsRecordReservation { Idle, Read, Write };
```

The authenticated state now owns one `record_reservation_`. All entry points
use it:

- begin read requires Idle, then records Read;
- active read requires Read;
- read completion/close/abandonment require Read;
- begin write requires Idle, then records Write;
- active write requires Write;
- write completion/poison require Write or fail closed;
- generic delivery-authority validation requires Idle before certificate or
  exporter revalidation.

The last rule prevents a database service call from using the channel verifier
as an accidental OpenSSL re-entry path while a WANT operation is pending. The
reservation is channel-wide rather than direction-only because the current
owner is single-thread-affine and unguarded. This costs potential full-duplex
throughput but eliminates a class of interleaving states that the present
architecture cannot prove safe.

## Failure matrix

| Frontier | Exact outcome | Stream authority after outcome |
|---|---|---|
| invalid limit or readiness policy | throw before state allocation/reservation | unchanged and reusable |
| heap allocation / label copy fails | throw before reservation | unchanged and reusable |
| session or strict socket proof fails at begin | throw before reservation; session contradiction may poison | no unreported active read |
| continuation destroyed before first `advance` | owner-fenced clean reservation release | reusable |
| first or later read returns WANT_READ | preserve exact buffer/length and reservation | only same continuation may retry |
| first or later read returns WANT_WRITE | preserve exact buffer/length and reservation | only same continuation may retry |
| wrapper moved after WANT | transfer heap pointer only | pending operation unchanged |
| WANT continuation abandoned or overwritten | owner-fenced poison | channel permanently unusable |
| partial prefix/body then abandonment or error | owner-fenced poison | channel permanently unusable |
| strict socket loses `O_NONBLOCK` before retry | throw and poison because I/O was already attempted | channel permanently unusable |
| empty, over-limit, or unrepresentable prefix | reject before body allocation; poison | channel permanently unusable |
| clean close-notify before any frame byte | PeerClosed terminal; mark channel closed | no fabricated frame; channel unusable |
| clean close-notify after any framing progress | truncation error and poison | channel permanently unusable |
| unclean EOF / syscall / protocol error | error and poison | channel permanently unusable |
| complete body | release reservation, return Complete | channel reusable for the next record |
| `take_frame_or_throw` before Complete | logic error, active operation unchanged | continuation still owns stream |
| foreign process/thread advance | process fail-stop or throwing thread rejection | no foreign SSL operation |
| foreign process/thread cleanup | immediate fail-stop before shared mutation | no silent foreign release/poison/free |
| second read, write, or delivery verifier during active read | reject before OpenSSL re-entry | original continuation remains owner |

The clean-destruction exception is intentionally limited to “no attempted
read.” Once `SSL_read_ex` has been called, even if it returned WANT before any
application byte, OpenSSL may retain operation-specific state. Releasing the
reservation as though nothing happened would allow a different buffer or
operation to inherit an ambiguous stream. Poisoning is conservative and
truthful.

## Runtime evidence

The compiled TLS integration test uses real TLS 1.3 handshakes and socket BIOs.
The rev0884 matrix adds cases for:

- empty nonblocking read returning WANT, public-wrapper move, then exact frame
  completion;
- three-byte prefix progress, WANT, move, remaining prefix, partial body, WANT,
  another move, and exact completion;
- clean destruction before any attempted read followed by channel reuse;
- abandonment after WANT followed by required poison;
- a second read and a write rejected while one read owns the duplex stream;
- loss of `O_NONBLOCK` after WANT, detected at the retry frontier;
- clean close-notify before a frame yielding PeerClosed;
- close-notify after a valid prefix yielding truncation and poison;
- an over-limit prefix rejected before body progress;
- strict rejection of a non-socket descriptor BIO;
- foreign-thread pre-I/O destruction in an inherited child process, which must
  fail stopped; and
- the legacy one-shot reader delegating to the incremental state machine and
  poisoning rather than spinning after WANT.

The tests also retain the earlier exact channel binding, write continuation,
first-prefix dispatch, SQLite claim, receipt, and convergence checks. The
source audit independently inventories reviewed state-machine shape but
explicitly disclaims semantic proof.

## Audit and refactor findings

### Corrected waste: duplicated active-operation states

A separate read flag beside the write flag would have multiplied every state
transition and audit check. The one enum reduces the representable state space
and gives ordinary channel verification one place to reject re-entry.

### Corrected risk: movable inline retry buffers

The implementation does not rely on `std::array` wrapper address stability or
on a particular `std::string` move implementation. The application buffers are
owned by one allocation whose address is invariant across wrapper moves.

### Corrected risk: hidden blocking loops

The incremental API performs one SSL read per advance. It cannot internally
spin through repeated WANT results or monopolize a database writer while
waiting. The legacy blocking-shaped helper remains explicit: it delegates to
the state machine and fails on WANT rather than pretending to provide event-loop
liveness.

### Corrected risk: verifier re-entry

The delivery authority used by durable services performs live TLS validation.
Without the new Idle requirement, a caller could invoke that verifier while a
read was pending and interpose exporter/certificate operations. The duplex
reservation now rejects that path before OpenSSL access.

### Remaining architectural waste

The newer causal SQLite owner, file-effect owner, authenticated delivery
service, first-prefix dispatcher, and incremental receive continuation are
still primarily exercised by tests. The shipped executable remains on an older
path. Continuing to deepen isolated correctness without composing a small
production-shaped service risks optimizing an oracle that users never execute.

The next implementation should be a narrow single-owner receiver service:

1. poll/epoll drives exactly one read continuation per connection;
2. bounded queues cap complete frames awaiting validation;
3. canonical request parsing and authenticated channel authority feed the
   existing receiver SQLite/effect owner;
4. immutable publication reaches a terminal effect receipt;
5. a write continuation sends that exact receipt;
6. crash injection covers every prefix byte, body offset, transaction,
   publication, receipt byte, and sender settlement frontier.

Partial TLS record offsets should initially remain ephemeral and poison on
process loss. Durable byte-level TLS resume is not meaningful across a lost TLS
session; durable authority belongs at canonical message, payload chunk, and
effect cutpoints above the transport.

## Deliberate nonclaims

Rev0884 does not claim:

- a production poll, epoll, io_uring, kqueue, IOCP, or coroutine integration;
- fairness, connection admission, bounded complete-frame queues, or timeout
  policy;
- simultaneous full-duplex use of one `SSL*`;
- support for custom, filtered, buffered, memory, QUIC, or non-socket BIOs under
  the strict readiness policy;
- durable resume of a partial TLS record after process or session loss;
- an authenticated TCP accept/connect owner or peer discovery;
- integration of received frames with the receiver SQLite/effect state machine
  in a shipped executable;
- terminal remote effect from a completed TLS read;
- peer receipt from read or write completion;
- exactly-once network delivery or non-idempotent remote execution;
- complete retry, backoff, jitter, dead-letter, lease-heartbeat, membership,
  revocation, compaction, rejoin, or key-recovery policy;
- ThreadSanitizer, formal verification, full-project Clang, or full-project
  sanitizer coverage;
- confidentiality beyond the configured TLS channel, or anonymity,
  unlinkability, endpoint hiding, traffic-shape protection, or resistance to a
  global observer; or
- that a lexical audit proves runtime behavior.

The source audit checks reviewed vocabulary, ordering, tests, package surface,
and nonclaims. It does not claim pointer stability, OpenSSL behavior, scheduler
behavior, kernel readiness, or race freedom by substring presence.

## Conclusion

Rev0884 converts nonblocking receive from an unowned error case into an exact,
move-only continuation with heap-stable OpenSSL retry arguments and one
channel-wide reservation. It distinguishes no-I/O cleanup, retryable readiness,
complete frame, clean pre-frame close, and ambiguous/truncated progress. It
also removes a two-boolean state-space trap and prevents durable-service
validation from re-entering a pending SSL operation.

The next mission-critical step is composition, not another isolated transport
primitive: place this reader and the existing exact write dispatcher under one
bounded event-loop owner and carry one canonical operation all the way to a
terminal receiver effect receipt.

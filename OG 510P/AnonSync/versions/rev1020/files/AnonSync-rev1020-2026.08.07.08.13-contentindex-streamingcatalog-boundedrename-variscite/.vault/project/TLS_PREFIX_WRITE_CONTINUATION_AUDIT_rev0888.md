# TLS prefix write continuation audit — rev0888

## Mission connection

AnonSync is an authority-accounting system. Exact validated evidence and the
capability that owns the current cutpoint decide whether a request may cross a
transport frontier, whether a receiver may publish an effect, whether a receipt
may settle a sender claim, and whether an interrupted operation may be retried.
A convenient control-flow shape, an integer descriptor, a local TLS return code,
or a source audit cannot acquire that authority.

Rev0887 introduced the first production receiver composition owner:

> complete bounded authenticated request → durable idempotent effect decision →
> exact authenticated receipt

The durable ordering was correct, but the receipt writer had an asymmetry. The
body was represented by a move-only resumable continuation, while the 8-byte
record-length prefix was synchronously driven inside
`begin_sync_replica_tls_record_write_or_throw`. A genuine nonblocking
`SSL_ERROR_WANT_READ` or `SSL_ERROR_WANT_WRITE` at that first prefix operation
could not be returned as typed state. The begin call threw, the stream was
poisoned, and the receiver lost the distinction between:

- deadline before any write attempt;
- zero-byte first-prefix WANT;
- partial prefix acceptance;
- complete prefix with partial body; and
- complete local receipt write.

That behavior was fail-closed, but it discarded useful exact evidence and made
ordinary first-prefix backpressure look like an exceptional transport defect.
It also left two write drivers in one transport path: a special synchronous
prefix loop and a resumable body state machine.

Rev0888 removes that split. One heap-stable, move-only owner now carries the
exact 8-byte prefix, exact bounded body, current phase, offsets, retry arguments,
readiness direction, and stream reservation from preparation through terminal
completion.

## Authority invariant

For one `SyncReplicaTlsRecordWriteContinuation`, exactly one of the following
states owns the authenticated record-write stream:

1. **Prepared, untouched.** Bounds, body copy, prefix encoding, diagnostics,
   authenticated channel validation, strict nonblocking transport proof, and
   stream reservation have completed. No `SSL_write_ex` has been attempted.
2. **Prefix operation.** One bounded call owns an exact pointer and length into
   the private 8-byte prefix. A WANT retains those exact arguments and readiness
   direction. Successful partial progress advances only the prefix offset.
3. **Body operation.** The complete prefix has been accepted. One bounded call
   owns an exact pointer and length into the private frame. A WANT retains those
   exact arguments and readiness direction. Successful partial progress advances
   only the body offset.
4. **Complete.** The exact prefix and exact body have completed locally and the
   exclusive stream reservation is released once.
5. **Failed or abandoned after attempt.** The channel is permanently poisoned.
   No replacement continuation may pretend to resume the pending OpenSSL
   operation or reinterpret later bytes.

The transition from prefix to body is an explicit public `Progress` result. One
call to `advance_or_throw()` never hides a body operation after completing the
prefix. This preserves the sender dispatch cutpoint: its SQLite claim guard can
remain held through the exact prefix, commit immediately after
`prefix_complete()`, and release before large body I/O.

The preparation factory is deliberately distinct from the legacy begin factory:

- `prepare_sync_replica_tls_record_write_or_throw` returns before the first
  OpenSSL write and therefore can represent first-prefix WANT as ordinary typed
  state;
- `begin_sync_replica_tls_record_write_or_throw` delegates to that same state
  machine but drives only until the complete prefix, preserving the existing
  guarded-dispatch contract.

Neither factory nor local completion is evidence that the peer received,
validated, durably applied, or acknowledged the record.

## Exact retry and zero-byte WANT

OpenSSL documents that after `SSL_write_ex` returns WANT, the operation must be
retried with the same arguments unless moving-write-buffer mode is used. Even
when zero application bytes were reported, OpenSSL may retain protocol state for
that exact operation. Rev0888 therefore treats the first attempted write as the
ownership frontier, not the first positive byte count.

Each fresh prefix or body request is capped at 64 KiB, even though the prefix
is only 8 bytes. That public cap bounds application-requested progress per
event-loop step; it does not claim a wall-clock or OpenSSL-internal work bound.

The private state records before each fresh operation:

- whether the operation addresses prefix or body;
- the exact offset;
- the exact bounded length; and
- the expected readiness direction after WANT.

Before a retry, the implementation re-proves the authenticated record owner,
transport anchor, exact socket lifetime, current nonblocking policy, and pending
phase/range. It then reconstructs the same private pointer and length. No body
mutation by the caller can alter the operation because the body was copied
before stream reservation, and moving the public wrapper moves only a
`unique_ptr`, not the underlying byte storage.

`io_started()` is intentionally separate from byte counts. The tuple

> `io_started == true`, `prefix_bytes_written == 0`, `body_bytes_written == 0`

can be exact evidence of a first-prefix WANT. Destroying that continuation must
poison. In contrast, an untouched prepared owner can release its idle
reservation cleanly because no OpenSSL operation and no stream progress exists.

## Sender guarded compatibility

The sender file-dispatch owner continues to call the begin factory while holding
its exact SQLite outbox-claim guard. The shared writer drives only the prefix.
Then:

1. the continuation reports `prefix_complete()`;
2. the dispatch owner commits the exact guard;
3. the database serialization owner is released; and
4. the continuation alone carries the body through ordinary backpressure.

A prefix WANT in this guarded API still throws and poisons the stream. That is a
deliberate compatibility policy, not a limitation of the shared writer: the
sender must not retain a SQLite writer or claim guard across an unbounded network
poll. The existing pre-prefix failure path exact-releases the claim; after
prefix acceptance, failure remains explicitly ambiguous.

A later sender-service refactor may separate claim validation from prefix
polling, but it must first define a durable intermediate authority state. Rev0888
does not invent one implicitly.

## Receiver post-effect behavior

The receiver exchange uses the preparation factory because the durable effect
decision already exists before receipt emission. It can therefore retain an
exact prefix WANT without holding SQLite authority across network wait.

The response driver now records four independent local diagnostics:

- whether any write operation was attempted;
- exact prefix bytes accepted locally;
- whether the complete prefix was accepted; and
- exact body bytes accepted locally.

On every receipt deadline it snapshots those values and destructively discards
the application channel. The durable inbound decision remains present in the
result and remains authoritative. The sender is not settled unless it later
receives and validates the exact terminal receipt.

The important new case is:

> durable visible effect → first receipt-prefix `WANT_WRITE` with zero accepted
> prefix bytes → receipt deadline → exact inbound result retained, old channel
> discarded, sender claim still live

A fresh exact sender retry on a fresh channel can then reconcile through the
receiver's existing idempotency and return `AlreadyPublished` without repeating
the visible effect.

## Refactor and waste correction

Before rev0888, prefix and body writes had divergent control flow. The prefix
used a special synchronous helper; the body used a move-only continuation. This
was wasteful in several ways:

- two places encoded OpenSSL write error handling;
- only one place exposed typed WANT;
- prefix progress could not be observed precisely by the receiver;
- tests had to infer “no prefix” from an exception path; and
- future changes to socket reproof, bounded progress, or retry identity could
  drift between phases.

The synchronous helper is removed. Prefix and body now share one bounded state
machine, one exact retry implementation, one readiness-target owner, one
abandonment rule, and one completion path. The old begin API is a thin policy
adapter over the shared owner rather than a second transport implementation.

The two lexical audits were also refactored. Their parent checks described the
retired body-only source shape and would have rejected the correct two-phase
implementation while previously accepting the missing prefix continuation.
They now inventory phase identity, untouched-versus-attempted cleanup, exact
prefix/body pointers, explicit prefix progress, receiver diagnostics, and the
new runtime cases. They remain lexical hygiene and are not promoted into
semantic proof.

## Failure matrix

| Frontier | Required behavior |
|---|---|
| Empty or oversized frame | Reject before body copy, stream reservation, or OpenSSL |
| Allocation or diagnostic failure before reservation | Throw; channel remains usable unless independent validation poisoned it |
| Strict socket/anchor validation failure during reservation | Fail closed according to the authenticated capability; no write continuation returned |
| Prepared owner destroyed before first `advance_or_throw` | Release exact Write reservation; do not emit ciphertext; do not poison |
| First prefix operation returns WANT with zero bytes | Retain exact prefix pointer/length and typed readiness; `io_started` is true |
| Prefix operation makes partial successful progress | Advance only prefix offset; return `Progress`; issue no hidden body operation |
| Complete prefix | Expose exact prefix frontier before any body operation |
| Body operation returns WANT | Retain exact body pointer/length and typed readiness |
| Successful partial body write | Advance only body offset and preserve bounded step accounting |
| BIO, socket lifetime, policy, owner-thread, or reservation contradiction before retry | Throw and poison; never redirect the pending operation |
| Fatal OpenSSL result after any attempted operation | Throw and poison |
| Continuation abandoned after any attempted operation | Poison, including zero-byte WANT |
| Complete prefix and body | Release reservation once and return `Complete` |
| Receiver deadline before first receipt attempt | Record `io_started=false`, zero progress, discard application channel, retain durable inbound decision |
| Receiver deadline after zero-byte prefix WANT | Record attempted write and zero prefix/body bytes, discard channel, retain durable inbound decision |
| Receiver deadline after partial prefix/body | Record exact local cutpoint, discard channel, retain durable inbound decision |
| Receiver complete local receipt write | Report local `ReceiptSent`; do not call it peer receipt or sender settlement |

## Runtime evidence

The compiled real-TLS matrix adds the following adversarial cases:

1. preparation freezes exact prefix/body bytes and returns with no OpenSSL work;
2. destroying an untouched prepared owner emits no ciphertext and permits a new
   write on the same authenticated stream;
3. mutating caller storage after preparation cannot substitute either length or
   body bytes;
4. the first successful advance exposes the complete prefix frontier before
   body progress;
5. a saturated real socket produces genuine first-prefix `WANT_WRITE` with zero
   prefix/body bytes;
6. moving that continuation preserves its exact readiness and retry frontier;
7. abandoning the attempted zero-byte WANT poisons the old stream; and
8. after durable receiver publication, a saturated receipt path reaches the
   same first-prefix WANT, expires under the absolute receipt deadline, preserves
   one visible effect, emits no accepted prefix byte, leaves the sender claim
   unsettled, and makes the old application channel unusable.

These cases run beside the existing TLS 1.3 peer pin, exporter, BIO/socket
identity, descriptor ABA, policy mutation, process/thread affinity, bounded
partial read/write, duplex poll, file-dispatch, receiver idempotency, malformed
request, close, and retry coverage.

## Online protocol review

The implementation was checked against the current OpenSSL 3.5 documentation:

- `SSL_write_ex` retry and partial-write semantics:
  <https://docs.openssl.org/3.5/man3/SSL_write/>
- `SSL_MODE_ENABLE_PARTIAL_WRITE` and
  `SSL_MODE_ACCEPT_MOVING_WRITE_BUFFER` semantics:
  <https://docs.openssl.org/3.5/man3/SSL_CTX_set_mode/>

The design deliberately keeps a stable pointer and exact length even though the
profile does not enable moving-write-buffer mode. It accepts successful partial
writes as completed operations and creates a new bounded operation only after
that progress. WANT retains the prior arguments exactly.

Those manuals constrain the implementation. They do not prove this code,
OpenSSL internals, kernel scheduling, peer behavior, durable effects, package
integrity, or anonymity.

## Rejected alternatives

**Keep the synchronous prefix helper and catch WANT.** This remains fail-closed
but throws away an ordinary nonblocking state, duplicates error handling, and
cannot distinguish deadline-before-write from zero-byte attempted prefix.

**Poll inside the begin factory.** That would hide an unbounded wait inside a
call used while the sender holds durable claim authority. It would also renew or
invent deadline policy below the owner that must decide it.

**Return a new prefix-only continuation and later allocate a body continuation.**
That creates another post-prefix allocation/handoff frontier and splits exact
record identity across two owners.

**Treat zero accepted bytes as no operation.** OpenSSL WANT still owns an exact
retry. Releasing the stream cleanly would permit a replacement operation against
protocol state that may already be pending.

**Enable moving-write-buffer mode and retain only offsets.** That weakens rather
than strengthens AnonSync's ownership proof and does not remove the need to
retain exact operation length, phase, readiness, and channel identity.

**Hold SQLite authority while polling the sender prefix.** This converts network
backpressure into database serialization and risks an unbounded writer/claim
critical section. The legacy guarded sender adapter therefore remains
fail-closed on prefix WANT.

## Nonclaims and remaining gaps

Rev0888 does not claim:

- peer receipt because OpenSSL accepted local prefix or body bytes;
- exactly-once network delivery or atomicity across two SQLite databases;
- that raw `SSL*`, BIO, or descriptor mutation is safe concurrently with this
  owner;
- strict non-Linux socket-lifetime authority;
- a production listener, authenticated connection acceptor, or long-running
  replica service;
- membership enrollment, key rotation, revocation, recovery, or rollback
  protection;
- peer/folder quotas, fairness, bounded staging lifetime, dead-letter policy, or
  garbage collection;
- complete crash injection at every OpenSSL, SQLite, payload, rename,
  directory-durability, receipt, and settlement frontier;
- deletion, rename, directory, permission, or conflict-effect protocols;
- traffic-analysis resistance, unlinkability, anonymity, or metadata privacy;
  or
- that either lexical audit proves retry identity, scheduling, durability, or
  package integrity.

The next production step remains a bounded replica service that owns connection
acceptance, membership epoch authentication, one receiver conversation per
application stream, terminal close/discard, and persistent retry/dead-letter
policy. A separate indexed owner should then be differentially checked against
the full-history SQLite correctness oracle before replacing it on the hot path.

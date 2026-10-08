# TLS incremental write continuation audit — rev0886

## Executive finding

AnonSync already treated a successful encrypted eight-byte frame-length prefix
as a one-way authority cutpoint. After that point the sender cannot truthfully
release the exact outbox attempt as though no network progress occurred. The
rev0885 writer nevertheless had two related gaps after that cutpoint:

1. it retained only the promised frame length, while the caller continued to
   own the body bytes; and
2. it offered only a synchronous `finish_or_throw(frame)` body operation that
   discarded and poisoned the channel on ordinary `SSL_ERROR_WANT_READ` or
   `SSL_ERROR_WANT_WRITE` backpressure.

The first gap allowed a caller to substitute different bytes of the same length
between prefix acceptance and body entry. A size comparison could not detect
that the canonical frame identity had changed. The second gap made a healthy
nonblocking transport unusable exactly where the future bounded event loop
needs a resumable capability. OpenSSL documents that a write returning WANT is
one incomplete operation whose retry must use the same arguments because some
of the supplied data may already have been processed.

Rev0886 changes the writer into a move-only, heap-stable state machine. It owns
an exact bounded copy of the frame before the prefix can be accepted, issues at
most one 64 KiB body request per `advance_or_throw()`, preserves the exact
pointer and length across WANT, exposes a typed advisory readiness target only
for strict direct-socket mode, and releases the shared stream reservation only
when the complete body has succeeded. Abandonment after prefix acceptance
poisons the channel. Transport completion is still not peer receipt or durable
receiver effect.

## Authority invariant

For one accepted prefix and its body, the implementation must maintain:

> Exactly one live continuation owns exactly one immutable application byte
> string, one monotonically advancing completed-body cutpoint, and at most one
> pending `SSL_write_ex` operation identified by the exact pointer, length,
> authenticated TLS owner, BIO/socket anchor, process, and thread on which that
> operation began.

The following are subordinate observations rather than authority:

- the caller's original `std::string` or `std::string_view`;
- the advertised frame length by itself;
- a descriptor integer returned for polling;
- poll readiness or scheduler wakeup;
- an `SSL_ERROR_WANT_*` code without the retained operation arguments;
- bytes accepted by OpenSSL without a terminal receiver effect receipt; and
- lexical audit success.

A retry must not be reconstructed from a semantically equivalent buffer. The
continuation retains the exact storage used by the first attempt. An event-loop
wakeup does not authorize progress by itself; the authentication-time BIO and
Linux socket lifetime, current nonblocking policy, record reservation, process,
and thread are re-proved before OpenSSL is re-entered.

## Parent defect and concrete failure sequences

### Same-length caller substitution

The rev0885 public sequence was conceptually:

1. caller passes `frame.size()` to `begin...`;
2. the writer encrypts and accepts the eight-byte length prefix;
3. the caller mutates or replaces `frame` with different bytes of equal size;
4. caller passes the changed view to `finish_or_throw(frame)`; and
5. the length check succeeds, so a prefix derived from one canonical message is
   joined to a different body.

The TLS framing remains syntactically valid. The authority failure is semantic:
the durable claim and preflight digest bound the old canonical frame, while the
wire body can be a same-length replacement. A receiver that validates only the
wire message cannot reconstruct which local claim the sender intended to
exercise.

Rev0886 removes the second body argument. The exact bytes are copied into
private state before any reservation or prefix I/O. Mutating the caller's source
after `begin...` returns has no effect on the body sent.

### Ordinary nonblocking backpressure

The rev0885 body helper loop treated WANT as terminal:

1. prefix succeeds;
2. body `SSL_write_ex()` reaches a full kernel send buffer;
3. `SSL_get_error()` reports `SSL_ERROR_WANT_WRITE` (or, because TLS writes may
   need inbound protocol work, `SSL_ERROR_WANT_READ`);
4. helper throws; and
5. continuation destruction poisons the channel.

Poisoning is correct if the pending operation is abandoned. It is wasteful if a
serialized event-loop owner is ready to retain and resume the exact operation.
The old API had no capability with which to do so.

Rev0886 returns typed `WantRead` or `WantWrite`. The continuation records the
exact offset and request length before entering OpenSSL and does not advance the
body cutpoint on WANT. The next `advance_or_throw()` reuses those arguments.

### Movable wrapper and pointer stability

A public continuation must be movable so queue and event-loop ownership can be
transferred without copying authority. Inline body storage would relocate when
the wrapper moves, violating OpenSSL's default same-pointer retry rule. The
public object therefore contains only a `std::unique_ptr` to private state. The
private `std::string` and all retry offsets remain at one heap address for the
lifetime of the operation.

## OpenSSL primary-source constraints

The implementation was reviewed against OpenSSL 3.5 documentation current at
revision time:

- `SSL_write_ex` / `SSL_write`:
  <https://docs.openssl.org/3.5/man3/SSL_write/>
- `SSL_get_error`:
  <https://docs.openssl.org/3.5/man3/SSL_get_error/>
- `SSL_CTX_set_mode` / `SSL_set_mode`:
  <https://docs.openssl.org/3.5/man3/SSL_CTX_set_mode/>
- `SSL_set_bio`:
  <https://docs.openssl.org/3.5/man3/SSL_set_bio/>

The load-bearing constraints are:

1. A nonblocking write may require either read or write readiness.
2. After WANT, the write must be repeated with the same arguments. The supplied
   data may already have been partially processed. The optional moving-buffer
   mode relaxes pointer identity only; data and length must remain the same.
3. `SSL_get_error` must run in the same thread, immediately after the I/O call,
   with a clear per-thread OpenSSL error queue.
4. Without partial-write mode, success means the complete requested chunk was
   written. With `SSL_MODE_ENABLE_PARTIAL_WRITE`, success may report a positive
   prefix of that chunk; that operation is complete and the next call must begin
   at the first unsent application byte.
5. A write is not necessarily write-only internally, so WANT_READ is a valid
   result even for application output.
6. BIO replacement transfers ownership and can free prior BIOs. The rev0886
   transport anchor independently retains the exact authentication-time BIO
   objects so pointer continuity cannot be forged by allocator reuse.

The code does not rely on `SSL_MODE_ACCEPT_MOVING_WRITE_BUFFER`. It is correct
if that mode is enabled, but retains the stronger same-pointer property. The
code also accepts successful partial writes, even though AnonSync does not
itself enable partial-write mode.

These documents constrain correct use of OpenSSL. They do not prove this C++
implementation, the kernel, the compiler output, or end-to-end delivery.

## C++ state machine

### Construction before authority mutation

`begin_sync_replica_tls_record_write_or_throw()` performs the following order:

1. validate that the configured maximum is positive and representable;
2. convert and validate the caller's frame size;
3. reject empty or over-limit input;
4. allocate exactly one private `std::string` copy;
5. validate the readiness-policy enum;
6. allocate the private write state and copy diagnostics;
7. construct the length prefix and its diagnostic label;
8. validate the live authenticated channel and acquire the exclusive Write
   reservation;
9. mark private state as owning that reservation; and
10. encrypt the complete prefix.

The bound check precedes the body copy. This matters for an over-limit lvalue:
a by-value API would first duplicate the entire input and only then reject it.
All potentially throwing local allocations happen before stream reservation and
prefix progress. Once the prefix succeeds, returning the public continuation is
only a no-throw `unique_ptr` move.

Any prefix exception calls `abandon_noexcept()`. Even a WANT during prefix I/O
can represent an incomplete OpenSSL operation, so the channel is poisoned. The
file-dispatch owner may exact-release the outbox attempt only because no body
can be sent on that poisoned old stream and the receiver cannot obtain a
complete application frame from the prefix alone.

### Private state

`SyncReplicaTlsRecordWriteState` owns:

- shared authenticated-channel state;
- the exact private frame string;
- strict-versus-caller-managed readiness policy;
- diagnostic label;
- completed `body_offset`;
- exact pending `pending_offset` and `pending_bytes`;
- reservation ownership;
- whether one OpenSSL operation is pending;
- its typed readiness requirement; and
- terminal state.

The destructor calls `abandon_noexcept()`. If the reservation is active, the
shared channel is poisoned and returned to Idle. Foreign-process or
foreign-thread cleanup reaches the existing fail-stop checks before mutating
shared TLS state.

### Fresh advance

When no write is pending, one public advance selects:

```
min(frame.size() - body_offset, 64 KiB)
```

and stores that selection as the pending offset and length before entering
OpenSSL. It then asks the authenticated state for the active Write owner. A
fresh operation revalidates the authentication-time transport anchor, live
peer/SPKI/exporter binding, and strict nonblocking policy where requested.

The 64 KiB value is an application request bound, not a claim about OpenSSL's
internal TLS record count, kernel writes, CPU time, or wall-clock latency.

### Exact WANT retry

When the previous call returned WANT, the next advance does not calculate a new
chunk. It checks that:

- pending length is positive;
- pending offset equals the unadvanced body cutpoint;
- offset is inside the owned string; and
- length fits the remaining owned bytes.

It then re-proves the exact Write reservation and authentication-time BIO/socket
anchor. Strict mode also re-proves current `O_NONBLOCK`. Peer certificate and
exporter queries are deliberately not interposed into an incomplete OpenSSL
operation. The input pointer is reconstructed from the same private string,
offset, and length.

Immediately before `SSL_write_ex`, the current thread's OpenSSL error queue is
cleared. On failure, `SSL_get_error` is the next OpenSSL call. WANT records only
the readiness direction; it does not change offsets.

### Successful progress

A successful call must report `0 < bytes_written <= pending_bytes`. Success
completes that OpenSSL operation, so pending state is cleared and the body
cutpoint advances by exactly `bytes_written`.

If bytes remain, public progress is `Progress` and the next advance starts a
fresh bounded operation. This handles `SSL_MODE_ENABLE_PARTIAL_WRITE` without
requiring or enabling it. Once `body_offset == frame.size()`, the shared Write
reservation is completed, the private shared-state reference is released, and
the public wrapper becomes inactive.

### Advisory readiness target

`pending_readiness_or_throw()` is available only when:

- the continuation is active;
- strict direct-socket readiness policy was selected; and
- an exact WANT_READ or WANT_WRITE is pending.

Caller-managed mode and a pre-WANT query throw without poisoning because no
system authority contradiction has been observed. Once a pending target lookup
enters authenticated socket reproof, any stale BIO, descriptor lifetime, or
nonblocking-policy failure makes exact retry impossible. The continuation is
then abandoned and the stream poisoned.

The returned descriptor remains advisory. `advance_or_throw()` repeats the
same proofs after poll/epoll wakeup and before OpenSSL retry.

### Synchronous compatibility adapter

`finish_or_throw()` loops over ordinary successful `Progress`, returns on
`Complete`, and throws on WANT. It exists for blocking callers and for the
current file-dispatch composition, which has not yet been moved under a real
event loop. It never spins on nonblocking readiness. Its failure path abandons
and poisons the accepted-prefix stream.

`write_sync_replica_tls_record_or_throw()` delegates to the same incremental
owner; there is no second body-write implementation.

## Durable file-dispatch composition

The file dispatcher retains its SQLite claim guard through:

1. frozen canonical request and channel preflight;
2. exact current claim attestation;
3. authenticated strict transport reproof; and
4. successful encrypted prefix acceptance.

Only then does it set `prefix_accepted`, commit the guard's bounded clock
observation, release the SQLite writer, and enter potentially large body I/O.
The continuation already owns the exact canonical frame bytes, so releasing the
database guard cannot permit caller substitution.

Failure before prefix acceptance rolls back the guard and durably exact-releases
the claim according to retry policy. Failure after prefix acceptance leaves the
attempt ambiguous and does not mint exact retry authority. TLS send completion
still does not settle the outbox; only a later authenticated terminal receiver
effect receipt may do that.

## Failure matrix

| Frontier | Forced condition | Required result |
|---|---|---|
| public begin | empty frame | reject before reservation or I/O |
| public begin | frame above configured ceiling | reject before duplicate body allocation and before I/O |
| pre-prefix policy | blocking/custom transport in strict mode | reject before I/O; untouched caller-managed channel may remain usable |
| prefix | socket/TLS/WANT failure | poison channel; no active continuation published |
| after prefix | caller mutates original buffer to different same-length bytes | peer receives the private original bytes |
| fresh body step | body larger than 64 KiB | one `SSL_write_ex` request is at most 64 KiB |
| body backpressure | WANT_WRITE | preserve exact pointer/length and expose writable advisory target |
| protocol backpressure | WANT_READ | preserve exact pointer/length and expose readable advisory target |
| pending wrapper | move construction | source becomes inactive; destination retains identical target and operation |
| pre-WANT query | no readiness pending | throw without poisoning active continuation |
| caller-managed query | WANT exists but no library-owned target policy | throw without poisoning; later abandonment poisons |
| poll target | descriptor close/`dup2` ABA | reject target, abandon continuation, poison stream |
| exact retry | `O_NONBLOCK` removed | reject before OpenSSL, abandon continuation, poison stream |
| accepted-prefix body frontier | `SSL_set_fd` / BIO replacement | reject before body, poison stream |
| pending operation | in-place BIO descriptor mutation | reject exact retry, poison stream |
| successful partial-write mode | positive short success | advance by exactly reported bytes and start a fresh operation |
| completion | exact body finished | release reservation once and make wrapper inactive |
| destruction/move assignment | active continuation discarded | poison stream |
| foreign thread/process cleanup | wrong owner | fail stopped before shared-state mutation |
| file dispatch before prefix | canonical/claim/channel/guard failure | exact-release attempt; no wire body |
| file dispatch after prefix | guard commit or body failure | preserve ambiguous attempt; discard channel |

The compiled runtime uses real TLS 1.3 socket BIOs. A two-megabyte body and a
small nonblocking send buffer force repeatable backpressure. Sender and receiver
continuations are alternated until completion, and the test verifies exact peer
bytes, typed targets, wrapper-move continuity, monotonic body offset, and the
64 KiB request ceiling. Separate adversarial cases force socket lifetime ABA,
readiness-policy loss, BIO replacement, caller-managed target rejection, and
same-length caller mutation.

## Audit and refactor review

### Single pending-readiness vocabulary

Read and write now share one private `SyncReplicaTlsPendingReadiness` enum and
one authenticated-state target mapper. This avoids independent interpretations
of WANT_READ and WANT_WRITE. The helper selects the directional authentication-
time socket anchor, re-proves both transport policy directions, and returns one
public descriptor/event value.

An initial centralization attempt placed caller-managed and no-WANT validation
inside the same catch block as stale socket reproof. That made a harmless query
abandon and poison an otherwise valid continuation. Rev0886 keeps semantic
precondition rejection outside the poison-on-system-contradiction block for both
reader and writer. Compiled tests prove that these queries reject without
mutation.

### One body-writing implementation

The old synchronous `finish_or_throw(frame)` contained its own whole-body loop.
The new one-shot writer and file-dispatch path both delegate to the incremental
state machine. This reduces divergent OpenSSL retry, error-queue, and poisoning
logic.

### Memory ownership versus copy cost

The private copy is intentional authority, but it is not free. The current file
service also freezes the caller-owned outbound request before obtaining the
SQLite writer, so one dispatch can temporarily retain multiple canonical-frame
copies. The ceiling keeps this bounded. A later optimization may add an explicit
rvalue/owned-frame entry point that validates before move and preserves the same
private-ownership invariant. It must not reintroduce an over-limit lvalue copy
or permit caller aliasing across prefix acceptance.

### Lexical audit limits

`tools/audit_sync_tls_write_continuation.py` inventories move-only ownership,
construction order, bounds, retry state, immediate error classification,
readiness mapping, completion/abandonment, file-dispatch ordering, runtime
labels, CTest registration, package requirements, and explicit nonclaims.

It cannot prove pointer stability, OpenSSL behavior, kernel identity, thread
safety, exception machine code, peer bytes, or durable delivery. Its result is
hygiene evidence only.

## Rejected alternatives

### Keep caller-owned bytes and compare only length

Rejected because equal length does not imply equal canonical evidence. A digest
check immediately before body I/O would detect ordinary mutation but would
still require reading caller memory after the prefix, and it would not satisfy
OpenSSL's exact-pointer retry requirement without another stable owner.

### Retain `std::string_view`

Rejected because the caller can mutate, reallocate, or destroy the referenced
storage. A view has no lifetime or immutability authority.

### Take `std::string` by value for every begin

Rejected as the only API because an over-limit lvalue would be copied before the
callee can validate its ceiling. An explicit rvalue overload may be added later,
but the general lvalue/view path must bound before allocation.

### Enable `SSL_MODE_ACCEPT_MOVING_WRITE_BUFFER`

Rejected as unnecessary weakening. The mode permits a new pointer on retry only
when bytes and length are identical. Heap-stable private storage already meets
the stronger default rule and avoids needing a second equality authority.

### Treat WANT as zero progress and start a new write

Rejected. OpenSSL says data may already have been partially processed and the
same operation must be repeated. Starting at a new offset or choosing a new
chunk can duplicate, omit, or corrupt application bytes.

### Poll and retry inside `finish_or_throw()`

Rejected because the transport layer does not own a scheduler, deadline,
cancellation policy, descriptor registration, or bounded event-loop queue.
Spinning or blocking internally would fabricate liveness authority. The typed
continuation exports the necessary state to a future exclusive event-loop owner.

### Mark the outbox attempt delivered on body completion

Rejected. `SSL_write_ex` success means bytes were written to the local SSL
connection; it is not proof that the peer parsed the complete frame, committed
receiver idempotency, staged the payload, durably published an effect, or sent a
terminal receipt.

### Permit write and read continuations concurrently on one `SSL*`

Rejected for now. OpenSSL can make a write require read readiness, and the
current code has no serialized duplex scheduler capable of preserving two
pending operation identities. One exclusive Idle/Read/Write reservation is a
conservative correctness boundary.

## Remaining risks and deliberate nonclaims

Rev0886 does not claim:

- safe concurrent or unsynchronized raw `SSL*`, BIO, descriptor, socket-mode,
  shutdown, or re-handshake mutation;
- a production poll/epoll owner, fairness policy, deadline, cancellation,
  wakeup coalescing, or queue budget;
- a bounded wall-clock duration for one OpenSSL call;
- that OpenSSL performs at most one TLS record or kernel syscall per 64 KiB
  application request;
- durable resume of a partial TLS frame after connection loss;
- safe migration of a pending continuation to another thread or process;
- concurrent full-duplex application I/O on one SSL object;
- hidden transport identity inside caller-managed custom/filter BIOs;
- strict exact socket-lifetime support outside Linux;
- cryptographic, durable, or globally unique meaning for `SO_COOKIE`;
- peer receipt, remote decode, receiver idempotency, payload availability,
  visible effect, or outbox settlement from local write completion;
- exactly-once remote execution;
- complete retry jitter/dead-letter policy, membership/key lifecycle,
  anti-entropy, compaction, tombstone collection, or rejoin;
- production-scale indexed replica ownership;
- ThreadSanitizer, formal proof, externally trusted signed provenance,
  anonymity, unlinkability, endpoint hiding, or traffic-analysis resistance.

## Next mission seam

The transport now has symmetric typed incremental read and write ownership plus
an authentication-time BIO/socket anchor. The next high-value C++ slice is one
bounded, process/thread-affine connection service that exclusively owns:

1. the raw SSL/BIO/descriptors and their close/shutdown lifecycle;
2. poll/epoll registration for the exact pending target;
3. one channel memory budget and complete-frame queue budget;
4. canonical frame decoding and validation;
5. receiver SQLite idempotency;
6. bounded payload staging and atomic visible publication;
7. terminal effect receipt generation after durable evidence; and
8. sender settlement from the exact authenticated receipt.

Connection loss must discard ephemeral prefix/body offsets and retry canonical
messages or payload chunks above TLS. Crash injection should cover every event-
loop ownership transfer, frame boundary, SQLite transaction, payload write,
rename, directory durability operation, receipt write, and sender settlement.

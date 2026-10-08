# TLS receiver session ownership audit — rev0889

## Mission context

AnonSync is an evidence-authorized convergence system under construction. Exact
validated evidence and live owned capabilities must govern every transition from
peer authentication through request framing, durable receiver admission,
visible effect, terminal receipt, retry, settlement, and cleanup. A function
name, successful local TLS write, queued socket byte, timeout, source audit, or
build report cannot silently become stronger authority than the exact cutpoint
it observes.

Rev0888 made the complete receipt record resumable, including first-prefix WANT.
It still exposed the receiver exchange as a borrowed `const` channel reference.
The implementation described one conversation, but successful completion left
the capability reusable and no type owned the channel, immutable deadlines, or
one-run lifecycle. It also discovered the absence of receiver effect authority
only after consuming a complete authenticated request frame.

## Authority invariant

The rev0889 receiver invariant is:

> Before the first application byte is consumed, the exact live authenticated
> channel must be valid for a service configured with receiver effect authority.
> After that preflight, exactly one move-only session owns the channel and two
> frozen absolute deadlines. Every terminal outcome—success, timeout, peer
> closure, exception, explicit abandonment, destruction, or replacement—must
> permanently discard that local application capability. Durable work still
> requires a fresh re-attestation after the complete request and immediately
> before receiver mutation.

The early preflight is deliberately weaker than durable authority. It is an
admission/configuration gate, not permission that survives arbitrary network
wait, process/thread change, BIO mutation, socket replacement, or peer-session
change.

## Concrete defect

`receive_one_sync_replica_file_delivery_over_tls_or_throw` previously began the
strict TLS record reader before calling
`SyncReplicaFileDeliveryService::receive_request_or_throw`. The latter checked
whether a receiver file-effect owner existed. A service constructed only for
sender work could therefore:

1. authenticate a valid peer;
2. reserve the receiver read stream;
3. consume and allocate the complete bounded request; and only then
4. reject because it had no receiver effect owner.

The rejection did not mutate durable state, but it spent peer bandwidth, kernel
buffer, OpenSSL work, framing work, and request memory under a configuration
that could have been rejected before one application byte. More importantly,
the sequencing made receiver role authority appear downstream of untrusted
resource consumption.

A second defect was semantic rather than memory unsafe: the low-level exchange
claimed one conversation but returned `ReceiptSent` without discarding the
channel. A caller could issue another record through the same capability. No
move-only owner prevented aliasing of the lifecycle policy, froze both absolute
deadlines at acquisition, or terminalized an abandoned accepted session.

## Pre-byte receiver preflight

`SyncReplicaFileDeliveryService::preflight_inbound_channel_or_throw` is a narrow
public composition seam. It:

1. rejects an empty diagnostic label;
2. revalidates the opaque live `SyncReplicaDeliveryChannelAuthority`;
3. validates peer actor and channel binding through the existing private path;
4. rejects a service without a receiver file-effect owner.

The TLS exchange constructs every diagnostic label, invokes this preflight, and
only then calls `begin_sync_replica_tls_record_read_or_throw`. Any preflight
failure discards the borrowed one-shot capability but does not consume a TLS
application byte.

`receive_request_or_throw` calls the same preflight again before decoding and
staging. This second check is load-bearing. The early observation cannot bridge
the time spent waiting for and reading the request; live channel authority is
reproved at the durable frontier.

The preflight intentionally does not take a full effect-database snapshot. Such
a snapshot would scan receiver state merely to reject role configuration and
would duplicate later owner work. Database availability, capacity, path policy,
and publication authority remain classified by the exact durable receiver
operations after a complete canonical frame.

## Exclusive one-conversation session

`SyncReplicaFileTlsReceiverSession` is a move-only C++ owner with:

- one `SyncReplicaFileDeliveryService*` whose lifetime must outlive the session;
- one optional, move-only `SyncReplicaTlsAuthenticatedChannel`;
- one frozen absolute request deadline;
- one frozen absolute receipt deadline; and
- one stable diagnostic label.

The constructor performs service/channel preflight before moving the channel.
Therefore a construction-time configuration failure leaves the caller's only
channel capability intact. Once construction succeeds, ownership transfers.
The class cannot be default-constructed or copied.

The custom move operations correct a subtle standard-library ownership trap:
moving `std::optional<T>` does not disengage the source optional. The contained
channel is moved-from, but `has_value()` would remain true. Rev0889 explicitly
resets the source optional and nulls the source service pointer so `active()` is
a truthful single-owner predicate. Move-assignment first discards any active
target capability before accepting the replacement.

`run_or_throw` may succeed or throw only once. It invokes the lower-level
exchange with the frozen deadlines, then calls `discard_noexcept` on both normal
and exceptional exits. A second call reports an inactive session before TLS or
durable work.

Freezing absolute deadlines at construction prevents a caller from renewing a
relative budget after ownership transfer. It does not create an autonomous
timer: a scheduler that never runs or destroys the session can still retain
resources indefinitely. A future listener/event-loop owner must guarantee wake,
cancellation, and transport closure.

## Successful receipt is terminal too

The borrowed exchange now discards the local authenticated capability on every
terminal return, including `ReceiptSent`. This is not evidence that the peer
received, validated, or durably applied the receipt. It means only that the
complete receipt record was accepted by local OpenSSL according to the existing
write-continuation contract.

Terminal local discard prevents a second application record from being
interpreted under an API whose protocol is exactly one request and one receipt.
The sender can still read ciphertext already emitted on its independently owned
TLS endpoint. The receiver's capability poison is local state and does not
revoke durable publication or erase the returned inbound decision.

## Close versus discard

AnonSync's `discard_sync_replica_tls_authenticated_channel_noexcept` poisons the
local application capability. It does **not** call `SSL_shutdown`, send a TLS
`close_notify`, close a socket descriptor, free the caller-owned `SSL*`, or prove
that the peer observed closure.

That separation is intentional in this revision:

- the authenticated channel owns an OpenSSL reference and policy evidence, but
  not the caller's raw `SSL*` lifecycle or socket descriptor;
- a nonblocking TLS shutdown is itself a resumable I/O state machine with
  WANT_READ/WANT_WRITE and an independent deadline;
- OpenSSL forbids `SSL_shutdown` after certain fatal SSL/SYSCALL errors;
- clean success and abortive protocol failure require different close policy;
- a response record accepted locally is not automatically flushed, received,
  or acknowledged merely because shutdown begins; and
- silently closing a borrowed descriptor would violate ownership rather than
  repair it.

The next transport owner should exclusively own `SSL*`, its socket, shutdown
state, and a close deadline. After a successful terminal receipt it can attempt
an orderly one-way or bidirectional close according to explicit protocol
policy. After fatal TLS/application framing failure it must avoid fabricating a
clean close and close the underlying transport abortively. Rev0889 makes this
missing owner visible instead of hiding it in a destructor.

## Refactor and waste correction

Receiver channel validation and receiver-role validation previously lived in
separate locations. Rev0889 centralizes them in one service preflight and makes
the durable receive path reuse it. This removes one duplicated nullable-owner
branch and prevents the transport and service paths from drifting on the meaning
of “receiver capable.”

The exchange also now has one terminal policy. Peer close, request deadline,
receipt deadline, successful local receipt write, preflight failure, reader
exception, application exception, and writer exception all converge on explicit
capability discard. The session wrapper adds type ownership without duplicating
the existing read/write/poll state machines.

A dedicated lexical audit inventories this boundary separately from the large
transport audit. It verifies declared ordering and retention only. It does not
promote source substrings into evidence of runtime byte counts, C++ lifetime
safety, OpenSSL semantics, durability, or protocol correctness.

## Failure matrix

| Frontier | Required behavior |
|---|---|
| Empty session/exchange label | Throw before ownership transfer or TLS work |
| Invalid/stale/misbound channel at session construction | Throw before moving the caller's channel |
| Sender-only service at session construction | Throw before moving the channel or consuming bytes |
| Allocation failure while preparing labels | Throw before stream reservation; constructor has not moved the channel |
| Borrowed exchange preflight failure | Consume zero application bytes, mutate no durable owner, discard local capability |
| Channel changes after early preflight but before durable callback | Fresh service re-attestation throws; discard stream; no receipt |
| Request deadline before first read | No durable callback; return exact zero cutpoint; discard capability |
| Partial request then deadline | Preserve exact local framing cutpoint; no durable callback; discard capability |
| Complete malformed request | No receipt; discard capability; do not reinterpret later bytes |
| Durable receiver effect then receipt deadline | Preserve inbound decision; do not roll back effect; discard capability |
| Complete local receipt write | Return `ReceiptSent`; discard capability; do not claim peer receipt |
| Session moved | Source becomes inactive; destination is sole active owner |
| Active session overwritten by move assignment | Discard displaced capability before accepting replacement |
| Session destroyed or explicitly abandoned before run | Discard local capability without TLS or durable work |
| Second `run_or_throw` | Reject inactive state before TLS or durable work |
| Fatal TLS/application exception | Preserve any already-durable effect; discard capability; higher owner closes transport |

## Runtime evidence

The real TLS/SQLite test adds a pre-byte rejection fixture:

1. a valid authenticated sender writes one framed record;
2. `FIONREAD` observes ciphertext queued on the receiver socket;
3. constructing a session with a sender-only service fails before moving the
   channel and leaves the exact queued byte count unchanged;
4. invoking the borrowed exchange with the same invalid service fails closed;
5. the exact queued byte count remains unchanged;
6. the receiver SQLite cutpoint remains unchanged;
7. no response ciphertext is emitted; and
8. the borrowed one-shot channel is poisoned.

The success fixture moves the receiver channel into a session, move-constructs a
new owner, proves the source inactive and destination active, performs exact
publication and receipt, proves the session inactive afterward, and rejects a
second run. A separate successful borrowed retry proves even `ReceiptSent` leaves
the receiver capability poisoned.

`FIONREAD` is a local Unix test observation, not a portable protocol primitive or
proof about every kernel/OpenSSL implementation. It is paired with the source
ordering, real TLS stream, and unchanged durable snapshots rather than treated
as sole authority.

## Online protocol review

The design was reviewed against primary TLS/OpenSSL material:

- TLS 1.3 closure alerts, RFC 8446 section 6.1:
  <https://datatracker.ietf.org/doc/html/rfc8446#section-6.1>
- OpenSSL 3.5 `SSL_shutdown`:
  <https://docs.openssl.org/3.5/man3/SSL_shutdown/>
- OpenSSL 3.5 `SSL_free`:
  <https://docs.openssl.org/3.5/man3/SSL_free/>

RFC 8446 distinguishes orderly `close_notify` from abortive error closure.
OpenSSL documents shutdown as a potentially two-step operation and warns that
it must not be called after specified fatal failures. Freeing an SSL object is
resource management, not a substitute for a reviewed orderly shutdown state
machine.

Those specifications constrain the next transport owner. They do not prove the
rev0889 C++ implementation, kernel buffering, peer behavior, durable effects,
package integrity, or anonymity.

## Rejected alternatives

**Discover receiver role after reading the complete frame.** This remains
mutation-safe but gives untrusted bytes resource authority before a static local
configuration decision.

**Call the early preflight once and skip the durable-frontier recheck.** A live
channel, thread, process, BIO, descriptor, socket lifetime, verification mode,
or session can change while the receiver waits. Early admission cannot mint a
lease over future durable work.

**Let successful exchange keep the channel reusable.** That contradicts the
one-request/one-receipt protocol, lets call-site discipline substitute for type
ownership, and makes later bytes inherit an unstated conversation boundary.

**Make the session copyable through shared state.** Shared lifecycle ownership
would make destruction and terminalization ambiguous and permit two call sites
to believe they own the one-run transition.

**Store relative durations and start them in `run_or_throw`.** That lets queueing
or caller delay renew the budget after channel acquisition. Absolute cutpoints
must be frozen by the policy owner.

**Call `SSL_shutdown` from `discard_noexcept`.** The capability does not own the
raw transport; shutdown can block or WANT, can be invalid after fatal errors,
and needs result classification plus a close deadline. A `noexcept` poison
primitive must not fake that larger state machine.

**Close the BIO descriptor in the session destructor.** The direct socket BIO is
configured caller-owned (`BIO_NOCLOSE`) in the supported path. Closing it here
would be an ownership violation and could race another raw holder.

**Take a full effect snapshot during preflight.** It would scan potentially
large state before reading every request while still failing to guarantee future
capacity, filesystem, or transaction success. The role pointer and live channel
are the early facts; exact durable methods classify the rest.

## Nonclaims and remaining gaps

Rev0889 does not claim:

- a production listener, socket acceptor, TLS handshake loop, or daemon;
- ownership or closure of raw `SSL*`, BIO chains, or socket descriptors;
- `close_notify`, peer-observed close, peer receipt, or transport flush;
- automatic deadline wakeup if the event loop never schedules the session;
- safe use if the referenced file-delivery service is destroyed first;
- safety against hostile same-process code retaining and mutating raw OpenSSL or
  descriptor handles;
- exactly-once network delivery or atomicity across independent databases;
- complete crash injection at every TLS, SQLite, payload, rename, directory
  durability, receipt, settlement, and close frontier;
- membership enrollment, key rotation, revocation, recovery, rollback
  protection, or old-epoch policy;
- peer/folder connection quotas, fairness, admission queues, staged-payload
  expiry, dead-letter ownership, or garbage collection;
- an indexed/scalable production owner, causal compaction, or offline rejoin;
- deletion, rename, directory, permission, or general conflict-effect protocol;
- traffic-analysis resistance, unlinkability, anonymity, or metadata privacy;
- externally trusted build provenance; or
- that lexical audits prove runtime ordering, byte non-consumption, lifetime
  safety, shutdown semantics, durability, package integrity, or security.

The next useful slice is an exclusive accepted-transport owner that composes
socket/`SSL*` RAII, authenticated channel construction, one rev0889 receiver
session, connection and peer/folder quotas, clean-success versus abortive-error
shutdown policy, and bounded close. Only after that owner exists should a
long-running listener expose this path. Persistent retry/dead-letter state and a
scalable indexed owner differentially checked against the current full-history
oracle remain separate production milestones.

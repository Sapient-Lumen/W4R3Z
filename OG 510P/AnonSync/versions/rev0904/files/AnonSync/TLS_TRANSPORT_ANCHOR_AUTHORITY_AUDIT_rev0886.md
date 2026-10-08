# TLS transport-anchor authority audit — rev0886

## Finding

AnonSync's authenticated TLS capability already bound a completed TLS 1.3
session to the expected peer SPKI, ALPN, exporter value, process incarnation,
thread incarnation, one duplex record reservation, and—since rev0885—the exact
Linux socket lifetime observed at strict record entry and every readiness
frontier. That still left a material authority gap before the first record and
inside an incomplete record operation.

The `SSL*` supplied to authentication remains a mutable OpenSSL object. A caller
that retained that raw handle could call `SSL_set_fd`, `SSL_set_rfd`,
`SSL_set_wfd`, or `SSL_set_bio` after authentication. `SSL_set_fd` constructs a
new socket BIO and frees the previously attached BIO ownership as documented by
OpenSSL. A caller could also retain a BIO pointer and invoke `BIO_set_fd` in
place. These mutations are distinct from ordinary descriptor ABA:

1. replacing the BIO changes the I/O object through which the authenticated SSL
   state will next operate;
2. mutating a socket BIO in place preserves its pointer while changing its
   descriptor; and
3. replacing a BIO can free the old object, allowing allocator address reuse to
   make pointer-only observation look continuous.

Rev0885 observed the socket lifetime only when a strict record operation began.
Consequently, a BIO replacement between authentication and first use could be
accepted as the initial strict socket proof. During a pending WANT, the cached
socket lifetime rejected ordinary descriptor replacement, but it did not prove
that the SSL object's current BIO pointer was the same BIO on which the
authenticated capability had been established. That is an authority laundering
path: peer and exporter evidence derived from one channel could be presented
beside a different transport adapter.

The first anchor draft also had a concrete ownership leak for caller-managed
filter BIOs. It retained the top-level BIO correctly with `BIO_up_ref`, but its
RAII deleter called `BIO_free`. OpenSSL documents that `BIO_free` releases only
one BIO and leaks the remainder when used on a chain. If `SSL_set_bio` detached
a retained filter chain, OpenSSL's own `BIO_free_all` stopped at the nonzero
anchor reference; the anchor's later head-only release could then strand every
downstream BIO. This was not an authority escalation, but it was a repeatable
resource leak on a supported caller-managed path and therefore a serious
long-lived-service defect.

## Authority invariant

The rev0886 invariant is:

> An authenticated channel owns the exact OpenSSL read and write BIO objects
> observed at its authentication-time capability frontier. Direct socket BIOs
> additionally own exact directional Linux `SOCK_STREAM` lifetime identities.
> Every later authority use must reprove BIO pointer identity, in-place BIO
> descriptor identity, and kernel socket lifetime before trusting peer,
> exporter, readiness, record, delivery-service, or durable-owner authority.
> Current `O_NONBLOCK` is mutable policy and must be reproved separately at each
> strict readiness frontier. A retained top-level BIO owns its complete chain
> lifetime and must release that chain with OpenSSL's chain-aware destructor.

This deliberately distinguishes three things that rev0885 partially combined:

- **BIO object identity** — retained OpenSSL object references and pointer
  equality;
- **kernel stream lifetime** — descriptor, stream type, device/inode evidence,
  and Linux `SO_COOKIE`; and
- **readiness policy** — the current `O_NONBLOCK` file-status flag.

A descriptor number is not authority. A BIO pointer by itself is not kernel
transport authority. `O_NONBLOCK` is not immutable identity. The authenticated
capability requires the strongest evidence available for each layer and refuses
to silently substitute one layer for another.

## OpenSSL and operating-system research

The implementation was checked against current primary documentation:

- OpenSSL `SSL_set_fd` documents that it creates a socket BIO and frees an
  already connected BIO; `SSL_set_rfd` and `SSL_set_wfd` can replace directions
  independently:
  <https://docs.openssl.org/3.5/man3/SSL_set_fd/>
- OpenSSL `SSL_get_fd` documents that the read and write descriptors can differ,
  so one undirected descriptor observation is insufficient:
  <https://docs.openssl.org/3.5/man3/SSL_get_fd/>
- OpenSSL BIO allocation documentation defines `BIO_up_ref` as retaining an
  additional reference, `BIO_free` as releasing only one BIO, and
  `BIO_free_all` as freeing an entire chain. It explicitly warns that applying
  `BIO_free` to a chain leaks the remainder:
  <https://docs.openssl.org/3.5/man3/BIO_new/>
- OpenSSL socket-BIO control documentation exposes `BIO_get_fd`/`BIO_set_fd` and
  therefore confirms that a BIO can preserve object identity while its
  descriptor association changes:
  <https://docs.openssl.org/3.5/man3/BIO_s_socket/>
- OpenSSL `SSL_read_ex` and `SSL_get_error` documentation requires an incomplete
  nonblocking operation to be retried according to its WANT condition and
  requires error classification immediately after the failed I/O call in the
  same thread:
  <https://docs.openssl.org/3.5/man3/SSL_read/>
  <https://docs.openssl.org/3.5/man3/SSL_get_error/>
- OpenSSL's nonblocking TLS guide treats readiness as a reason to retry an
  existing operation, not as proof that the underlying object or session is
  unchanged:
  <https://docs.openssl.org/3.5/man7/ossl-guide-tls-client-non-block/>
- Linux `socket(7)` describes `SO_COOKIE` as a socket-specific value suitable
  for identifying one socket while it exists. It is used only as local
  observational evidence, never as cryptographic or protocol identity:
  <https://man7.org/linux/man-pages/man7/socket.7.html>
- Linux `fcntl(2)`/`F_GETFL` semantics make `O_NONBLOCK` a mutable file-status
  flag associated with the open file description, not an immutable property of
  the descriptor integer:
  <https://man7.org/linux/man-pages/man2/fcntl.2.html>
  <https://man7.org/linux/man-pages/man2/F_GETFL.2const.html>

These sources support the threat model and API constraints. They do not prove
this C++ implementation, its race freedom, allocator behavior under arbitrary
memory corruption, kernel uniqueness under every fault, or end-to-end delivery.
The conclusions below are applied engineering inferences tested by compiled
negative cases.

## C++ implementation

### Authentication-time transport anchor

`src/sync_replica_tls_transport.cpp` adds a move-only
`SyncReplicaTlsTransportAnchor` owned by the shared authenticated state. It
contains:

- a retained reference to the exact read BIO;
- a retained reference to the exact write BIO;
- an optional exact Linux socket lifetime for the read direction; and
- an optional exact Linux socket lifetime for the write direction.

`capture_tls_transport_anchor_or_throw` obtains both current BIO pointers,
retains each with `BIO_up_ref`, observes direct socket lifetimes, constructs the
anchor, and immediately validates the result against the live SSL object. If
read and write share one socket BIO, the directional values may contain equal
lifetime evidence while retaining independent reference-count ownership.

Retention is essential rather than decorative. If a later `SSL_set_fd` or
`SSL_set_bio` detaches the original BIO, the anchor's reference prevents that
BIO object from being destroyed and its address reused. A later pointer equality
therefore denotes the retained object rather than an allocator coincidence.
The anchor releases those references through RAII with `BIO_free_all`, matching
OpenSSL's own SSL/BIO ownership rule. For a direct socket BIO this is equivalent
to freeing one BIO. For a caller-managed filter BIO it ensures that the final
retained reference eventually traverses and releases the entire downstream
chain rather than only its head.

Authentication now captures this anchor after the completed TLS profile is
validated and before final peer-SPKI/exporter derivation. It revalidates the
anchor after those derivations and before publishing the authenticated state.
This detects mutation during capability construction and prevents a partially
mixed identity/transport snapshot from escaping.

### Directional validation

`validate_tls_transport_anchor_direction_or_throw` fails closed in this order:

1. the current OpenSSL BIO pointer must equal the retained object;
2. if a direct socket lifetime was captured, the BIO method must remain a socket
   BIO;
3. its current `BIO_get_fd` value must equal the anchored descriptor; and
4. the descriptor must still name the exact captured Linux stream-socket
   lifetime.

The read and write directions are checked independently. This matters because
OpenSSL allows distinct directional BIOs and descriptors. A mutation on only
one side cannot borrow authority from the other.

### Immutable lifetime versus mutable readiness policy

The generic leaf previously named `SyncSocketReadinessIdentity` included
`O_NONBLOCK` in the captured identity. That made a mutable policy bit appear to
be part of immutable socket lifetime and caused two avoidable problems:

- a blocking direct socket could not be authenticated even when the caller used
  the explicitly caller-managed blocking API; and
- toggling readiness policy looked indistinguishable from replacing the socket.

Rev0886 refactors that leaf into `SyncSocketLifetimeIdentity` while retaining
its established source filenames and CMake target names for package stability.
Capture requires an exact Linux `SOCK_STREAM`, stable `fstat` observations, and
stable nonzero `SO_COOKIE` observations. It no longer requires `O_NONBLOCK`.

`require_sync_stream_socket_nonblocking_or_throw` is a separate policy proof. It
reproves the exact lifetime, reads `F_GETFL`, requires `O_NONBLOCK`, and reproves
the lifetime again. This identity-policy-identity sandwich prevents policy
inspection from silently spanning descriptor replacement. Clearing
`O_NONBLOCK` no longer falsifies lifetime equality, but it prevents strict
bounded-readiness entry or continuation.

### Channel and continuation frontiers

The authenticated state now has one immutable transport anchor instead of a
second mutable per-record socket-proof cache. The refactor reduces duplicated
authority and makes the following frontiers explicit:

- **ordinary channel authority:** transport anchor first, then live
  peer/exporter session revalidation;
- **strict record reservation before any I/O:** full channel authority, followed
  by nonblocking policy proof; an otherwise valid blocking/custom BIO is a
  preflight policy rejection and does not poison an untouched channel;
- **fresh write after accepted prefix:** full transport/session revalidation
  plus nonblocking policy before one new bounded `SSL_write_ex` operation;
  failure poisons because framing progress already exists;
- **fresh incremental read step:** full transport/session revalidation before a
  new OpenSSL operation;
- **pending read or write WANT retry:** exact transport-anchor and policy
  reproof only, then the same heap-stable buffer pointer and length are supplied
  to the incomplete `SSL_read_ex` or `SSL_write_ex` operation; unrelated
  peer/exporter OpenSSL calls do not interpose in that retry frontier;
- **poll-target disclosure:** ownership, exact anchor, and policy are reproved
  before returning the advisory descriptor; and
- **completion, peer close, abandonment, or contradiction:** the reservation is
  released or the channel is permanently poisoned according to whether stream
  progress had occurred.

`SSL_get_error` remains immediately adjacent to each failed `SSL_read_ex` or
`SSL_write_ex` call. Transport reproof happens before entering OpenSSL, not
between the I/O result and its error classification. The exact owned writer
state machine is audited separately in
`TLS_INCREMENTAL_WRITE_AUDIT_rev0886.md`.

### Exception and ownership review

BIO retention occurs in local RAII values before shared state publication. If
retaining the second BIO, observing either socket, constructing diagnostics, or
final authentication validation throws, already acquired references are
released by stack unwinding. The RAII type is deliberately chain-aware: its
deleter is `BIO_free_all`, not `BIO_free`. Independent retained read/write
references remain safe when both directions share one top BIO because
`BIO_free_all` stops while the top reference count is nonzero; whichever final
owner reaches zero performs the downstream traversal.

The authenticated-state constructor validates the complete anchor before
calling `SSL_up_ref`. After successful `SSL_up_ref`, the constructor performs
only no-throw member publication. This prevents an extra SSL reference from
being leaked by a later throwing operation. Destruction and move paths continue
to enforce process/thread ownership before releasing OpenSSL state.

The retained BIO references do not authorize concurrent raw mutation. OpenSSL
object mutation and record I/O must remain serialized by the channel owner.
Unsynchronized mutation is outside the C++ memory model and can invalidate any
observational proof before it can fail closed.

## Failure matrix

| Mutation or condition | Frontier exercised | Required result |
|---|---|---|
| `SSL_set_fd` after authentication, before first record | strict record begin | Rejected because the current BIO object differs; channel poisoned as an authority contradiction |
| `BIO_set_fd` on the retained socket BIO | strict record begin | Rejected because the in-place descriptor differs; channel poisoned |
| `SSL_set_fd` after the encrypted length prefix | writer body entry | Rejected before body progress; channel remains poisoned because the stream cutpoint is no longer reusable |
| `SSL_set_fd` while `SSL_read_ex` is pending on WANT | poll-target lookup | Rejected before a stale descriptor is disclosed; continuation abandoned and channel poisoned |
| `BIO_set_fd` while WANT is pending | exact retry | Rejected before re-entering OpenSSL; continuation abandoned and channel poisoned |
| close/`dup2` replacement at the same descriptor | poll, retry, fresh read, or writer body | Rejected by exact Linux socket-lifetime reproof even though the integer is unchanged |
| valid direct stream socket becomes blocking before strict entry | pre-I/O policy check | Rejected without poisoning an otherwise untouched channel |
| valid direct stream socket becomes blocking after progress or pending WANT | continuation frontier | Rejected and poisoned because the incomplete operation cannot be truthfully resumed |
| datagram socket, pipe, non-socket fd, or missing exact Linux lifetime | strict mode | Rejected before I/O |
| custom/filter BIO under caller-managed mode | blocking/caller-managed API | Permitted with explicit nonclaim about mutable hidden transport |
| retained caller-managed filter chain is detached with `SSL_set_fd` | authenticated-state destruction | Exact top BIO remains alive until anchor release; final `BIO_free_all` destroys both filter head and downstream socket BIO exactly once |
| stale peer, exporter, process, thread, reservation, or close state | corresponding existing frontier | Existing fail-closed behavior remains in force |

The runtime matrix uses completed TLS 1.3 socket pairs, not mocks, for the BIO
replacement and descriptor mutation paths. Source audits inventory the intended
frontiers but remain lexical hygiene rather than proof.

## Rejected alternatives

### Capture only `SSL_get_rfd`/`SSL_get_wfd`

Rejected. Descriptor integers are reusable, and these accessors do not retain or
identify the BIO object. This would regress to the exact ABA problem rev0885
corrected and would not detect `SSL_set_fd` followed by installation of another
socket at the same integer.

### Compare only BIO pointers

Rejected. `BIO_set_fd` mutates a socket BIO in place, so pointer identity alone
cannot detect a changed kernel transport. Without retaining a reference, BIO
replacement could also free and allocator-recycle an address.

### Release retained BIOs with `BIO_free`

Rejected after ownership review. `BIO_free` is sufficient only for a single BIO.
The public channel permits caller-managed top-level filter BIOs, so the retained
object can be the head of a chain. OpenSSL explicitly documents that head-only
free leaks the remainder. The anchor therefore mirrors SSL ownership and uses
`BIO_free_all` for every retained reference.

### Treat `O_NONBLOCK` as socket identity

Rejected. It is mutable open-file-description policy. The socket lifetime can be
unchanged while the correct strict-readiness decision changes. Identity and
policy now have separate types and proof functions.

### Re-capture a new transport at every record

Rejected. Re-capture would bless post-authentication mutation instead of proving
continuity. The immutable authentication anchor is the authority; later
observations are comparisons against it.

### Re-run peer/exporter queries before a pending WANT retry

Rejected. OpenSSL requires the failed I/O result to be classified immediately,
and an incomplete operation must be retried with stable arguments. The retry
frontier performs only observational BIO/socket checks before repeating the
same operation. Full session checks occur at fresh-operation boundaries.

### Make all preflight failures poison

Rejected. A caller-managed blocking channel can be valid even though it cannot
enter the strict nonblocking API. Pure policy mismatch before any record I/O is
not evidence that the authenticated session or stream is corrupt. Actual anchor
contradiction always poisons; policy loss poisons after progress or pending WANT.

## Audit/refactor scope

The old socket audit was rewritten to inventory immutable stream lifetime and
mutable readiness policy as separate concepts. It checks `SOCK_STREAM`, stable
`SO_COOKIE`, double observations, the readiness sandwich, rejection matrices,
CMake linkage, and verifier surface.

A new `audit_sync_tls_transport_anchor.py` inventories authentication ordering,
BIO reference retention, directional pointer/descriptor/lifetime validation,
state ownership, pre-I/O policy behavior, accepted-prefix and WANT frontiers,
poll-target proof, immediate `SSL_get_error`, compiled test labels, CTest
registration, release-verifier requirements, and explicit nonclaims. A second
new `audit_sync_tls_write_continuation.py` inventories exact frame ownership,
bounded write steps, same-argument WANT retry, completion, abandonment, and the
durable file-dispatch cutpoint.

The existing TLS receive-continuation and file-dispatch audits were updated to
refer to the immutable authentication anchor rather than the removed mutable
per-record proof. The transport runtime also uses destruction callbacks on a
null-filter head and its downstream socket BIO: SSL replacement must destroy
neither while retained, and final channel release must destroy both exactly
once. This deterministic ownership assertion complements ASan/LSan rather than
relying on leak detection alone. These scripts can detect accidental
source-shape drift; they cannot establish OpenSSL semantics, memory safety,
concurrency safety, kernel identity, or delivery correctness.

## Remaining risks and deliberate nonclaims

Rev0886 does not claim:

- safe unsynchronized mutation of `SSL`, BIO, descriptor, or file-status state;
- historical proof that no caller replaced the transport after the handshake
  but before invoking AnonSync authentication;
- proof of the mutable source/sink hidden beneath a retained custom or filter BIO;
- strict exact-lifetime support outside Linux;
- cryptographic, durable, globally unique, or remotely meaningful identity for
  `SO_COOKIE`, inode, descriptor, or BIO address;
- a production poll/epoll owner, backpressure controller, connection acceptor,
  deadline/cancellation scheduler, or bounded ready-work queue;
- bounded OpenSSL CPU time, kernel work, scheduler delay, or wall-clock latency;
- durability of partial TLS record position across process or connection loss;
- receiver SQLite/effect composition in the shipped `anonsync_core` executable;
- exactly-once remote effect, complete retry/dead-letter policy, membership/key
  lifecycle, compaction/rejoin, anonymity, unlinkability, endpoint hiding, or
  traffic-analysis resistance;
- ThreadSanitizer, formal verification, reproducible machine code, or externally
  trusted signed provenance.

For a custom/filter BIO, the anchor proves only that the top-level retained BIO
object remains attached. Its method callbacks or downstream chain may contain
mutable state that this adapter cannot inspect. Strict mode therefore requires
an authentication-anchored direct socket BIO in both directions. Caller-managed
mode deliberately preserves broader OpenSSL composition but carries that
nonclaim.

## Next mission seam

With the exact writer continuation now implemented and documented in
`TLS_INCREMENTAL_WRITE_AUDIT_rev0886.md`, the next highest-value step remains an
executable receiver owner rather than more isolated transport vocabulary. It should own authentication, the exact
channel and event-loop registration, bounded continuation queues, canonical
frame decoding, SQLite receiver idempotency, staged payload/effect ownership,
atomic visible publication, terminal effect receipt, and sender settlement.

The new anchor gives that owner a credible rule for event-loop registration:
register only the advisory descriptor returned after exact proof, serialize all
raw SSL/BIO/fd mutation behind the owner, and discard the connection on any
proof contradiction. Crash injection must remain at canonical message/effect
frontiers; no design should attempt to durably resume a partial TLS byte stream
on a different connection.

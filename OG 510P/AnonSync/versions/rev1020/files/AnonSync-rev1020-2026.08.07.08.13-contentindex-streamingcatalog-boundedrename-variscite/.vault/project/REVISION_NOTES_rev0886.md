# AnonSync rev0886 revision notes

## Mission

AnonSync is an evidence-authorized convergence system under construction. Exact
validated history and live owned capabilities govern identity, causality,
dispatch, retry, receipt, visible effect, and cleanup. File-descriptor integers,
BIO addresses, readiness notifications, TLS return codes, caller-owned buffers,
summaries, indexes, source audits, and build reports are subordinate evidence;
none may silently manufacture continuity or delivery authority.

Rev0886 closes two adjacent TLS authority gaps:

1. the authenticated capability now retains and re-proves the exact OpenSSL BIO
   objects and direct Linux socket lifetimes observed during authentication; and
2. the accepted-prefix writer now privately owns the exact bounded frame and
   resumes one incomplete nonblocking `SSL_write_ex` operation across WANT; and
3. one duplex bounded poll owner now composes exact read/write WANT frontiers
   with target reproof and one absolute monotonic scheduling deadline.

## Severe defects corrected

### Authentication identity could outlive its transport

Rev0885 captured an exact Linux socket lifetime when strict record I/O began and
reproved it at WANT, poll, fresh-read, and writer-body frontiers. It did not bind
the exact OpenSSL BIO objects at authentication.

A caller retaining the raw `SSL*` could invoke `SSL_set_fd` or `SSL_set_bio`
after authentication but before first record I/O. The replacement transport
would become the first socket lifetime rev0885 observed while still borrowing
peer-SPKI and exporter authority derived from the old channel. During an
incomplete operation, replacing the BIO or mutating it in place with
`BIO_set_fd` also sat outside the cached socket proof's object model.

Rev0886 makes the transport observed during authentication immutable capability
evidence.

### Retained filter BIO chains could leak downstream objects

The first transport-anchor draft paired `BIO_up_ref` with an RAII deleter that
called `BIO_free`. That is correct for one direct BIO but not for a top-level
filter BIO. OpenSSL documents that `BIO_free` frees only one object and leaks the
rest of a chain. After SSL detached a chain while the anchor still retained its
head, a later head-only anchor release could strand the downstream socket BIO.
Rev0886 now uses `BIO_free_all`, matching SSL's own ownership semantics.

### Prefix authority did not own body identity

The rev0885 move-only writer retained the frame length after the encrypted
length prefix succeeded, but the caller retained the body bytes and supplied
them later to `finish_or_throw(frame)`. A caller could substitute a different
same-length canonical frame between those calls. The length check would pass,
joining durable claim authority for one message to wire bytes from another.

The synchronous body helper also treated ordinary nonblocking
`SSL_ERROR_WANT_READ` or `SSL_ERROR_WANT_WRITE` as terminal channel loss. That
was fail-closed, but it discarded a healthy connection instead of preserving
the exact pending OpenSSL operation for a bounded event loop.

Rev0886 copies the exact bounded frame into heap-stable private state before the
prefix can succeed and exposes typed, resumable body progress.

## C++ implementation

### Retained directional BIO/socket anchor

The authenticated shared state now owns a move-only transport anchor containing
retained references to both exact OpenSSL read/write BIO objects. `BIO_up_ref`
prevents a detached BIO from being destroyed and allocator-recycled into false
pointer continuity. Read and write directions remain independent because
OpenSSL permits different BIOs and descriptors.

The retained-reference RAII deleter is `BIO_free_all`. A direct socket BIO is
still released as one object, while the final reference to a caller-managed
filter chain releases its complete downstream chain. Two retained directions
that share one top BIO remain reference-count safe: chain traversal occurs only
when the final reference reaches zero.

For each direct socket BIO on Linux, authentication also captures one exact
`SOCK_STREAM` lifetime. Every later channel-authority use checks:

1. current BIO pointer equals the retained object;
2. direct socket method remains present where it was captured;
3. current BIO descriptor equals the anchored descriptor; and
4. that descriptor still names the exact captured kernel socket lifetime.

Authentication captures the anchor before final SPKI/exporter derivation and
revalidates it before publishing the channel capability. Delivery authority,
strict record reservation, accepted-prefix body entry, fresh read/write steps,
pending WANT retry, and poll-target disclosure all consult the same immutable
anchor.

### Lifetime/readiness refactor

The generic socket leaf is now `SyncSocketLifetimeIdentity`. Established source
filenames and target names remain stable, but `O_NONBLOCK` is no longer treated
as immutable identity.

Lifetime capture requires an exact Linux `SOCK_STREAM`, stable `fstat` evidence,
and stable nonzero `SO_COOKIE` observations. `O_NONBLOCK` is separate mutable
policy checked by `require_sync_stream_socket_nonblocking_or_throw()`. The helper
reproves lifetime, reads `F_GETFL`, requires the flag, and reproves lifetime
again.

This split allows a valid blocking socket to remain usable through the explicit
caller-managed API while strict readiness mode fails before I/O. A pure
preflight policy mismatch does not poison an untouched channel. Loss of policy
after framing progress or a pending WANT poisons because the continuation can no
longer satisfy its declared contract.

### Exact owned write continuation

`SyncReplicaTlsRecordWriteContinuation` is now a move-only `unique_ptr` PIMPL.
Its private state owns:

- the exact frame string;
- completed and pending body offsets;
- exact pending request length;
- typed WANT direction;
- strict readiness policy;
- the exclusive Write reservation; and
- shared authenticated channel authority.

The public begin API receives a `std::string_view`, validates empty/maximum
bounds, and only then makes one private body copy. That ordering prevents an
over-limit lvalue from forcing an equally large duplicate allocation. All local
allocation and diagnostic construction happens before stream reservation. Once
the complete eight-byte prefix succeeds, returning the continuation is a
no-throw pointer move.

The caller can no longer supply body bytes after prefix acceptance.
Same-length mutation of its original buffer cannot change the private frame.
Destroying or move-assigning an active writer abandons and poisons the stream.

### Bounded resumable `SSL_write_ex`

Each `advance_or_throw()` performs at most one body `SSL_write_ex` request and
selects no more than 64 KiB for a fresh operation. Before entry, it records the
exact private-string offset and length. WANT_READ or WANT_WRITE does not advance
that cutpoint. A retry reuses the same pointer and length after exact
reservation, BIO/socket, process/thread, and nonblocking-policy reproof.

`ERR_clear_error()` precedes I/O. On failure, `SSL_get_error()` is the immediate
next OpenSSL call in the same thread. Successful short writes are accepted so
`SSL_MODE_ENABLE_PARTIAL_WRITE` remains compatible: the next call begins at the
first byte not reported written.

`pending_readiness_or_throw()` exposes one typed advisory descriptor only in
strict direct-socket mode and only after WANT. Caller-managed or pre-WANT lookup
rejects without poisoning. Once system reproof discovers stale transport or
policy, exact retry is impossible, so the continuation is abandoned and the
stream poisoned.

The old synchronous `finish_or_throw()` now delegates to the incremental state
machine. It continues ordinary successful progress, returns on completion, and
fails rather than spinning on nonblocking WANT. The one-shot writer delegates to
the same implementation.

### Durable file-dispatch composition

The file-delivery dispatcher passes the exact frozen canonical frame into
`begin...`, retains the SQLite outbox-dispatch guard through complete prefix
acceptance, commits its bounded clock observation, releases the database writer,
and only then performs the potentially large body transfer.

The continuation already owns the exact frame when database authority is
released. Failure before prefix acceptance exact-releases the claim. Failure
after prefix acceptance remains an ambiguous attempt and never fabricates peer
receipt or retry authority.

## Duplex bounded poll owner

`SyncReplicaTlsRecordReadContinuation` and
`SyncReplicaTlsRecordWriteContinuation` now share one isolated `poll(2)`
composition leaf. It accepts only a strict continuation already at WANT, asks
the continuation for the exact re-proved readiness target before every wait,
and uses one absolute `steady_clock` cutpoint. Positive fractional milliseconds
round upward, large intervals clamp to `INT_MAX`, and `EINTR`/`EAGAIN` restart
from target reproof without renewing the deadline.

A nonzero wakeup authorizes at most one `advance_or_throw()`. Error, hangup, and
invalid descriptor bits are advisory; the continuation and OpenSSL retain
protocol classification. Deadline expiry leaves exact pending read state or
write pointer/length/cutpoint unchanged. The read and write public result enums
preserve their distinct clean-close and terminal states. Unsupported platforms
fail closed.

The real TLS runtime covers read and write pre-WANT rejection, already-expired
and idle timeout retention, one-step prefix/body separation, clean close, real
signal delivery during the bounded wait, saturated write retry, and a complete
two-megabyte cooperative transfer. Every successful write poll advances no
more than the public 64 KiB write-operation budget.

## Release verifier authority correction

The failed package gate was not a source defect. The verifier applied a
`build-` directory heuristic to the final file basename, rejecting the valid
`build-shape-observation.json` evidence file, while an exact `build/` directory
was not forbidden. `is_forbidden_release_file()` now applies exact and prefix
build rules only to `path.parts[:-1]`; suffix and forbidden-basename rules own
the final file. A registered executable matrix covers actual generated trees
and legitimate evidence/documentation names. Renaming evidence to satisfy the
wrong classifier was deliberately rejected.

## Audit and refactor

The mutable per-record socket-proof cache was removed. One authentication-time
anchor owns transport identity; record state retains only reservation, progress,
readiness requirement, stable retry buffer, and terminal status.

Read and write share one private pending-readiness enum and one authenticated-
state target mapper. During refactor, a harmless caller-managed or no-WANT target
query briefly fell inside the same poison-on-failure block as stale socket
reproof. That would have destroyed a valid continuation merely for asking an
invalid optional question. The semantic precondition checks now occur before
the system-authority catch block, and compiled reader/writer cases prove
rejection without mutation.

The same ownership review found that the anchor's original `BIO_free` deleter
was single-object cleanup applied to a potentially chained object. It was
replaced by `BIO_free_all`, and the runtime now attaches destruction callbacks
to both a null-filter head and its downstream socket BIO. Detaching the chain
cannot destroy either retained object early; releasing the channel must destroy
both exactly once. This turns a sanitizer-only leak suspicion into a
deterministic ownership assertion.

New `tools/audit_sync_tls_write_continuation.py` inventories construction order,
private ownership, exact retry state, bounded progress, immediate error
classification, target semantics, failure cleanup, file-dispatch cutpoints,
runtime cases, CTest registration, package surface, and explicit nonclaims.
Existing transport-anchor, receive-continuation, delivery-channel,
socket-lifetime, and file-dispatch audits were updated for the shared authority
model. These scripts remain lexical hygiene, not semantic proof.

Detailed primary-source review, state machines, failure matrices, rejected
alternatives, and residual risks are recorded in:

- `TLS_TRANSPORT_ANCHOR_AUTHORITY_AUDIT_rev0886.md`; and
- `TLS_INCREMENTAL_WRITE_AUDIT_rev0886.md`; and
- `TLS_DUPLEX_POLL_AUTHORITY_AUDIT_rev0886.md`.

## Compiled negative matrix

The real TLS 1.3 runtime now forces and rejects or safely resumes:

- `SSL_set_fd` after authentication before first record;
- counted complete release of a retained filter-over-socket BIO chain after
  post-authentication replacement;
- in-place `BIO_set_fd` after authentication;
- BIO replacement after an accepted prefix and before body;
- BIO replacement during pending read or write WANT;
- close/`dup2` descriptor ABA at writer, poll, retry, and fresh-step frontiers;
- loss of `O_NONBLOCK` before exact pending retry;
- blocking direct sockets in strict mode while preserving untouched
  caller-managed reuse;
- same-length mutation of caller bytes after prefix acceptance;
- two-megabyte nonblocking body backpressure through typed WANT, wrapper move,
  bounded repeated progress, and exact peer-byte completion;
- absolute-deadline read/write poll expiry without consuming exact WANT state;
- `EINTR` restart with target reproof and no deadline renewal;
- one-prefix-step isolation, OpenSSL-owned clean close, and duplex poll-driven
  exact peer-byte completion under write backpressure;
- release-path rejection of actual build trees while accepting build-named
  evidence files;
- caller-managed or pre-WANT target lookup without false poisoning; and
- existing stale process/thread, duplex reservation, exporter, peer, framing,
  file-dispatch, retry-release, and durable-owner contradictions.

Final numeric build, runtime, sanitizer, stress, audit, projection, manifest,
directory, and ZIP results are generated only after the immutable source
snapshot passes the release gates. They are recorded in `RELEASE_GATE.json` and
`REVISION_EVIDENCE/rev0886/`.

## Research and inference

The design was checked against current OpenSSL 3.5 primary documentation for
`SSL_write_ex`, `SSL_get_error`, `SSL_CTX_set_mode`, `SSL_set_bio`, BIO reference
ownership, and nonblocking retry, plus Linux socket-cookie and descriptor
semantics. Those sources support the requirements that a write can WANT either
read or write readiness, a retry must preserve its arguments because data may
already have been processed, successful partial-write mode begins a new
operation at the remaining bytes, error classification is same-thread and
immediate, and BIO replacement can free prior objects. OpenSSL's BIO allocation
documentation additionally states that `BIO_free` frees only one BIO and leaks
the remainder of a chain, while `BIO_free_all` performs chain-aware release.
That constraint directly caused the anchor RAII correction.

The sources do not prove this implementation, race freedom, compiler output,
kernel correctness, peer receipt, durable delivery, or anonymity. Applied
inferences and exact links are retained in the three rev0886 transport audits and current
revision research evidence.

## Cloudtainer retention correction

Validation initially stopped because retained, reproducible build and sanitizer
trees from older revisions exhausted the cloudtainer filesystem. The cleanup
removed only regenerated compiler outputs and kept source workspaces, compact
revision evidence, parent archives, and sealed handoffs. This is operational
hygiene rather than product correctness, but it prevents stale build products
from becoming a de facto denial of validation. The observed failure mode,
retention boundary, and recommended content-addressed build-cache policy are
recorded in `CLOUDTAINER_BUILD_RETENTION_AUDIT_rev0886.md`.

## Remaining mission gap

The authenticated transport now has symmetric typed incremental read and write
owners, but they remain primarily exercised through tests and service seams.
The shipped executable still lacks one complete path from authenticated event-
loop input through canonical decoding, receiver SQLite idempotency, bounded
payload/effect staging, atomic visible publication, terminal effect receipt, and
exact sender settlement.

The next milestone should be a bounded process/thread-affine receiver service
that exclusively owns raw SSL/BIO/fd mutation, poll/epoll registration,
continuation queues, channel and frame memory ceilings, durable operation
acceptance, effect publication, and terminal receipt dispatch. Connection loss
must discard partial TLS byte state and retry canonical messages or payload
chunks above transport.

## Deliberate nonclaims

Rev0886 does not claim safe unsynchronized raw SSL/BIO/fd or socket-mode
mutation, historical proof before AnonSync authentication, hidden transport
identity inside custom/filter BIOs, strict exact-lifetime support outside Linux,
cryptographic or durable meaning for `SO_COOKIE`, a production event loop,
thread/process migration of pending I/O, concurrent full-duplex application I/O,
bounded wall-clock OpenSSL calls, durable partial TLS-frame resume, peer receipt
from local write completion, receiver-effect composition in `anonsync_core`,
exactly-once remote execution, complete retry/dead-letter or membership/key
lifecycle, anti-entropy/compaction/rejoin policy, production-scale indexed
ownership, ThreadSanitizer, formal proof, externally trusted signed provenance,
anonymity, unlinkability, endpoint hiding, or traffic-analysis resistance.

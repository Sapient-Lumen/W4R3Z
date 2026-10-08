# rev0885 audit record

## Heart of the mission

AnonSync is an exact-authority accounting system. Canonical evidence and live
capabilities own identity, causality, dispatch, retry, receipt, visible effect,
and cleanup. File-descriptor integers, readiness events, TLS return codes,
buffer addresses, summaries, indexes, and test reports may carry or verify
information, but they must not silently acquire authority beyond the exact
validated cutpoint that created them.

Rev0885 applies that rule below OpenSSL: a strict pending TLS operation is bound
to one authenticated session *and* the exact kernel socket lifetime beneath its
direct BIOs.

## Severe gap corrected

The parent rechecked `SO_TYPE` and `O_NONBLOCK` before strict TLS progress. A
close followed by `dup2()` could nevertheless install another nonblocking stream
socket at the same descriptor number. Those property checks would still pass,
allowing a pending `SSL_read_ex()` retry or a post-prefix write body to cross
onto the wrong transport lifetime.

The new `SyncSocketReadinessIdentity` binds a Linux descriptor to socket type,
stat device/inode/mode, and mandatory nonzero `SO_COOKIE`, with stat and cookie
double observation. Exact reproof rejects closure, descriptor reuse, socket
substitution, loss of nonblocking state, non-sockets, and unavailable evidence.
Unsupported platforms fail closed.

## Ownership and refactor

The kernel proof is now an OpenSSL-independent leaf with opaque fields. The only
public component is the advisory descriptor required by an event loop; callers
cannot compare only the cookie or serialize process-local evidence as protocol
identity.

`SyncReplicaTlsAuthenticatedState` owns one optional read/write socket proof
beside its exclusive `Idle/Read/Write` record reservation. Pending WANT retries
perform only system-call reproof, avoiding unrelated SSL-object inspection
before the exact retry. Successful progress ends that operation; each fresh
step revalidates the live peer/exporter binding and recaptures the current BIO
and socket identity. The writer repeats this at the prefix/body frontier.

`pending_readiness_or_throw()` now exposes a typed readable/writable target only
after WANT. Lookup re-proves before returning the integer; `advance_or_throw()`
proves again. Lookup failure abandons the impossible continuation and poisons the
stream. Every success, close, abandonment, poison, and reservation-contradiction
path clears the retained proof.

Each public body read requests at most 64 KiB from one `SSL_read_ex()`. This is
an application-step bound, not a wall-clock or OpenSSL-internal bound.

## Runtime evidence

- exact rev0884 parent archive independently reverified **26/26**;
- GCC 14.2 Debug full all-target graph and final no-work closure;
- complete registered gate **195/195** and audit-named gate **63/63**;
- focused authority slice **5,280/5,280** under GCC Debug, Clang 17 Release C++
  `-Werror`, and GCC ASan/UBSan with leak detection and bundled SQLite
  instrumented;
- mixed repeated campaign **7,400/7,400** checks;
- 100 TLS/socket-lifetime runs, **14,800/14,800** checks, exact iterations 1–100
  with no gaps or duplicates;
- 200 generic socket-identity runs, **1,600/1,600** checks;
- 19 selected source audits, **565/565** checks; and
- active projection `13db40823f2623f9ecda63ada9082557089e444403f8b9373037f757a54bcc7f`, exact parent delta, patch, compact
  evidence index, full manifest, and fail-closed package verification.

The TLS tests use real TLS 1.3 direct socket BIOs and deliberately replace an
owned descriptor with another nonblocking stream socket at the same number.
The matrix rejects ABA at poll-target disclosure, direct retry, a fresh read
after successful partial progress, strict writer body entry, and file-dispatch
composition.

## Corrected waste

Socket readiness syscalls previously lived inside the OpenSSL adapter, making
reuse and independent testing difficult and inviting subtly different checks.
The new leaf contains the exact Linux policy once and is private-linked by the
TLS adapter.

The first draft also overexposed raw identity fields, accepted a weaker
non-Linux tuple, and returned a stored poll descriptor without reproof. Review
removed all three shortcuts. This is a meaningful authority refactor rather
than surface cleanup.

## Remaining architectural waste

A narrow transport change still traversed a 307-action clean GCC graph and a
116-action focused cross-compiler graph. The project currently declares 76
static libraries, 90 executables, and 198 literal CTest registrations, yet
several semantic centers remain monolithic. Link-time modularity exceeds actual
ownership decomposition.

More importantly, the causal SQLite owner, file-effect owner, authenticated
delivery service, atomic publisher, and TLS state machines remain more composed
in tests than in `anonsync_core`. More isolated correctness vocabulary now has
diminishing value relative to one production-shaped receiver path.

## Next mission-critical slice

Build one bounded process/thread-affine poll or epoll owner that authenticates a
connection, drives this continuation, caps aggregate frame memory and ready
work, validates one canonical operation, enters receiver SQLite idempotency,
performs one atomic visible effect, mints a terminal effect receipt only after
durable evidence, and settles the sender only from that receipt. Inject crashes
at every prefix/body, transaction, staging, rename, directory durability,
receipt, and settlement frontier.

## Nonclaims

This revision does not claim safety under unsynchronized raw descriptor
mutation, cryptographic or durable meaning for `SO_COOKIE`, exact strict support
outside Linux, a production reactor, resumable write WANT, durable partial TLS
record resume, authenticated accept/connect or discovery, receiver-effect
composition in the shipped executable, peer receipt from local TLS completion,
exactly-once remote execution, ThreadSanitizer, formal proof, externally trusted
signed provenance, anonymity, unlinkability, endpoint hiding, or traffic-
analysis resistance.

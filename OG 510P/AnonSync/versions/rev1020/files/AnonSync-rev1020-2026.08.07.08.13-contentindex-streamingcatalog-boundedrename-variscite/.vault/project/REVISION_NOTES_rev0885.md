# AnonSync rev0885 revision notes

## Mission

AnonSync is an evidence-authorized convergence system under construction. Its
core rule is that exact validated history and live capabilities own identity,
causality, dispatch, retry, receipt, visible effect, and cleanup. Descriptor
numbers, readiness events, TLS return codes, summaries, indexes, source audits,
and build reports are subordinate evidence; none may silently manufacture
authority.

Rev0885 applies that rule to the kernel object beneath a strict nonblocking TLS
record operation.

## Severe defect corrected

Rev0884 proved that the read and write BIOs were direct sockets and that their
file-status flags included `O_NONBLOCK`. Those checks prove properties of the
*object currently occupying a descriptor number*. They do not prove it is the
same socket object on which the authenticated TLS session was established.

A concrete ABA sequence was possible:

1. a strict read entered `SSL_ERROR_WANT_READ` on descriptor 17;
2. unrelated code closed descriptor 17;
3. a fresh nonblocking stream socket was installed at 17 with `dup2()`;
4. the old `SO_TYPE` and `O_NONBLOCK` checks still passed; and
5. OpenSSL retried the pending operation through the replacement transport.

The analogous write defect existed between the already accepted eight-byte
record prefix and the frame body. Continuing either operation would mix one TLS
state machine with another kernel stream lifetime. The only truthful result is
fail-closed poisoning.

## C++ implementation

### Opaque Linux socket-lifetime capability

`src/sync_socket_readiness_identity.{hpp,cpp}` introduces
`SyncSocketReadinessIdentity`, a process-local observational value with private
identity fields and one public advisory descriptor accessor.

On Linux, capture requires and binds:

- a valid socket descriptor proven by `fstat` and `S_ISSOCK`;
- exact `SO_TYPE`;
- a mandatory nonzero `SO_COOKIE`;
- current `O_NONBLOCK` file-status state;
- identical device, inode, and mode across a second `fstat`; and
- the same cookie across a second `getsockopt`.

Exact reproof observes the original descriptor again and compares the entire
opaque tuple. Closure, `dup2` replacement, another socket lifetime, a pipe,
loss of nonblocking state, unavailable cookie evidence, or any required syscall
failure is rejected. Linux builds without `SO_COOKIE` support fail at compile
time; other platforms fail closed at runtime until an equivalently strong
adapter exists.

The value is deliberately not ownership, durable identity, a serializable
protocol field, or protection against unsynchronized raw descriptor mutation.
The channel owner must serialize `close`, `dup2`, `fcntl`, BIO replacement, and
all other raw mutation.

### TLS owner composition

The generic proof has no OpenSSL dependency. The TLS adapter now owns only the
composition policy:

- direct read/write socket BIO inspection;
- exact proof capture before accepting a Read or Write reservation;
- retention beside the authenticated channel's one duplex reservation;
- system-only reproof before an exact pending WANT retry;
- full live session/BIO/socket recapture before every fresh read operation;
- full recapture between the writer's accepted prefix and body;
- proof before returning an advisory poll target and again before retry; and
- proof removal on every completion, close, abandonment, poison, or reservation
  contradiction path.

A stale poll-target lookup abandons the impossible continuation immediately.
Because OpenSSL I/O has already been attempted, abandonment poisons rather than
pretending the channel can be reused.

### Bounded event-loop step

Each body `advance_or_throw()` supplies no more than 64 KiB to one
`SSL_read_ex()` call. Prefix reads request only the remaining prefix bytes. WANT
does not advance offsets, so the heap-stable continuation reconstructs the same
pointer and bounded length on retry.

This is an application request bound. It does not claim a bound on OpenSSL's
internal kernel reads, TLS record processing, CPU time, or scheduler latency.

## Audit and refactor

The old socket syscalls were embedded in the OpenSSL transport implementation.
That encouraged duplicated, subtly different readiness checks and made the
kernel capability difficult to test independently. Rev0885 moves them into a
small private-linked library with an isolated runtime lane.

The initial rev0885 draft was tightened during review in three material ways:

1. raw cookie/inode/type getters were removed, leaving an opaque exact value;
2. a weaker non-Linux fallback was rejected in favor of fail-closed behavior;
3. poll-target disclosure gained its own exact reproof instead of relying only
   on the later retry.

The new 31-check structural audit inventories the leaf, opaque construction,
Linux evidence ordering, TLS proof lifecycle, retry/fresh distinction, poll-
target abandonment, 64 KiB step bound, CMake linkage, runtime cases, package
surface, and explicit nonclaims. The existing receive and file-dispatch audits
were extended accordingly. These scripts remain lexical hygiene, not semantic
proof.

## Runtime evidence

The exact rev0884 parent archive SHA-256 is
`87a788275e320000e4987396520822c45c5a7cda47bf74aff5456a3dd8b82b90` and the
current verifier independently accepted it at **26/26** ZIP checks before this
revision was sealed.

The final rev0885 source snapshot completed:

- GCC 14.2 Debug full all-target build and no-work dependency closure, with no
  compiler warnings or errors in the recorded build;
- **195/195** registered CTests in one invocation;
- **63/63** audit-named registered tests in one invocation;
- **14/14 executables and 5,280/5,280 focused checks** under GCC 14 Debug;
- the same **5,280/5,280** under Clang 17 Release with C++ `-Werror`;
- the same **5,280/5,280** under GCC 14 ASan/UBSan with leak detection and the
  bundled SQLite amalgamation instrumented;
- **7,400/7,400** checks in 20 mixed authority iterations;
- **14,800/14,800** checks in 100 exact TLS/socket-lifetime runs, with a checked
  iteration sequence containing no gaps or duplicates;
- **1,600/1,600** checks in 200 isolated socket-identity runs; and
- **565/565** checks across 19 selected source audits.

The focused TLS executable reports 148 checks; the generic identity executable
reports eight. The TLS matrix uses real TLS 1.3 socket BIOs and intentionally
replaces descriptors with fresh nonblocking stream sockets at the same integer.
It rejects ABA at poll-target disclosure, direct WANT retry, fresh read after
successful progress, strict writer body entry, and file-dispatch composition.

## Research and inference

The design was reviewed against OpenSSL 3.5 documentation for `SSL_read_ex`,
`SSL_write_ex`, `SSL_get_error`, descriptor/BIO access, and nonblocking retry;
Linux documentation and the kernel change introducing `SO_COOKIE`; and POSIX/
Linux descriptor replacement semantics. Those sources support the constraints
that WANT is one incomplete operation, readiness is advisory, descriptor
integers are reusable, read and write BIO descriptors may differ, and Linux
socket cookies remain stable for a socket lifetime.

The sources do not prove this implementation, uniqueness under every possible
kernel fault, race freedom, machine code, or end-to-end delivery semantics.
Applied inferences and links are recorded in
`TLS_SOCKET_LIFETIME_AUTHORITY_AUDIT_rev0885.md` and
`REVISION_EVIDENCE/rev0885/RESEARCH.md`.

## Remaining mission gap

The latest transport, causal SQLite owner, file-effect owner, atomic publisher,
and authenticated delivery service remain more integrated in tests than in the
shipped executable. The next milestone should be one bounded process/thread-
affine receiver service:

1. authenticate and own one connection;
2. drive the typed read continuation through poll/epoll;
3. bound channels, aggregate frame bytes, complete-frame queues, and ready work;
4. decode and validate one canonical operation;
5. enter receiver SQLite idempotency and effect authority;
6. stage and atomically publish one bounded visible effect;
7. mint and send a terminal effect receipt only after durable evidence; and
8. settle the sender's exact outbox claim only from that receipt.

Crash injection should cover every prefix/body, transaction, staging, rename,
directory durability, receipt, and sender-settlement cutpoint. Partial TLS byte
positions should remain ephemeral; durable retry belongs to canonical messages
and payload chunks above a lost session.

## Deliberate nonclaims

Rev0885 does not claim safe unsynchronized descriptor mutation, a cryptographic
meaning for `SO_COOKIE`, exact strict support outside Linux, a production event
loop, resumable nonblocking write WANT, bounded wall-clock OpenSSL calls,
authenticated accept/connect or discovery, durable partial TLS-frame resume,
receiver-effect composition in `anonsync_core`, peer receipt from local TLS
completion, exactly-once remote execution, complete retry/dead-letter policy,
complete membership/key lifecycle, anti-entropy/compaction/rejoin policy,
production-scale indexed ownership, ThreadSanitizer, formal proof, externally
trusted signed provenance, anonymity, unlinkability, endpoint hiding, or
traffic-analysis resistance.

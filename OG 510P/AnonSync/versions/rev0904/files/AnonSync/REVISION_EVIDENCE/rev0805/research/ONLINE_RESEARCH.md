# Rev0805 online research and design implications

Accessed 2026-07-16. Implementation recommendations rely on official
documentation or primary research. Speculative implications are labeled.

## SQLite crash and I/O testing

SQLite's own test documentation uses alternative VFS implementations to inject
I/O failures at increasing operation counts. Its crash simulation runs the
operation in a separate process, randomly crashes during writes, reorders or
corrupts unsynchronized writes, then reopens the database and verifies that the
transaction either completed or rolled back and that the database remains
well-formed.

Sources:

- https://sqlite.org/testing.html#ioerr
- https://sqlite.org/testing.html#crashtesting

Implication for AnonSync: copy the mechanism, but add a protocol oracle. SQLite
can establish whether its database is structurally sound and whether a SQLite
transaction committed or rolled back. AnonSync must also establish that WAL or
journal state, receipts, checkpoints, manifests, sidecars, staging files,
renames, and external filesystem effects jointly represent a permitted domain
state.

Concrete next implementation:

1. custom fault VFS with enumerated write/sync/truncate/lock cut points;
2. separate child process with abrupt termination;
3. random reorder/corruption only for writes not proven durable;
4. restart from the exact surviving artifact set; and
5. differential comparison with an executable domain model.

## SQLite hostile-input guidance

SQLite's “Defense Against The Dark Arts” recommends defensive mode, reducing
run-time limits, using an authorizer, progress interruption, and memory limits
when processing untrusted SQL or database content.

Source:

- https://sqlite.org/security.html
- https://sqlite.org/c3ref/c_dbconfig_defensive.html
- https://sqlite.org/c3ref/progress_handler.html
- https://sqlite.org/c3ref/hard_heap_limit64.html

AnonSync already has several related controls: authorizer/connection profiles,
geometry bounds, verification budgets, progress limits, exact projection
boundaries, and defensive schema checks. Those controls reduce the accepted
input and execution surface but do not create complete process containment.

Implication: move hostile database interpretation to a disposable worker.
Production foreign-key enforcement should remain enabled; a test that needs to
manufacture inconsistent artifacts should do so through an explicit test-only
offline connection, as rev0805 now does.

## Conflict-free replicated data types

The CRDT literature defines replicated data types whose replicas can update
without coordination and deterministically reach the same state after receiving
the same update set. Delta-state CRDT research shows how small incremental
states can be disseminated over unreliable channels and joined through
anti-entropy, including causal variants.

Primary sources:

- https://arxiv.org/abs/1805.06358
- https://arxiv.org/abs/1603.01529

Implication: AnonSync should not infer convergence from tombstones, conflict
copies, lineage IDs, idempotency keys, or receipts. It needs an explicit
operation algebra and generated trace model.

Recommended operation classification:

```text
commutative / order-sensitive
idempotent / single-use
monotone / retracting
causally dependent / independent
coordination-free / coordination-required
epoch-compatible / epoch-barriered
```

Speculation: after that model exists, a delta-state anti-entropy or
content-addressed evidence DAG could reduce transfer and support partial sync.
A digest must remain evidence about bytes, not authority for an operation.

## Messaging Layer Security and key lifecycle

RFC 9420 specifies asynchronous group keying with forward secrecy and
post-compromise security. RFC 9750 explains that MLS is one component of a
larger system: authentication and delivery services, application policy,
metadata exposure, key-package use, and other infrastructure choices affect the
actual security properties.

Sources:

- https://www.rfc-editor.org/rfc/rfc9420.html
- https://www.rfc-editor.org/rfc/rfc9750.html

Implication: MLS is relevant research for device groups, epochs, member
add/update/remove transitions, key deletion, forward secrecy, and
post-compromise recovery. It is not a drop-in proof that AnonSync is anonymous,
metadata-private, or even end-to-end encrypted.

The design must first state:

- adversaries and trust roots;
- visible payload, path/name, size, timing, equality, topology, and membership
  metadata;
- device enrollment and credential transparency;
- epoch advancement and offline devices;
- revocation and stolen-device recovery;
- forward secrecy and post-compromise goals;
- backup/recovery key policy; and
- in-memory secret lifetime and erasure.

## Linux containment primitives

The Linux kernel documentation describes Landlock as an unprivileged mechanism
for restricting ambient filesystem and network rights, layered on top of
system-wide controls. Seccomp filters reduce the kernel syscall surface, but the
kernel documentation explicitly says seccomp is not a complete sandbox.
`setrlimit()`/`prlimit()` provide kernel-enforced soft/hard resource ceilings,
including address-space and CPU limits.

Sources:

- https://www.kernel.org/doc/html/latest/userspace-api/landlock.html
- https://www.kernel.org/doc/html/latest/userspace-api/seccomp_filter.html
- https://man7.org/linux/man-pages/man2/getrlimit.2.html

Implication: the hostile-database worker should layer controls rather than rely
on one mechanism:

- no inherited capabilities;
- minimal file descriptors and environment;
- `PR_SET_NO_NEW_PRIVS`;
- narrow seccomp allowlist;
- Landlock restrictions when supported;
- `RLIMIT_CPU`, `RLIMIT_AS`, `RLIMIT_FSIZE`, `RLIMIT_NOFILE`, and no core dumps;
- parent-enforced wall-clock timeout; and
- disposal after one request.

Unsupported Landlock or seccomp features must be reported as an explicit
capability result. A partial sandbox must not silently be presented as complete.

## Overall research conclusion

AnonSync's local authority model is directionally strong. The research points
to four missing proof systems rather than another collection of checks:

1. an executable convergence algebra;
2. a crash-cut/domain-state oracle;
3. a disposable hostile-input worker; and
4. a threat/leakage/key-lifecycle model.

These should drive the next C++ boundaries. Additional source-text audits are
valuable only as drift guards behind those executable or model-based proofs.

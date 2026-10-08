# AnonSync rev0890 audit

## Mission heart

AnonSync remains an authority-accounting system before it is a transport or
file-copy utility. Exact authorized evidence owns identity, causality, durable
receiver admission, visible effect, retry, receipt, and settlement. Derived
summaries, readiness, local TLS completion, cached counters, and policy labels
may accelerate or diagnose that history but may not mint authority.

Rev0890 tightens the identity-to-application transition. A certificate that
passes the configured TLS trust policy is not automatically an authorized
AnonSync actor. The accepted-session path now receives a validated immutable
membership snapshot by value and performs one exact SPKI lookup after the TLS
handshake and before any durable receiver mutation.

## Defect removed

Rev0889's actual packaged source still accepted a
`std::function<std::optional<SyncReplicaActor>(std::string_view)>` membership
resolver. It ran after peer authentication while the server owned a live
accepted descriptor and `SSL` object. Even a post-callback descriptor reproof
would only detect some mutations after arbitrary code had already executed; it
could not undo reentrant service changes, lock inversion, unbounded blocking,
allocator pressure, racing policy maps, or unrelated side effects.

Rev0890 removes that application callback from the live-session API. It does not
claim that OpenSSL itself invokes no callbacks during the caller-configured TLS
handshake.

## Immutable membership authority

`SyncReplicaTlsMembershipSnapshot` is a small value type backed by shared
`const` state. Construction validates:

- nonempty receiver folder identity;
- a valid receiver-local actor;
- positive policy epoch;
- a hard ceiling of 65,536 entries;
- canonical lowercase SHA-256 SPKI digests;
- valid remote actors that do not reuse the receiver's own device identity; and
- uniqueness of every SPKI pin.

Entries are sorted by SPKI. Multiple pins may map to one actor for key-rotation
overlap, but one pin cannot map ambiguously to multiple actors. Lookup is exact
and allocation-free after construction.

The domain-separated digest binds folder ID, local actor device and epoch,
policy epoch, entry count, and every sorted SPKI-to-actor tuple using explicit
length and integer encodings. The digest is evidence for snapshot content, not a
signature or rollback guard.

## Server composition

Before accept, the server rechecks that the snapshot belongs to the exact
receiver service and records its epoch, entry count, and digest in the result.
After TLS authentication it hashes the verified peer SPKI and performs the exact
snapshot lookup. Missing membership terminates as `PeerUnauthorized` without a
durable receiver mutation. A successful lookup is followed by live accepted-
socket policy reproof before constructing the authenticated channel and
one-shot receiver session.

Every terminal server result attributes the membership snapshot that governed
the decision. The existing complete path still exercises authenticated request
framing, durable idempotent file effect, receipt transmission, and exact sender
settlement.

## Audit/refactor work

Three source audits define the reviewed surface:

1. `audit_sync_file_tls_server.py` was refactored to follow the actual ordering
   from snapshot service preflight through SPKI lookup, unauthorized outcome,
   socket reproof, channel construction, and receiver session.
2. `audit_sync_tls_membership_snapshot.py` records the canonical immutable-value
   shape and runtime test matrix.
3. `audit_authority_callback_boundaries.py` inventories every retained
   `std::function` occurrence instead of banning callbacks lexically. It
   distinguishes selftest assertion sinks, a production-empty SQLite test hook,
   and the payload supplier from the retired live TLS membership callback.

These are drift and hygiene checks, not semantic proof. Compiled real-TLS tests,
independent compilers, sanitizers, complete CTest closure, and package
verification are load-bearing.

## Validation

- Parent rev0889: 26/26 ZIP checks and exact 5,785-file Git-import match.
- GCC 14 Debug: complete all-target continuation and final `ninja: no work to
  do` closure.
- Registered tests: 208/208 in one invocation.
- Audit and policy selection: 80/80 serially in one invocation.
- Focused real-TLS transport: 1,921/1,921 independently under GCC Debug, Clang
  17 Release C++ `-Werror`, and GCC ASan/UBSan with leak detection and bundled
  SQLite instrumentation; 5,763/5,763 combined.
- Debug process stress: 15/15 fresh processes, 28,815/28,815 assertions.
- Sanitizer stress: 5/5 processes, 9,605/9,605 assertions.
- Selected source audits: 66/66 checks; package-path policy 14/14 and verifier
  policy 13/13.

Two foreground cloudtainer wrapper loops stopped returning after ten completed
child processes. A detached per-process diagnostic launcher completed 15/15 at
the normal cadence, including the eleventh process. This is retained as an
execution-environment observation; neither a product hang nor extra product
stress coverage is inferred from the wrapper behavior.

## Severe or wasteful areas still present

1. **No durable membership owner.** The snapshot is validated and immutable but
   caller-constructed. There is no authenticated update provenance, monotonic
   generation, prior-digest chain, revocation, recovery, or rollback protection.
2. **Payload callback debt.** Payload acquisition remains arbitrary local code
   while a durable outbox lease exists. Its authority ordering is fenced, but
   execution time and temporary resource use are not bounded.
3. **Product integration gap.** The shipped `anonsync_core` executable still
   does not make the causal SQLite/file/TLS path its sole durable authority.
4. **Receiver pressure.** There is no bounded production accept pool,
   per-principal handshake admission, protected reserve, fair staging, expiry,
   dead-letter lifecycle, causal-stability compaction, or garbage collection.
5. **Oracle scale.** Full-history SQLite owners remain valuable correctness and
   repair oracles but are O(history) production paths without separate indexed
   owners and differential validation.
6. **Build shape.** The current CMake file still contains 82 literal libraries,
   91 executables, and 125 literal `add_test` calls. `sync_domain.cpp` is 15,167
   lines and `sync_domain_selftests.cpp` is 9,601 lines. Link-target granularity
   still exceeds semantic decomposition and imposes expensive rebuilds.
7. **Privacy overclaim.** Mutual TLS and exact membership authorization do not
   provide anonymity, unlinkability, endpoint hiding, or traffic-analysis
   resistance.

## Recommended next implementation

Introduce a durable membership configuration owner that validates complete
updates before commit, persists a monotonic generation and prior-snapshot digest,
reconstructs and re-attests the full set on restart, and publishes immutable
snapshots only after durable success. Preserve this pure snapshot as the value
passed into live accepted sessions.

In parallel, replace `SyncReplicaFilePayloadSource` with a bounded
content-addressed reader capability whose identity, byte ceiling, lifetime, and
failure classification are explicit. Then compose a small production listener
with bounded accept/handshake/session concurrency and overload evidence, while
retaining the current full-history owners as differential oracles.

## Nonclaims

Rev0890 does not claim durable enrollment, signed membership updates,
revocation, key recovery, policy freshness, rollback protection, hostile
same-process isolation, a production daemon, internet deployment safety,
exactly-once network execution, atomicity across independent databases,
complete retry/dead-letter policy, fair scheduling, compaction/rejoin,
ThreadSanitizer coverage, formal proof, anonymity, unlinkability, endpoint
hiding, traffic-analysis resistance, or externally trusted signed provenance.

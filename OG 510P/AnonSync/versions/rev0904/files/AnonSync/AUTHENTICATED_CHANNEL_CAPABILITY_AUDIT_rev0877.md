# AnonSync rev0877 — authenticated channel capability, TLS lifetime, stream cutpoint, and cube audit

## Executive finding

The heart of AnonSync remains unusually clear:

> Exact authorized evidence must own identity, causality, projection, dispatch,
> retry, receipt, and visible effect. Every summary, cache, lease, clock,
> transport session, capability, and test report is subordinate evidence and may
> not manufacture authority.

Rev0876 made a major composition step by adding a canonical operation-delivery
protocol, a delivery service around the causal SQLite owner, and real mutual TLS
1.3. Deep review found that the new chain still broke its own mission at the
service boundary. The service accepted a public context value containing the
peer actor and TLS exporter digest. Any ordinary caller could construct that
value. The type named evidence from authentication but did not prove that
authentication occurred, remained live, or still referred to the same TLS
session.

That was not merely a type-style concern. A fabricated or stale context could
reach durable outbox claim, receiver admission, or receipt settlement. The TLS
record helpers had a stronger opaque capability, but the service did not require
it. Transport authority and durable authority were therefore split.

Rev0877 corrects that split with one privately minted, move-only, process/thread
bound delivery authority shared with the TLS adapter's live authenticated state.
Before every service call, the authority validates move state, process
incarnation, exact thread lifetime, and—when TLS-backed—the current TLS profile,
peer SPKI, and exporter binding. A stale channel after `SSL_clear()` or a fresh
handshake now fails before SQLite access.

The audit also found three adjacent forms of waste or unsafe ambiguity:

1. The TLS channel borrowed a raw `SSL*`; releasing the caller's last reference
   could leave the apparent capability dangling.
2. An invalid record prefix or uncertain write could consume part of the stream
   while leaving the channel reusable, allowing later bytes to be parsed at the
   wrong framing boundary.
3. The outbox owner could durably claim an operation that the active delivery
   model could not encode, creating an endless claim/fail/expiry cycle.

Rev0877 retains an OpenSSL reference, permanently poisons a stream after an
uncertain record cutpoint, and validates the first ready canonical operation
before lease mutation. Compiled negative tests prove that all three corrections
fail before the authority they protect.

The largest product gap is unchanged: no production executable calls the new
service. The path is evidence-terminal, not effect-terminal. It has no payload
transfer, visible filesystem publication, durable membership owner, reconnect
manager, complete retry/dead-letter policy, or anonymity property. The next
revision should resist further horizontal assurance work unless it composes one
real process path through bounded payload and atomic receiver effect.

## Heart of the mission

AnonSync should be understood as a system for **authority accounting under
partial failure**, not as a high-level synchronization loop. A useful design
question for every state transition is:

> What exact evidence owns this transition, where is that evidence durably
> retained, and what prevents a derived representation or failed side effect
> from silently becoming the new source of truth?

The mission decomposes into nine linked authorities.

### 1. Observation authority

Physical time, process identity, thread identity, namespace identity, filesystem
metadata, network peer identity, and trust state are observations with provenance
and uncertainty. Their source and capability must be recorded before they affect
liveness or identity. A platform version string, pointer value, caller assertion,
or cached summary is not equivalent to observing the required capability.

### 2. Canonical identity

Every operation must have one canonical byte representation. Identity is derived
from those bytes, not from a mutable object graph, transport frame, database row
number, local filename, or retry attempt. Equivalent evidence must produce the
same operation ID across replicas and restarts.

### 3. Exact causality

Immediate predecessor evidence is authority. Vector summaries, clocks, counters,
and indexes may accelerate discovery but cannot substitute for the exact parent
set when validating or projecting history.

### 4. Actor and membership authority

A device identifier alone is not an authenticated actor. The system needs actor
key epochs and a durable rule for enrollment, rotation, revocation, compromise,
recovery, rollback, and old-epoch evidence. A transport certificate accepted by a
generic trust store must not silently authorize folder membership.

### 5. Durable publication authority

A transition is not authoritative because a function returned success. Operation
bytes, predecessor edges, projection, payload commitment, outbox intent, lease,
clock evidence, receiver admission, effect intent, visible publication, and
receipt must each have a named durable cutpoint. Where several facts constitute
one decision, they must share one transaction or a recoverable protocol.

### 6. Deterministic projection authority

Evidence retention and visible state are distinct. Trust or dependency changes
may require re-evaluating retained evidence. Deleting evidence merely because it
is not currently active destroys the ability to derive the same future state.

### 7. Bounded dissemination authority

Every untrusted dimension needs an explicit bound: bytes, operations, identities,
predecessors, paths, payloads, CPU, storage, retries, deadlines, wakeups, and
concurrent work. A bound that is checked only after durable dispatch can itself
create permanent liveness debt.

### 8. Receiver effect authority

Durably retaining operation evidence is not the same as durably realizing its
payload and filesystem effect. The eventual terminal receipt must bind the exact
operation, exact payload commitment, exact effect identity, exact visible
publication cutpoint, and exact authenticated receiver authority.

### 9. Privacy authority

Encryption does not imply anonymity. Endpoint addresses, timing, direction,
volume, certificate presentation, peer discovery, folder identifiers, path
shape, and access patterns can remain observable. AnonSync must specify an
adversary and leakage budget before the name “Anon” becomes a product claim.

## Parent path and authority graph

Rev0876's focused path was:

`outbox claim → canonical request → pinned mutual TLS 1.3 → receiver atomic`
`admission/cutpoint → canonical receipt → sender settlement`

The components were individually strong:

- the request and receipt were canonical, bounded, and structurally digested;
- the receiver returned the cutpoint from the same transaction that admitted the
  operation;
- TLS required exact ALPN, successful verification, actor/SPKI pinning, a fresh
  non-resumed TLS 1.3 session, and RFC 9266 exporter binding; and
- record I/O required an opaque `SyncReplicaTlsAuthenticatedChannel`.

The authority graph nevertheless forked at the application boundary:

- record I/O required the opaque TLS capability;
- delivery-service methods accepted only `SyncReplicaDeliveryChannelContext`;
- the context was a public aggregate with actor and binding fields; and
- the service trusted those fields as though they proved live authentication.

The distinction matters because the service owns durable effects. It can mint a
claim, admit remote evidence, and settle an intent. The weaker input was accepted
at the stronger boundary.

## Severe defects found and corrected

### A. Public descriptive context was accepted as durable service authority

**Severity:** high within the trusted application process.

`SyncReplicaDeliveryChannelContext` is intentionally serializable-looking data:

- peer actor device ID;
- peer actor epoch; and
- channel binding type/digest.

Those values are necessary to bind canonical requests and receipts. They are not
proof that a handshake happened. Before rev0877 a caller could construct a
syntactically valid context from arbitrary bytes and invoke the service.

The service still checked that the expected peer matched the local actor and
that request/receipt bytes matched the context. That prevented many accidental
cross-peer errors, but it did not answer the foundational question: who minted
the context, and is the underlying authenticated channel still the one it names?

**Correction:** every public delivery-service operation now accepts
`const SyncReplicaDeliveryChannelAuthority&`. Its constructor is private. The
TLS channel and a separately linked test factory are the only friends that mint
it. The service validates the authority before extracting the public context or
opening the owner path.

**Boundary honesty:** this is not protection against malicious code with
arbitrary read/write access inside the process. C++ access control, move-only
types, and link separation prevent ordinary accidental construction and make
reviewed authority flow explicit. They do not withstand memory corruption,
undefined behavior, binary patching, debugger control, or a hostile plugin.

### B. Service authority did not track TLS session liveness

**Severity:** high for stale-session confusion.

Rev0876 record I/O revalidated the TLS session. The service did not. A caller
could authenticate, obtain context bytes, call `SSL_clear()` or perform a fresh
handshake on the same `SSL` object, then use the old context directly with the
service. The old actor/exporter values could authorize a new durable claim even
though the live session had changed.

**Correction:** TLS constructs one shared
`SyncReplicaTlsAuthenticatedState`. That state implements the internal delivery
verifier. The authority keeps a shared pointer to the verifier, while the TLS
channel uses the same object for record I/O. Every service entry rechecks:

- TLS 1.3 profile;
- verification mode and successful result;
- exact ALPN;
- non-resumed/no-early-data conditions;
- current peer certificate SPKI against the authenticated pin; and
- current RFC 9266 exporter against the stored binding.

A failed check marks the state poisoned and throws. The service test records the
complete sender snapshot before attempting a stale claim and proves exact
snapshot equality afterward. A fresh channel authenticated on the new handshake
then receives attempt 1 for the preserved intent.

### C. The channel borrowed a raw OpenSSL lifetime

**Severity:** high memory-safety risk if API ownership was misunderstood.

The old channel stored a raw `SSL*` but did not increment the OpenSSL reference
count. The type looked like an owned capability while its lifetime was actually
subordinate to an external smart pointer. Releasing the caller's last reference
could make later capability use dereference freed state.

**Correction:** the authenticated state calls `SSL_up_ref()` after validating its
constructor inputs and calls `SSL_free()` when its last shared owner is released.
A real TLS integration test authenticates both directions, resets both original
caller smart pointers, sends a record, and receives the exact bytes through the
retained channels.

Destruction is also process/thread-affine. Releasing the last reference in a fork
child or foreign thread fail-stops rather than invoking `SSL_free()` under a
lifetime authority that was never acquired there.

**Remaining caveat:** OpenSSL reference counting protects lifetime, not concurrent
mutation. Another alias can still clear, re-handshake, or race the same object.
The API explicitly forbids concurrent mutation. Sequential mutation is detected
at the next validation point.

### D. Uncertain record cutpoints left a stream reusable

**Severity:** high for framing confusion and cross-message reinterpretation.

The record format is an eight-byte big-endian length followed by one canonical
frame, all inside TLS. Several failures imply that the exact application stream
position is no longer known:

- the prefix may have been partially processed before a failed write;
- the body may have been partially processed;
- the reader may have consumed a complete length whose body exceeds local
  policy; or
- the peer may have sent an invalid zero length.

Continuing on the same stream would allow residual body bytes to be interpreted
as the next record length. The TLS layer remains cryptographically valid; the
application framing does not.

**Correction:** every I/O exception after live validation poisons the shared
state. Every invalid peer prefix also poisons it. Future record or service use
fails with an explicit poisoned-channel error. The peer-overlimit runtime test
first observes bounded rejection and then proves that a second read cannot reuse
the consumed stream.

Local preflight errors—zero local frame, local frame above configured maximum, or
invalid maximum—occur before touching the channel and do not poison it because
no stream byte could have moved.

### E. A locally unsendable operation could acquire a durable lease

**Severity:** medium-to-high liveness and operational waste.

Global delivery-limit validation proved that a model-consistent worst-case
operation could fit the configured request envelope. It did not guarantee that
every operation already retained under a broader local model fit the currently
selected delivery model. The service claimed first and encoded second. A
particular oversized operation could therefore:

1. acquire attempt N and a lease;
2. fail request construction;
3. remain unavailable until expiry;
4. acquire attempt N+1; and
5. repeat indefinitely.

This is a classic example of a downstream bound becoming durable work debt.

**Correction:** the owner now exposes
`claim_next_outbox_for_delivery_or_throw()`. Both public claim APIs delegate to
one private core. After writer serialization, full restore, owned clock
observation, first-ready intent selection, and exact operation lookup, the core
validates the operation against the supplied delivery model. Only then can the
lease state machine mint a claim and publish it.

The runtime test uses a history where the second operation is pending for the
selected destination, applies a restrictive model, and proves:

- the exact full snapshot is unchanged;
- no claim ID exists;
- no worker is recorded;
- attempt count remains zero; and
- a compatible service subsequently obtains attempt one.

A clock anomaly remains independently authoritative and may publish durable
clock quarantine before delivery eligibility. The no-mutation claim applies to a
normal accepted clock observation, not to suppression of unrelated safety
publication.

### F. The first fork probe bypassed the cube's process-boundary owner

**Severity:** maintainability and test-authority regression.

The initial TLS negative test used raw `fork()` and `waitpid()`. The complete
registry failed four audits. Three were brittle lexical assumptions about the
old claim function shape. The fourth was correct: all inherited-process tests
are required to use one shared harness so exit semantics, timeout, cleanup, and
raw-fork inventory remain centrally owned.

**Correction:** the TLS test now uses
`spawn_inherited_test_process_or_throw()` and asserts the exact process-capability
violation exit code. The repository again contains one raw fork call in one
owned harness. Exact inventory audits account for the new consumer.

The three claim audits were refactored rather than weakened. They now verify that
both public wrappers delegate to `claim_next_outbox_impl_or_throw()` and inspect
the ordering inside that core. This is a useful example of audits adapting to
semantic refactoring without pretending that lexical checks prove behavior.

## New authority design

### Public context

`SyncReplicaDeliveryChannelContext` remains a plain public value. Its purpose is
descriptive:

- canonical request construction;
- receipt verification;
- logging and diagnostics; and
- equality checks in tests.

Its header explicitly states that the value alone is not authority to invoke the
service.

### Delivery authority

`SyncReplicaDeliveryChannelAuthority` has no default constructor and no copy
operations. Move construction and move assignment invalidate the source. Its
private state contains:

- context;
- process incarnation;
- thread incarnation;
- optional shared live verifier; and
- a valid/moved-from bit.

`require_current_or_throw()` checks in this order:

1. valid/move state;
2. process incarnation, with fail-stop on mismatch;
3. exact thread incarnation, with exception on mismatch; and
4. lower-layer verifier, when present.

Ordering is intentional. A fork child must not enter a transport verifier or
SQLite. A foreign thread must not touch OpenSSL's connection state. A moved-from
object must fail before any authority comparison.

### TLS authenticated state

The shared TLS state owns:

- retained `SSL*` reference;
- exact authenticated peer SPKI;
- exact exporter binding;
- process incarnation;
- thread incarnation; and
- sticky poison bit.

Validation is continuous rather than one-time. The stored SPKI and binding are
not treated as proof by themselves; they are comparison anchors for a new live
observation of the current `SSL` state.

The state is referenced by both:

- `SyncReplicaTlsAuthenticatedChannel::state_`, for record I/O; and
- `SyncReplicaDeliveryChannelAuthority::verifier_`, for service entry.

This prevents the service and transport from drifting into separate liveness
models.

### Test authority

Unit tests need deterministic actor/binding authority without constructing a
full TLS connection for every service case. The test factory is placed under
`tests/`, is a private-constructor friend, and is linked only into the service
unit-test target. No production library links the test mint.

This is the correct compromise for testability, provided its nonsecurity nature
is explicit. A future plugin-capable or hostile-extension process would require a
real isolation boundary—separate process, IPC capability, code signing, sandbox,
or hardware-backed key use—not stronger C++ privacy keywords.

## Transaction and ordering analysis

The new claim core preserves the previous critical ordering:

1. validate pure caller arguments;
2. acquire CSPRNG entropy before waiting for SQLite's single writer slot;
3. begin `IMMEDIATE` transaction;
4. require write authority;
5. restore complete exact/redundant state;
6. observe the owned clock;
7. accept the observation or durably publish clock quarantine;
8. select the first claimable ordered intent;
9. resolve its exact canonical operation;
10. optionally validate the operation against delivery limits;
11. transition the pure lease state with exact cutpoint/entropy/time evidence;
12. publish and attest the staged cutpoint; and
13. commit.

The delivery preflight is intentionally inside the transaction. Validating a
caller-provided operation before restore would not prove that it is the exact
operation currently owned by the first ready intent. Validating after lease
publication would recreate the churn defect.

The cost is that an incompatible operation holds the writer slot while canonical
validation executes. The operation and bounds are already bounded, and the
O(history) restore dominates. In the future indexed owner, the same semantic
ordering should be retained while the restore and lookup become indexed.

## Stream I/O analysis

### Why WANT is treated as channel loss here

OpenSSL documents that a failed `SSL_write()`/`SSL_write_ex()` returning WANT may
have partially processed data and must be retried with the same arguments. The
current API accepts a one-shot frame and does not expose a resumable operation
object, readiness handle, or exact retry buffer lifetime. Treating WANT as a
normal exception while leaving the channel reusable would lose the required
OpenSSL retry state.

Rev0877 therefore treats WANT as an uncertain I/O frontier and poisons the
channel. That is conservative and correct for the current blocking adapter. It
is not an event-loop implementation.

A future async transport should introduce an owned state machine roughly like:

`Idle → WritingPrefix(offset) → WritingBody(offset) → Complete`

and

`Idle → ReadingPrefix(offset) → ValidatingLength → ReadingBody(offset) → Complete`

The state machine must retain the exact buffer and arguments required by
OpenSSL, expose readiness, bind cancellation to connection disposal, and never
permit a second logical record while one is incomplete.

### Why an over-limit peer frame poisons rather than drains

Draining the advertised body would allow stream reuse but grants an attacker the
ability to force work proportional to a length already rejected by policy. It
also requires a bounded discard strategy, timeout semantics, and confidence
that the peer is not using the stream maliciously. Closing and reconnecting is
simpler, bounded, and fail-closed.

A future multiplexed protocol could isolate logical streams, but this adapter is
one ordered TLS byte stream. One invalid application frame retires it.

## Runtime proof

### Complete registry

The final GCC Debug registry passes 180/180 tests in one invocation. The audit
subset passes 55/55. The new delivery-channel source audit is registered in the
normal CTest graph.

### Focused runtime

All three focused toolchain lanes execute the same 2,896 checks:

- delivery protocol: 2,644;
- SQLite owner: 189;
- delivery service: 38;
- TLS transport: 25.

The lanes are:

- GCC 14.2 Debug;
- Clang 17 Release with C++ warnings fatal; and
- GCC 14.2 ASan/UBSan Debug with leak detection, halt-on-error, and bundled
  SQLite C instrumentation.

### Repeated stress

The repeated Debug campaign passes:

- owner: 20/20 iterations, 3,780 checks;
- delivery service: 20/20 iterations, 760 checks;
- TLS transport: 50/50 iterations, 1,250 checks; and
- total: 5,790/5,790 repeated checks.

### Negative authority matrix

The runtime proof includes:

- authority cannot be default constructed or copied;
- moved-from service authority fails before owner access;
- foreign-thread service authority fails before owner access;
- wrong peer authority cannot mutate a destination's owner;
- incompatible wire policy rolls the complete sender snapshot back;
- caller-owned `SSL` references may be released safely;
- foreign-thread record use fails before OpenSSL;
- fork-inherited use exits through the process-capability fail-stop code;
- post-authentication verification weakening is detected;
- stale authority after `SSL_clear()` and fresh handshake cannot mutate SQLite;
- failed live validation poisons the old channel;
- a refreshed channel can claim the preserved intent; and
- an over-limit peer frame permanently retires the reader.

### What these tests do not prove

The tests do not prove arbitrary concurrent alias safety, malicious memory
corruption resistance, all OpenSSL provider/configuration combinations, network
partition behavior, production socket timeout policy, Windows process semantics,
formal noninterference, or crash recovery around payload/effect publication that
does not yet exist.

## Cube audit and waste findings

### Assurance remains ahead of executable delivery

The new channel, service, causal owner, and TLS adapter are production-source
libraries. A production-source search still finds no caller outside their own
implementation headers. `anonsync_core` remains on the older stack.

This is now the most important prioritization signal. Another revision can make
the isolated path safer, but the marginal mission value will fall unless one
actual executable adopts it. The cube risks optimizing proof density rather than
shipping the authority chain.

### Build modularity is only partly semantic

The current CMake file contains approximately:

- 71 `add_library` calls;
- 92 `add_executable` calls; and
- 183 literal `add_test` calls.

At the same time, large semantic centers remain:

- `src/sync_domain.cpp`: about 15,167 lines;
- `src/sync_replica_sqlite_owner.cpp`: about 3,581 lines; and
- `tests/sync_replica_sqlite_owner_test.cpp`: about 3,640 lines.

Targets are useful for dependency and validation isolation, but target count is
not state-machine decomposition. The better refactor axis is authority ownership:
canonical codec, exact history owner, dispatch owner, session owner, receiver
effect owner, membership owner, and projection owner.

### Historical evidence is still expensive

Before rev0877 evidence, `REVISION_EVIDENCE/` contains approximately 4,526 files
and 40.6 MB of file payload, occupying about 52 MB in the extracted filesystem.
ZIP compression reduces transfer size but not review, hashing, inode, extraction,
lineage, or handoff cost.

The current revision should remain compact. Longer term:

- retain the current projection, parent hash, patch, validation summary, and
  selected proof logs in the source handoff;
- move historical logs to a content-addressed store;
- sign provenance externally; and
- permit deterministic retrieval by digest rather than copying every historical
  proof into every descendant archive.

### Lexical audits are hygiene

The four initial audit failures illustrate both sides of lexical auditing:

- the raw-fork audit caught a real ownership violation; and
- three audits failed because they assumed one old function shape.

The correction is not to delete audits. It is to keep their claims narrow and
couple them to executable tests. Source audits are effective for exact file
inventory, forbidden APIs, target isolation, obvious ordering, and retired
vocabulary. They cannot prove runtime TLS state, SQLite rollback, process exit,
or cryptographic binding.

The new delivery audit writes this nonclaim into its JSON output.

## What remains severely missing

### 1. No production executable path

There is no process that opens membership, establishes the new TLS channel,
claims work, transfers requests, handles reconnect, receives operations, applies
payload/effect work, and settles receipts. The new path is not user-visible.

### 2. No payload or receiver effect owner

Operations carry payload commitment metadata, not payload bytes. The path does
not spool content, verify chunks, bind an effect intent, publish an atomic file,
fsync the containing directory, or produce a receipt proving that visible
cutpoint.

### 3. Evidence-terminal receipts are not durable independent proofs

A receipt is authenticated by the exact TLS channel while received. It is not
independently signed by a receiver key and is not a durable response journal.
After sender process loss, the service intentionally retries rather than trusting
receipt fields detached from the expected request.

### 4. Membership authority does not exist

The caller supplies actor epoch and SPKI pin. There is no database that owns the
mapping, monotonic epoch, revocation generation, recovery, or rollback rules. A
channel minted before a future revocation is not checked against dynamic
membership state.

The outbox names only destination device ID. The product must decide whether an
intent survives receiver key rotation, requires explicit rebinding, or is
quarantined until policy resolves the new epoch.

### 5. Reconnect and retry policy are incomplete

Stream poison is local fail-stop, not recovery. There is no reconnect manager,
endpoint discovery, per-peer circuit breaker, typed transport failure,
backoff/jitter, maximum attempt age/count, dead-letter queue, remote retry-hint
clamping, operator replay authority, or wake scheduler.

### 6. Permanent wire rejection has no durable state

The first incompatible ready operation blocks later work. That is preferable to
silent skipping but not operationally complete. A dead-letter transition needs:

- exact operation and destination identity;
- policy generation and model digest;
- stable reason code and bounded diagnostics;
- whether the condition is permanent or policy-reclassifiable;
- operator-visible state;
- explicit retry/reclassification authority; and
- ordering semantics for later intents.

### 7. The correctness owner is O(history)

Every write restores and re-attests complete state. That is excellent as an
oracle and poor as a production throughput model. A separate indexed owner must
be built and differentially tested rather than mutating the oracle into an
unreviewable optimization.

### 8. No anti-entropy, compaction, or rejoin policy

There is no scalable inventory exchange, missing-parent protocol, causal
stability proof, tombstone retirement, checkpoint authority, revoked/offline
replica policy, or old-replica full-resync rule.

### 9. “Anon” remains aspirational

Mutual TLS authenticates and encrypts a connection. It does not hide endpoints,
timing, volume, direction, certificates, or application access patterns from all
observers. The project should either define a concrete privacy target and threat
model or continue describing itself as an evidence-authorized sync core rather
than claiming anonymity.

## Online primary-source research and implications

### OpenSSL object ownership

OpenSSL 3.5 documents `SSL` objects as reference counted. `SSL_up_ref()`
increments the count and `SSL_free()` decrements it, freeing resources at zero.
This supports rev0877's retained reference rather than a borrowed raw pointer.

Source:
`https://docs.openssl.org/3.5/man3/SSL_new/`

**Implication:** API types that outlive a call should make OpenSSL lifetime
ownership explicit. Retaining the reference does not grant concurrency safety;
it only prevents premature destruction.

### OpenSSL object reuse

The same OpenSSL documentation says recycling a noninitial `SSL` handle with
`SSL_clear()` may be possible but is best avoided; it recommends constructing a
fresh handle for each connection. The `SSL_clear()` page warns that several
settings from the prior session remain and recommends `SSL_free()`/`SSL_new()`
when reuse is not required.

Sources:

- `https://docs.openssl.org/3.5/man3/SSL_new/`
- `https://docs.openssl.org/3.5/man3/SSL_clear/`

**Implication:** rev0877 must detect stale authority because callers can still
hold aliases and reuse the object, but the eventual session manager should never
reuse connected `SSL` objects. One connection should own one fresh handle and one
capability lifetime.

### OpenSSL write retry semantics

OpenSSL documents that after WANT, a write must be repeated with the same
arguments because data may have been partially processed.

Source:
`https://docs.openssl.org/3.5/man3/SSL_write/`

**Implication:** a one-shot helper cannot safely expose WANT as ordinary
recoverable failure unless it retains an exact resumable operation. Poisoning is
the correct conservative behavior for the current adapter.

### OpenSSL error classification and thread affinity

`SSL_get_error()` inspects the current thread's OpenSSL error queue, must be
called in the same thread as the I/O operation, and should have no intervening
OpenSSL call. The queue must be cleared before the I/O attempt for reliable
classification.

Source:
`https://docs.openssl.org/3.5/man3/SSL_get_error/`

**Implication:** binding the current adapter to an exact thread lifetime is not
arbitrary. A future event-loop design can remain single-thread-owned or build a
carefully synchronized connection actor, but it should not casually migrate one
`SSL` object among workers.

### OpenSSL read behavior

OpenSSL documents that nonblocking read can return WANT_READ or WANT_WRITE and
must be repeated after satisfying the underlying BIO's requirement. A read may
need to write protocol data.

Source:
`https://docs.openssl.org/3.5/man3/SSL_read/`

**Implication:** “read readiness” is not equivalent to a simple socket read loop.
An async adapter needs explicit bidirectional readiness ownership.

### RFC 9266 channel binding

RFC 9266 defines `tls-exporter` for TLS 1.3 using label
`EXPORTER-Channel-Binding`, zero-length context, and 32 bytes. It describes the
binding as identifying a specific lower-layer TLS connection and warns that the
output is channel-binding data, not a secret key.

Source:
`https://www.rfc-editor.org/rfc/rfc9266`

**Implication:** the exporter is appropriate evidence for binding requests and
receipts to one exact TLS connection. It does not replace peer membership,
application protocol identity, or durable receipt signatures. Exact ALPN and
actor/SPKI policy remain necessary.

### TLS 1.3 and application boundaries

RFC 8446 defines the TLS 1.3 connection and exporter machinery but does not
provide AnonSync's application record semantics, retry policy, membership model,
or effect receipt.

Source:
`https://www.rfc-editor.org/rfc/rfc8446`

**Implication:** cryptographic transport correctness is a lower-layer premise,
not the completion of the sync protocol. The application must own framing,
canonical identity, replay, durable cutpoints, and effects.

## Speculation and recommended sequence

### 1. Build a connection/session actor, not more free functions

The next transport layer should own one fresh `SSL` object, one file descriptor,
one peer policy generation, one channel authority, one record state machine, one
poison/close state, deadlines, and reconnect classification. It should be
single-thread-owned and expose messages or futures rather than allowing external
aliases to mutate OpenSSL.

### 2. Introduce durable membership before reconnect sophistication

A session actor needs a source of truth for peer actor epoch and SPKI pin. Create
one membership owner with monotonic policy generation, enrollment evidence,
rotation/revocation transitions, rollback checks, and a query that mints a
short-lived connection policy snapshot. Channel service validation should later
include that policy generation or a revocation observer.

### 3. Compose one bounded payload operation

Support one operation type and one payload path first:

1. receive canonical operation evidence;
2. create durable bounded payload intent;
3. receive chunks into a temporary owned file;
4. verify exact size and content commitment;
5. fsync file;
6. create durable effect intent;
7. atomically rename into visible location;
8. fsync containing directory;
9. record terminal effect cutpoint; and
10. return an effect-terminal receipt.

Do not expand operation variety before crash recovery is complete for this path.

### 4. Make effect receipts independently verifiable

A terminal receipt should likely be a canonical signed object containing folder,
operation ID, payload commitment, effect identity, receiver actor/key epoch,
membership policy generation, effect cutpoint, and request/attempt binding.
Channel binding can remain anti-confusion evidence but should not be the only
authentication once the receipt is stored and replayed across sessions.

### 5. Add crash-frontier generation

Inject process death around every durable edge:

- sender claim publication;
- request record prefix/body;
- receiver admission;
- payload temporary creation/write/fsync;
- effect-intent publication;
- rename;
- directory fsync;
- receipt journal;
- response transmission; and
- sender settlement.

For each frontier, restart both owners and require convergence to either the
pretransition or one exact valid posttransition state.

### 6. Add typed failure and dead-letter ownership

Model transport and application failure classes explicitly:

- transient transport;
- authentication/membership stale;
- local policy incompatible;
- remote capacity blocked;
- permanent protocol invalid;
- effect conflict;
- operator intervention required.

Every class needs bounded retry, wake, and observability rules. Remote hints must
be clamped by local policy and cannot directly mint liveness authority.

### 7. Add an indexed owner beside the oracle

Keep the current O(history) owner unchanged as the reference semantics. Build a
separate indexed implementation. Generate operation/outbox/clock histories,
apply them to both, inject crashes, reopen, and compare exact evidence, active
projection, outbox, clock state, generation, and cutpoint digests.

### 8. Reduce handoff and build waste

Create declarative CMake helpers for repeated library/test/audit wiring. Define a
fast authority slice for affected components and a periodic complete registry.
Move historical bulk evidence to a digest-addressed external store while keeping
current proof compact and reproducible.

### 9. Define the privacy claim last but explicitly

Choose an adversary model: storage provider, relay, passive ISP observer, active
network attacker, peer, compromised endpoint, or some subset. List observable
metadata and acceptable leakage. Only then choose mechanisms such as relays,
traffic padding, rendezvous indirection, encrypted metadata, or group keying.

## Deliberate nonclaims

Rev0877 does not claim:

- use of the new delivery path by `anonsync_core`;
- security against hostile code already executing in the same process;
- safe concurrent mutation or migration of one OpenSSL `SSL` object;
- nonblocking/event-loop or production socket-timeout behavior;
- reconnect/session lifecycle completeness;
- payload transfer, content availability, or receiver filesystem effect;
- effect-terminal, independently signed, or exactly-once receipts/effects;
- complete membership, enrollment, rotation, revocation, recovery, or rollback;
- complete retry classification, backoff, jitter, dead-letter, or wake policy;
- absence of head-of-line blocking after permanent wire incompatibility;
- third-party gossip, anti-entropy, causal stability, compaction, or rejoin;
- production-scale performance from the O(history) owner;
- malicious-host, kernel, database, or build-system compromise resistance;
- anonymity, unlinkability, endpoint hiding, or traffic-analysis resistance;
- external signed provenance;
- full-project Clang, sanitizer, or ThreadSanitizer coverage;
- Windows runtime behavior; or
- formal proof.

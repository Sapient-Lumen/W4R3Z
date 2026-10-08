# AnonSync rev0876 — authenticated evidence delivery, atomic admission cutpoints, and composition audit

## Executive finding

AnonSync's heart remains **authority accounting under crash, partial trust,
duplication, reordering, resource pressure, and ambiguous responses**. The
project is not fundamentally a file copier. It is trying to ensure that every
identity, causal edge, projection decision, dispatch attempt, receiver
admission, visible effect, retry, and settlement can be traced to exact bounded
evidence and one explicit authority transition.

Rev0875 proved that two independent causal SQLite owners could survive an
ambiguous response, but the proof manually moved in-memory operations between
test fixtures. It did not define production framing, authenticate a peer, bind a
request to one channel, or protect the receiver-admission-to-receipt cutpoint
from a second transaction.

Rev0876 implements the first production-source authenticated **operation-evidence
delivery** chain:

`durable outbox claim → canonical bounded request → fresh mutual TLS 1.3 →`
`exact ALPN + verified chain + actor/SPKI pin + RFC 9266 exporter binding →`
`receiver atomic admission/cutpoint → canonical bounded receipt → exact sender`
`settlement`

The implementation is deliberately narrower than the product mission. A
successful receipt is **evidence-terminal** only: it says that the exact
immutable operation was durably retained or was already retained at the
receiver. It does not say that payload bytes were transferred, that a target
path was published, that a directory entry is durable, or that a user-visible
filesystem effect occurred. Calling this merely "terminal" would be a serious
semantic error, so the APIs and documentation use the longer name.

The most important result of this work is not TLS by itself. It is the removal of
several composition footguns discovered while connecting the newer causal owner
to a real encrypted stream:

1. receiver admission and receipt cutpoint were initially separated by a second
   SQLite snapshot and therefore subject to a post-commit race;
2. wire-envelope limits were initially borrowed from mutable receiver retention
   policy, conflating safe decoding with aggregate storage admission;
3. the first service draft restored complete O(history) owner state before most
   calls only to recover limits already known at construction;
4. OpenSSL's verification result can look successful even when peer verification
   was never enabled;
5. certificate validity and a key pin do not identify the intended application
   protocol without exact ALPN negotiation;
6. record helpers that accepted raw `SSL*` could bypass the actor/SPKI pin after
   generic certificate verification;
7. request/receipt frame ceilings could be internally valid yet too small to
   encode an operation or receipt that the same configuration authorized;
8. an unknown receipt enum could become terminal if helper code used a permissive
   default; and
9. "terminal receipt" language invited future callers to confuse evidence
   retention with payload or effect completion.

Each of those defects is corrected in rev0876 and covered by focused runtime
checks. The broader cube still has a central delivery gap: these are production
libraries, but the shipped `anonsync_core` executable still follows the older
sync-domain/peer-ingress/replay-ledger stack. There is also no receiver payload
or filesystem-effect owner in this new path. The next milestone should compose
existing bounded-file, payload-store, and atomic-publication components behind
this authenticated evidence boundary rather than add another isolated proof
island.

## Heart of the mission

The mission can be expressed as one authority chain.

### 1. Observation authority

Local filesystem observations, peer bytes, membership state, time, resource
pressure, and operator actions need typed provenance and explicit limits. An
unbounded or unattributed observation must not become canonical history.

### 2. Canonical identity

One exact versioned operation representation mints one immutable operation ID.
A parser may reject malformed or noncanonical bytes, but it may not silently
normalize attacker-selected alternatives into the identity of another
operation.

### 3. Exact causal authority

Immediate predecessor operation IDs own causality. Vector clocks, indexes,
Bloom filters, checkpoints, and summaries can locate missing work but cannot
stand in for the exact parent evidence whose existence they summarize.

### 4. Actor and membership authority

Every operation and delivery must bind to an actor/key epoch and a membership
rule. Rotation, revocation, compromise recovery, old-epoch evidence, and offline
members are part of correctness, not merely deployment configuration.

### 5. Durable publication authority

Operation bytes, causal edges, projection, sender intent, attempt identity,
receiver admission, payload state, effect state, and receipts must cross crash
cutpoints atomically or through an explicit recoverable state machine.

### 6. Deterministic projection authority

Retained evidence is not identical to active or visible state. Dependency
arrival, trust changes, conflict rules, and policy replacement must be able to
recompute projection without rewriting history.

### 7. Bounded dissemination authority

Bytes, identities, operations, dependencies, attempts, leases, wakeups,
storage, parsing, and repair work need independent ceilings. Pressure must yield
an explicit bounded outcome rather than hidden loss, partial mutation, or an
unfinishable protocol state.

### 8. Receiver effect authority

A true effect-terminal receipt must name the exact payload and exact receiver
publication outcome and must be stable across duplicate delivery and restart.
Operation admission alone is not that receipt.

### 9. Privacy authority

The name AnonSync does not itself establish anonymity. The project needs an
adversary model for discovery, addresses, certificates, device identifiers,
timing, sizes, relays, traffic shape, and compromise before it can claim
unlinkability or metadata hiding.

The compact invariant is:

> Given the same authorized canonical evidence and trust state, replicas derive
> the same state; no untrusted input, crash cutpoint, duplicate, missing
> dependency, resource claim, stale receipt, channel reuse, schema mutation,
> clock movement, retry response, migration shortcut, or local pressure decision
> may silently gain authority.

## What rev0876 implements

### Canonical delivery protocol

`sync_replica_delivery_protocol` defines a versioned, bounded request and receipt
format independent of sockets and cryptography.

One request contains:

- folder identity;
- sender actor/device and epoch;
- receiver actor/device and epoch;
- exact outbox claim ID;
- dispatch attempt number;
- typed channel-binding digest;
- and one complete canonical operation.

The request requires the operation's dot actor to equal the transport sender.
This deliberately supports origin delivery only. Third-party gossip,
store-and-forward, and anti-entropy forwarding need a different authority model
and are not smuggled into this envelope.

One receipt contains:

- the same folder and actor epochs;
- operation, claim, and attempt identities;
- the exact request digest;
- the same channel-binding digest;
- an admission disposition;
- the retained evidence state, when one exists;
- receiver state generation;
- and the receiver cutpoint digest captured by the deciding transaction.

The structural SHA-256 trailer detects malformed or accidentally changed bytes.
It is explicitly not an authentication key. Authentication comes from the lower
channel and its exported binding.

The parser is exact rather than permissive:

- version, magic, lengths, field limits, and enum values are checked;
- the body digest is recomputed;
- all body bytes must be consumed;
- the parsed object is canonically re-encoded;
- and the original frame must equal that canonical encoding.

The focused adversarial matrix truncates at every byte position, mutates every
byte position, and appends multiple trailing lengths for both request and
receipt. This does not constitute a general fuzzing proof, but it closes a large
class of parser boundary mistakes deterministically.

### Configuration coherence

A subtle liveness defect appeared during the framing audit. It was possible to
configure a request ceiling large enough to hold the fixed header but smaller
than a maximum operation allowed by the wire model. It was also possible to
configure a receipt ceiling too small for any complete maximum receipt.

That configuration can create a permanent authority trap:

1. the sender durably claims an operation the wire configuration can never
   encode; or
2. the receiver durably admits evidence and then can never encode the receipt
   needed to settle the sender.

Rev0876 computes the exact worst-case frame capacity implied by the model and
rejects incoherent limits in the constructor/validation boundary. A valid
configuration must be able to encode every operation it authorizes on the wire
and every canonical receipt. Allocation failure can still occur, but retry and
idempotency can recover from that; a deterministic impossible configuration
cannot.

### Transaction-bound receiver admission

The first service draft called `accept_remote_or_throw()` and then opened a
second owner snapshot to populate receipt generation and cutpoint. Another
writer could commit between those calls. The receipt would still describe a real
later cutpoint, but it would not identify the cutpoint that decided this exact
admission. Under concurrency, the protocol could no longer prove what it
claimed.

`SyncReplicaSqliteOwner::accept_remote_with_cutpoint_or_throw()` now returns a
compact result from the deciding write transaction:

- admission disposition;
- exact retained evidence state, if any;
- state generation;
- and cutpoint digest.

Inserted evidence returns the staged values that were independently restored and
attested before commit. Duplicate and capacity-blocked no-ops return the exact
unchanged cutpoint loaded in the transaction. `accept_remote_or_throw()` remains
source compatible and delegates to the new method.

This is a small API refactor with a large semantic effect: protocol receipt
creation no longer needs a race-prone second read.

### Delivery service

`sync_replica_delivery_service` is the first non-test orchestration layer around
`SyncReplicaSqliteOwner`.

The sender path:

1. validates an authenticated peer/channel context;
2. claims one exact destination intent through the owner;
3. binds the current peer actor epoch and channel binding;
4. encodes one canonical request; and
5. retains the exact request needed to validate a later receipt.

The receiver path:

1. bounds and decodes the complete frame before mutation;
2. verifies folder, sender actor epoch, receiver actor epoch, and channel binding;
3. admits the operation through the transaction-bound owner API;
4. creates a receipt from that exact result; and
5. canonically encodes it.

The sender receipt path:

1. decodes the bounded receipt;
2. proves it binds the exact request, claim, attempt, actors, operation, folder,
   and channel;
3. leaves capacity-blocked outcomes nonterminal; and
4. settles only a current exact evidence-terminal claim.

A process crash after sending but before applying the receipt intentionally loses
the in-memory expected request. The sender does not reconstruct authority from
untrusted receipt fields. It waits for lease expiry, creates a fresh attempt, and
relies on receiver idempotency. This is conservative and correct, although a
future durable request/response journal could reduce duplicate work.

### Wire policy separated from retention policy

The initial service reused the receiver's mutable model/retention limits as wire
decoder limits. That was conceptually wrong. A decoder must safely parse one
bounded operation before the owner can decide whether aggregate retention
capacity is available. Per-envelope validity and aggregate admission are
separate authority decisions.

`SyncReplicaDeliveryServiceLimits` therefore owns stable wire-operation and frame
limits. The SQLite owner retains its own mutable aggregate policy. A valid wire
operation can receive `CapacityBlocked` without being mislabeled malformed.
Policy-invalid operations still fail without admission; a typed permanent policy
rejection receipt remains future work.

This separation also removed waste. The first draft restored complete O(history)
owner state before each ordinary service operation merely to borrow limits.
Rev0876 caches immutable owner identity once and uses explicit wire policy,
leaving complete snapshots only on the uncommon capacity-receipt classification
path. The owner itself is still O(history), so this is not a throughput claim,
but it avoids adding redundant full restores on top of every owner call.

### Real TLS 1.3 adapter

`sync_replica_tls_transport` provides one narrow OpenSSL profile rather than a
bespoke handshake.

The configured profile requires:

- TLS 1.3 only;
- peer certificate verification enabled;
- a client certificate on the server side;
- exact ALPN `anonsync-replica-delivery-v1`;
- early data disabled;
- server session tickets disabled; and
- fresh, non-resumed sessions until membership-aware resumption exists.

After the handshake, the application supplies an exact peer policy containing:

- actor device ID and epoch; and
- lowercase SHA-256 of the peer certificate's DER SubjectPublicKeyInfo.

Authentication then requires:

1. a completed TLS 1.3 handshake;
2. no resumption and no early-data attempt;
3. `SSL_VERIFY_PEER` actually enabled;
4. successful chain verification;
5. exact delivery ALPN;
6. a peer certificate;
7. constant-time equality with the membership-supplied SPKI pin; and
8. successful export of the RFC 9266 `tls-exporter` channel binding.

The raw 32-byte exporter is domain-separated into the protocol's typed channel
binding. The two endpoints derive the same value, and requests/receipts cannot be
replayed onto another fresh TLS connection because the binding changes.

The membership layer remains responsible for associating actor epoch with SPKI,
installing trust roots, verification depth, revocation policy, and rotation.
The TLS adapter cannot infer membership from a certificate chain alone.

### Opaque authenticated-channel capability

Another audit defect appeared after the TLS profile existed. Public record
helpers originally accepted raw `SSL*`. A caller could complete a generally
verified TLS handshake, skip the actor/SPKI pin function, and still send or read
AnonSync delivery records. The correct check existed but was optional at the
call site.

Rev0876 replaces that API with move-only
`SyncReplicaTlsAuthenticatedChannel`. Only
`authenticate_sync_replica_tls13_channel_or_throw()` can construct it, and the
record helpers accept only that capability. The raw `SSL*` remains private and
non-owning.

Each record operation also rechecks live TLS version, freshness, early-data
status, peer-verification mode/result, and ALPN. This catches accidental
post-authentication weakening such as disabling `SSL_VERIFY_PEER` on the live
object. The SPKI pin itself is stable for a TLS connection and is not re-read on
every record.

The capability is not a cryptographic token that can survive process restart.
It is a type-level proof that one live `SSL` object crossed the required
application boundary.

### Bounded TLS stream records

One encrypted record is:

`8-byte unsigned big-endian length || one canonical delivery frame`

The prefix is inside TLS. The reader checks the advertised length before
allocation, rejects zero, and requires an explicit maximum. The helpers are for
blocking `SSL` objects with an application-owned descriptor timeout. They fail
on `WANT_READ`/`WANT_WRITE` rather than spin. A protocol error should cause the
caller to discard the connection because unread bytes may remain in the stream.

This is framing, not a complete server. There is no accept loop, connection
quota, idle deadline, cancellation model, worker pool, or denial-of-service
scheduler in rev0876.

## Audit corrections made during implementation

### Verification result without verification mode

OpenSSL documents `SSL_VERIFY_NONE` as the default. A successful-looking
`SSL_get_verify_result()` does not by itself prove that certificate verification
was requested. Rev0876 checks the mode and the result. A regression test performs
a valid handshake, disables verification mode afterward, and proves both SPKI
inspection and authenticated record I/O fail closed.

### Cross-protocol certificate reuse

A valid chain and correct key pin identify a peer key, not the intended
application protocol. Exact ALPN is negotiated inside the authenticated TLS
handshake and is now mandatory. A real mutual TLS connection with the same
certificates but no ALPN is rejected.

The current ALPN is project-private and not registered with IANA. It is suitable
for this internal prototype but must be registered or replaced with an assigned
identifier before broad interoperable deployment.

### TLS 0-RTT and resumption

TLS 1.3 explicitly gives 0-RTT weaker replay guarantees than ordinary handshake
data. AnonSync request identity and receiver idempotency reduce some replay harm,
but membership epochs, revocation, and application state can change between
sessions. Rev0876 disables early data and rejects any connection that attempted
it.

Session resumption is also rejected for now. Resumption is not inherently
unsafe, but AnonSync does not yet persist or validate the membership/key epoch,
revocation generation, ALPN policy, and application authority needed to decide
whether a resumed session remains valid. Fresh handshakes are the conservative
boundary.

### `SSL` object reuse after authentication

The first opaque capability was tied only to an `SSL*`. OpenSSL explicitly
supports resetting an `SSL` object for another connection. A caller could
therefore retain the old capability, complete a fresh handshake through the same
pointer, and reach record I/O with stale actor/channel metadata. Rechecking only
TLS version, verification result, and ALPN would not detect that transition.

The capability now retains the authenticated peer SPKI and exporter-derived
binding. Every record operation re-observes both from the live handshake and
requires exact equality. A runtime regression resets both `SSL` objects,
performs a second full handshake with the same certificates, and proves the old
capability is rejected because the exporter binding changed. Fresh
authentication mints a new capability and one new role-independent binding.

### Zero-generation backpressure receipts

The first receipt validator required nonzero receiver generation only for
evidence-terminal dispositions. `CapacityBlocked` nevertheless claims an exact
unchanged receiver cutpoint, and every valid owner cutpoint has a positive
generation. Permitting zero created a protocol state no real receiver could
produce. All receipt dispositions now require a nonzero generation, while
capacity remains nonterminal and carries no evidence state.

### Fail-closed unknown enum handling

`sync_replica_delivery_receipt_is_evidence_terminal()` enumerates every known
terminal value and returns false for both `CapacityBlocked` and unknown enum
values. Validation rejects unknown values. This avoids a common future-version
failure where an unrecognized disposition accidentally falls into a permissive
"not blocked" branch.

### Evidence-terminal nomenclature

The service result is `EvidenceSettled`, and the predicate includes
`evidence_terminal` in its name. This is intentionally verbose. The current
receipt is not permission to delete payload staging, report visible completion,
or claim exactly-once effects.

## Runtime proof surface

The focused suite includes four executables:

1. delivery protocol parser/canonicalization/adversarial matrix;
2. SQLite owner transaction-bound admission and existing owner invariants;
3. two-database delivery service with capacity, restart, duplicate, and stale
   receipt frontiers; and
4. real mutual TLS 1.3 over a Unix `socketpair` with ephemeral Ed25519 test PKI.

The TLS integration test proves:

- fresh TLS 1.3 on both endpoints;
- mutual chain verification;
- exact peer SPKI observation;
- rejection without ALPN;
- rejection when verification mode is disabled;
- rejection under a wrong actor/SPKI policy;
- symmetric RFC 9266 exporter binding;
- record I/O only through the authenticated capability;
- rejection of an old capability after the same `SSL` objects complete a fresh
  handshake;
- exact encrypted request/receipt byte preservation;
- receiver durable admission through a separate SQLite database;
- sender settlement and canonical evidence convergence;
- oversize rejection before body allocation; and
- empty-record rejection.

The service integration proves:

- wrong sender epoch and tampered request fail before mutation;
- the receipt generation/cutpoint equals the deciding receiver transaction;
- receipt replay on another channel fails;
- true aggregate capacity pressure fabricates no evidence and remains
  nonterminal;
- explicit retry creates a fresh claim and fences the old capacity receipt;
- receiver commit followed by process loss survives restart;
- retry before lease expiry is refused;
- retry at exact expiry creates a fresh attempt;
- duplicate receipt returns the original unchanged receiver cutpoint;
- the stale first receipt cannot settle the replacement claim; and
- sender and receiver evidence digests converge after fresh settlement.

Final compiler, sanitizer, complete CTest, stress, projection, and package
results are recorded in `RELEASE_GATE.json` and
`REVISION_EVIDENCE/rev0876/validation/`.

## What is still missing

### No shipped executable uses this path

The new protocol, service, and TLS adapter are production sources and not merely
test helpers. Nevertheless, a repository production-caller search still finds
no narrow executable that owns a listener, membership store, receiver payload,
or effect lifecycle around them. `anonsync_core` still follows the older stack.

This means rev0876 materially reduces composition uncertainty but does not yet
change user-visible synchronization behavior. The next revision should resist
the temptation to add another standalone invariant and instead create a small
executable or service process that consumes these exact libraries.

### No payload or filesystem-effect receipt

The operation carries size and content digest, but rev0876 sends no payload
bytes. The receiver does not spool, verify, publish, fsync, conflict-resolve, or
recover a target filesystem effect. A malicious or broken sender could deliver
operation metadata for bytes the receiver never obtains.

The repository already contains bounded regular-file handling, payload-store,
effect-intent, and atomic-file-publication components. The missing work is their
composition under one receiver-owned restart state machine.

A future effect-terminal receipt should commit to at least:

- operation ID and actor epoch;
- payload digest and exact length;
- receiver effect-intent ID;
- target-path/conflict decision;
- publication generation;
- durable state classification, including directory-sync outcome;
- receiver identity/key epoch;
- and a receipt authentication form that can be verified after the TLS session
  disappears.

### Receipts are channel-authenticated, not independently durable

A receipt is authentic to the sender because it arrives on the exact pinned TLS
channel whose exporter is embedded in the receipt. The receipt is not signed or
MACed with a durable receiver key. Persisting it for third-party audit after the
connection closes does not preserve independent cryptographic verifiability.

That is sufficient for current online sender settlement but not for offline
proof, replicated audit, or dispute resolution. A future signed effect receipt
must define canonical signing bytes, key epochs, algorithm agility, revocation
semantics, and replay/freshness rules. Do not simply sign the current structural
digest without specifying those authorities.

### Membership and key lifecycle are absent

The caller supplies actor epoch and SPKI pin. There is no durable membership
database, enrollment protocol, monotonic membership generation, root/recovery
key, rotation, revocation, rollback protection, or old-epoch acceptance rule.

The outbox itself is keyed by logical destination device ID, not receiver actor
epoch. The service binds the current authenticated epoch at claim time. That may
be correct if the product defines destination intent as "deliver to this logical
device under its currently authorized incarnation," but the rule is not yet
durable or specified. Membership design must decide whether an intent survives
rotation, is reauthorized, or is dead-lettered.

### No protocol negotiation beyond one exact version

Exact version rejection is safe, but there is no supported-version negotiation,
feature bitmap, limit negotiation, or migration path. Different request ceilings
at two peers can cause connection-level failure even though each local
configuration is coherent. Negotiation itself must not let a peer loosen local
bounds.

### No typed permanent rejection

`CapacityBlocked` is a recoverable nonterminal result. Invalid operation policy,
unsupported version, revoked actor, wrong membership, and poison payload are
currently exceptions or future transport errors. A production sender needs a
bounded typed outcome system with retry class, backoff, attempt/age ceilings,
dead-letter authority, and operator-visible evidence.

### No scalable production owner

`SyncReplicaSqliteOwner` restores and independently re-attests complete history
for every public operation. This is valuable as a correctness oracle, migration
verifier, repair authority, and crash-test scaffold. It is not a production
throughput claim.

The right optimization is not to weaken this owner. Add a separately named
indexed/incremental owner and differentially test generated operation histories,
crash frontiers, policy changes, and repairs against the full-history oracle.

### No anti-entropy, compaction, or causal stability

The request is origin-only and sends one complete operation. There is no missing
parent request protocol, range/index summary, peer inventory, chunked
anti-entropy, causal stability proof, tombstone retirement, checkpoint authority,
revoked/offline member treatment, or full-resync rule.

### No anonymity claim

Mutual TLS exposes endpoints and certificates to the endpoints, and ordinary
network observation still reveals addresses, timing, direction, and volume.
Device IDs, folder behavior, operation sizes, and retry patterns can create
linkable metadata. Relays can hide direct addresses from peers but not
necessarily from the relay or global observers. Payload encryption is not
anonymity.

## Cube audit and waste findings

### Assurance remains ahead of executable delivery

The newer causal path is increasingly rigorous, while the shipped executable
remains on another semantic stack. Rev0876 narrows this gap by creating reusable
production libraries and a real encrypted integration test, but it does not
eliminate it. Release planning should measure "executed by the product path" as a
separate gate from "proved in a focused authority fixture."

### Build modularity exceeds semantic modularity

After this revision CMake contains approximately:

- 69 libraries;
- 92 executables; and
- 182 literal `add_test` calls.

At the same time, major semantic centers remain large:

- `src/sync_domain.cpp`: about 15,167 lines;
- `src/sync_domain_selftests.cpp`: about 9,601 lines;
- `src/sqlite_replay_ledger.cpp`: about 4,529 lines;
- `src/sync_replica_sqlite_owner.cpp`: about 3,546 lines;
- `tests/sync_replica_sqlite_owner_test.cpp`: about 3,640 lines; and
- `include/anonsync_core.hpp`: about 3,544 lines.

The new subsystem adds roughly 3,591 lines across six production files and three
tests. Its small authority boundaries are useful, but its TLS test contains a
large ephemeral-PKI/socket/SQLite fixture. If more authenticated transports or
process-level tests appear, that fixture should become shared test
infrastructure rather than being copied.

The long-term correction is semantic decomposition, not merely more static
libraries. Split by state-machine owner and transaction boundary, use generated
CMake helpers for repetitive wiring, and maintain a fast affected-authority gate
alongside periodic complete regression.

### Historical evidence continues to dominate handoffs

Before adding rev0876, `REVISION_EVIDENCE/` contains about 4,497 files and 52 MB
extracted. The ZIP compresses this well, but every handoff still pays extraction,
hashing, review, and navigation cost. Much of that evidence is immutable
historical output rather than source needed to build the current implementation.

Rev0876 keeps its own evidence compact: exact active projection, changeset,
lineage, research, focused validation logs, and summary. Longer term, bulk logs
should move to a content-addressed external store with signed provenance. The
source handoff should retain current essential evidence plus hashes and trusted
references to historical artifacts.

### Lexical audits are hygiene, not semantic proof

The cube contains many useful Python audits that search for filenames, tokens,
ordering fragments, or retired vocabulary. They catch packaging drift and some
obvious regressions, but they cannot prove that OpenSSL verification is enabled,
that a receipt cutpoint comes from the same transaction, or that a frame limit
cannot deadlock protocol completion.

Rev0876's important defects were found through composition and executable
negative tests, not token presence. Release authority should continue shifting
toward typed total state machines, generated adversarial inputs, crash-frontier
injection, differential oracle tests, compiler/AST checks, and real process or
socket composition. Lexical audits should remain a lower-level hygiene gate.

## Online research and design implications

The implementation and audit used primary sources.

### RFC 9266 — TLS exporter channel bindings

RFC 9266 defines the `tls-exporter` channel binding using the exact exporter
label `EXPORTER-Channel-Binding`, empty context, and 32 bytes. It also cautions
that the binding is not a secret or a general-purpose key and discusses
connection/upper-layer protocol uniqueness. Rev0876 follows that construction,
then hashes the raw bytes into an AnonSync-specific typed binding rather than
using them as encryption or signing key material.

Source: <https://datatracker.ietf.org/doc/rfc9266/>

### OpenSSL peer verification

OpenSSL documents `SSL_VERIFY_NONE` as the default and separates verification
mode from the stored verification result. This supports the rev0876 rule that
`SSL_get_verify_result() == X509_V_OK` is insufficient unless
`SSL_VERIFY_PEER` was actually enabled.

Source: <https://docs.openssl.org/3.5/man3/SSL_CTX_set_verify/>

### OpenSSL exporter API

The OpenSSL exporter API documents label, context, and `use_context` semantics.
Rev0876 passes the RFC 9266 label, a null/zero context, and `use_context = 0`.

Source: <https://docs.openssl.org/3.4/man3/SSL_export_keying_material/>

### OpenSSL `SSL_clear()` lifecycle

OpenSSL documents `SSL_clear()` as resetting one `SSL` object for another
connection while retaining multiple settings, and warns that object reuse is
best avoided. That lifecycle means pointer identity cannot serve as handshake
identity. Rev0876 therefore rechecks the exporter and peer SPKI on every record
operation rather than assuming a once-authenticated pointer remains bound to the
same session.

Source: <https://docs.openssl.org/3.3/man3/SSL_clear/>

### RFC 8446 — TLS 1.3 early-data replay

TLS 1.3 gives 0-RTT data weaker replay guarantees and requires applications to
consider replay consequences. Rev0876 does not attempt to make operation
idempotency carry the entire burden; it disables and rejects early data until a
complete membership and replay policy exists.

Source: <https://datatracker.ietf.org/doc/html/rfc8446>

### RFC 7301 — ALPN

ALPN selects an application protocol inside the authenticated TLS handshake.
Rev0876 uses exact ALPN to prevent a certificate-valid connection for another
protocol from being treated as AnonSync delivery. RFC 7301 also establishes an
IANA registry, which is why the current private identifier is explicitly not a
public interoperability claim.

Source: <https://datatracker.ietf.org/doc/html/rfc7301>

### SQLite isolation

SQLite serializes writers, and `BEGIN IMMEDIATE` acquires write-transaction
authority before the owner applies a transition. That supports the local
transaction-bound admission cutpoint. It does not create atomicity across sender
and receiver databases. Ambiguous response is handled through fresh attempts and
receiver idempotency, not a fictional distributed transaction.

Source: <https://sqlite.org/isolation.html>

### Speculation: durable membership and group keys

For an initial two-peer vertical slice, pinned TLS identities plus a small durable
membership ledger are simpler than a full group protocol. If AnonSync later
supports large dynamic folders, MLS may help with group key epochs and member
changes, but it assumes separate authentication and delivery services and does
not solve application-level durable effects, suppression, or retry semantics.

Source: <https://datatracker.ietf.org/doc/rfc9420/>

This is a design inference, not a commitment to adopt MLS.

## Recommended sequence

### 1. Build one narrow receiver effect owner

Compose one operation kind with the existing bounded-file, payload-store,
effect-intent, and atomic-publication code. Persist an explicit state machine for
payload absent, partial, verified, publication prepared, visible, directory-sync
classified, receipt ready, and cleanup complete.

### 2. Add one process-level executable

Create a small `anonsync_replica_service` whose only durable replica authority is
`SyncReplicaSqliteOwner` (or a clearly named future indexed equivalent). It should
load one folder membership record, accept one TLS connection, process one
operation/payload/effect, send one receipt, and restart safely.

### 3. Inject crashes at every authority frontier

Cover sender claim, request encoding, prefix/body writes, receiver decode,
admission commit, payload writes, digest verification, temp-file sync,
publication prepare, rename, directory sync, receipt persistence, receipt write,
and sender settlement. Reopening both databases and filesystem staging must
converge without invented success.

### 4. Define effect-terminal receipt authentication

Add a canonical receiver-signed or durable-key-MACed receipt only after key epoch,
revocation, signing bytes, algorithm agility, and replay rules are explicit. The
current TLS-bound evidence receipt should remain a separate type.

### 5. Complete retry and dead-letter policy

Introduce typed local/transient, network, TLS, membership, protocol, capacity,
payload-integrity, effect, permanent, and operator-replay outcomes. Bind each to
bounded backoff/jitter, attempt count/age, due-time index, reason evidence, and
remote-hint clamping.

### 6. Add an indexed owner beside the oracle

Preserve the current full-history owner unchanged as reference authority. Build a
separate incremental implementation and require generated histories, concurrent
schedules, restart frontiers, and repairs to converge to the oracle's exact
canonical state and cutpoint.

### 7. Specify membership before resumption or group transport

Define enrollment, logical device versus actor epoch, key rotation, revocation,
recovery, rollback protection, old evidence, offline devices, and outbox behavior
across epoch change. Only then consider TLS resumption, richer anti-entropy, or
MLS-based group keys.

### 8. Define the privacy target

State which observers may learn peer addresses, timing, sizes, folder
association, device identity, and relay use. Then choose discovery, relays,
padding, batching, cover traffic, pseudonyms, or onion routing according to that
explicit target. Do not let encrypted payloads substitute for an anonymity
model.

## Deliberate nonclaims

Rev0876 does not claim:

- that `anonsync_core` uses the new authenticated causal path;
- payload transfer or payload availability;
- receiver filesystem publication or effect-terminal completion;
- exactly-once delivery or exactly-once filesystem effects;
- durable independently signed receipts;
- complete membership, enrollment, rotation, revocation, or recovery;
- safe TLS session resumption or 0-RTT;
- public ALPN registration or interoperability;
- nonblocking/event-loop transport, connection quotas, or network DoS resistance;
- typed permanent rejection, complete retry backoff, or dead-letter scheduling;
- anti-entropy, third-party gossip, causal stability, compaction, or tombstone GC;
- production throughput from the O(history) SQLite owner;
- malicious-host or privileged-local-writer defense;
- confidentiality of all metadata, anonymity, unlinkability, or traffic-analysis
  resistance;
- externally trusted signed build provenance;
- full-project Clang `-Werror`, full-project sanitizer, ThreadSanitizer, Windows
  runtime, or formal proof.

What rev0876 does claim is narrower and useful: one exact operation-evidence
attempt can be durably claimed, canonically framed, carried over a fresh
mutually authenticated and actor-pinned TLS 1.3 channel, admitted with a
transaction-bound receiver cutpoint, receipted on that same channel, and settled
only against the exact current sender claim, including duplicate/restart and
capacity-pressure frontiers.

# AnonSync rev0864 mission, gap map, and corrective roadmap

Date of review: 2026-07-20

## Executive assessment

AnonSync's best idea is not “file sync” and it is not yet “anonymous sync.” Its
best idea is **evidence-authorized transition**: an external value is merely an
observation until a narrow owner freezes the exact bytes, identity, incarnation,
generation, policy, lifetime, resource budget, and durability evidence needed by
one transition. The code has repeatedly turned that idea into concrete C++
owners around files, descriptors, process/thread identity, SQLite connections,
callbacks, transactions, manifests, replay records, checkpoint publication, and
peer-ingress state.

That is the heart of the mission and it is worth preserving.

The severe risk is that the project has become much better at proving local
boundary facts than at constructing the distributed system those facts are
supposed to protect. The repository now resembles an **authority and durability
kernel with a large assurance bureaucracy**, while the production peer
protocol, remote transport, formal replicated-state model, end-to-end daemon,
and anonymity threat model remain absent or explicitly unclaimed.

The most valuable change is therefore not to weaken the local invariants. It is
to redirect them into a vertical product path:

> Define the replicated state machine and adversarial network model; build a
> deterministic multi-replica simulator; then make a real authenticated remote
> connection carry exactly those operations through the existing bounded and
> durable ingress machinery.

Rev0864 also makes one immediate C++ correction that illustrates the broader
problem. `frame_digest_checked` was true after a digest was merely computed. No
expected digest was compared. The new move-only digest-bound frame owner restores
the missing relation before decode or enqueue.

## 1. The heart of the mission

### 1.1 The governing principle

The repeated design maxim is sound:

> Observation is not authority.

A pathname can race. A descriptor can be reused. A process ID can name a later
process. A callback can outlive the connection state it borrows. A digest can be
computed from the wrong bytes. A row count can be small while VM work is huge. A
successful `rename()` can still lack directory durability. A deterministic
conflict rule can still fail to converge under a network behavior it never
modeled.

AnonSync's distinctive engineering goal is to make those missing relations
visible and difficult to bypass in C++.

### 1.2 The three required layers

The mission is complete only when three layers meet.

#### Layer A: epistemic and authority correctness

- Freeze exact bytes before deriving identities or side effects.
- Bind identities to incarnation and generation, not reusable scalar handles.
- Make capability lifetime and revocation explicit.
- Reject malformed, ambiguous, stale, or over-budget authority before work
  amplifies.
- Prevent success-looking booleans from being set without the proposition their
  names claim.

This is where AnonSync is strongest.

#### Layer B: bounded execution and durable transition

- Bound independent dimensions independently: output bytes/rows, parser work,
  SQLite VM work, lock waiting, elapsed time, retries, filesystem effects, and
  global admission pressure.
- Keep callbacks and owners alive through the cleanup that may need them.
- Publish only after the intended file/database/directory durability frontier.
- Make replay, idempotency, crash recovery, and external effects part of one
  transition protocol.

AnonSync has substantial work here, especially around SQLite and local
publication, though important I/O, crash, and hostile-input dimensions remain.

#### Layer C: replicated semantics and privacy

- Define replica state and the exact operation algebra.
- State the network assumptions and prove or test convergence under every
  admitted behavior.
- Define peer/device identity, enrollment, rotation, revocation, recovery, and
  protocol version migration.
- Establish an authenticated encrypted remote channel.
- State what “Anon” protects: payloads, filenames, sizes, timing, topology,
  membership, IP location, server visibility, access patterns, or some subset.

This is the least developed layer. Without it, the first two layers are a strong
kernel, not yet the named product.

## 2. What is already valuable

The review found real implementation, not merely release prose.

- Canonical manifests, chunk identities, wire framing, bounded decoders, and
  deterministic conflict machinery exist.
- Peer ingress has SQLite-backed enqueue, replay/idempotency, payload storage,
  lifecycle, claims, retry, retention, authority decisions, and checkpoint
  integration.
- Process, thread, descriptor, namespace, connection, transaction, callback,
  schema, and publication ownership have increasingly narrow C++ types.
- Local transport fixtures exercise AF_UNIX socketpair and IPv4 loopback with
  partial read/write behavior.
- Crash-oriented publication and SQLite recovery paths have extensive focused
  tests.
- The release tree is exact-manifested and has a revision-scoped verifier.
- The current GCC all-target graph and all 163 registered tests pass.

The project should not throw this away in pursuit of a quick networking demo.
The right move is to make the distributed protocol consume these owners instead
of allowing them to become an end in themselves.

## 3. What rev0864 found severely wrong

### 3.1 A “checked” boolean with no check

Before rev0864, both local transport paths performed this effective sequence:

1. receive bytes;
2. compute `sha256(received_bytes)`;
3. set `frame_digest_checked = true`;
4. decode and enqueue.

There was no expected frame digest and no equality comparison. Hashing one value
does not establish integrity. The field name therefore asserted evidence the
code did not possess.

This matters beyond one boolean. The project exposes 592 public boolean fields
in `include/anonsync_core.hpp`. Many are useful diagnostics, but boolean-rich
result objects invite partial-state combinations and make semantic naming carry
more authority than the type system. Every `*_checked`, `*_verified`,
`*_authorized`, `*_durable`, or `*_bound` field deserves the same question:
**what exact relation was established, by which owner, and can the field become
true any other way?**

#### Correction in this revision

`SyncPeerTransportDigestBoundFrame` now:

- accepts a canonical expected digest frozen from canonical encoded bytes before
  transmission;
- takes ownership of exact received bytes;
- rejects malformed expected digests, zero budgets, empty frames, oversized
  frames, and digest mismatch;
- publishes expected digest, independently computed observed digest, exact
  bytes, and byte count only after success;
- is nondefault-constructible and noncopyable; and
- gates decode and durable enqueue in both local transport harnesses.

This is intentionally narrow. Because the expected digest is generated by the
same local fixture, it proves local send/receive identity, not remote peer
authenticity.

### 3.2 Mission-critical work has been repeatedly deferred

The historical evidence is unusually explicit. Across the 56 available revision
notes from rev0805 through rev0863:

- 49 mention convergence;
- 40 mention anonymity;
- many repeat hostile-worker, key-lifecycle, secure-erasure, or remote-system
  nonclaims.

Rev0805 already named real remote transport, privacy/anonymity/key lifecycle,
disposable hostile-database workers, monolith extraction, and deterministic
fault simulation as priority work. Rev0863 still says distributed convergence
and anonymity are unclaimed.

A repeated nonclaim is honest. After dozens of revisions, however, it also
becomes evidence of prioritization failure. The code has optimized the safety of
components that do not yet participate in a complete remote replicated system.

### 3.3 Assurance inversion

The current tree contains:

- `REVISION_EVIDENCE`: 3,911 files, 34,549,940 bytes;
- `src`: 160 files, 4,768,942 bytes;
- first-party C/C++ under `include`, `src`, `tests`, and `fuzz`: 254 files,
  125,651 lines, 6,641,345 bytes;
- Python tools: 53 files, 24,526 lines, 1,074,658 bytes;
- CMake: 3,031 lines and 154,350 bytes;
- registered tests: 163, of which 49 are named audits.

Historical evidence is about 7.2 times the size of current production `src` and
about 59% of the present release-tree bytes before rev0864 evidence is added.
Every cumulative package carries all previous evidence. Retaining every
cumulative archive therefore duplicates old evidence repeatedly and tends
toward quadratic aggregate storage over revision history.

This evidence is not worthless. The inversion is that evidence production has
become a major product surface while remote synchronization and anonymity remain
nonproducts.

### 3.4 Lexical audits are overtrusted

The 50 `audit_*.py` programs and related tools contain 153 `read_text()` calls
and 118 direct Python regex API uses. The scan found no Python `ast` import,
tree-sitter use, libclang binding, or `compile_commands.json` consumer.

Lexical checks are excellent for narrow inventory assertions: a file must exist,
a target must be linked, a forbidden literal must be absent. They are weak for
semantic claims: ownership, lifetime, exception safety, graph reachability,
call-order dominance, or “all paths pass through this owner.” Rev0863's own
history records both a stale-literal false failure and a transitive sanitizer
graph gap.

The correction is not “delete the audits.” It is to classify them:

- **Inventory audits:** keep lexical and exact.
- **Build-graph audits:** derive from CMake file API, Ninja commands, or
  `compile_commands.json`.
- **C++ semantic invariants:** enforce with types, focused negative tests,
  compiler diagnostics, sanitizers, and—where justified—AST tooling.
- **Protocol properties:** enforce with model checking, property-based state
  machines, deterministic simulation, and cross-process tests.

### 3.5 Public API and implementation concentration

Current concentration includes:

- `src/sync_domain.cpp`: 15,157 lines;
- `src/sync_domain_selftests.cpp`: 9,598 lines;
- `src/reporting_selftests.cpp`: 4,992 lines;
- `src/sqlite_replay_ledger.cpp`: 4,529 lines;
- `src/sync_peer_ingress_lifecycle.cpp`: 3,846 lines;
- `include/anonsync_core.hpp`: 3,544 lines, 134 public structs, 592 boolean
  fields, and 123 `uint64_t` fields whose names contain `epoch`.

The project has successfully extracted many leaf owners, but orchestration and
public shape remain broad. Caller-supplied scalar epochs are especially risky:
exact-generation owners are sophisticated, yet time authority often arrives as
an ambient integer.

### 3.6 The transport is a fixture, not a peer protocol

The reviewed source contains AF_UNIX socketpair and IPv4 loopback calls. The scan
found no AF_INET6 path and no `SSL_connect`/`SSL_accept` usage. OpenSSL is present
for cryptographic primitives, but there is no demonstrated remote TLS session,
peer certificate policy, discovery, relay, NAT traversal, reconnect/session
resumption, wire-version negotiation, or streaming backpressure protocol.

The local harness is still valuable. It proves bounded framing and durable
admission over a real byte stream. It should be named and treated as a fixture,
not mistaken for production transport.

### 3.7 Whole-frame copying remains a bounded but costly design

The local path encodes a complete frame into a `std::string`, sends it, appends
all received bytes into another string, hashes the complete frame, decodes it,
and materializes decoded chunk strings. With a default 16 MiB frame limit this is
bounded, but the peak-copy and allocator cost is material under concurrency.

A future remote path should preserve the exact-byte authority model while using
a bounded streaming decoder or immutable spool:

- hash while reading;
- enforce frame length before allocation;
- stream canonical fields and chunk bodies into bounded sinks;
- retain exact bytes only when replay/audit policy actually requires them; and
- distinguish transport buffer budget, decoded-object budget, and durable-spool
  budget.

Do not optimize this before the protocol model exists, but do not carry the
whole-frame fixture architecture unquestioned into production.

## 4. What is missing, in priority order

## P0.1 — A formal replicated state and operation model

AnonSync needs a small, explicit answer to these questions:

- What is replica state?
- What operation is transmitted?
- Which fields determine operation identity and causal relation?
- What are the preconditions for applying an operation?
- Is the design operation-based, state-based, delta-state, log-based, or a
  hybrid?
- What exactly is the conflict rule for every file/tombstone/rename case?
- Which network behaviors are admitted: duplication, loss, reordering,
  partitions, redelivery after restart, Byzantine peers?
- What property is claimed: eventual delivery plus deterministic merge, strong
  eventual consistency, or something weaker?

The current deterministic conflict tests are useful but are not a whole network
model. Published CRDT verification work is a warning: even algorithms with
mechanized proofs have been wrong when the formalization omitted realistic
network behavior. The model must include the network assumptions.

### Cloudtainer implementation path

Create a dependency-light C++ library with pure values:

- `ReplicaId`, `DeviceEpoch`, `OperationId`, `VersionVector` or chosen causal
  witness;
- `ReplicaState`;
- `Operation` variants;
- `apply_local`, `receive_remote`, and `merge`/delivery rules;
- canonical serialization separate from semantics;
- a deterministic network simulator with drop, duplicate, reorder, delay,
  partition, heal, crash, and restart actions; and
- invariants checked after every action.

Start without SQLite or sockets. Once the state machine is comprehensible, bind
its operations to existing ingress and durability owners.

## P0.2 — A production peer connection and protocol transcript

A production connection needs an authority object that binds at least:

- authenticated local device identity and key epoch;
- authenticated remote device identity and key epoch;
- protocol version and negotiated capabilities;
- channel/session identifier;
- transcript or exporter binding;
- frame sequence/replay policy;
- resource/deadline policy;
- close/reconnect generation; and
- the exact bytes admitted to the application protocol.

TLS 1.3 with pinned device certificates is the shortest path using the available
OpenSSL toolchain and resembles the separation used by Syncthing's Block
Exchange Protocol. A Noise handshake is a credible alternative when identity
hiding or a custom transcript is a primary requirement. Choose one initial
channel design; do not stack TLS, Noise, Tor, and MLS without a threat-driven
reason.

The first vertical slice should connect two local processes over IPv6/IPv4 TCP,
authenticate pinned test identities, negotiate one wire version, transfer one
operation, durably enqueue it, crash/restart one side, reconnect, replay safely,
and converge.

## P0.3 — An explicit anonymity and leakage model

The name “AnonSync” is currently ahead of the implementation. “Anonymous” can
mean very different properties:

- payload confidentiality;
- filename/path confidentiality;
- equality, size, timing, and access-pattern hiding;
- peer pseudonymity;
- membership hiding;
- IP/location hiding;
- topology hiding from relays or rendezvous services;
- deniability;
- resistance to a malicious peer, server, local user, kernel, or global passive
  observer.

Write the adversaries and acceptable leakage before selecting cryptography.

- TLS or Noise can protect a channel and authenticate peers.
- MLS can help with asynchronous group key epochs, forward secrecy, and
  post-compromise security, but it does not define the whole application,
  storage, metadata, or anonymity architecture.
- Tor onion services can provide location hiding, authenticated onion identity,
  end-to-end encryption, and outgoing-only reachability, but introduce latency,
  availability, and traffic-analysis tradeoffs.

A practical product may support privacy profiles rather than claim universal
anonymity. Until one is implemented and tested, use the stage label **AnonSync
Authority Kernel** in technical status material.

## P0.4 — End-to-end multi-process and fault testing

Current focused tests are strong at local invariants. The product needs a test
that starts multiple independently durable replicas and subjects them to:

- message loss, duplication, delay, and reordering;
- network partitions and asymmetric reachability;
- concurrent edits and deletes;
- process death at every durable cut point;
- database lock contention and disk-full/short-write failures;
- reconnect, identity rotation, and protocol upgrade;
- clock skew or, preferably, removal of wall-clock authority from correctness;
- malformed and malicious peer frames; and
- bounded resource pressure across many peers.

The oracle must compare recovered domain state, not merely SQLite integrity or
successful process exit.

## P1.1 — Hostile-input isolation

Untrusted database and document interpretation still occurs in the principal
process. SQLite authorizers, limits, progress handlers, path owners, and schema
checks reduce attack surface but are not a sandbox.

A disposable POSIX worker is implementable in this cloudtainer using existing
process-incarnation work:

- pass only sealed descriptors and a typed request;
- close unrelated descriptors and clear environment;
- enforce CPU, address-space, file-size, descriptor, and wall-time limits;
- add seccomp/Landlock where available as defense in depth;
- bound output and kill on protocol deviation; and
- dispose of the worker after every hostile artifact or small batch.

## P1.2 — Complete multidimensional budgets

Recent revisions correctly separated SQLite VM work from lock waiting. Apply the
same discipline system-wide:

- network bytes and connection count;
- transport buffer and decoded-object bytes;
- filesystem bytes and operations;
- durable spool size;
- CPU and wall-clock deadlines;
- retries and reconnects;
- per-peer, per-session, and global quotas; and
- cleanup work after failure.

A local per-operation cap is not sufficient when thousands of authorized small
operations can exhaust a process.

## P1.3 — Time and epoch authority

The public header contains 123 `uint64_t` epoch-named fields. Many are supplied
by callers. Replace correctness-sensitive ambient timestamps with typed sources:

- monotonic clock observations for deadlines;
- logical or causal versions for replicated ordering;
- lease-generation tokens for ownership;
- explicit test clocks; and
- conversion only at boundary adapters.

Wall time should be diagnostic or policy input unless the protocol explicitly
proves what clock assumptions it needs.

## P1.4 — Protocol migration and compatibility

Source revision numbers are not a wire protocol. Define:

- a stable protocol identifier and version negotiation;
- capability advertisement;
- canonical unknown-field behavior;
- downgrade policy;
- schema migration and rollback rules;
- old/new peer interoperability tests; and
- durable state migration independent of build revision archaeology.

## P1.5 — API decomposition and impossible states

Continue leaf extraction, but prioritize transition capabilities over more
boolean-rich result bags.

Examples:

- return `DigestBoundFrame` rather than a result containing
  `frame_digest_checked`;
- return `DurablyPublished<T>` rather than a set of publication booleans;
- represent lifecycle states with a tagged union/state enum plus state-specific
  payloads;
- split `anonsync_core.hpp` by manifest, transport, ingress, checkpoint,
  persistence, and operator APIs; and
- hide internal diagnostic fields behind structured evidence records.

## P2.1 — Evidence architecture

Keep exact lineage, but stop copying every historical log into every source
archive.

A better shape is:

1. The source package contains current source, current release gate, exact
   manifest, parent artifact digest, current active projection, and a compact
   attestation index.
2. Large logs and historical validation bundles live in a content-addressed
   store keyed by digest.
3. A signed in-toto/SLSA-style attestation records build inputs, resolved
   dependencies, builder identity, commands or build type, and output digests.
4. Consumers fetch historical byproducts only when needed.

SLSA's provenance guidance explicitly favors useful, nonreproducible byproducts
rather than every intermediate file. In-toto supplies a standard vocabulary for
what steps ran, by whom, and in what order. Neither standard automatically makes
local evidence trustworthy; signing keys, builder isolation, and a trust policy
are still required.

## P2.2 — Build and audit graph simplification

CMake now has 61 libraries, 81 executables, 166 textual `add_test()` calls, and
139 `target_link_libraries()` calls. The narrow-target pattern is defensible,
but the declaration boilerplate is expensive and can hide omissions.

Introduce a reviewed helper/registry that declares one invariant unit from data:
source, dependencies, test, sanitizer eligibility, timeout, and verifier
inventory. Generate compiler-derived graph evidence from CMake/Ninja rather than
repeating target names across hand-maintained lists. Make the migration in small
steps and compare the generated graph before and after each conversion.

## 5. Online research and what it implies

Sources were consulted on 2026-07-20. These are design inputs, not claims that
AnonSync already implements their properties.

### Syncthing Block Exchange Protocol v1

URL: https://docs.syncthing.net/specs/bep-v1.html

The protocol separates block exchange from the lower encryption/authentication
and reliable transport layers, requires TLS 1.3 or higher, and describes
certificate-based device authentication. It also defines a local/global model
for devices trying to converge folders. For AnonSync, the useful lesson is
layering: replicated semantics, authenticated channel, and transport reliability
must each have an explicit contract.

### Noise Protocol Framework

URLs:

- https://noiseprotocol.org/
- https://noiseprotocol.org/noise.html

Noise is a framework for authenticated key-exchange and encrypted transport
patterns, with options including mutual authentication, identity hiding, and
forward secrecy. It is relevant when AnonSync's threat model needs a custom
handshake or identity-hiding property. It is not a synchronization, metadata
privacy, or key-recovery protocol by itself.

### Tor onion services

URL: https://community.torproject.org/onion-services/overview/

Tor documents location hiding, onion-address authentication, end-to-end
encryption, outgoing-only reachability/NAT traversal, introduction points, and
rendezvous. This is relevant only if “Anon” includes hiding peer location or
avoiding inbound ports. Onion transport does not hide application-level sizes,
timing, filenames, membership, or malicious-peer behavior by itself.

### Messaging Layer Security

URLs:

- https://www.rfc-editor.org/rfc/rfc9420.html
- https://www.rfc-editor.org/info/rfc9750/

MLS specifies asynchronous group key establishment with forward secrecy and
post-compromise security. The architecture document emphasizes that important
application infrastructure and security/privacy tradeoffs remain outside the
core protocol. MLS is a candidate for multi-device/group key epochs after
AnonSync defines membership and threat semantics; it should not be adopted as a
substitute for those definitions.

### Strong eventual consistency verification

URLs:

- https://arxiv.org/pdf/1707.01747
- https://github.com/trvedata/crdt-isabelle

The work formalizes CRDT convergence with an explicit network model and notes
that published algorithms—including some with purported mechanized proofs—have
later proved incorrect. The direct implication is that deterministic conflict
functions and local replay tests are not enough. AnonSync needs a stated network
model and a theorem/property over all admitted executions.

### Merkle-CRDTs

URL: https://arxiv.org/abs/2004.00107

Merkle-DAGs can combine logical history, content addressing, deduplication, and
weak messaging assumptions. This is promising for evidence and anti-entropy,
but speculative for AnonSync. A Merkle structure does not automatically provide
access control, deletion semantics, privacy, bounded storage, or the desired
conflict policy. Model the operation algebra first.

### SLSA and in-toto

URLs:

- https://slsa.dev/spec/v1.2/build-requirements
- https://slsa.dev/spec/v1.0-rc2/provenance
- https://in-toto.io/

SLSA frames provenance authenticity, accuracy, completeness, dependency
capture, builder isolation, and byproducts. In-toto models supply-chain steps,
actors, and order. These support replacing cumulative evidence copies with
content-addressed, signed attestations while retaining exact lineage.

### SQLite callback boundaries

URLs:

- https://sqlite.org/c3ref/busy_handler.html
- https://sqlite.org/c3ref/progress_handler.html
- https://sqlite.org/c3ref/set_authorizer.html
- https://sqlite.org/threadsafe.html

SQLite's callback contracts reinforce AnonSync's recent ownership direction:
busy handling, progress interruption, compile-time authorization, and connection
threading are different mechanisms with different lifetimes and blind spots.
They should remain separate capabilities. They still do not isolate hostile
SQLite execution from the principal process.

## 6. Speculative architecture

The following is deliberately speculative.

### 6.1 Split the product into three explicit deliverables

1. **Authority kernel:** current exact-value, generation, lifetime, budget,
   persistence, and publication owners.
2. **Replica semantics laboratory:** pure C++ state machine, deterministic
   network/filesystem simulator, property tests, and model artifacts.
3. **Peer daemon:** authenticated remote transport, discovery/relay adapters,
   durable operation exchange, operator controls, and privacy profile.

This makes progress legible. A release can say which deliverable advanced rather
than treating every new local owner as equivalent product progress.

### 6.2 Make evidence a typed graph

Instead of hundreds of independent booleans, model evidence as immutable nodes:

- each node names the proposition, exact input digests, owner/generation,
  policy/budget, and parent evidence nodes;
- transition capabilities hold the minimal evidence roots they require;
- diagnostics serialize the graph; and
- release evidence can content-address the same format.

This could unify runtime authority and build provenance, but it risks complexity.
Prototype it on one path—transport frame to ingress enqueue—before generalizing.

### 6.3 Use a vertical-slice budget for future revisions

A governance experiment: after at most three local-hardening revisions, require
one revision that advances a vertical product slice—replica model, network
simulation, remote connection, multi-process durability, or privacy semantics.
This is not a technical invariant, but it would counter the observed drift.

### 6.4 Keep cryptographic choices threat-driven

A reasonable staged hypothesis is:

- initial remote interoperability: mutual TLS 1.3 with pinned device
  certificates and exporter-bound application transcript;
- optional identity-hiding/custom handshake: evaluate Noise;
- optional location-hiding profile: Tor onion transport;
- group membership with FS/PCS: evaluate MLS after semantics exist.

Do not promise all properties from one layer. Channel authentication, content
confidentiality, metadata leakage, location hiding, group key recovery, and
replicated correctness are separate claims.

## 7. Recommended next implementation sequence

### Rev0865: executable replica/network specification

- Add pure C++ `ReplicaState` and operation types for the smallest useful file
  lifecycle: create/update/delete with content identity and one conflict rule.
- Add a deterministic network scheduler with duplicate, reorder, drop,
  partition, heal, crash, and restart actions.
- Assert convergence when delivery assumptions are eventually satisfied.
- Keep SQLite and sockets out of the semantic core.

### Rev0866: bind model operations to canonical wire and durable ingress

- Define a stable protocol version and operation envelope.
- Prove canonical encode/decode round trips and reject ambiguity.
- Feed model operations through the existing bounded ingress store.
- Recover after process restart and compare domain state with the pure model.

### Rev0867: two-process authenticated transport slice

- Add IPv6/IPv4 TCP abstraction and explicit read/write deadlines.
- Use OpenSSL TLS 1.3 with pinned ephemeral test device certificates.
- Bind a connection transcript capability to remote identity, protocol version,
  session generation, and frame sequence.
- Transfer and durably apply one operation across two processes.

### Rev0868: privacy and key-lifecycle contract

- Publish the adversary/leakage matrix.
- Define enrollment, rotation, revocation, recovery, and stolen-device behavior.
- Choose whether location hiding is in scope and whether a Tor adapter is a
  profile.
- Choose whether group epochs justify MLS experimentation.

### Parallel maintenance, not the main sequence

- audit all semantic `*_checked` booleans;
- derive build graph evidence from compiler/CMake metadata;
- split the public header by domain;
- introduce typed clock/epoch sources;
- prototype hostile SQLite workers; and
- design content-addressed release evidence.

## 8. Bottom line

AnonSync's mission is not to accumulate proofs that local helper functions are
careful. Its mission is to make **authorized replicated transitions converge
without inventing authority from observation**, under an explicit privacy and
adversary model.

The current authority kernel is unusually serious and should be preserved. The
missing center is the networked state machine and the meaning of “Anon.” The
most wasteful future would be to continue polishing local evidence indefinitely
while those two questions remain nonclaims. The most productive future is to
make every next invariant owner serve an executable end-to-end replica story.

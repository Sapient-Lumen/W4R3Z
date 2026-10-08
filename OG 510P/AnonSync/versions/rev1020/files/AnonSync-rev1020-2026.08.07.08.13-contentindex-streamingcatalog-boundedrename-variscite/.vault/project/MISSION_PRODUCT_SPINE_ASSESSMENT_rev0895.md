# AnonSync rev0895 mission and product-spine assessment

**Assessment date:** 2026-07-25
**Scope:** deep source review, clean build and runtime validation in the cloudtainer, process-level composition work, current primary-source research, and clearly labeled speculation.

## Executive verdict

AnonSync's heart is **authority-preserving convergence**. It is trying to make a strong statement that ordinary synchronization systems often blur: a digest, cache, lease, retry counter, current directory listing, live socket, or test report is not allowed to become truth merely because it is convenient. Exact authorized history, identity-bearing observations, durable causal state, and live owned capabilities must determine what exists, who may act, what may be retried, which remote result is acceptable, and when bytes may become visible.

That mission is coherent and unusually rigorous. The repository contains substantial real implementation: causal operation/evidence models, SQLite owners, bounded resource policies, crash cutpoints, durable payload storage, anchored TLS membership, receiver-side file effects, and receipt-bound settlement. The central failure before this revision was not absence of mechanisms. It was **absence of a product spine**. The strongest newer owners existed mainly as libraries and in-process tests, while the shipped `anonsync_core` executable was a diagnostic/self-test aggregation and did not make the causal SQLite + durable payload + authenticated transport + filesystem effect + receipt chain its actual runtime authority.

Rev0895 closes the first bounded vertical slice. A separate `anonsync_replica` executable now performs one-shot enqueue, membership publication, authenticated send, and authenticated receive. A production TLS client authenticates the expected actor and SPKI before claiming work, then crosses the guarded request-prefix frontier, receives one exact receipt, and settles the matching durable claim. A registered process test runs two independent databases and two executable processes over real TCP/TLS and proves exact destination bytes and terminal settlement.

This is an important transition from “correct components” to “a real system path,” but it is not yet a usable synchronization product. The next center of gravity should be a durable peer loop, status and recovery operations, directory/tombstone semantics, reachability/GC, a separately checked indexed catalog, and an explicit privacy threat model. More local micro-hardening without those vertical slices would repeat the repository's prior drift.

## The heart of the mission

The repository's own maxim is the right one:

> Exact history is authority; summaries are acceleration.

That maxim decomposes into eight practical obligations:

1. **Observation authority.** Filesystem, database, clock, socket, certificate, and process observations must name the exact object and lifetime they authorize. Path strings and descriptor numbers alone are not identity.
2. **Canonical identity.** Equivalent evidence must encode and hash identically; malformed, ambiguous, or context-free encodings must fail closed.
3. **Exact causality.** Operations and effects must retain enough history to distinguish concurrent, stale, duplicate, and unauthorized work without inventing a total order that was never observed.
4. **Durable publication.** A crash must not transform prepared state into committed state, or a network ambiguity into permission to retry.
5. **Owned liveness.** Leases and deadlines are useful only when the clock, process/thread incarnation, and durable high-water evidence are explicit.
6. **Authenticated dissemination.** A transport session may carry authority only after cryptographic peer identity and current membership policy are bound to the exact channel.
7. **Effect ownership.** Visible filesystem mutation must have a single bounded owner and a truthful terminal cutpoint; a receipt must not precede the effect it acknowledges.
8. **Deterministic projection.** Replicas with equivalent authorized evidence and trust state should derive the same active and visible state. Indexes and summaries may optimize this derivation but may not replace the oracle.

This makes AnonSync closer to an **authenticated causal operation/effect log with filesystem projection** than to an ordinary folder copier. It should resist being described merely as a CRDT, because the project cares as much about observation provenance, authorization, crash publication, and side-effect truth as it does about merge convergence.

## Current architecture, as actually present

The source tree contains two partially overlapping eras:

- A large legacy/runtime aggregation centered on `include/anonsync_core.hpp`, `src/sync_domain.cpp`, `src/runner.cpp`, `src/sync_operator_cli.cpp`, and `anonsync_core`.
- A newer replica kernel centered on `sync_replica_*` owners: causal state, SQLite authority, payload store, membership/anchor stores, TLS transport, file-delivery service, receiver effect owner, and exact receipt settlement.

Before rev0895, the second stack had stronger authority semantics but no production `SSL_connect` owner and no independently invokable end-to-end executable. `SSL_connect` existed only in test support. The first stack supplied the nominal executable but linked self-test implementation libraries and was not the sole composition of the newer durable authorities.

Rev0895 deliberately does not merge the two eras. It creates a narrow product-spine executable around the newer owners and leaves the diagnostic executable intact. That is the safest direction: prove a small coherent product boundary first, then retire or quarantine legacy overlap by measured migration rather than by another giant rewrite.

## What rev0895 changes

### Production outbound TLS owner

`SyncReplicaFileTlsClientContext` retains one caller-configured `SSL_CTX` by reference count and is move-only. `send_one_sync_replica_file_delivery_tls_session_or_throw` owns one complete outbound conversation:

1. validate the numeric endpoint, peer policy, worker, lease, and absolute deadlines;
2. prove the durable payload snapshot and folder identity before opening a socket;
3. create one nonblocking, close-on-exec TCP socket;
4. perform bounded numeric-address connect and verify `SO_ERROR`;
5. perform a bounded TLS 1.3 client handshake;
6. derive and compare the peer SPKI and bind the expected actor;
7. only after authentication, claim at most one ready SQLite outbox item;
8. cross the guarded complete encrypted request-prefix frontier;
9. finish the request body under an absolute deadline;
10. receive one bounded authenticated receipt;
11. apply that exact receipt to the matching operation/claim; and
12. make TLS shutdown subordinate to the application result, then close unconditionally.

No claim is spent before durable payload preflight and peer authorization. Once the guarded request prefix has been accepted, a request timeout, peer close, or receipt timeout leaves the claim live and ambiguous; the transport owner does not launder uncertainty into an eager retry release.

### Product-spine executable

`anonsync_replica` exposes bounded one-shot commands:

- `certificate-spki`
- `enqueue-file`
- `membership-publish`
- `send-one`
- `serve-one`

It links the replica product stack and not the self-test implementation libraries. In the current GCC Debug build it is approximately 16 MiB, versus approximately 29 MiB for the diagnostic `anonsync_core`; symbol inspection found no self-test symbols in `anonsync_replica`. Size is not the security property, but the result demonstrates that a product surface no longer needs the diagnostic corpus in its link closure.

### Explicit container clock profile

The default kernel clock source remains fail-closed. This cloudtainer hides or withholds enough host clock-synchronization evidence that the default owner can enqueue but cannot safely mint a lease claim. Rev0895 adds an optional, explicit operator-trusted profile with a canonical authority ID and claimed uncertainty. It still binds boot identity, the best available calling-thread time-namespace observation, bracketed `CLOCK_BOOTTIME`/`CLOCK_REALTIME` samples, hard uncertainty limits, cumulative drift checks, sticky quarantine, and explicit recovery rules.

This profile is a **deployment assertion**, not a measurement or attestation. It is never selected implicitly. The CLI requires both `--operator-clock-authority-id` and `--operator-clock-uncertainty-ns`; absent those paired options, the normal fail-closed source remains in force.

### Process-level proof

`tools/test_anonsync_replica_cli.py` runs the shipped executable as separate processes and proves:

- generated Ed25519 CA and leaf credentials;
- exact SPKI extraction through the product CLI;
- first-generation anchored membership bootstrap and a later generation;
- durable binary payload publication and causal enqueue;
- real loopback TCP, mutual TLS 1.3, SPKI/actor binding, request and receipt framing;
- receiver filesystem publication before receipt;
- exact bytes at the destination; and
- terminal sender settlement after the matching receipt.

This process proof found three composition defects that in-process library tests had not found:

1. **Genesis membership publication was impossible.** The CLI asked for current authority on a new database instead of using the coordinator's explicit reconciled genesis target.
2. **The request-frame budget was guessed incorrectly.** Payload plus 1 MiB did not preserve the protocol's independently bounded evidence envelope. The CLI now derives the reviewed non-payload headroom from protocol constants.
3. **The executable could never claim in this cloudtainer.** The default clock correctly reported synchronization authority as unknown; the product had no explicit deployment trust profile.

A fourth product boundary was intentionally not “fixed” by convenience: the receiver does not manufacture missing parent directories. The process test pre-provisions the destination directory. Directory creation, tombstones, renames, and symlink policy need causal semantics rather than hidden CLI side effects.

## What is strong

### Authority-first design

The strongest parts of the repository consistently refuse ambient authority. Exact database generations, process/thread incarnations, filesystem object identity, retained callback claims, immutable membership snapshots, and move-only continuation objects are not cosmetic abstractions; they encode meaningful cutpoints.

### Crash and ambiguity discipline

The project repeatedly distinguishes “did not happen,” “may have happened,” and “did happen and is durably evidenced.” This is especially valuable around atomic file publication, outbox claims, request-prefix transmission, receiver effects, and receipts. Many synchronization bugs begin when a timeout is treated as proof that a side effect did not occur.

### Boundedness

Protocol frames, retained histories, payloads, callbacks, polls, retries, evidence sets, and scans usually have explicit ceilings. The new sender preserves absolute deadlines and numeric-only routing. Boundedness should remain a top-level product property rather than being relaxed when a daemon appears.

### Full-scan oracle philosophy

The durable payload store is intentionally a complete, expensive correctness oracle. That is a good foundation for introducing an index: build a separate indexed owner and continuously compare it against the oracle. Do not mutate the oracle into an optimization and lose the independent reference.

### Tests that model real cutpoints

The repository has extensive crash, fork, descriptor, SQLite, TLS, and filesystem tests. The new process test demonstrates the next needed pattern: test the same executable and process boundaries operators will actually run, not only owners composed inside one address space.

## What is missing, ranked

### P0 — Dependency currency: SQLite 3.53.4

The tree vendors SQLite 3.53.3. SQLite 3.53.4 was released on 2026-07-24 and explicitly fixes problems remaining in 3.53.0 through 3.53.3. The official amalgamation archive is `sqlite-amalgamation-3530400.zip`, SHA3-256 `628a44cfe82c66aed1ccbbe85a562d2e33ebe64b3288981ed76285612227934e`; the official `sqlite3.c` SHA3-256 is `67f423e9ebbbdc473cbc4772c872ee6b89f31fde4ed0279a5c25d5f65c043a16`.

The exact archive could not be acquired in this cloudtainer: direct container networking lacked external DNS and the available download bridge rejected archive media. Rev0895 therefore does **not** claim the dependency upgrade. Acquiring the official archive, verifying both published hashes, updating all runtime pins, rebuilding every lane, and rerunning the full database corpus should be the first dependency task in the next capable environment.

### P1 — Durable peer loop and operator surface

One-shot send/receive proves composition but is not a daemon. Missing product authorities include:

- durable peer configuration and discovery policy;
- a bounded scheduler with backoff, quotas, fairness, and jitter;
- listener lifecycle and graceful shutdown;
- status/health output that distinguishes no work, quarantine, ambiguity, and permanent rejection;
- explicit clock-quarantine status and recovery commands;
- certificate and membership rotation workflows;
- metrics that remain summaries rather than authority; and
- restart recovery tests spanning real processes.

The loop should call the one-shot owners; it should not absorb their socket/TLS/claim logic into a new monolith.

### P1 — Directory, deletion, rename, and type semantics

The current product slice writes a file only when its parent directory already exists. A synchronization product needs causal operations for:

- directories and their creation/removal;
- tombstones and deletion retention;
- rename/move semantics;
- file-versus-directory conflicts;
- symlink policy;
- executable/permission metadata policy;
- case-folding and Unicode normalization boundaries; and
- platform-specific forbidden names.

These should be explicit evidence-bearing operations. Recursive `create_directories()` in the receiver would make tests pass while silently inventing state.

### P1 — Reachability and garbage collection

The payload store can retain bytes, but the system lacks a complete authority model for when content becomes unreachable and when deletion is safe across replicas, delayed peers, retries, receipts, snapshots, and rollback windows. GC must be derived from exact retained evidence, not only current projection. A useful design is:

- full-scan reachability oracle;
- explicit retention epochs/watermarks tied to membership and receipt evidence;
- tombstone retention policy;
- dry-run proof output;
- crash-safe deletion queue; and
- differential tests between retained content and every live reference source.

### P1/P2 — Indexed catalog and scalable history

Several owners intentionally reconstruct or scan O(history) or O(total payload bytes). That is correct for an oracle and not acceptable as the sole production fast path. Introduce separate indexes and checkpoints with domain-separated digests, exact source-generation bindings, rebuildability, and continuous differential testing. Never let “index says absent” authorize deletion unless the exact oracle and retention policy agree.

### P2 — Privacy meaning of “Anon”

Today, AnonSync has authenticated and encrypted channels. It does not provide anonymity, unlinkability, endpoint hiding, private interest discovery, metadata minimization, traffic-analysis resistance, or at-rest confidentiality. The name creates expectations the implementation does not meet.

Before adding cryptography, write a threat model that answers:

- anonymous from whom: peers, relays, local administrators, network observers, or membership authorities?
- which metadata must be hidden: device identity, folder identity, paths, file sizes, membership, interests, timing, IP addresses?
- is pseudonymity sufficient, or is unlinkability across sessions required?
- may peers learn that they have no overlapping interest?
- which resource-abuse protections are required when identity is hidden?
- how are revocation, audit, and recovery reconciled with anonymity?

A plausible near-term interpretation is **metadata-minimized capability sync**: peers disclose and transfer only authorized overlapping areas, without revealing non-overlapping folder/path interests. Endpoint anonymity should remain an optional outer routing profile, separate from the authority kernel.

### P2 — Key evolution and compromise recovery

Current TLS/SPKI pinning and anchored membership are a sound baseline for peer authentication. Long-lived groups still need explicit key rotation, member removal, stale-key rejection, and compromise-recovery semantics. Messaging Layer Security offers useful concepts—epochs, authenticated membership changes, forward secrecy, and post-compromise security—but MLS is not a file synchronization protocol and should not be imported wholesale. Its group-state ideas may inform a later membership-key layer while AnonSync retains its own causal operation/effect semantics.

### P2 — External artifact provenance

The package manifest and in-tree evidence bind bytes, but the release does not have external signed build provenance. SLSA's model usefully separates an immutable artifact from attestations about the build platform, inputs, and process. AnonSync should eventually emit a compact artifact-bound provenance statement from an isolated builder and verify it outside the archive. The current ever-growing in-tree evidence should not be mistaken for independent attestation.

## Places where things went severely wrong or became wasteful

### 1. The assurance/product inversion

The repository accumulated very strong proofs around isolated owners while the product executable did not use the strongest path. This is the most severe strategic error because it can create confidence without deployability. The correction is not fewer tests; it is a rule that every few hardening revisions must produce or extend a real vertical product slice.

**Policy recommendation:** after at most three local hardening revisions, require one end-to-end process-level increment unless a documented blocker makes that unsafe.

### 2. A diagnostic executable masqueraded as the shipping surface

`anonsync_core` links self-test implementation libraries and is approximately 29 MiB in this Debug build. The newer replica stack had no product TLS client. Rev0895 creates a separate product binary instead of attaching another mode to the diagnostic aggregation.

**Correction over time:** keep `anonsync_core` explicitly diagnostic; move operational commands to `anonsync_replica`; prevent self-test libraries from entering the product link graph; eventually rename or install the binaries in ways that make the distinction unmistakable.

### 3. Two synchronization architectures coexist

The giant legacy `sync_domain`/runner/CLI path and the newer `sync_replica_*` kernel overlap conceptually. Parallel implementations multiply invariant vocabulary, test burden, and uncertainty about which path is authoritative.

**Correction over time:** define a migration ledger. For each legacy capability, mark it as product-required, diagnostic-only, superseded, or pending replacement. New production behavior should target the replica spine. Delete superseded code only after process-level parity evidence exists.

### 4. Translation-unit and target fragmentation

Current observed shape after rev0895:

- about 116,000 production C/C++ lines across 239 source/header files;
- about 179,000 C/C++ lines including tests and fuzz sources;
- a 4,057-line `CMakeLists.txt`;
- 88 `add_library` calls, 102 `add_executable` calls, 185 `target_link_libraries` calls, and 217 textual `add_test` calls;
- more than 400 Ninja actions for the existing Debug graph; and
- giant files including `src/sync_domain.cpp` at roughly 15,000 lines.

Small static libraries can express ownership, but dozens of one-file archives and a huge central CMake file impose build and review cost. Conversely, giant translation units make narrow changes rebuild too much. Both extremes are present.

**Correction over time:** organize a small number of cohesive component libraries with explicit internal headers; split giant translation units without creating a new archive per file; generate repetitive test registration from data; use target graph metrics in review; and measure clean/incremental build time before and after refactors.

### 5. Public API and state-vocabulary overload

`include/anonsync_core.hpp` is about 3,544 lines with roughly 134 struct/class definitions, nearly 600 `bool` tokens, and many epoch-like fields. Large flat result documents with many booleans make impossible combinations easy to represent and hard to review.

**Correction over time:** replace groups of booleans with discriminated terminal states; separate immutable identity, evidence, and diagnostics; move internal types out of the public aggregate; use typestate/move-only continuations only at true authority frontiers, not as vocabulary inflation.

### 6. Evidence retention became a second product

`REVISION_EVIDENCE` contains roughly 5,353 files and 50 MB in the imported tree. The Python tools contain roughly 39,000 lines. Evidence is valuable, but the volume makes review, package size, and trust harder. Many lexical audits assert exact token inventories; rev0895's new legitimate consumers caused three full-suite failures until the audits were retargeted.

**Correction over time:** retain compact machine summaries, source/changeset digests, and the few logs needed to substantiate claims. Store large raw logs externally by digest. Replace exact-count lexical audits with AST/link/runtime checks where feasible. Every audit should state its false-positive and false-negative boundary. Avoid adding an audit for every new class.

### 7. README revision drift

The package imported as rev0894 still began with `# AnonSync rev0892`. Release notes and gates were newer, but the main entry point lagged. This is a small edit with a large trust impact: readers cannot know which narrative is current.

**Correction:** rev0895 updates the heading and adds a current product-spine section. Future packaging should verify that the README's declared revision matches `RELEASE_GATE.json`.

### 8. Bootstrap and process assumptions were under-tested

Genesis membership, request-frame sizing, and clock authority all worked in focused library fixtures but failed when separate product processes were used. This is not a failure of the lower-level proofs; it shows that composition has independent invariants.

**Correction:** every newly claimed product command should have a clean-directory process test, including genesis, restart, malformed configuration, and deadline behavior.

## Research comparison

### Syncthing Block Exchange Protocol

Syncthing's BEP specifies TLS 1.3 or later, certificate-based authentication, certificate fingerprints as device identities in the reference implementation, explicit file metadata, tombstones, version vectors, block requests/responses, and bounded block sizes. This supports AnonSync's current TLS 1.3 + SPKI identity baseline and highlights the next semantic gaps: file type, deletion, symlink, block/chunk, and ongoing index exchange.

AnonSync should not copy BEP's state model blindly. Its own differentiator is stronger authority accounting around durable causal evidence, effects, and receipts. BEP is most useful as an interoperability-shaped checklist of product semantics that mature file synchronization requires.

### Willow Confidential Sync and private interest overlap

Willow explicitly targets partial synchronization, capability-enforced read access, private discovery of overlapping namespaces/areas, resource limits, and transport independence. This is the most relevant current reference for defining the missing “Anon” mission. It demonstrates that encrypted transport alone does not hide folder IDs, paths, interests, or non-overlapping data.

A future AnonSync privacy layer could adopt the design principle—capability-authorized private overlap—without adopting Willow's data model. The authority kernel should receive an immutable capability-derived area projection; privacy negotiation should not bypass causal or effect rules.

### Noise Protocol Framework

Noise provides a disciplined framework for authenticated key exchange, bounded messages, channel binding, and several identity-hiding handshake patterns. Its own specification warns that handshake identity hiding does not hide IP addresses, traffic patterns, or identities leaked by application payloads.

AnonSync should keep TLS 1.3 as the reviewed production baseline. A Noise profile is justified only after a threat model requires handshake identity-hiding properties TLS/SPKI does not provide. Replacing transport now would create risk without solving path, interest, timing, or endpoint metadata.

### Messaging Layer Security

MLS specifies asynchronous group key establishment with epochs, authenticated membership changes, forward secrecy, and post-compromise security. These are useful concepts for future membership/key evolution. MLS does not define filesystem causality, payload reachability, side effects, or retry/receipt authority, so it should remain a separate cryptographic layer or source of design patterns.

### Local-first software

The local-first literature emphasizes offline operation, collaboration, longevity, security/privacy, and user ownership. AnonSync's durable local authority and deterministic convergence fit that direction. The project is currently much stronger on low-level correctness than on the user-visible local-first experience: background synchronization, understandable status, conflict presentation, recovery, and long-term data portability are missing.

### SLSA provenance

SLSA treats provenance as an attestation binding an artifact to its build platform, inputs, and process, and recommends artifact-bound verification. This reinforces a distinction AnonSync should make more clearly: in-tree manifests and validation logs are useful release evidence, but they are generated within the same trust domain as the source package. External signed provenance is a separate future property.

## Speculation: what “AnonSync” should become

The following is design speculation, not an implementation claim.

### Proposed mission sentence

> AnonSync is a local-first, capability-authorized replication engine that converges exact causal evidence and filesystem effects while minimizing disclosure of identity, interests, and metadata to the least required by each peer relationship.

### Layering proposal

1. **Authority kernel:** exact operations, evidence, membership generations, payload identity, effects, receipts, and deterministic projection.
2. **Replica runtime:** durable peer loop, scheduling, quotas, status, recovery, checkpoints, index and GC.
3. **Disclosure policy:** capability-scoped folders/areas, path/name transforms where feasible, private overlap discovery, metadata budgets.
4. **Transport profiles:** direct TLS/SPKI baseline; optional relay/onion/oblivious profile when endpoint privacy is required; possible identity-hiding handshake profile only with a concrete threat model.
5. **User model:** conflict/status/recovery UX and exportable local data.

This separation prevents “anonymous transport” from contaminating the authority kernel and prevents the kernel's exact identity needs from forcing unnecessary identity disclosure on the wire.

### Privacy budgets as first-class evidence

A promising AnonSync-specific idea is to treat disclosure as another bounded capability. A peer session could carry an immutable budget describing which folder/area identifiers, path prefixes, sizes, timestamps, and membership facts may be revealed. Protocol encoders would consume only that capability. This aligns privacy with the project's existing ownership style instead of adding ad hoc redaction later.

### Keep the full-history oracle, but add verified checkpoints

“Exact history is authority” need not mean every process replays all history forever. A checkpoint can be authoritative if it is itself an immutable, domain-separated statement over an exact source frontier, signed or otherwise anchored, with retained proof sufficient to reject forks and rebuild indexes. The project should define checkpoint authority explicitly rather than allowing performance pressure to turn an index into truth accidentally.

## Recommended roadmap

### Rev0896–rev0898: operational spine

- Acquire and verify SQLite 3.53.4; update exact pins and run the full corpus.
- Add `status` and explicit clock-quarantine `recover` commands.
- Add a bounded multi-peer loop that invokes one-shot send/serve owners.
- Persist scheduler decisions, backoff, and terminal reasons without treating counters as authority.
- Add restart/process tests for ambiguous claims, listener shutdown, membership rotation, and expired deadlines.
- Keep the new README/gate/artifact/ZIP filename agreement check in every later release.

### Rev0899–rev0902: filesystem semantics

- Model directories and tombstones as causal operations.
- Define rename as identity-preserving move, delete+create, or an explicit operation, and test concurrent cases.
- Define symlink and permission policy by platform.
- Add conflict projection and operator-visible explanations.
- Introduce chunked payload transfer only after content identity and receipt semantics are preserved at the chunk frontier.

### Rev0903–rev0906: scale without surrendering the oracle

- Define exact reachability roots and retention windows.
- Implement dry-run and crash-safe GC.
- Add a separately owned indexed catalog and differential oracle tests.
- Add verified checkpoints/compaction and rebuild tests.
- Reduce CMake/target fragmentation and split giant translation units with measured build improvements.

### Later: privacy and key evolution

- Publish the privacy threat model and metadata inventory.
- Prototype capability-scoped partial sync and private overlap discovery.
- Design membership key rotation and compromise recovery, informed by MLS but separate from file semantics.
- Evaluate an identity-hiding or relay transport profile only against explicit threats and measurable leakage.
- Add external artifact-bound build provenance.

## Explicit nonclaims for rev0895

Rev0895 does not claim a production daemon; continuous/background synchronization; discovery; NAT traversal; scheduler fairness; clock attestation; automatic clock-quarantine recovery; directory creation semantics; tombstones; rename/symlink/permission convergence; chunked transfer; reachability; garbage collection; indexed performance; bounded retained-history growth; cross-resource atomicity; exactly-once network delivery; at-rest encryption; capability-private partial sync; anonymity; unlinkability; endpoint hiding; traffic-analysis resistance; forward secrecy or post-compromise security beyond the properties supplied by the configured TLS session; hostile same-UID/privileged-writer resistance; universal network-filesystem semantics; Windows runtime coverage; external signed build provenance; or formal proof.

## Primary sources consulted

Accessed 2026-07-25.

- SQLite 3.53.4 release log: https://sqlite.org/releaselog/3_53_4.html
- SQLite download page and published archive hashes: https://sqlite.org/download.html
- Syncthing Block Exchange Protocol v1: https://docs.syncthing.net/specs/bep-v1.html
- Willow Confidential Sync: https://willowprotocol.org/specs/confidential-sync/index.html
- Willow Read Access and Confidentiality / Private Interest Overlap: https://willowprotocol.org/specs/pio/index.html
- Noise Protocol Framework: https://noiseprotocol.org/noise.html
- RFC 9420, Messaging Layer Security: https://www.rfc-editor.org/rfc/rfc9420.html
- Local-first software: https://www.inkandswitch.com/essay/local-first/
- SLSA v1.2 Build Provenance: https://slsa.dev/spec/v1.2/build-provenance
- SLSA v1.2 Distributing Provenance: https://slsa.dev/spec/v1.2/distributing-provenance

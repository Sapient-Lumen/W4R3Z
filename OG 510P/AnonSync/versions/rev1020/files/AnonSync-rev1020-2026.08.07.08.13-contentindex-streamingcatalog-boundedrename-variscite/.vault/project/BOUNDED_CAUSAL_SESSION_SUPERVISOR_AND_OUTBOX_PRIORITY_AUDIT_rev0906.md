# AnonSync rev0906 bounded causal session supervisor and outbox priority audit

**Assessment date:** 2026-07-26  
**Scope:** deep source and lineage review, a bounded C++ product-spine increment,
clean GCC and Clang builds, the complete registered test suite, focused
ASan/UBSan execution, parent-package verification, primary-source research, and
explicitly labeled speculation.

## Executive verdict

AnonSync's heart is **authority-preserving convergence**. It is not trying to be
merely a faster file copier. Its strongest and most coherent invariant is:

> Exact history is authority; summaries are acceleration.

An authorized observation becomes an immutable, identity-bearing operation.
Durable causal history and explicit live capabilities decide what exists, who
may act, what may be retried, which remote result is acceptable, and when bytes
may become visible. Projections, indexes, clocks, leases, receipts, pathnames,
TLS sessions, counters, and reports are allowed to coordinate and verify work,
but they may not silently acquire authority beyond the exact evidence and
cutpoint from which they were derived.

That mission is unusually rigorous and worth preserving. The project already
contains substantial C++ machinery for bounded resource policy, causal
operations, SQLite ownership, crash cutpoints, durable payload storage,
authenticated transport, receiver effects, receipt-bound settlement, and
forensic observation. The strategic problem is not a lack of primitives. It is
that the proof surface has repeatedly grown faster than the product loop.

Rev0906 adds one missing product layer: a bounded multi-session sender and
receiver supervisor over the existing one-session authority owners. It also
corrects a liveness defect exposed by the new process test: canonical digest
order had accidentally become dispatch priority. A causally later operation
could be sent first, receive authenticated `receiver_evidence_pending`, be
released, and then be selected first again. That could deterministically starve
its predecessor. Dispatch now chooses the oldest durable generation while
canonical digest order remains unchanged for attestation.

This is a real vertical increment, not a daemon. A continuous
scan/exchange/transfer/effect/repair/retention owner remains the largest missing
piece.

## What rev0906 implements

### Bounded sender supervisor

`anonsync_replica send-batch --max-sessions N` now executes up to `N` authenticated
one-delivery sessions in one process, with `N` required to be in `[1, 256]`.
The command owns one:

- parsed deployment manifest and fixed peer endpoint;
- existing-only database authority set;
- immutable payload inventory snapshot;
- client TLS context and expected peer identity; and
- bounded sequence of fresh per-session staged absolute deadlines.

The supervisor does not add a second claim, receipt, payload, TLS, or clock
implementation. `send-one` and `send-batch` delegate to the same executor;
`send-one` simply sets the bound to one and retains its previous output and exit
semantics.

The aggregate JSON result records the configured bound, sessions attempted,
receipts applied, settled and deferred deliveries, stop reason, and every
session result. The sender stops on:

- the explicit session bound;
- no ready delivery;
- one authenticated receiver-deferred receipt;
- local receipt/claim conflict; or
- transport/session failure.

Receiver deferral is bounded progress, not authority to spin. The exact claim is
released by existing service semantics and the process exits successfully
without sleep, backoff, or an invented retry loop. Local ambiguity and transport
failure remain fail-closed errors.

### Bounded receiver supervisor

`anonsync_replica serve-batch --max-sessions N` accepts up to `N` authenticated
sessions through one listener and one retained TLS/store authority set. It
resolves anchored membership before opening the later stores for the first
session, then refreshes membership authority before each subsequent accepted
session. Each session still uses the proven one-session receiver service and a
fresh staged deadline set.

`serve-one` delegates to that executor with a bound of one. Listener timeout is
a successful bounded stop; session failure is an error. The revision does not
invent an unbounded accept loop, background worker pool, automatic restart,
retry authority, or daemon lifecycle.

### Dispatch priority is no longer attestation order

`read_outbox_or_throw()` intentionally retains the canonical order
`destination_device_id, operation_id`. That order is useful for deterministic
state attestation and must not be changed merely to influence scheduling.

`claim_next_outbox_impl_or_throw()` now evaluates every matching claimable
candidate, preserves pre-lease wire and payload policy validation, filters by
available payload inventory, and chooses the available candidate by:

1. smallest `enqueued_generation`;
2. destination device ID; then
3. operation ID.

This separates two concepts that had been accidentally coupled:

- **canonical order**, which makes equivalent durable state attest identically;
- **dispatch order**, which should make causal and operational progress.

The first version of this repair moved permanent payload-policy validation too
late. The complete registry caught the regression: an oversized committed
payload could be bypassed when another candidate was selected. Rev0906 restores
the prior fail-closed rule that every matching claimable candidate must satisfy
permanent delivery policy before any lease is minted, while still selecting the
oldest policy-valid available candidate.

### Process-level proof

The existing real TCP/TLS two-process test now enqueues two causally ordered
files, starts one `serve-batch --max-sessions 2`, and starts one
`send-batch --max-sessions 2`. It proves:

- invalid bounds `0` and `257` are rejected;
- exactly two client and two server sessions execute;
- both authenticated receipts are applied and both claims settle;
- the operations traverse in durable enqueue chronology;
- request and receipt frame lengths are exact;
- peer and receipt metadata match the intended authorities; and
- both destination files contain the exact expected bytes.

A focused SQLite-owner test constructs operation IDs until lexical digest order
conflicts with enqueue chronology, then proves the first durable generation is
claimed and settled before the second.

## Heart of the mission, made operational

Rev0906 reinforces six mission rules.

### 1. Authority must be explicit

The batch bound is supplied by the operator. A receiver-deferred result does not
become permission to retry forever, and a timeout does not become permission to
extend a session invisibly.

### 2. One authority path is safer than parallel convenience paths

The one-session commands and batch commands share executors. Batch composition
reuses the existing database, payload, TLS, claim, effect, and receipt owners
instead of reimplementing them.

### 3. Canonical representation must not silently become policy

Sorting by hashes is excellent for reproducible attestation and arbitrary as a
causal scheduler. Rev0906 makes that distinction executable.

### 4. Durable chronology is stronger than process-local convenience

`enqueued_generation` is committed state. It survives restart and provides a
stable priority tie to the cutpoint that created the outbox intent.

### 5. Bounded progress is preferable to pressure amplification

A batch handles a declared number of sessions and stops. It does not contain an
internal sleep/retry/backoff loop that could amplify a remote deferral, local
conflict, or network failure.

### 6. Negative evidence is part of engineering

The initial full-suite regression was not hidden. It demonstrated that scheduler
refactoring can weaken fail-closed policy even when the happy-path process test
passes. The final implementation retains both causal priority and pre-lease
policy rejection.

## What is still missing

### P0: one durable causal product loop

The project still lacks one owner that continuously joins:

1. authorized filesystem discovery;
2. operation/evidence minting;
3. catalog reconciliation and peer-interest negotiation;
4. bounded scheduling and transport;
5. durable effect application;
6. receipt settlement and repair;
7. quarantine and operator recovery; and
8. reachability, retention, and garbage collection.

Rev0906 supplies a bounded transport drain/accept layer, not that whole state
machine. The next product increment should make the phases and terminal states
explicit rather than place an infinite `while` loop around these commands.

### P0: complete filesystem semantics

The current product slice is narrow file delivery. A usable synchronization
system still needs evidence-bearing semantics for directories, deletion and
tombstones, rename/move, file-versus-directory conflicts, symbolic links,
permissions and executable bits, case-folding, Unicode normalization,
platform-forbidden names, and parent creation. Recursive convenience operations
must not invent filesystem state that no operation authorized.

### P0/P1: scalable catalog and anti-entropy

Full-history reconstruction is a valuable correctness oracle and a poor sole
production query plan. Add a separately derived indexed catalog, range or Merkle
summaries, checkpoint generations, and differential verification against the
exact-history oracle. An index miss must never independently authorize deletion
or forget retained evidence.

### P1: retention and garbage collection

The project needs a formal definition of reachability across active operations,
receipts, outbox claims, tombstones, delayed peers, repair windows, membership
changes, and rollback windows. A safe implementation should include a full-scan
oracle, explicit retention epochs/watermarks, a dry-run proof, a crash-safe
deletion queue, and tests where old or partitioned peers return.

### P1: a production scheduler and lifecycle owner

The batch supervisor deliberately omits fairness between peers, quotas, jitter,
backoff, graceful shutdown, signal handling, listener rotation, certificate and
membership rotation, durable next-attempt time, health/metrics, and restart
recovery. Those policies should be a typed scheduler authority around the
one-session services, not hidden inside transport code.

The batch is also bounded by session count, not one command-wide wall-clock
budget. Total runtime may approach the sum of each session's staged deadlines.
A later supervisor should own both a work bound and an absolute command/epoch
budget.

### P1: cross-store cutpoints

The stores have strong individual transactional behavior, but there is no
atomic transaction across replica, payload, effect, membership, and anchor
stores. `status` is intentionally non-mutating but is not an atomic multi-store
snapshot. Cross-store protocols need explicit prepare/commit/recovery evidence
rather than a claim that several independent SQLite transactions are one
transaction.

### P1/P2: privacy meaning of “Anon”

Mutual TLS and pinned identity provide channel confidentiality and peer
authentication. They do not establish anonymity, unlinkability, private
interest discovery, endpoint hiding, traffic-analysis resistance, or at-rest
confidentiality. The project needs a threat model answering anonymous from whom,
which metadata is protected, which actors may link sessions, and how abuse,
revocation, audit, and recovery interact with hidden identity.

### P2: key lifecycle and compromise recovery

Long-lived peer or group relationships need explicit key rotation, member
removal, stale-key rejection, epoch evolution, and recovery after compromise.
This should be a separate authority plane; it should not be inferred from a live
TLS socket or bolted onto file-operation semantics.

### P2: dependency update and platform breadth

The source remains on bundled SQLite 3.53.3. SQLite published 3.53.4 on
2026-07-24. Its official release record and archive hashes were identified, but
the cloudtainer could not import the archive bytes through its permitted media
bridge. Rev0906 therefore leaves the dependency unchanged rather than introduce
unverifiable bytes. The update should be an isolated revision that repeats all
VFS, WAL, crash, corruption, process, sanitizer, and package lanes.

Descriptor-rooted and anonymous-WAL mechanisms remain Linux-specific. Native
non-Linux authority needs separate designs rather than emulation claims.

## Places where the project went severely wrong or became wasteful

### 1. Canonical hash order became dispatch authority

This was the concrete severe defect fixed in rev0906. The outbox's canonical
attestation order was iterated as the scheduling order. SHA-256 lexical order
has no causal meaning. When a child sorted before its predecessor, the receiver
correctly deferred the child, but the sender could select that same child again
and starve the predecessor. The fix separates attestation from scheduling.

### 2. Assurance/product inversion

The repository has exceptional local authority proofs but still lacks the
continuous product loop those proofs are intended to support. Assurance is not
the problem; the allocation of effort is. A practical governance rule would
require a process-level product increment after a small number of local
hardening revisions unless a documented blocker prevents it.

### 3. Two synchronization architectures coexist

The large legacy `sync_domain`/runner path and the newer `sync_replica_*` path
both express synchronization concepts. Parallel architectures multiply
vocabulary, invariants, tests, and uncertainty about the shipping authority.
Create a migration ledger that marks every legacy capability as required,
diagnostic-only, superseded, or pending replacement. New operational behavior
should target `anonsync_replica`; deletion should follow process-level parity,
not precede it.

### 4. Both giant translation units and target fragmentation

Observed starting rev0906 shape includes:

- `src/sync_domain.cpp`: 15,167 lines and about 1.11 MB;
- `src/sync_replica_sqlite_owner.cpp`: about 4,000 lines;
- `src/anonsync_replica.cpp`: about 3,600 lines after this revision;
- `src/runner.cpp`: 2,558 lines and about 214 KB;
- `CMakeLists.txt`: 4,282 lines and about 218 KB;
- 93 textual `add_library`, 105 `add_executable`, 229 `add_test`, and 193
  `target_link_libraries` declarations.

Small targets can express authority boundaries, but hundreds of targets and one
central CMake file impose clean-build, incremental-build, and review cost.
Giant files impose the opposite cost. Refactor by authority domains into a
small number of cohesive components, generate repetitive test registration from
data, and measure target count plus clean/incremental build time before and
after each structural change.

### 5. Evidence retention has become a second product

Before adding rev0906 evidence, `REVISION_EVIDENCE` already contained about
5,600 files and 54 MB, while Python tools were roughly 45,000 lines. The
historical record is valuable, but carrying every raw log in every descendant
archive makes review and trust harder. Retain compact machine summaries and the
few decisive transcripts in-package; keep large raw logs externally by digest
when an external evidence store exists. Prefer semantic/runtime checks over
fragile token counts, and document each audit's false-positive/false-negative
boundary.

### 6. Public state vocabulary is overloaded

Many APIs and JSON records carry broad groups of booleans and disposition
strings. Impossible combinations are easy to represent. Use discriminated
terminal states and typed continuations at real authority frontiers; separate
identity/evidence from diagnostics; and avoid adding another boolean each time a
new failure mode appears.

### 7. Fail-closed poison needs an operator path

Preserving pre-lease rejection means one permanently invalid durable candidate
can stop a matching claim attempt. That is safer than silently bypassing
corrupt or policy-incompatible evidence, but production needs an explicit
quarantine, explain, and authorized repair/remove workflow. Repeated command
failure must not be the only diagnostic surface.

## Research comparisons and informed speculation

### Syncthing: product loop and filesystem breadth

Syncthing's public design documents describe watcher-driven and periodic full
scans, block hashing, an index database, and a computed global version. That is
a useful comparison for the product machinery AnonSync still lacks. AnonSync's
potential differentiator is stronger exact-history authority and crash
attestation, not the basic ability to keep a daemon scanning and transferring.
The likely winning architecture is a production scheduler around a smaller
reference-correctness kernel, not one monolith that mixes both concerns.

### Willow: selective, bounded interest

Willow models entries across subspace, path, and time, and its areas of interest
can bound both entry count and total payload size. AnonSync currently has a
per-destination outbox but no protocol for selective or privacy-preserving
interest negotiation. A future catalog exchange could borrow the *shape* of
bounded areas—without importing Willow wholesale—so peers disclose only an
authorized overlap and explicit resource budget.

### Noise: channel patterns are not anonymity

Noise demonstrates that transport handshakes can offer optional/mutual
authentication, identity-hiding patterns, and forward secrecy, while its own
specification warns that payloads, traffic analysis, and IP metadata can still
expose identity. This supports a strict separation in AnonSync between channel
correctness, identity disclosure policy, private interest negotiation, and an
optional outer traffic/endpoint layer.

### MLS: key evolution is a separate state machine

RFC 9420 defines asynchronous group key establishment with forward secrecy and
post-compromise security. MLS is not a file synchronization protocol, but its
epoch and membership-change model is evidence that group key lifecycle deserves
its own explicit state machine. If AnonSync expands beyond fixed pairwise peers,
file operations should reference an authorized key/membership epoch rather than
implicitly treating current TLS membership as eternal.

### Speculative next architecture

A high-leverage design would retain the immutable evidence DAG and full-history
oracle as the normative correctness kernel, then add:

1. a rebuildable Merkle/range catalog tied to exact source generations;
2. bounded private-interest exchange;
3. a typed supervisor state machine with durable scheduling decisions;
4. explicit dependency/topological readiness rather than generation alone;
5. separate content-key epochs and membership/key recovery; and
6. differential tests that continuously compare every fast path with the oracle.

Oldest durable generation is the correct repair for the observed local causal
starvation. It is not a general topological scheduler for arbitrary imported
DAGs. The next scheduler should make dependency readiness explicit and use
generation only as a fairness/tie-break signal.

## Validation performed

- Clean GCC 14.2 Debug build: complete target graph compiled and linked.
- GCC 14.2 Debug registered registry: **226/226 passed**.
- Clean Clang 17.0 Debug build: complete target graph compiled and linked.
- Clang 17.0 Debug registered registry: **226/226 passed**.
- Clang 17 ASan+UBSan focused lane: SQLite owner, file-delivery service, and
  real multi-process TLS spine, **3/3 passed** with leak detection and
  halt-on-first-error settings.
- Focused SQLite owner result: **250 checks passed**.
- Deployment-binding source audit: **27/27 passed**.
- Database-open policy audit: **38/38 passed**.
- Bootstrap-authority source audit: **25/25 passed**.
- Parent rev0905 package: **32/32 checks passed** under the current verifier.

The first complete GCC registry exposed the oversized-payload regression and two
source-audit assumptions made stale by executor sharing. Those issues were
corrected before the clean final GCC, Clang, and sanitizer results above.

## Explicit nonclaims

Rev0906 does not claim:

- a daemon, service manager integration, background worker pool, retry/backoff
  engine, or graceful-shutdown lifecycle;
- a continuous scan/exchange/repair/retention loop;
- complete filesystem synchronization semantics;
- a command-wide absolute runtime bound beyond per-session staged deadlines and
  the session-count cap;
- a general topological scheduler for arbitrary evidence DAGs;
- atomicity across all stores or an atomic multi-store status snapshot;
- at-rest encryption, key rotation, forward secrecy or post-compromise security
  for stored content/history;
- anonymity, unlinkability, private interests, endpoint hiding, or
  traffic-analysis resistance;
- safe garbage collection, scalable indexed anti-entropy, or production
  retention policy;
- native non-Linux descriptor-rooted behavior;
- ThreadSanitizer coverage, formal proof, external signed provenance, or defense
  against hostile root/in-process code; or
- SQLite 3.53.4 integration.

## Recommended next implementation order

1. Add a typed, durable supervisor epoch: scan, mint, reconcile, schedule,
   transfer, apply, repair, and retain, each with explicit terminal outcomes.
2. Add directory/tombstone/rename semantics and their process-level tests.
3. Add a rebuildable indexed catalog and continuously differential-test it
   against the exact-history oracle.
4. Add quarantine/explain/authorized-repair operations for permanently invalid
   durable work.
5. Isolate and verify the SQLite 3.53.4 dependency update when trusted bytes can
   enter the cloudtainer.
6. Write the privacy and key-lifecycle threat models before choosing additional
   cryptography or routing technology.
7. Begin a measured legacy-architecture and build-graph consolidation after the
   new replica spine reaches functional parity.

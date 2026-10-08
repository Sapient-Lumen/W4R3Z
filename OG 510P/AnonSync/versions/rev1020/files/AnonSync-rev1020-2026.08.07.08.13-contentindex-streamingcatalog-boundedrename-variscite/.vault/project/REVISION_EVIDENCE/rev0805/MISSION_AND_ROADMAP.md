# AnonSync mission audit and implementation roadmap

## Mission in one sentence

AnonSync should make every replicated state transition carry sufficient,
owner-verified evidence to remain safe under concurrency, replay, crash,
compromise, and partial failure—and should prove that the authorized transitions
converge without confusing observation, identity, freshness, or a digest with
authority.

## What the repository is becoming

The name suggests a file synchronizer, but the C++ implementation is more
ambitious. It is becoming a kernel for **evidence-authorized state transition**:

1. normalize and bind inputs to exact bytes and policy;
2. prove process, owner-generation, schema, transaction, and lifetime authority;
3. reject replay, stale identity, capability aliasing, and malformed storage;
4. make durable effects idempotent and recoverable; and
5. eventually reconcile independent replicas under a stated convergence model.

That ordering matters. A replica protocol that converges to unauthorized state
is wrong. A perfectly authenticated operation that does not converge is also
wrong. Authentication, persistence, convergence, confidentiality, and anonymity
are separate properties and must have separate proofs.

## Current strengths

The codebase has unusually explicit local authority work:

- process-incarnation checks rather than PID-only assumptions;
- owner-generation borrows for SQLite handle lifetimes;
- source-first transfer and callback reentry fences;
- exact scalar, row, schema, geometry, and projection boundaries;
- transaction and replay-ledger capabilities;
- path and sidecar binding checks;
- bounded verification and progress controls;
- signed transitions, effect outboxes, receipts, and recovery corpora; and
- release evidence that binds active implementation bytes to a manifest.

These are the foundation of the mission. They should not be discarded in favor
of a generic synchronization framework.

## Current proof map

| Property | Current evidence | Current limit |
|---|---|---|
| Local SQLite ownership | process/generation/borrow/fence tests | raw API paths remain broad |
| Input and schema exactness | typed scalar/projection/schema boundaries | not every call site uses them |
| Replay/idempotency | ledger and effect diagnostics | no complete distributed model |
| Local durability | WAL/snapshot/restore corpora | no exhaustive crash-cut oracle |
| Release integrity | manifest and active projection | tests can still drift unless audited |
| Convergence | domain mechanisms and deterministic tests | no algebra/reference model |
| Remote transport | local transport fixtures | no production remote secure transport |
| Payload confidentiality | signatures/HMAC are present | no demonstrated payload-encryption protocol |
| Anonymity/metadata privacy | not specified | no threat/leakage model |
| Hostile database containment | in-process budgets and hardening | no disposable OS sandbox worker |

## What went severely wrong

### 1. The release gate proved a subset and presented it as the surface

The binary advertised 38 selftests, CMake registered 27, and the release
reported 67/67. Two omitted security diagnostics were broken. This is the most
important rev0805 finding because it was a failure of proof composition: every
individual statement was syntactically plausible while the overall conclusion
was too strong.

Correction: make the binary's advertised set and the build system's registered
set machine-comparable, register every public diagnostic, and treat drift as a
failing test.

### 2. A production hardening change invalidated adversarial fixtures

Foreign-key enforcement correctly prevented test code from manufacturing
inconsistent state on a production connection. The fixture failed, not the
production invariant.

Correction: explicitly model hostile/offline mutation as a test-only authority
on a separate connection. Never weaken runtime invariants to satisfy a corpus.

### 3. Runtime consumers carried thousands of lines of diagnostic machinery

A test-support translation unit was part of the production static library. That
inflated every runtime consumer and made full instrumentation more expensive.

Correction: keep production reporting small, put diagnostics in a one-way
support library, and guard the source lists.

### 4. The runtime API advertised implementation diagnostics

Thirty-nine selftests were declared in the public runtime header, including one
entry with no definition or caller.

Correction: an explicit test API with declaration/definition parity and a
runtime header containing zero diagnostics.

## What is still wasteful

### Monolithic translation units

`sync_domain.cpp` is 24,531 lines. Its first selftest entry begins at line
15,811, leaving an 8,721-line diagnostic tail in a production translation unit.
`sqlite_replay_ledger.cpp` has a 908-line selftest tail. These structures slow
incremental builds, multiply sanitizer memory, hide ownership boundaries, and
make review less local.

The correct split is not “every 500 lines.” Split by invariant owner:

- data model and canonical identity;
- operation validation;
- reconciliation algebra;
- filesystem effect planning;
- checkpoint/receipt semantics;
- generated trace harnesses; and
- deterministic corpora.

### Broad public header

`include/anonsync_core.hpp` remains 3,455 lines and 168,102 bytes. It is a large
compile dependency and mixes many domains. Migrate consumers toward focused
headers, but preserve one compatibility facade until dependency graphs prove
that downstream callers no longer require it.

### Raw SQLite surface

A lexical scan finds 751 `sqlite3_*(` call sites in source. A count cannot tell
which are legitimate boundary owners, but it is a useful migration inventory.
Every direct call should eventually be categorized as:

- invariant owner: permitted and tested;
- compatibility bridge: scheduled for migration;
- test-only fixture: moved behind test API; or
- accidental bypass: corrected immediately.

### Revision archaeology in active code

There are 284 revision-token occurrences and 55 revision-needle comment lines
in active first-party files. Historical needles should move into evidence or a
machine-readable invariant registry. Active code should say what the invariant
is, not preserve every old grep phrase.

### Fuzz naming and coverage

Three binaries named `anonsync_fuzz_*` are deterministic corpus wrappers. The
project also has two actual coverage-guided targets. Rename or clearly label the
legacy wrappers, then build coverage-guided targets for:

- complete wire framing and canonicalization;
- stateful replay-ledger sequences;
- SQLite hostile-schema and hostile-row interpretation;
- recovery manifest/sidecar combinations;
- domain reconciliation operations; and
- process-generation/lifetime transition sequences.

## Recommended execution order

### P0-A — convergence reference model

Create a small independent model, preferably in a separate C++ target with a
minimal data representation. For every operation, record:

```text
operation_id
preconditions
identity/evidence inputs
causal dependencies
join/merge rule
idempotency rule
conflict rule
retraction/tombstone rule
epoch/schema compatibility
external effects
```

Generate traces with duplicate delivery, omission, reordering, partitions,
concurrent edits, update/delete races, stale devices, restart, and key/schema
epoch changes. Run the same trace against the model and production
implementation, then compare canonical states and effect obligations.

Exit condition: a documented operation matrix and a CTest target that explores
generated traces and shrinks failures.

### P0-B — crash-cut protocol oracle

Implement a custom SQLite VFS or focused wrapper layer that can enumerate and
fault:

- open/close;
- read/write;
- truncate;
- sync;
- lock/unlock;
- file-control boundaries;
- WAL/journal visibility;
- sidecar creation;
- temp/staging publication; and
- rename/directory-sync edges outside SQLite.

Each scenario should run in a separate child process that can be killed without
cleanup. The parent restarts the exact artifact set and asks both SQLite and the
domain model whether recovery is permitted.

Exit condition: cut-point coverage is enumerated, every surviving result is
either a committed allowed state or a rolled-back allowed state, and no receipt,
checkpoint, sidecar, or filesystem publication contradicts the database.

### P0-C — hostile SQLite worker

Create a narrow worker executable:

```text
parent -> immutable input descriptor + policy + budget
worker -> typed result or typed failure
```

The worker should not receive live application database handles, network
sockets, secrets unrelated to verification, or writable paths beyond a private
temporary directory. Apply rlimits, no-new-privileges, a syscall allowlist,
Landlock where available, minimal environment/fds, and a parent wall-clock
kill. Treat unsupported sandbox layers as explicit capability outcomes, not
silent success.

Exit condition: malformed databases cannot exhaust or corrupt the long-lived
parent, and every result is reproducible from a bounded worker transcript.

### P0-D — privacy and key lifecycle specification

Before selecting a protocol, write a table of adversaries and observations:

| Adversary | Payload | Path/name | Size/timing | Membership/topology | Device keys | Local state |
|---|---|---|---|---|---|---|
| Network observer | ? | ? | ? | ? | no | no |
| Relay/server | ? | ? | ? | ? | no | no |
| Malicious peer | ? | ? | ? | ? | peer scope | peer scope |
| Stolen device | historical/current? | ? | ? | ? | compromised | compromised |
| Later key compromise | historical/current? | ? | ? | ? | compromised | maybe |

Then define enrollment, authentication service, device identity, epochs,
rotation, revocation, recovery, forward secrecy, post-compromise recovery,
backup, and secure deletion. Only then choose TLS/QUIC, HPKE, MLS, pairwise
ratchets, or another construction.

Exit condition: every privacy claim maps to an adversary, leakage statement,
protocol mechanism, and executable test or formal argument.

### P1-A — extract domain selftests

Move the 8,721-line selftest tail out of `sync_domain.cpp` into the test-support
library without changing runtime semantics. Give it a focused test API and
build-graph audit. This is the highest-return compile-cost change now visible.

Exit condition: runtime consumers no longer compile the domain corpus, and the
same diagnostic checks pass through the CLI/test library.

### P1-B — isolate one production domain owner

After the test tail is gone, extract one production slice—preferably canonical
operation identity and precondition validation—behind a focused header and
library. Do not attempt a wholesale rewrite.

Exit condition: a no-core focused test, adversarial cases, and a measurable
reduction in the monolith's exposed lines.

### P1-C — typed SQLite migration ledger

Create a machine-readable inventory of the 751 lexical raw calls and assign an
owner/status. Fail CI when a new call appears without a classification. Migrate
highest-risk interpretation and lifetime sites first.

Exit condition: raw call count and unclassified count trend down; high-risk
paths have typed owners and focused tests.

### P1-D — production remote transport

Define a bounded versioned frame independent of source revision comments.
Separate transport security from application end-to-end protection. Add remote
loopback integration first, then a network namespace or two-process test, then
packet loss/reordering and reconnect traces.

Exit condition: two independent processes can authenticate, exchange bounded
frames, restart, replay, and converge under an explicit transport and privacy
contract.

### P2 — evidence DAG / delta anti-entropy experiment

A content-addressed evidence DAG or delta-state anti-entropy protocol could
reduce transfer and improve partial synchronization. This is promising only if:

- authorization does not collapse to “hash matches”;
- tombstones and retractions have explicit causal semantics;
- garbage collection preserves proof obligations;
- membership/key epochs are bound to operations; and
- differential convergence tests exist first.

Treat this as an experiment, not a replacement for the P0 model.

## Engineering rules for future cloudtainer revisions

1. Every public diagnostic is a registered gate or is explicitly marked
   non-gating in machine-readable metadata.
2. Every security fixture states which production invariant it intentionally
   bypasses and uses a separate test-only authority to do so.
3. Test support depends on runtime; runtime never depends on test support.
4. New invariant owners receive focused tests and no-core build guards.
5. Source-text audits are secondary drift guards, not substitutes for executable
   behavior or model-based testing.
6. Sanitizer claims state exactly which translation units and libraries were
   instrumented.
7. Privacy, convergence, durability, and authentication claims remain separate.
8. The release package binds active source bytes, exact lineage, all tests, and
   deliberate limits.

# AnonSync rev0805 — false-green closure, hostile-fixture authority, and runtime/selftest separation

## Lineage

Rev0805 is derived from the complete uploaded archive
`AnonSync-rev0804-2026.07.15.20.58-sourcefirst-schemapin-callbackfence-focusgraph(1).zip`,
SHA-256 `ddc449742935aaf6345ca8821dd61f631defb857cdf209fd3e458bb58f621b70`.
The archive passes **25/25** checks in its packaged release verifier and contains
42 production C++ implementation files, 30 production headers, and 28 test
implementation files. The archive is the byte-authoritative parent for this
revision; no recovered build directory was used as lineage input.

## Heart of the mission

AnonSync is an **evidence-authorized convergence engine**. Its deepest design
claim is not “synchronize files” and not merely “reject malformed input.” It is:

> Make every replicated state transition carry sufficient owner-verified
> evidence to be safe under concurrency, replay, crash, compromise, and partial
> failure; reject invalid authority before unrelated valid state is destroyed;
> then make the authorized transitions converge.

A successful syscall, callback, query, database open, row, pointer, PID,
signature, or commit is an observation. It becomes authority only when the
boundary that owns the relevant invariant verifies exact content, identity,
process incarnation, owner generation, lifetime, policy, relationship, schema,
resource budget, and durability evidence. Hashes, signatures, paths, handles,
and timestamps are evidence components, not universal authority tokens.

Rev0805 applies that rule to the release gate itself: a green subset is not
authority for the claim that every advertised diagnostic passed.

## Severe finding: 67/67 was false-green

The rev0804 CLI advertised 38 public `--selftest-*` modes. Its CMake gate
registered only 27 of them. The published **67/67 CTest** result was therefore a
correct count of the registered set but not a complete proof of the advertised
selftest surface.

The omitted diagnostics were:

1. `--selftest-boundary-fuzz`
2. `--selftest-fuzz-json`
3. `--selftest-ledger-backend-adapter`
4. `--selftest-ledger-backend-interface`
5. `--selftest-ledger-batch-transaction`
6. `--selftest-ledger-crash-injection`
7. `--selftest-ledger-durable-io`
8. `--selftest-ledger-journal-hardening`
9. `--selftest-ledger-sqlite-backup-restore`
10. `--selftest-ledger-sqlite-crash-corpus`
11. `--selftest-ledger-sqlite-hardening`

Running those 11 directly produced nine passes and two failures. The preserved
parent failures were:

```text
ledger sqlite hardening selftest exception: sqlite hardening raw exec failed:
FOREIGN KEY constraint failed ...
anonsync_core ledger sqlite hardening selftest passed=3 failed=1
```

```text
ledger sqlite crash corpus selftest exception: sqlite crash corpus raw exec failed:
FOREIGN KEY constraint failed ...
anonsync_core ledger sqlite crash corpus selftest passed=9 failed=1
```

This was not a reason to weaken the production database. Foreign-key
enforcement was doing exactly what the runtime boundary required. The tests had
drifted: they attempted to construct an intentionally inconsistent database by
issuing hostile mutations through a connection whose production invariants
forbade that inconsistency.

### Correction: explicit hostile/offline mutation authority

`reporting_selftests.cpp` now owns a shared test-only helper that:

1. opens a separate read/write SQLite connection to the fixture path;
2. executes `PRAGMA foreign_keys=OFF` only on that hostile connection;
3. reads back and verifies the exact scalar pragma value;
4. executes the requested hostile mutation with contextual errors; and
5. closes the hostile connection before the production verifier reopens or
   inspects the database.

The production connection profile and foreign-key enforcement remain unchanged.
The distinction is explicit: production code verifies a hostile artifact; test
support is authorized to manufacture that artifact in a separate offline
connection.

The repaired results are:

- SQLite hardening: **12 passed / 0 failed**;
- SQLite crash corpus: **15 passed / 0 failed**; and
- SQLite backup/restore: **10 passed / 0 failed** in the mixed sanitizer lane.

Both repaired security diagnostics passed together for 10 consecutive
iterations.

## Gate correction: advertised diagnostics are obligations

All 11 omitted modes are now registered with CTest, with explicit 60-second
timeouts. The new `tools/audit_selftest_registration.py` obtains the CLI help
text from the built binary, extracts the advertised `--selftest-*` set, compares
it with CMake registrations, and fails on either direction of drift.

Current audit result:

```text
advertised=38
registered=38
missing_from_ctest=[]
registered_but_unadvertised=[]
passed=true
```

The complete project gate is now **80/80 CTest**, not 67 plus an informal set of
manual commands.

## Waste correction: test machinery was in the runtime library

The parent `anonsync_core_lib` compiled and linked `src/reporting_selftests.cpp`.
That file carried deterministic corpora, hostile-database construction, RSA test
key generation, lock-holder subprocess helpers, temporary fixture logic, and
all selftest entry points. Ordinary runtime consumers paid for that test-only
surface even when they never invoked the diagnostic CLI.

Rev0805 extracts the 90-line production `report_json()` implementation into
`src/reporting.cpp` and introduces a one-way dependency:

```text
anonsync_selftests_lib -> anonsync_core_lib
```

`anonsync_core_lib` no longer owns `reporting_selftests.cpp`. The diagnostic CLI
and the three legacy deterministic fuzz-named wrappers link
`anonsync_selftests_lib`; ordinary runtime consumers continue to link only the
runtime library. CMake fails configuration if the selftest source is added back
to the core list.

A representative runtime consumer,
`anonsync_sqlite_runtime_payload_store_test`, changed as follows:

| Metric | Parent graph | Rev0805 graph |
|---|---:|---:|
| First-party translation units | 42 | 42 |
| First-party lines exposed | 56,278 | 51,809 |
| `reporting_selftests.cpp` lines exposed | 4,559 | 0 |
| `reporting.cpp` lines exposed | 0 | 90 |

This removes **4,469 lines**, or **7.94%**, from that runtime consumer's
first-party compile graph. The translation-unit count is unchanged because a
small runtime implementation replaces a large test implementation; the quality
of the dependency is what changes.

## API correction: diagnostics no longer masquerade as runtime API

The public runtime header previously declared 39 selftest entry points. One,
`run_ingress_reservation_service_selftest()`, had no definition and no caller.
The other 38 were implementation diagnostics rather than runtime behavior.

Rev0805 adds `include/anonsync_selftest_api.hpp`, containing the 38 real
selftests and five diagnostic helper declarations. `include/anonsync_core.hpp`
now contains zero selftest declarations, and the dead declaration is removed.
The CLI includes both APIs because it is the diagnostic host. The deterministic
wrapper binaries include only the selftest API instead of the 3,455-line runtime
header.

`tools/audit_runtime_selftest_separation.py` verifies eight invariants:

- no selftest declaration in the runtime header;
- exactly 38 entry points in the selftest header;
- every declared entry point has exactly one definition;
- every definition is declared by the test API;
- the stale ingress-reservation declaration is absent;
- the CLI includes the test API;
- CMake excludes selftests from the runtime library; and
- all three deterministic wrappers use only the test API.

The audit passes **8/8** and is itself a CTest obligation.

## Validation

### Complete debug gate

- GCC 14.2.0
- C++20
- Debug
- bundled SQLite 3.53.3
- `-Wall -Wextra -Wpedantic -Werror`
- complete build passed
- **80/80 CTest passed**

### Strict changed-object lanes

The final changed C++ objects passed Clang 17 with:

```text
-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror
```

They also passed GCC 14 with:

```text
-O3 -DNDEBUG -Wall -Wextra -Wpedantic -Werror
```

The changed-object scope is the CLI, selftest implementation, and three
legacy deterministic wrapper translation units. These are not represented as
full-project optimized or full-project Clang builds.

### Sanitizer scope

A mixed GCC ASan/UBSan executable instrumented the final CLI and final
selftest-support implementation while linking the final runtime libraries
without instrumentation. The repaired SQLite hardening, crash-corpus, and
backup/restore diagnostics passed. `detect_leaks=0` was used; no leak-detection
claim is made.

A full-core sanitizer build was attempted. Every first-party object except
`src/sync_domain.cpp` compiled before the attempt was stopped after that single
24,531-line translation unit exceeded the available 4 GiB/no-swap cloudtainer
build budget over repeated command windows. No full-core ASan/UBSan claim is
made, and the attempted compile is not treated as a substitute for execution.

## Deep audit: what is missing

### Priority 0: executable convergence algebra

The repository has many mechanisms associated with convergence—manifests,
tombstones, idempotency keys, lineage, conflict copies, receipts, checkpoints,
and replay controls—but mechanisms are not an algebra. Each durable operation
needs an explicit classification:

- commutative or order-sensitive;
- idempotent or single-application;
- monotone or retracting;
- causally dependent or independent;
- locally decidable or coordination-requiring; and
- safe or unsafe across key/schema epochs.

A compact executable model should generate duplicate, loss, reorder, partition,
retry, concurrent update/delete, clock-skew, restart, and epoch-change traces.
The C++ implementation should be differentially checked against that model. The
strong convergence claim should be earned from those traces rather than inferred
from feature names.

### Priority 0: crash-cut protocol oracle

The current crash corpora mostly exercise application-selected cases. The next
proof should enumerate durability cuts. A custom VFS and separate process should
fail each write/sync/truncate/lock edge, reorder or corrupt writes not yet proven
durable, terminate without cleanup, restart, and compare recovered protocol
state with a reference model.

The oracle must cover the database, WAL/journal, sidecars, snapshot manifests,
receipts, checkpoints, staging files, rename/publication state, and external
filesystem effects as one protocol. `PRAGMA integrity_check` can establish a
structural property of a database; it cannot establish that AnonSync recovered
to a permitted domain state.

### Priority 0: disposable hostile-database worker

Untrusted SQLite interpretation remains inside the long-lived process.
Connection authorizers, trusted-schema controls, geometry checks, limits, and
progress budgets reduce risk, but they do not bound every allocator path,
parser behavior, extension surface, or kernel resource.

A worker should run with:

- a small typed input and typed output protocol;
- no inherited application capabilities;
- minimal descriptors and environment;
- parent-enforced wall-clock termination;
- CPU, address-space, file-size, and descriptor limits;
- best-effort filesystem restriction such as Landlock;
- a narrow seccomp policy as one layer, not as the whole sandbox; and
- process disposal on every result.

### Priority 0: privacy, anonymity, and key lifecycle

The code audit found HMAC-SHA256 and RS256 authentication/signature machinery,
but no established payload-encryption, ratchet, group-epoch, or metadata-hiding
protocol in the reviewed implementation. This lexical/source audit is not a
formal impossibility proof, but it is enough to reject an unqualified anonymity
or confidentiality claim.

The system needs a written adversary and leakage model covering payloads,
filenames/paths, sizes, timing, equality, access patterns, topology, membership,
server visibility, local compromise, stolen devices, and malicious peers. It
then needs explicit device enrollment, key epochs, rotation, revocation,
recovery, forward secrecy, post-compromise recovery, and secret-memory policy.
MLS is relevant research for asynchronous group epochs and forward/post-
compromise properties, but it is not a drop-in transport or anonymity proof.

### Priority 1: extract the monolith by invariant ownership

Repository concentration remains severe:

| Path | Lines | Specific concern |
|---|---:|---|
| `src/sync_domain.cpp` | 24,531 | production model plus 8,721-line selftest tail |
| `src/sqlite_replay_ledger.cpp` | 5,312 | production persistence plus 908-line selftest tail |
| `src/reporting_selftests.cpp` | 4,475 | intentionally test-only, still one large diagnostic TU |
| `src/sync_peer_ingress_lifecycle.cpp` | 3,831 | lifecycle state and a small embedded test tail |
| `include/anonsync_core.hpp` | 3,455 | broad public compile surface |

The next extraction should first move the 8,721-line domain selftest tail to the
selftest library, then isolate one narrow production authority owner at a time.
Every extraction should have a focused executable, an adversarial test, a
no-core dependency guard, and a before/after build-graph snapshot.

### Priority 1: finish typed SQLite ownership

A lexical inventory finds 751 `sqlite3_*(` call sites across 27 source files.
Some are legitimate low-level owners and some are test support, but the number
shows that typed boundaries are not yet the only route to persistence. Continue
migration toward explicit connection authority, exact scalar/row extraction,
owner-generation borrows, transaction capabilities, schema identities,
verification budgets, and typed projection decoders.

### Priority 1: separate current source from revision archaeology

Active first-party files contain 284 `rev####` token occurrences and 55
revision-needle comment lines. These breadcrumbs help recovery, but they also
couple current behavior to historical search strings and make broad headers and
CLI files accumulate textual archaeology. Move history-sensitive needles into
evidence manifests or generated audit inventories. Current code should express
the invariant and point to a stable rule identifier, not carry every old
revision phrase forever.

### Priority 1: real remote transport and compatibility contract

The reviewed transport implementation is local fixture plumbing: Unix
`socketpair()` and IPv4 loopback appear in `sync_peer_local_transport.cpp`.
There is no demonstrated production remote authenticated/encrypted transport in
this revision. A future transport should separate:

- remote connection security;
- application end-to-end payload protection;
- peer/device authentication;
- anti-replay and epoch semantics;
- framing and bounded decoding;
- metadata-leakage policy; and
- schema/wire compatibility independent of source revision tokens.

### Priority 2: speculative architecture

After the P0 proofs exist, useful experiments include:

- a content-addressed evidence DAG or delta-state anti-entropy layer for partial
  synchronization and deduplication, while keeping digests as evidence rather
  than authority;
- typed `Authority<T, Invariant>` or transition capabilities that make proof
  ownership visible in function signatures;
- deterministic simulation of process, network, clock, and filesystem faults;
- small-state model checking for recovery and convergence state machines; and
- a control-plane/data-plane separation so authorization and key epochs do not
  share the bulk payload path.

These are hypotheses, not rev0805 claims.

## Revision contents

### Added

- `include/anonsync_selftest_api.hpp`
- `src/reporting.cpp`
- `tools/audit_selftest_registration.py`
- `tools/audit_runtime_selftest_separation.py`
- `REVISION_NOTES_rev0805.md`
- `REVISION_EVIDENCE/rev0805/` handoff evidence

### Modified

- `CMakeLists.txt`
- `include/anonsync_core.hpp`
- `src/anonsync_core.cpp`
- `src/reporting_selftests.cpp`
- `fuzz/fuzz_json_codec.cpp`
- `fuzz/fuzz_jwt_codec.cpp`
- `fuzz/fuzz_route_event_ledger.cpp`
- `README.md`
- `RELEASE_GATE.json`
- `MANIFEST.sha256`

No production invariant was weakened to make the new tests pass.

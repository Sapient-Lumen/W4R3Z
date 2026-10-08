# AnonSync rev0801 — fork lineage, process authority, and parent-safe cleanup

Prepared from the last complete byte-verifiable source archive,
`AnonSync-rev0799-2026.07.15.13.58-finitework-statefusion-readfence-stagingtruth.zip`
(SHA-256 `55adbf2151bdfa0b0e11e1c0247937cf7debaa1ac9ca7244fbabd2c8acfb6f8a`).
That package passed all 25 release-package verifier checks before modification.

The supplied rev0800 archive is not used as a source parent. It is 2,751 bytes,
has ten ZIP entries, and contains only a 2,733-byte reproducer plus a 148-byte
manifest. Rev0801 preserves that archive's digest, listing, and reproducer under
`REVISION_EVIDENCE/rev0800/` and records the recovery decision under
`REVISION_EVIDENCE/rev0801/lineage/`.

## Heart of the mission

AnonSync is an **evidence-authorized convergence engine**. Observation is not
authority. A pathname, descriptor, PID, callback, SQLite handle, successful
query, signed digest, row, transaction, or reported count may be evidence. It
must not authorize a transition until the boundary that owns the invariant has
proved the exact bytes, identity, process incarnation, generation, lifetime,
policy, relationship, schema, resource, and durability conditions needed for
that transition.

That principle has a direct process consequence:

> `fork()` duplicates representation; it does not duplicate ownership.

A copied C++ object, file descriptor, VFS pointer, progress-handler context, or
pathname is not fresh child authority. The child must either fail closed on the
inherited object or mint a new local capability from child-local evidence.

## Severe defect corrected: child cleanup could destroy the parent seal

`SealedSqliteSnapshot` was described as process-local, but rev0799 stored no
process proof. After `fork()`, the child inherited the same staging pathname,
directory descriptor, snapshot descriptor, and destructor. Assigning a default
seal to the inherited object ran `cleanup_noexcept()` in the child and unlinked
the parent's private snapshot.

The preserved rev0799 reproducer records:

```text
child_exit=0
staged_exists_after_child_cleanup=false
parent_verification_failed=true
```

This is not merely a leaked temporary-file concern. SQLite's official corruption
guidance warns that a child must not use an inherited connection and must not
even call `sqlite3_close()` on it because cleanup can delete content required by
the parent. Rev0799's C++ cleanup owner had the same class of authority error.

Rev0801 records the opposite behavior:

```text
child_exit=86
staged_exists_after_child_cleanup=true
parent_verification_failed=false
```

The child exits directly before C++ unwinding or `atexit` processing, and the
parent retains verification, immutable-open, and final cleanup authority.

## Refactor: one process-incarnation owner

`src/sync_sqlite_process_incarnation.cpp` is now an independently linked
boundary instead of process identity being an incidental helper inside generic
SQLite support. There is one process-global token owner in the final link graph.

The public token is opaque and non-serializable. On fork-capable platforms its
64-bit representation combines:

- the current kernel PID in the low 32 bits; and
- a nonzero ordinary-fork lineage generation in the high 32 bits.

A registered `pthread_atfork()` child handler advances the copied token before
ordinary child code resumes. The refresh operation is idempotent so an earlier
registered child handler that asks AnonSync for the current token cannot cause a
second advance when AnonSync's own handler runs. A lock-free atomic is required
at compile time, and malformed state or generation exhaustion poisons authority
instead of wrapping.

PID is retained as evidence, but raw PID equality is no longer sufficient. A
grandchild reached through an intermediate process that never explicitly asks
for a token still advances two generations. A later descendant that reuses an
ancestor PID therefore cannot recreate the ancestor token.

## Process-bound persistence owners

Three existing owners now retain the minting process-incarnation token:

1. `SqlitePathFamilyGuard` rejects inherited inspection, verification, opens,
   moves, assignment, and destruction before a child can close its copied
   directory owner or use parent path evidence.
2. `SealedSqliteSnapshot` rejects inherited getters, verification, immutable
   opens, moves, assignment, destruction, descriptor close, and staging unlink.
3. `SqliteVerificationBudget` rejects inherited accounting, inspection,
   callback execution, detachment, and destruction before a child can detach a
   parent progress handler or use its context.

The focused fork proof installs hostile `terminate` and `atexit` handlers to
show that denial uses the direct `_Exit(86)` path rather than throwing, unwinding,
terminating, or running process-exit callbacks. It also proves the positive
case: a controlled child can create a new path guard, capture a new seal, open a
new immutable database, install a new budget, execute a query, close, and verify
the child-local seal.

## Build-graph correction

The process-incarnation boundary has its own library and focused executable:

- four Ninja actions;
- two first-party translation units;
- 382 first-party lines;
- no core monolith, SQLite, or OpenSSL dependency.

The integrated persistence fork proof is still narrow relative to the
application:

- 14 Ninja actions;
- six first-party translation units;
- 2,268 first-party lines;
- bundled SQLite and OpenSSL, but no `anonsync_core_lib`.

CMake guards reject reabsorption of the process source into the core source list
and reject focused-boundary dependencies on the monolith.

## Release-lineage correction

The rev0800 failure shows that a package cannot be trusted merely because its
manifest exactly describes the few files it contains. The release verifier's
required baseline now includes the process-incarnation implementation, path
security, snapshot seal, verification budget, process/fork proofs, process audit,
and package verifier itself, in addition to minimum source/header/test counts.

The strengthened verifier rejects the supplied rev0800 cube for missing source,
headers, tests, release gate, and revision evidence. Historical bytes are
preserved; they are not rewritten into a fictional complete parent.

## Validation

- Complete parent rev0799 package verification: **25/25**.
- GCC 14 Debug/`-Werror`: full build and **64/64 CTest**.
- Five focused executables, 20 repetitions: **100/100 executions**.
  - process incarnation: 22 checks/run;
  - persistence process authority: 21 checks/run;
  - existing SQLite owner process proof: 39 checks/run;
  - snapshot seal: 68 checks/run;
  - verification budget: 63 checks/run.
- GCC 14 ASan/UBSan focused lane: **25/25 executions**.
- Clang 17 conversion/sign-conversion/shadow `-Werror`: **25/25**.
- GCC 14 `-O3 -DNDEBUG -Werror`: **25/25** first-party focused executions.
- Nine architecture/source audits passed; process-authority audit: **83/83**.
- Incomplete rev0800 negative package proof: rejected as required.

No full-core sanitizer claim is made. The optimized claim covers the focused
first-party boundary; the bundled SQLite amalgamation is not claimed
warning-clean under every optimizer diagnostic.

## What remains missing

### 1. Universal SQLite process authority

The active audit still inventories 416 raw SQLite pointer declarations, 34 raw
open-output candidates, and 25 raw prepare-output candidates across production
and tests. Rev0801 protects the shared C++ owners it touches, not every raw
`sqlite3*` path. The operational rule remains strict: do not fork with live
SQLite objects and then use or close inherited connections in the child.

The next monotone migration should replace raw connection lifetimes with one
process-bound RAII connection owner and narrow borrows, then make direct
`sqlite3_open_v2`, `sqlite3_prepare_v2`, and `sqlite3_close*` calls auditable
exceptions rather than ordinary control flow.

### 2. Post-fork execution containment

After a multithreaded `fork()`, only async-signal-safe operations are generally
safe before `exec()`. The successful child-local proof is intentionally a
controlled single-threaded executable test; it is not permission to run the
full application in an arbitrary multithreaded fork child.

`_Fork()` and raw clone paths do not invoke `pthread_atfork()`. A direct child is
rejected on first token lookup through PID mismatch, but an entirely unobserved
lineage that eventually reuses an ancestor PID remains outside the proof. A
stronger architecture would make the child immediately `exec()` a small worker
and communicate only through typed pipes or descriptor passing.

### 3. Hostile-snapshot worker and crash oracle

The in-process verification budget still does not exactly contain SQLite heap,
page cache, allocator metadata, blocked I/O, VFS/libc defects, or kernel faults.
Move hostile snapshot interpretation into a disposable worker with OS-enforced
CPU, address-space/RSS, file-size, descriptor, syscall, and wall-clock limits.

The highest-value persistence proof remains a crash-cut VFS/protocol oracle that
interrupts every write, sync, truncate, rename, journal/WAL interaction,
sidecar publication, staging transition, receipt, and checkpoint cut; restarts
in another process; and separately asks whether SQLite is structurally valid
and whether the recovered AnonSync state belongs to the protocol's permitted
outcome set.

### 4. Formal convergence and privacy contracts

The repository contains many convergence mechanisms—lineage, tombstones,
conflict copies, replay records, idempotency keys, receipts, checkpoints, and
workorders—but no executable merge algebra classifying operations by
commutativity, idempotence, monotonicity, causality, and coordination need.
Property-generated traces should compare production C++ against a small
reference state machine under duplication, omission, reordering, partitions,
restart, concurrent edit/delete, clock skew, and key-epoch changes.

The name AnonSync still implies privacy properties not established by
authentication and exact persistence. The project needs an explicit adversary,
payload-encryption layer, metadata-leakage budget, device enrollment and
revocation design, key epochs, forward secrecy, and post-compromise recovery.
RFC 9420's Messaging Layer Security is a useful reference for asynchronous group
keying, not an automatic fit or proof for AnonSync.

### 5. Monolith decomposition by invariant ownership

The largest current files are:

```text
src/sync_domain.cpp                    24,531 lines
src/sqlite_replay_ledger.cpp            5,312
src/reporting_selftests.cpp             4,509
src/sync_peer_ingress_lifecycle.cpp     3,831
include/anonsync_core.hpp                3,499
src/runner.cpp                           2,198
```

Continue extraction only where a boundary has an independently expressible
invariant and adversarial proof. Arbitrary file splitting would add names while
preserving the same rebuild fan-out and reasoning burden.

## Primary research references

- SQLite inherited-connection corruption guidance:
  <https://www.sqlite.org/howtocorrupt.html#_carrying_an_open_database_connection_across_a_fork_>
- POSIX `pthread_atfork()`:
  <https://pubs.opengroup.org/onlinepubs/9799919799/functions/pthread_atfork.html>
- POSIX `fork()`:
  <https://pubs.opengroup.org/onlinepubs/9799919799/functions/fork.html>
- SQLite VFS contract:
  <https://sqlite.org/c3ref/vfs.html>
- SQLite crash and fault-testing strategy:
  <https://sqlite.org/testing.html>
- Local-first software principles:
  <https://www.inkandswitch.com/essay/local-first/>
- CRDT convergence foundations:
  <https://hal.inria.fr/inria-00555588/document>
- Messaging Layer Security, RFC 9420:
  <https://datatracker.ietf.org/doc/rfc9420/>

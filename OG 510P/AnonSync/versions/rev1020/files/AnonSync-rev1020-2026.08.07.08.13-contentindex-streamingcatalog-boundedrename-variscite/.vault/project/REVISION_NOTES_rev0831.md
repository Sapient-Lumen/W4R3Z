# AnonSync rev0831 — self-exec child authority, descriptor hygiene, bounded reap, exact evidence rebinding

## Executive result

Rev0831 removes direct full C++/filesystem/SQLite execution from the raw
post-`fork()` branches of the focused replay-ledger reset test and the combined
reset/immutable-receipt crash-frontier test. Both now enter a fresh executable
image through a reusable Linux test-only process owner, verify the process
boundary, and reconstruct exact parent-selected evidence before touching the
fixture.

No production transition semantics are changed. The revision strengthens the
credibility and determinism of the test machinery that authorizes future
production changes.

## Defect

The prior tests called `fork()` and then immediately used ordinary C++ objects,
exceptions, `std::filesystem`, fixture helpers, and SQLite-related production
code in the child. This is not a sound general crash-test boundary in a
multithreaded executable:

- only the thread that called `fork()` survives in the child;
- allocator, iostream, filesystem, and library mutex state is copied;
- copied locks may name vanished parent threads;
- every open descriptor is inherited unless separately closed;
- signal mask and dispositions are inherited with nontrivial rules; and
- SQLite warns that a connection opened by the parent must not be used or even
  closed through SQLite in the child.

An observed PID and exit status therefore did not prove that the child reached
the selected crash frontier through a valid runtime state.

## New C++ process owner

`tests/self_exec_test_process.hpp/.cpp` introduces
`anonsync::test::SelfExecTestProcess`.

### Canonical execution

- resolves `/proc/self/exe`;
- canonicalizes it to one absolute regular file;
- invokes `posix_spawn()`, not `posix_spawnp()`;
- never trusts `argv[0]` or searches `PATH`; and
- rejects missing/noncanonical executable objects.

### Instruction and environment budgets

- at most 32 arguments;
- at most 4096 bytes per argument;
- at most 64 KiB aggregate argv bytes;
- embedded NUL denied;
- at most 64 KiB environment bytes; and
- environment rebuilt from `LC_ALL=C`, `TZ=UTC`, and only reviewed
  sanitizer/symbolizer variables.

### Descriptor boundary

The parent opens a deliberate non-`CLOEXEC` `/dev/null` descriptor and proves it
is visible before spawn. The spawn file-action list applies
`posix_spawn_file_actions_addclosefrom_np(..., 3)`. This single child-side action
covers descriptors created after any parent enumeration and avoids an
open-descriptor race in a multithreaded test process.

The exec image independently verifies:

- descriptors 0, 1, and 2 are open;
- no descriptor above 2 is open;
- only allowlisted environment names are present;
- locale and timezone are exact and nonduplicated;
- no signal is blocked; and
- the helper is leader of its isolated process group.

### Move-only reap authority

One object owns one child PID. Copying is disabled. Move construction transfers
that authority. Move assignment first kills/reaps the target’s previous process
group and leader, then accepts replacement authority. Destructor cleanup,
timeout, and unexpected wait errors also kill the group and synchronously reap
the leader.

`wait_for_exact_exit()` uses a monotonic deadline, requires one normal
byte-sized exit status, and clears ownership on every terminal path.

## Executable owner oracle

`tests/self_exec_test_process_test.cpp` proves **11 checks**:

1. one live owner is returned;
2. move construction transfers without duplication;
3. exact wait consumes authority;
4. move assignment transfers replacement authority;
5. move assignment reaps the prior helper;
6. the replacement exact wait consumes authority;
7. timeout reports killed-and-reaped status;
8. timeout clears authority;
9. destructor cleanup leaves `ECHILD`;
10. a missing executable is denied; and
11. an oversized argument is denied.

The helper mode itself performs the child-boundary verification, so a successful
exact-exit test simultaneously proves descriptor, environment, signal, and
process-group behavior.

## Reset helper migration

`sqlite_replay_ledger_reset_tests.cpp` now dispatches the versioned helper mode
`--anonsync-reset-focused-helper-v1` before ordinary test execution. Its strict
instruction has seven fields and supports:

- write-gate lifetime inversion;
- write-gate cross-thread destruction; and
- durable commit before report loss.

The exec child verifies its process boundary first, reopens the fixture, and
rebinds exact state and receipt hashes. Parent waits are bounded at ten seconds.
The source contains no raw `fork()` or `waitpid()` path.

The runtime corpus remains **68/68**.

## Combined crash-frontier migration

`sqlite_replay_ledger_reset_crash_frontier_test.cpp` now uses
`--anonsync-reset-receipt-crash-helper-v1`. Its strict instruction binds:

- action;
- normalized absolute fixture root;
- canonical case component;
- expected state SHA-256;
- expected receipt SHA-256;
- request SHA-256; and
- publication cutpoint index or `none`.

The child verifies the process boundary and reloads the fixture after exec.
Supported actions cover reset after durable commit and selected atomic-publication
cutpoints. Parent waits are bounded at ten seconds.

The first rebuilt run revealed a real naming mismatch: reviewed publication
cutpoint names use underscores, while fixture path components intentionally
accept lowercase hyphenated grammar. The correction converts underscore to
hyphen at the evidence-to-fixture boundary. The path grammar was not broadened.

The combined runtime corpus remains **462/462**.

## Structural release gate

`tools/audit_self_exec_test_process.py` contributes **28/28** obligations. It
requires test-only ownership, dependency-free support, canonical self-exec,
argument/environment budgets, close-from sanitation with a positive sentinel,
child-side descriptor/environment/signal verification, process-group isolation,
move-only and bounded reap semantics, executable timeout/destructor/move tests,
exact reset/frontier rebinding, CMake/sanitizer integration, release-verifier
coverage, and no regression to raw post-fork application work in the migrated
callers.

Strengthened existing audits contribute:

- replay-ledger reset: **102/102**;
- crash frontier: **20/20**;
- reset receipt: **42/42**;
- reset receipt protocol: **29/29**; and
- atomic publication: **39/39**.

Aggregate focused source obligations: **260/260**.

## Raw-fork inventory

A separate audit classifies 22 actual calls in 13 translation units. Highest
priority migrations are:

- five calls in the production-linked selftest tail of
  `src/sqlite_replay_ledger.cpp`;
- peer-ingress schema attestation;
- runtime payload-store crash testing;
- atomic-publication cutpoint testing;
- atomic-publication multi-process contenders; and
- the allocator-fault fork/dup2/exec shim.

Raw fork remains semantically necessary for tests whose exact subject is an
object or process-incarnation token inherited from the parent. Mixed tests
should be split so isolation-only scenarios can use self-exec.

## Validation

- parent archive SHA-256:
  `625c895ebbed7970456803083b7d6b17941ba1a2da9787d01aa3f0016f5ca663`;
- parent ZIP verifier: **25/25**;
- parent directory verifier: **21/21**;
- active source patch replay: **201/201**;
- source delta: **10 files**, **2,099 insertions**, **150 deletions**;
- GCC 14.2 Debug all-target build: passed;
- final dependency closure: `ninja: no work to do.`;
- complete post-closure CTest: **118/118** in 50.83 seconds;
- focused final CTest: **9/9**;
- direct owner/reset/frontier: **11/11**, **68/68**, **462/462**;
- stress: owner **100/100**, reset **25/25**, frontier **20/20**;
- Clang 17 `-Werror`: **9/9**;
- Clang 17 ASan/UBSan: **9/9**, with leak detection disabled; and
- source audits: **260/260**.

The first clean all-target attempt used parallelism two and was terminated by
the cloudtainer during the large-object phase without a compiler diagnostic.
Ninja’s retained state was resumed at parallelism one and completed. A subsequent
full link closure completed, the exact post-closure binaries passed 118/118, and
the final build invocation reported no work.

## Research basis

Rev0831 was informed by the current POSIX `fork()` and `posix_spawn()` contracts,
the Linux man-pages, SQLite’s explicit fork warning, and GNU close-from spawn
actions. Exact URLs and resulting design inferences are recorded in
`REVISION_EVIDENCE/rev0831/RESEARCH.md`.

## Claim boundary

This helper is Linux/glibc test infrastructure, not a portable production
process abstraction and not a hostile-input sandbox. It does not prove arbitrary
VFS/storage failures, one atomic transaction across SQLite and receipt
publication, Windows behavior, distributed convergence, confidentiality,
anonymity, metadata hiding, key lifecycle, or secure erasure.

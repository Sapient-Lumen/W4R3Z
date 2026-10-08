# AnonSync rev0832 — restore-lock owner, extracted diagnostic corpus, self-exec holder proof

## Executive result

Rev0832 removes replay-ledger restore diagnostics and subprocess choreography from the production replay-ledger translation unit, introduces an independently linked process-bound restore-lock owner, and migrates two general lock-holder scenarios from raw `fork()` to the canonical self-exec test boundary.

The result is a one-way architecture:

```text
anonsync_sqlite_replay_ledger_selftests_lib
    -> anonsync_core_lib
    -> anonsync_sqlite_replay_ledger_restore_lock
```

The runtime never links the diagnostic archive. `src/sqlite_replay_ledger.cpp` falls from **5,356 to 4,409 lines**.

## What changed

- Added `SqliteReplayLedgerRestoreLock`, a noncopyable/nonmovable process-incarnation-bound owner for the adjacent private lock file, guarded path family, nonblocking `flock`, durable PID marker, and child-destruction fail-stop.
- Moved five restore diagnostics and their fixtures into `tests/sqlite_replay_ledger_selftests.cpp`.
- Added a three-function bridge exposing only the production verifier operations the corpus needs.
- Added an exact self-exec helper mode dispatched before ordinary CLI parsing.
- Replaced two raw fork holder paths with `SelfExecTestProcess`; three raw forks remain only for inherited-capability probes.
- Reused the exact SQLite integer extraction boundary in the moved fixture.
- Added a 21-check separation audit and strengthened process, scalar, snapshot, budget, runtime-separation, CMake, sanitizer-list, and release-package ownership checks.

## Audit finding during integration

The first complete run passed 118/119. The existing self-exec ownership audit correctly rejected the new diagnostic corpus because it was still physically under `src/`, even though CMake linked it only into tests. The correction moved the file to `tests/`; the audit was not weakened. Final complete coverage is 119/119.

## Validation

- parent ZIP: **25/25**; parent directory: **21/21**;
- active source patch replay: **206/206**, zero mismatches;
- source delta: **15 files**, **1,802 insertions**, **1,013 deletions**;
- GCC 14.2 Debug all-target build: passed;
- final dependency closure: `ninja: no work to do.`;
- exact post-closure complete CTest: **119/119** in six bounded batches;
- final five restore diagnostics: **37/37**;
- stress: write-gate **45/45**, restore-lock **30/30**;
- focused source audits: **281/281**; and
- Clang 17 `-Werror` changed translation-unit compile: **2/2**.

No single uninterrupted final CTest, sanitizer, hostile worker, arbitrary VFS/power-loss completeness, Windows runtime, distributed convergence, confidentiality, anonymity, metadata hiding, key lifecycle, or secure-erasure claim is made.

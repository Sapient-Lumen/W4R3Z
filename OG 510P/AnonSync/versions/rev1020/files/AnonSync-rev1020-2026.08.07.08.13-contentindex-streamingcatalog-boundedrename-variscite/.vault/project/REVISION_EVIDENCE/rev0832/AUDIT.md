# Audit — AnonSync rev0832

## Result

Rev0832 separates three owners that were previously fused:

1. `src/sqlite_replay_ledger.cpp` owns production replay-ledger and restore transitions;
2. `src/persistence/sqlite_replay_ledger_restore_lock.*` owns the process-incarnation-bound restore serialization capability; and
3. `tests/sqlite_replay_ledger_selftests.cpp` owns fixture generation, subprocess choreography, and five restore diagnostics.

The runtime translation unit falls from **5,356 to 4,409 lines**, a net reduction of **947 lines**. The generated Ninja graph proves the diagnostic archive depends on the core and focused lock owner, while neither runtime archive depends on the diagnostic corpus.

## Process-boundary correction

The prior diagnostic tail contained five raw forks. Rev0832 converts the ordinary write-gate holder and restore-lock holder to `SelfExecTestProcess`. The fresh executable verifies descriptor, environment, signal-mask, and process-group boundaries before parsing an exact helper instruction and acquiring a new capability.

Three raw forks remain in the extracted test file. They are not general child execution: each deliberately tests an inherited lock/gate object, uses a bounded wait, kills/reaps on timeout, and does not open or use SQLite in the child. Project-wide actual raw fork calls decline from **22 to 20**; all are now under `tests/`.

## Restore-lock owner

`SqliteReplayLedgerRestoreLock` is noncopyable and nonmovable. It retains one guarded path family and one locked descriptor for its lifetime, creates a private 0600 regular single-linked lock file relative to the retained parent descriptor, acquires nonblocking exclusive `flock`, writes and syncs an exact PID marker, and fail-stops if an inherited child attempts destruction.

## Audit repair without weakening

Moving the corpus first exposed three audits that searched the production file for diagnostic evidence. Those checks were retargeted to the test owner while production-negative checks remained on `src/sqlite_replay_ledger.cpp`. A pre-existing self-exec audit then correctly rejected the corpus while it still lived physically under `src/`; the file was moved to `tests/` rather than weakening the audit.

The extracted scalar fixture now consumes `sqlite_exact_i64_or_throw`, removing a duplicate raw SQLite scalar conversion path.

## Deterministic obligations

Focused source audits pass **281/281**:
- replay-ledger-selftest-separation: **21/21**
- runtime-selftest-separation: **9/9**
- self-exec: **28/28**
- sqlite-process-authority: **87/87**
- sqlite-scalar-extraction: **30/30**
- sqlite-snapshot-seal: **61/61**
- sqlite-verification-budget: **45/45**


Runtime proof:

- five final restore diagnostics: **37/37**;
- write-gate stress: **45/45** checks across five executions;
- restore-lock stress: **30/30** checks across five executions;
- final post-closure CTest inventory: **119**;
- complete dependency-aware batched gate: **119/119**;
- GCC 14.2 Debug all-target build: passed;
- final dependency closure: `ninja: no work to do.`; and
- Clang 17 `-Werror` compile of both changed translation units: passed.

The complete gate is accurately described as six bounded batches. A prior 118/119 complete attempt found the physical `src/` ownership mismatch; that finding caused the move to `tests/` and was not suppressed.

## Claim boundary

This revision does not claim arbitrary power-loss or VFS cutpoint completeness, a cross-resource atomic transaction, hostile-worker isolation, Windows runtime coverage, a full-project sanitizer result, distributed convergence, confidentiality, anonymity, metadata hiding, key lifecycle, or secure erasure.

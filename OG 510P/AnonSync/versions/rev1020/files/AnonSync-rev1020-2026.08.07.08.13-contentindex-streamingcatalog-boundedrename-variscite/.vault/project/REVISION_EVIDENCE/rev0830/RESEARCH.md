# Rev0830 research and speculation

## Primary sources reviewed

1. SQLite, **How SQLite Is Tested**  
   https://sqlite.org/testing.html

   SQLite describes alternative VFS implementations that inject one-shot and
   persistent I/O failures at increasing operation ordinals. After disabling the
   fault, tests inspect the database, including `PRAGMA integrity_check`. Its
   crash tests simulate the post-crash file image and reopen the database.

2. SQLite, **Atomic Commit In SQLite**  
   https://sqlite.org/atomiccommit.html

   The crash-test VFS models incomplete sector writes, garbage from incomplete
   writes, and out-of-order writes at varying transaction points. Each case
   reopens and checks that the transaction happened completely or not at all and
   that the database remains consistent.

3. SQLite, **How To Corrupt An SQLite Database File**  
   https://sqlite.org/howtocorrupt.html

   SQLite explicitly cannot defend against a rogue process overwriting an
   ordinary database file. It also warns that copying only the main file while a
   transaction is active or after a failed write can omit required WAL/journal
   state. This supports AnonSync’s object-identity fences but also bounds what an
   in-process database verifier can claim.

4. SQLite, **Write-Ahead Logging**  
   https://sqlite.org/wal.html

   In WAL mode, commit is represented by a commit record appended to the WAL;
   readers pin an end mark, and checkpointing is a separate operation. An
   operation-level crash oracle must therefore model main DB, WAL, shared memory,
   sync, and checkpoint state rather than treating the main file as the complete
   durable image.

5. SQLite, **PRAGMA statements**  
   https://sqlite.org/pragma.html

   SQLite documents that `journal_mode=OFF` disables atomic commit/rollback and
   that `MEMORY` journaling is unsafe across process crash. An AnonSync VFS oracle
   should attest the actual runtime journal/synchronous profile for every trace,
   not merely assume the configured value took effect.

The pages above were rechecked online on 2026-07-18. They are design inputs, not
claims that AnonSync already has equivalent coverage.

## Design inference: the next oracle should join two state machines

A useful custom VFS test should not stop at `PRAGMA integrity_check`. The domain
oracle must classify both resources after each injected failure or process exit:

- SQLite state: prior reset, exact reset receipt identity, a legitimate later
  state, or invalid/indeterminate;
- receipt state: absent, unpublished temp residue, published but directory
  durability indeterminate, or published and directory-synced; and
- recovery authority: none, exact fresh-path replay, identity resolution, or
  operator intervention.

This is an inference from SQLite’s crash-testing model plus AnonSync’s existing
atomic-publication state model.

## Proposed C++/VFS architecture

A small test-only VFS should wrap the selected production VFS rather than fork a
second SQL implementation. It should assign deterministic ordinals to relevant
operations and record file role plus byte range:

- VFS: `xOpen`, `xDelete`, `xAccess`, `xFullPathname`;
- file I/O: `xRead`, `xWrite`, `xTruncate`, `xSync`, `xFileSize`;
- locking: `xLock`, `xUnlock`, `xCheckReservedLock`;
- WAL/shared memory: `xShmMap`, `xShmLock`, `xShmBarrier`, `xShmUnmap`; and
- file-control operations that change persistence behavior.

Two modes are needed:

1. **returned fault mode**: return a documented SQLite error once or persistently
   after ordinal N; and
2. **crash image mode**: terminate an exec-launched helper and reconstruct the
   durable image from writes known to have crossed the modeled sync frontier,
   optionally dropping, tearing, or reordering unsynchronized writes within
   explicitly stated filesystem assumptions.

The parent should then reopen using a fresh process and preferably the ordinary
production VFS. Each trace should have a bounded operation count, wall clock,
artifact size, and structured instruction/result file.

## Speculative refinement

The current three correlated dimensions—phase, durable evidence, and recovery
action—are constructor-validated and useful for diagnostics. If the state space
grows, a discriminated recovery-authority object may become safer than adding
more enum combinations. That change should wait for the VFS oracle to reveal the
actual additional states rather than designing them from intuition.

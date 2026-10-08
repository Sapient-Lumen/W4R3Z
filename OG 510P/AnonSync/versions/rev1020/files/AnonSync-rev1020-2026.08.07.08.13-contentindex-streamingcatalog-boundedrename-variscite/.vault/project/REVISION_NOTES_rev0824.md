# AnonSync rev0824 revision notes

## Mission-level result

AnonSync remains an **evidence-authorized convergence engine**. Rev0824 removes
the last production SQLite-family deletion authority from ordinary ledger
opening. Destructive administration now requires one exact logical image, one
exact filesystem object, one explicit operator intent, one bounded transaction,
and one deterministic durable receipt.

## Parent gap

Rev0823 still allowed `SqliteWalReplayLedger::load(path, reset=true)` to call a
helper that deleted the main database and its `-wal`, `-shm`, and `-journal`
sidecars. The boolean did not bind the database identity, current chain heads,
outbox or replay-cache contents, namespace object, operator, reason, or recovery
receipt. A delayed reset request could therefore erase state that had advanced
since the caller decided to reset it.

The local JSONL backend had a related lifecycle weakness: failed reload and
explicit close could release the lock while leaving the object enabled, allowing
later calls to observe a stale writable-looking capability.

## Production correction

`IReplayLedgerBackend::load` no longer accepts a reset boolean. Normal load is
non-destructive for both backends, and the legacy `--ledger-reset` CLI spelling
is rejected.

`sqlite_replay_ledger_reset.cpp` is a separately linked administrative owner.
Its inspection phase acquires the same exclusive write gate as the live ledger,
opens only an existing guarded database, pins a read transaction, attests the
exact schema and backend/connection profile, checks integrity and foreign keys,
and hashes every durable value in a canonical table/row/column order under a
bounded SQLite progress budget.

A reset request binds:

- the absolute normalized ledger path;
- parent-directory and database device/inode identities as lossless unsigned
  decimal evidence;
- ledger instance identity;
- the complete canonical logical-state digest;
- redundant human-reviewable chain heads and row counts;
- a bounded operator ID, reason digest, and unique intent ID; and
- the reset request format and schema version.

The reset phase revalidates all of that evidence inside a typed
`BEGIN IMMEDIATE` transaction. It deletes only the four reviewed operational
tables, verifies exact changed-row counts, resets both metadata roots, and
rotates `ledger_identity` to the deterministic reset receipt before one commit.
The database inode is preserved; there is no unlink, rename, replacement,
CREATE, DROP, ALTER, VACUUM, ATTACH, or DETACH path in the owner.

Exact replay is non-destructive. Receipt identity recovers the committed
outcome even after legitimate post-reset writes; those writes set
`state_advanced_after_commit` and are never cleared by the retry.

A final review found a commit-classification frontier: COMMIT could succeed and
a later namespace, integrity, or receipt-postcondition check could throw. The
owner now raises `SqliteReplayLedgerResetDurableOutcomeError`, retaining the
exact outcome and receipt while nesting the original cause. The CLI returns a
distinct recoverable status and directs the operator to replay the exact
digest-pinned request rather than falsely reporting a precommit denial.

## Audit/refactor result

The process-bound SQLite write gate was extracted from
`sqlite_replay_ledger.cpp` into an independently tested library. Its scope token,
process incarnation, parent policy, and nesting semantics are now explicit.
Administrative inspection/reset requires a fresh, non-nested gate.

State-report and receipt publication are fenced from the ledger main name, all
reviewed sidecars and lock names, the digest-pinned request, and existing
hard-link/symlink aliases before any reset effect. The CLI oracle proves lexical,
hard-link, sidecar, request, and lost-receipt cases leave the exact inode and
logical state unchanged when denied.

The local JSONL ledger now revokes `enabled` state before releasing its lock on
failed load or close. New selftests prove rejected reuse cannot stage or commit,
and a later clean reload reacquires authority normally.

## Validation

- exact parent archive SHA-256:
  `a65e4ed21b7d55f554227da7e84135c0183d64577105918edb96d21a25cbf1fb`;
- exact rev0823 parent: ZIP 25/25 and directory 21/21;
- GCC 14 Debug all-target build: passed;
- final dependency closure: no work;
- complete sequential CTest: 107/107 in 70.22 seconds;
- focused reset owner: 67/67 checks;
- reset source audit: 98/98 checks;
- replay-ledger load-authority audit: 28/28 checks;
- CLI integration oracle: 332/332 checks;
- repeat stress: 50/50 executions and 9,975/9,975 checks;
- GCC 14 and Clang 17 `-Werror`: reset owner, source audit, and CLI oracle pass;
- scoped GCC 14 ASan/UBSan: focused reset owner passes with leak detection; the
  bundled SQLite amalgamation and full project are not claimed instrumented.

## Highest-priority next work

Build a deterministic VFS crash-cut model over the complete administrative
protocol: state inspection, request publication, write-gate acquisition,
`BEGIN IMMEDIATE`, each delete/update, WAL sync, COMMIT, postcommit verification,
receipt atomic rename, and parent-directory sync. The oracle must classify each
cut as denied, committed/recoverable, or durably published without relying on
process-local observations.

After that, move hostile SQLite interpretation into a disposable worker with
CPU, memory, wall-clock, descriptor, syscall, and filesystem ceilings, then
resume the independent convergence algebra for replicated operations.

No arbitrary power-loss, hostile same-UID namespace isolation, full-project or
bundled-SQLite sanitizer, Windows runtime, distributed convergence,
confidentiality, anonymity, metadata-hiding, key-lifecycle, or secure-erasure
property is claimed.

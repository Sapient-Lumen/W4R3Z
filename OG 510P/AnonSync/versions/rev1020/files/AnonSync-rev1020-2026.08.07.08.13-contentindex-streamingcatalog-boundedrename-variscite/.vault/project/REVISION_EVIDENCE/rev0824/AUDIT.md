# Rev0824 audit

## Boundary selected

Rev0823 left one ordinary API parameter with whole-database-family deletion authority. The rev0824 invariant is:

> A reset may erase only one explicitly identified logical ledger image, resident in one explicitly identified filesystem object, under one exclusive process-bound capability and one operator intent. The mutation must be finite, transactional, in-place, receipt-bearing, replay-safe, and distinguish a durable commit from a precommit denial.

## Severe parent gap

`SqliteWalReplayLedger::load(path, reset=true)` deleted the main file and three SQLite sidecars before opening a replacement. The boolean did not bind current durable rows, chain heads, outbox state, replay-cache state, database inode, parent namespace, operator, reason, or an idempotent receipt. A delayed call could therefore erase state created after reset was chosen, and ordinary opening carried authority far beyond opening.

## Production correction

Normal backend `load()` no longer accepts reset. The legacy CLI spelling fails closed. A separately linked reset owner now provides inspection and mutation stages.

Inspection acquires a fresh non-nested write gate, opens only an existing guarded database, pins a read transaction, attests the exact schema and backend/connection profile, checks integrity and foreign keys, and streams every durable value through a canonical SHA-256 transcript under a finite progress budget. The resulting expectation binds the absolute path, parent and database device/inode values, ledger identity, complete logical-state digest, redundant chain/count summaries, operator, reason digest, and intent.

Mutation reacquires the same exclusive capability, verifies the namespace object before and after open, rechecks every expectation inside typed `BEGIN IMMEDIATE`, deletes four reviewed operational tables in dependency order, verifies exact direct change counts, resets both chain roots, and rotates the ledger identity to the deterministic receipt before one commit. The owner contains no namespace deletion, rename, replacement, schema mutation, vacuum, attachment, or recreation path.

## Additional defects found during review

The first partial design bound only ledger identity. That remained vulnerable to a stale intent because normal writes do not rotate identity. Rev0824 instead binds the complete logical state.

The next design bound pathname and logical bytes but not the current directory object. A byte-identical replacement file could satisfy the logical request at the same name. The final protocol serializes parent and database device/inode evidence losslessly and re-inspects the directory entry before SQLite open authority is used.

An early retry rule required the reset database to remain empty. Legitimate writes after a successful reset then made receipt recovery impossible. The final rule separates historical outcome from current state: receipt identity proves the reset commit, `state_advanced_after_commit` reports subsequent work, and replay never clears it.

A later review found that a successful commit followed by a failed namespace, integrity, or postcondition observer could be reported like a precommit exception. The final owner throws a typed `SqliteReplayLedgerResetDurableOutcomeError` containing the exact outcome and receipt while preserving the underlying cause.

The CLI initially allowed state or receipt output to alias the ledger, a sidecar, or the request itself. The publication fence now rejects lexical aliases, symlinks, and existing hard links before any reset effect.

The adjacent local JSONL backend also released its lock before revoking enabled state on failed reload or close. That capability-ordering defect is corrected and covered by reuse and rejection selftests.

## Validation

- exact rev0823 parent: ZIP 25/25 and directory 21/21;
- exact source patch replay: 184/184 active files and 29/29 changed active files;
- GCC 14 Debug all-target graph: passed; final dependency closure: no work;
- one uninterrupted complete CTest gate: 107/107 in 70.22 seconds;
- focused reset executable: 67/67 checks;
- reset source audit: 98/98;
- load-authority audit: 28/28;
- CLI integration oracle: 332/332;
- focused stress: 50/50 executions and 9,975/9,975 checks;
- fresh GCC 14 and Clang 17 warning-as-error focused CLI graphs: passed; and
- focused GCC 14 ASan/UBSan reset owner: passed with leak detection enabled.

## Explicit limits

The write gate coordinates participating processes but does not isolate a hostile same-UID directory writer. The transaction tests do not enumerate arbitrary filesystem, kernel, storage-controller, or power-loss cutpoints. The focused sanitizer lane does not instrument the bundled SQLite amalgamation or claim full-project coverage. No Windows execution, distributed convergence, confidentiality, anonymity, metadata hiding, key lifecycle, or secure erasure property is claimed.

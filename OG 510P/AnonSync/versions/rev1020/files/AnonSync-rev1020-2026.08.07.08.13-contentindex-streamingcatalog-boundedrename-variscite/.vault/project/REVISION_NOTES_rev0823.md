# AnonSync rev0823 revision notes

## Mission-level result

AnonSync is an **evidence-authorized convergence engine**. A successful syscall, open, query, signature, callback, transaction, backup step, or rename is only an observation. It becomes transition authority when the invariant owner binds the exact bytes, identity, generation, process incarnation, lifetime, policy, relationship, resource budget, progress measure, and durability evidence required for the transition.

Rev0823 applies that rule inside live SQLite capture. The unit of authority is no longer “copy the rest of the database.” It is one finite copy step against one pinned source image, followed by exact evidence that the same process, transaction, geometry, and monotone progress relation still hold.

## Parent gap and correction

Rev0822 preflighted source page geometry, opened a private destination, and called `sqlite3_backup_step(..., -1)`. That design checked policy before and after an unbounded effect. SQLite's backup semantics permit source changes to restart copying when no read snapshot is pinned, so concurrent growth could consume work or allocation before the postcheck rejected it.

Rev0823 introduces `anonsync_sqlite_live_backup`, a separately linked C++ owner. It rejects explicit and implicit entry transactions, begins and pins a fresh source read transaction, samples geometry inside that snapshot, copies exactly 64 pages at a time, and derives a finite step ceiling. Process incarnation, read-transaction state, reported page count, remaining-page bounds, and strict progress are reasserted at every cutpoint. Incomplete destinations roll back, and finish/rollback cleanup evidence is captured without allocation before any diagnostic is built.

The snapshot seal delegates raw backup lifecycle to this owner. Snapshot-header and live-database geometry now share one monotone policy implementation rather than parallel checks.

## Audit/refactor result

The focused 34-check owner test exercises multi-step progress, concurrent WAL growth, lost snapshot authority, partial-destination rollback, named destinations, and explicit/hidden transactions. The seal test now has 94 checks, including a trace-profile race in which a writer commits 4 MiB between early preflight and snapshot pin.

That race replaced a false proof discovered during review: a VFS open counter did not observe private in-memory opens, so its assertion was vacuous. Rev0823 removes it and proves the actual ordering at the source SQL boundary.

## Validation

- exact rev0822 parent: ZIP 25/25; directory 21/21;
- exact source patch replay: 14/14 changed active files and all 176 active files;
- all-target Debug build: passed; final dependency closure: no work;
- complete CTest: 103/103;
- source audits: 305/305;
- focused stress: 50/50 executions, 3,200/3,200 checks;
- GCC 14 and Clang 17 `-Werror`: 2/2 focused targets each;
- scoped GCC 14 ASan/UBSan: 2/2 focused tests with leak detection enabled; and
- independent pinned-snapshot probe: destination remains at 50 pages while the live WAL source grows to 1,029 pages.

## Highest-priority next work

The sole remaining `unlink_sqlite_family(path_)` production call is still reached by `load(reset=true)`. It should be replaced by an explicit administrative transition carrying expected durable identity, owner generation, namespace proof, and a durable receipt.

After that, add a deterministic VFS crash-cut model across backup, canonicalization, serialization, atomic publication, and directory sync; then move hostile SQLite interpretation into a disposable resource-limited worker.

No arbitrary power-loss, hostile-directory isolation, full-project or bundled-SQLite sanitizer, Windows runtime, distributed convergence, confidentiality, anonymity, metadata-hiding, key-lifecycle, or secure-erasure property is claimed.

Full evidence is under `REVISION_EVIDENCE/rev0823/`.

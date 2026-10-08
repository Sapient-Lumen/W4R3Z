# Rev0823 audit

## Boundary selected

Rev0822 correctly separated live source capture from destination publication, but its private-copy protocol still sampled geometry before the copy and then invoked `sqlite3_backup_step(..., -1)`. The governing invariant for rev0823 is:

> One owned source connection may authorize one finite, snapshot-pinned sequence of copy effects. Every effect must remain bounded by geometry sampled inside that snapshot, preserve process and transaction authority, produce exact monotone progress evidence, and leave no partial destination authority on failure.

## Severe parent gap

The exact rev0822 source contains a separate early `PRAGMA main.page_count` observation and later asks SQLite to copy every remaining page in one call. SQLite documents that a negative step count copies all remaining pages, that remaining/page-count observations correspond to the most recent step, and that source modifications can restart a backup unless a source read transaction pins the snapshot. The parent therefore had no observation boundary between starting and completing a potentially large effect, and its after-the-fact geometry check could not prove transient work stayed within policy.

The defect is not characterized as memory corruption. It is an authority and resource-proof gap: policy was checked before and after, while the effect between those checks was unbounded and could track a changing source.

## Production correction and refactor

`sqlite_live_backup.cpp` is a new separately linked production owner. It rejects explicit and hidden entry transactions, begins a fresh source transaction, performs the reads that pin the source image, and verifies exact page geometry through the shared geometry owner. It copies at most 64 pages per step and derives a finite maximum number of calls from the pinned page count.

Before and after every observer cutpoint it reasserts process incarnation and `SQLITE_TXN_READ`. After every SQLite step it requires the reported page count to equal the pinned count, remaining pages to stay within that count, and remaining work to decrease strictly. A restart, lost read transaction, non-progress result, or step overrun denies further effects.

Cleanup was also made part of the invariant. `sqlite3_backup_finish` and source rollback results are captured without allocation, incomplete private destinations are rolled back, and diagnostic formatting happens only after cleanup evidence exists. This avoids an exception-allocation path silently skipping rollback.

The snapshot seal no longer owns raw `sqlite3_backup_*` lifecycle. It delegates to the bounded owner, then continues its existing hardening, canonicalization, exact serialization, digest, verification, and publication pipeline. Live page geometry and serialized-header geometry now share one public, monotone policy boundary.

## Executable proofs and a false-proof removal

The 34-check focused live-backup executable covers fixed-step progress, exact page-count and remaining evidence, an 8 MiB concurrent WAL writer while the destination remains on the old pinned image, lost snapshot authority before the next step, rollback of a partial destination, named-destination rejection, and explicit/implicit transaction rejection.

The 94-check seal executable adds a deterministic source trace cutpoint. A writer commits 4 MiB immediately after the seal's early page-count observation. The early observation still describes the old image; the bounded owner pins the enlarged image and rejects it before copy under the test policy.

During review, a VFS open-count assertion was found to be vacuous because it did not observe private in-memory opens. It was removed rather than decorated. The trace cutpoint now proves the intended event ordering directly.

## Validation

- exact rev0822 parent: ZIP 25/25 and directory 21/21;
- source patch replay: all 176 active files and 14 changed active files match byte-for-byte;
- Debug all-target GCC build passed; final dependency closure reported no work;
- one uninterrupted complete CTest gate: 103/103 in 81.09 seconds;
- eight structural audits: 305/305;
- focused stress: 50/50 executions and 3,200/3,200 checks;
- GCC 14 and Clang 17 `-Werror`: both focused targets pass in each lane;
- scoped GCC 14 ASan/UBSan: both focused tests pass with leak detection enabled; bundled SQLite and the full project are not claimed instrumented; and
- independent backup probe: a pinned 50-page image remains 50 pages while a WAL writer grows the live source to 1,029 pages.

## Broader audit and explicit limits

`load(reset=true)` remains the sole production caller of `unlink_sqlite_family(path_)`. A boolean load option still mints destructive family authority and should become an explicit administrative transition carrying expected prior identity, owner generation, namespace proof, and a durable receipt.

The bounded owner addresses online-copy work for a cooperative SQLite source connection. It does not isolate hostile same-UID directory writers, prove arbitrary power-loss behavior, sandbox hostile SQLite interpretation, or establish distributed convergence, confidentiality, anonymity, metadata hiding, key lifecycle, Windows behavior, or secure erasure.

# Revision notes: AnonSync rev0862

## Mission increment

A bounded result is not a bounded operation when SQLite may perform unbounded
internal work to produce it. Rev0862 gives checkpoint-sidecar hydration one
finite, typed execution budget bound to the same exact connection generation
and transaction as its returned evidence.

## Principal corrections

1. Added `SyncSqliteSidecarSnapshotExecutionBudget`, a final exact-generation
   adapter over the established `SqliteVerificationBudget` singleton callback
   owner.
2. One budget now spans the claimed-path frontier and all nested schema,
   apply-intent, manifest, chunk, and lineage reads in one transaction.
3. Added reviewed public ceilings for progress callbacks, opcode interval, and
   monotonic elapsed milliseconds; callers may tighten but cannot widen them.
4. Recovered `SQLITE_INTERRUPT` into typed progress-limit or elapsed-limit
   failures with sticky observed/limit diagnostics.
5. Made `detach()` an irreversible authority revocation and added a live-
   transaction regression proving detached objects cannot authorize work.
6. Ordered teardown so callback revocation precedes commit on success and
   budget destruction precedes rollback on failure.
7. Removed duplicate fail-stop checks from the progress callback hot path while
   preserving process/thread fencing before sticky state reads.
8. Migrated every registered Python CTest audit command to `python -B -S` and
   made complete hermetic coverage an executable package invariant.
9. Expanded the focused runtime corpus to 35 checks and the structural audit to
   94 checks; release verification from rev0862 requires the generic budget
   owner and audit sources.

## Compatibility

No protocol or durable-document spelling changes. Valid work below the reviewed
limits is unchanged. Excessive VM work or elapsed time, widened caller limits,
wrong-generation execution authority, detached authority, stale transaction
authority, or partial post-interruption publication is newly rejected.

## Validation summary

GCC Debug all-target closure; 162/162 registered tests in nine exact ranges;
49/49 registered audits; 35/35 focused checks; 94/94 new audit checks; 100
focused and 100 audit repeat executions; Clang 17 `-Werror` focused and
integrated-core build with 35-check and 609-check runtime; GCC ASan+UBSan focused
and domain runtime with leak detection plus 25 focused repeats; exact replay of
the 15-file delta across all 311 active files; sealed-parent verification 26/26
ZIP and 22/22 directory.

## Deliberate nonclaim

SQLite's progress callback is cooperative and approximate. This revision does
not claim a hard wall-clock deadline, bounded lock waits outside callback
opportunities, a budget for every SQLite path, full-project sanitizer coverage,
or isolation of hostile persistence interpretation from the principal process.

# Rev0980 — replica database incarnation and recovery epoch

## Database-lineage correction

- Raised the durable replica SQLite schema from v6 to v7.
- Added one CSPRNG-minted canonical database incarnation and one nonzero recovery epoch to `sync_replica_meta`.
- Bound both fields into every current SQLite cutpoint.
- Preserved the exact released v6 schema and cutpoint as a migration source.
- V6 migration retains operations, evidence states, visible heads, outbox and clock state, limits, policies, and the exact historical-version pin set while minting the new lineage and advancing state generation once.
- Added an exact `advance_database_recovery_epoch_or_throw` transaction for explicit restore/replacement workflows.

## Retention authority correction

- Added database incarnation and recovery epoch to retention plans and mark requests.
- Advanced the durable candidate witness to v2, writer-fenced page digest to v2, and exact deletion-free mark digest to v5.
- Re-proved incarnation, epoch, and state generation before payload observation, immediately before durable publication, and after publication.
- Kept the fixed-width retention-record layout unchanged: the opaque candidate witness carries the new lineage binding.
- Advanced service status to `anonsync.peer-service.status.v24` and the local retention response to `anonsync.local-retention-plan.response.v6`.

## Focused regressions

- Independent databases with identical causal contents no longer alias cutpoints or retention witnesses.
- Exact v6 migration preserves historical pins and mints a distinct lineage.
- Wrong incarnation, epoch, or cutpoint cannot advance recovery state.
- Explicit recovery advances epoch and state generation exactly once while preserving all other authority.
- Foreign-database and stale-pre-recovery mark requests fail at `retention_mark_publication` before payload observation.

## Adjacent audit/refactor

- Removed an unrelated eleven-file local-control/service prototype that had contaminated an early CMake source cache; none of its build results are retained as authority.
- Avoided a second retention-record format by binding lineage through the existing opaque candidate witness.
- Corrected two stale rev0966 labels: the historical-pin schema v6 was introduced by rev0973.
- Refactored the structural oracle to follow the shared cutpoint-authority helper instead of pressuring production to duplicate its digest grammar.
- Corrected the rev0980 release policy so it requires the changed SQLite-owner source audit; a package can no longer omit that authority while satisfying the revision-scoped file gate.
- Kept the limitation explicit: in-database lineage is not external exact-image anti-rollback authority.

## Product boundary

Rev0980 remains deletion-free. It adds no trusted clock, grace consumption, quota decision, collection quarantine, restore-loss UI, rename, reclaim, or unlink.

## Validation

Exact rev0980 C++ source passed a clean GCC 14.2 Debug graph (532/532 configured build edges), all 259/259 registered tests in an uninterrupted serial replay in 123.72 seconds, and an independent 40/40 GCC product replay in 67.12 seconds. The finalized source audits passed 43/43 SQLite-owner checks and 372/372 structural authority checks. Focused exact-source suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 30 retention-mark, 640 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 334 SQLite-owner, 470 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 158 local-control, 87/87 observer, and 6/6 observer-race checks. A clean Clang 17 Debug product dependency graph completed 243/243 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 40/40 product tests passed serially in 122.76 seconds with leak detection and halt-on-error. Focused sanitizer proof passed the 640-check payload-store suite in 16.57 seconds at 514,388 KiB peak RSS, the 470-check folder-owner suite in 21.90 seconds at 1,467,012 KiB peak RSS, and the 158-check local-control suite in 1.12 seconds at 106,900 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0979 parent SHA-256 matched 5fc1ee63e991a261b9473f7a80887eb2b010e5d6167dc09405dba20fb779f58f and passed 41/41 wrapper-aware package checks. Validation excluded the divergent local-control prototype, vanished or interrupted build caches, source-divergent workers, the superseded v6-only SQLite audit oracle, duplicate validators, and every result not bound to the reconstructed schema-v7 source. The binary-aware source patch reconstructed all 16/16 changed active files and the complete 573-file projection byte-for-byte and by mode. The final active implementation projection contains 573 files / 26,745,576 bytes with SHA-256 c3b2f86e2a279e4114a546260c4010af75030ae5cf03657beb5371f55405248f.

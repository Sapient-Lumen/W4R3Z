# Rev0982 — canonical replica-database backup and detached reproof

## Offline backup artifact

- Added `anonsync_sync database-backup-create --manifest ABSOLUTE_JSON --snapshot ABSOLUTE_SQLITE`.
- Added `anonsync_sync database-backup-inspect --manifest ABSOLUTE_JSON --snapshot ABSOLUTE_SQLITE`.
- Creation acquires the retained deployment singleton before source SQLite authority, then publishes one immutable create-new artifact; an existing destination is never replaced.
- Detached inspection requires the artifact and deployment manifest but does not open the live primary database family. The manifest supplies the exact deployment, role, normalized source path, folder, and actor authority used to attest the artifact binding.
- Output paths are rejected when they collide with the manifest, any configured SQLite family member, payload storage, or synchronized files.

## One canonical artifact

- Reused the retained bounded live backup and SQLite snapshot-seal owners rather than adding a second copy engine.
- Captures one transactionally pinned logical source image, canonicalizes it to sidecar-free rollback-journal format, hashes exact bytes, proves geometry, and publishes owner-only mode 0600.
- Brackets capture with complete current-schema source observations and a final rooted source reproof.
- Reopens the published artifact independently and repeats exact bytes, SHA-256, page geometry, schema-v7, deployment-binding, and cutpoint proof.
- The reviewed artifact ceiling is 512 MiB and 262,144 pages. This remains a bounded resident implementation, not a streaming or total-RSS claim.

## Detached inspector

- SQLite can report a `SQLITE_DESERIALIZE_READONLY` in-memory image as writable through `sqlite3_db_readonly()`, so the first detached verifier rejected a valid sealed image.
- Named forensic files retain the strict `sqlite3_db_readonly()==1` gate.
- Detached images instead prove filename-free MEMORY-journal identity, retained `query_only`, and an actual `SQLITE_READONLY` write denial before complete schema restoration.
- The process regression requires both the misleading introspection result and the real denied write.

## Audit/refactor: typed rollback authority

- The first detached write probe emitted raw `SAVEPOINT`, `ROLLBACK TO`, and `RELEASE` SQL beside the existing transaction owner.
- The final verifier receives the exact outer `SyncSqliteTransactionAuthority`, creates one nested `SyncSqliteSavepoint`, rolls it back through that typed owner before interpreting the result, and uses a separate guard only to restore `PRAGMA query_only`.
- Production deployment-binding code now contains no raw savepoint-transition literals. The transaction-stack authority audit and the backup audit both enforce that boundary.
- The same audit removed retention of multiple complete causal/outbox snapshots beside the resident artifact: each full observation is restored and validated, then immediately reduced to one compact exact cutpoint witness.
- Corrected the first CMake integration, which named a nonexistent profile library, to link the retained deployment/profile owner actually used by the shipping graph.

## Adjacent service-lifecycle correction

- The sanitizer product lane exposed a completed-drain race: the service can send a valid stop response and remove its owner-only Unix socket before the client performs its final pathname reproof.
- The local client now carries an explicit completion-path policy. Only `stop` permits exact post-response `ENOENT`; if the path survives, it must still be the same owner and inode at mode 0600.
- Response validation remains mandatory after pathname disappearance, and every non-stop command retains the strict final socket-identity requirement.
- A deterministic one-shot Unix server regression unlinks before replying and proves successful stop completion, malformed-stop rejection, and status-query rejection under the same disappearance.

## Recovery bridge and nonclaims

- The backup response supplies the exact recovery expectation embedded in the artifact.
- Restore still requires an offline, rollback-preserving database-family replacement followed by `database-recovery-advance`; rev0982 intentionally does not add an in-place restore writer.
- The artifact contains only the primary replica SQLite database. It excludes payload bytes, folder catalog, membership, effect and anchor databases, rooted files, network state, and durable retention-mark age.
- It is not a whole-share backup, an authenticated transport envelope, external anti-rollback authority, trusted time, or permission to collect payloads.
- Unknown continuity still requires retention-age reset.

## Runtime oracle

- The real-process oracle covers path confinement, source-family byte stability, create-new collision, mode and link count, exact digest and page geometry, sidecar absence, source-absent detached inspection with required exact deployment binding, damaged-artifact rejection, recovery advance, and old-artifact immutability.
- The final oracle passed 265 checks.

## Boundary

Rev0982 makes one database backup artifact inspectable and suitable for the
next offline replacement ceremony. It does not yet automate database-family
replacement, preserve a rollback family, verify payload-store completeness,
reset retention age durably, or provide an external monotonic continuity
anchor.

## Validation

Exact rev0982 active source passed a fresh GCC 14.2 Debug graph (534/534 configured build edges), all 261/261 registered tests after final release-prose sealing, and an independent 41/41 product replay. Focused proofs passed 334 SQLite-owner checks, 38 deployment-binding checks, and the 265-check database backup/recovery process oracle. Source audits passed 27/27 deployment-binding checks, 100/100 transaction-stack authority checks, 27/27 backup checks, and 393/393 final structural authority checks. A fresh Clang 17 Debug product dependency graph completed 245/245 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 41/41 product tests were accounted for in bounded fresh invocations with leak detection and halt-on-error, and focused sanitized proofs passed the same 334 and 38 checks. Aggregate authoritative-log inspection retained no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0981 parent SHA-256 matched 1f27e580cae7e25d5b0f55df14688ff975e4e3b88f103a96e36f47421716b934 and passed 41/41 wrapper-aware package checks. The binary-aware patch reconstructed all 17 changed active files and the complete 577-file projection byte-for-byte and by mode. The final active implementation projection contains 577 files / 26,906,635 bytes with SHA-256 3e15ca2ba0f24c68b808290b11d64e0cd8b3d5b05c99eca5a7be358a988faaf4. Validation excluded the raw-savepoint prototype, source-divergent workers, vanished build trees, stale caches, and interrupted runs without terminal evidence.

Archive: `AnonSync-rev0982-2026.08.02.23.59-backupartifact-detachedverify-recoverybridge-scapolite.zip`

Codename: **scapolite**

# Rev0981 — offline database recovery and deployment singleton

## Operator recovery surface

- Added `anonsync_sync database-recovery-inspect --manifest ABSOLUTE_JSON`.
- Added `anonsync_sync database-recovery-advance --manifest ABSOLUTE_JSON --expected v1:INCARNATION:EPOCH:CUTPOINT`.
- Inspection is current-schema, existing-only, descriptor-rooted, deployment-bound, and read-only.
- Advance first performs the same descriptor-rooted forensic observation and rejects a stale expectation before writable SQLite authority is opened.
- Canonical lowercase SHA-256 fields and a positive canonical decimal epoch are required.
- An accepted expectation is independently re-proved by the rev0980 exact `BEGIN IMMEDIATE` recovery-epoch transition.
- Responses explicitly deny payload, catalog, rooted-file, network, and external anti-rollback authority.

## Stale-expectation audit/refactor

- The first retained implementation constructed a writable operational database and mutable SQLite owner before discovering that an expectation was stale.
- The final ceremony owner retains only the deployment manifest, singleton, and label. Each forensic or writer handle is short-lived.
- Malformed expectations fail during canonical parsing. Noncanonical, foreign-incarnation, future-epoch, foreign-cutpoint, and consumed-token cases are rejected through the read-only forensic profile before any writable open.
- The process oracle fingerprints the exact SQLite family by membership, mode, size, and SHA-256 around every rejection class, proving that stale authority cannot trigger WAL recovery, SHM creation, checkpointing, migration, journal transitions, or another writer-side effect.
- The forensic preflight is not mutation authority: after it closes, the accepted token is rechecked under the existing `BEGIN IMMEDIATE` transition.

## Lifecycle correction

- `anonsync_sync once` now acquires the same deployment singleton as the retained service before route, TLS, peer, folder, or network authority.
- Offline inspection and recovery advance acquire that singleton before opening SQLite.
- Duplicate-service diagnostics now name another AnonSync process rather than incorrectly limiting the collision to services.

## Read-only database refactor

- Added `ExistingForensicReadOnly` to the shared process-facing operational database wrapper.
- Selected the exact descriptor-rooted read-only VFS and `SQLITE_OPEN_READONLY` without creation fallback.
- Applied connection-local exclusive WAL indexing and the hardened query-only profile before the first page read.
- Extracted shared attested primary-database writer and read-only seams from the retained folder-process owner.
- Corrected the first refactor's pre-profile schema read, which attempted read-only WAL shared-memory access before private indexing was selected.

## Commit-result and route-order audit/refactor

- The recovery owner previously committed the new epoch and only then copied its owning string result fields. A host allocation failure at that point could report an exception after durable success.
- The final owner constructs the complete result before `COMMIT` and statically requires a nothrow move across the committed cutpoint. Process death or output failure can still make command completion observationally uncertain; a fresh read-only inspection is the recovery oracle rather than blind token reuse.
- The one-shot singleton regression now supplies a missing native-I2P private-destination file. Ownership must fail before route parsing can open that path, proving the singleton order with an authority-bearing route rather than an incomplete syntax-only invocation alone.

## Runtime and audit

- Added a 105-check real-process recovery oracle covering byte-stable inspection, hidden unrelated stores, canonical parsing, three stale expectations, exact advance, token reuse, restart inspection, and full non-lineage status preservation.
- Extended the retained-service process oracle to reject both offline inspection and intentionally incomplete one-shot synchronization while the exact deployment owner is live.
- Advanced the database-open policy source audit to v22 and 48 checks.
- Registered the recovery process oracle in the normal product lane.

## Boundary

Rev0981 makes the in-database recovery epoch operable. It does not validate a
backup, replace database files, provide an external monotonic counter, detect
exact whole-image rollback, reset retained-mark age, or add destructive
retention. Continuity uncertainty still requires a conservative retention-age
reset.

## Validation

Exact rev0981 active source passed a fresh GCC 14.2 Debug graph (532/532 configured build edges), all 260/260 registered tests after final release-prose sealing, and an independent 41/41 product replay. The 105-check real-process recovery oracle proved descriptor-rooted read-only inspection, byte-for-byte SQLite-family preservation for malformed and stale expectations, exact one-step advancement, consumed-token rejection before writable open, narrow authority, and deployment-singleton ordering. The database-open policy audit passed 48/48 checks and the structural authority audit passed 385/385 checks. A fresh Clang 17 Debug product dependency graph completed 243/243 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 41/41 product tests passed serially with leak detection and halt-on-error. Aggregate authoritative-log inspection retained no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0980 parent SHA-256 matched 0fc470ab43ce97374e1a562f9c2c275b18bbc6f4e3f8c27127711ed7b18ca40d and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed active files and the complete 574-file projection byte-for-byte and by mode. The final active implementation projection contains 574 files / 26,812,446 bytes with SHA-256 d399a8ad3f077bf3467752e4355933be71117cdfff0f4cd789cd0cfd445f1b16. Validation was rerun from the reconstructed exact source after the cloudtainer removed prior unsealed worktrees; all vanished, interrupted, stale-cache, and source-divergent results were excluded. The final wrapper directory and ZIP are publication-gated on 41/41 package checks, CRC integrity, canonical paths, absence of symlinks, and clean-extraction path/byte/type/mode equality.

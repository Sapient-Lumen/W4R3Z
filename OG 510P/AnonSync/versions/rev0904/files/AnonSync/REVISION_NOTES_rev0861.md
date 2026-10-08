# Revision notes: AnonSync rev0861

## Mission increment

A recovery result assembled from multiple valid SQLite snapshots is not a valid
observation of any database generation. Rev0861 binds claimed sidecar paths,
schema, apply-intent, manifest, chunk, and lineage evidence to one exact read
transaction, then publishes the staged C++ value only after that transaction
commits.

## Principal corrections

1. Replaced multi-connection and multi-autocommit checkpoint-sidecar hydration
   with one read-only FULLMUTEX connection and one deferred read transaction.
2. Added `SyncSqliteSidecarClaimedPathSnapshotReader`, an exact-generation,
   separately linked claimed-path frontier owner.
3. Established the WAL snapshot with the claimed-path query as the first read
   and carried one typed transaction authority through every nested query.
4. Added path-count, path-byte, manifest-row, chunk-row, lineage-row, and shared
   metadata ceilings with exact `expected + 1` sentinels.
5. Forced byte-exact `COLLATE BINARY` identity for session, worker, lease,
   state, path, and nested manifest joins even when the durable schema declares
   a hostile `NOCASE` collation.
6. Cached schema inventory once per snapshot and removed per-path table probes.
7. Staged the complete result locally and published it only after `COMMIT`
   through a statically nonthrowing move, leaving caller-visible output sticky
   at its initialized baseline on every failure.
8. Added a 27-check WAL/authority/collation corpus and a 69-check structural
   audit; packages from rev0861 onward must contain both.

## Compatibility

No protocol or durable-document spelling changes. Valid evidence from one
snapshot is unchanged. Cross-generation, nonbinary, malformed, ambiguous,
stale, foreign, or over-budget evidence is newly rejected before publication.

## Validation summary

GCC Debug all-target closure; 162/162 registered tests in nine exact ranges;
49/49 registered audits; 27/27 focused checks; 69/69 new audit checks; Clang 17
`-Werror` owner and integrated-core build with focused and 607-check domain
runtime; GCC ASan+UBSan focused and domain runtime with leak detection and 25
repeated focused executions; exact replay of the nine-file delta across all 311
active files; sealed-parent verification 26/26 ZIP and 22/22 directory.

## Deliberate nonclaim

The returned rows and copied bytes are bounded, but the claimed-path
`SELECT DISTINCT` does not yet carry a finite SQLite VM-step or wall-time
budget. A duplicate-heavy durable table can therefore spend more internal work
than the small returned frontier suggests. This is recorded as next work rather
than hidden behind the output limits.

# Replica database lineage and retention-witness audit — rev0980

## Mission boundary

AnonSync exists to replace Resilio Sync with one practical C++ folder-sync product. This revision remains a deletion-free prerequisite for deliberate version retention: it prevents retention evidence produced for one replica database lineage from being mistaken for evidence about another database that happens to contain the same causal rows. It does not add collection, quota enforcement, trusted time, rename, quarantine, reclaim, or unlink.

## Defect: identical databases could alias retention authority

Rev0979 bound the retention mark to SQLite `state_generation`. That closes digest ABA during ordinary forward mutation in one retained database image, but two independently created replica databases can have identical operations, evidence, pins, visible state, policy, outbox, and generation. Before rev0980 they could therefore produce the same restart-stable candidate witness over one shared payload store. A stale request from database A could be presented to database B and survive every content-based comparison.

The defect matters before destructive collection exists. Once grace, quota, or collection authority consumes a durable mark, cross-database aliasing could inherit age or policy evidence that was never established for the current replica lineage.

## Schema v7 lineage

`sync_replica_meta` schema v7 adds two exact fields:

- `database_incarnation_sha256`: a canonical SHA-256 value minted from 32 CSPRNG bytes with a domain-separated folder/actor binding whenever a new database lineage is created; and
- `database_recovery_epoch_be`: a nonzero monotonic epoch initially set to one.

Both fields participate in the v7 SQLite cutpoint together with all prior causal, policy, outbox, clock, and historical-pin authority. Independent databases with identical logical contents therefore have different cutpoints and different retention witnesses.

The implementation uses OpenSSL `RAND_bytes` and fails closed if entropy acquisition fails. It does not derive the incarnation from pathnames, timestamps, PID, device IDs, or current database contents.

## Exact v6 migration

The released historical-pin schema remains embedded as an exact v6 schema and cutpoint oracle. Migration first restores and attests the complete v6 model, evidence states, outbox, clock state, limits, policy generation, and canonical historical pin set. In the same writer transaction it mints a new database incarnation, starts recovery epoch one, advances state generation once, publishes schema v7, and re-attests the complete successor cutpoint.

Pre-v6 migrations continue to restore their exact historical schema before the same v7 publication path. V6 pins are preserved; pre-v6 sources seed an empty pin set exactly as before. Unknown or lexically similar schemas are rejected rather than guessed.

## Explicit recovery epoch

`advance_database_recovery_epoch_or_throw` is an exact operator/recovery boundary. The caller supplies the current incarnation, recovery epoch, and v7 cutpoint. Under `BEGIN IMMEDIATE`, the owner restores and re-attests the complete current database, rejects stale expectations, increments the recovery epoch and state generation with overflow checks, preserves every causal/policy/outbox/clock/pin fact, publishes one new v7 cutpoint, and commits atomically.

This API is intentionally not wired to an automatic startup guess. A recovery tool can call it after a known restore, replacement, or rollback event; ordinary mutation cannot silently reset it.

## Retention-witness binding

The retention planner and mark request now carry the exact database incarnation and recovery epoch in addition to state generation. The following domains advance:

- restart-stable candidate witness: v2;
- writer-fenced candidate-page digest: v2; and
- exact deletion-free mark digest: v5.

All three bind folder identity, database incarnation, recovery epoch, state generation, causal/evidence/pin/visible roots, physical and transient payload roots, and their domain-specific live or candidate fields. Pre-observation, pre-publication, and post-publication SQLite brackets compare all three lineage values.

The fixed-width payload-retention record format does not change. Its opaque durable-candidate witness now contains the v2 lineage binding, so an older v1 witness conservatively fails equality without creating a second record codec or downgrade parser.

## Runtime proof

Focused tests establish:

1. two independent empty databases with identical causal facts and state generation mint different incarnations and v7 cutpoints;
2. exact v6 migration preserves pins and all prior authority while minting one new lineage;
3. stale incarnation, epoch, or cutpoint expectations do not mutate the database;
4. explicit recovery increments epoch and generation exactly once while preserving all other state across restart;
5. two replica owners over the same payload store and identical causal contents produce different retention witnesses;
6. a database-A mark request is rejected by database B before payload observation while the exact store writer lease is independently held; and
7. a pre-recovery request is rejected after epoch advance even though causal and payload digests and the public history cutpoint remain unchanged.

## Adjacent audit and rejected work

A divergent unsealed rev0980 prototype modified eleven local-control and service files and became the accidental source of an early CMake cache. It was reduced to a forensic patch, removed, and every build result from that source was excluded. The accepted revision was reconstructed from the sealed rev0979 bytes and limited to the lineage, retention, rendering, tests, documentation, audit, and release-policy surfaces required by this correction.

The audit also retained the fixed-width retention record rather than adding a second schema merely to duplicate lineage fields already transitively bound by the candidate witness. This reduces migration surface and prevents two competing freshness definitions.

A final provenance and audit-shape pass corrected two stale labels that called schema v6 a rev0966 schema; durable historical-version pins and schema v6 were introduced by rev0973. The structural oracle now follows the shared `append_cutpoint_authority` helper when checking state, policy, causal, evidence, visible, and outbox roots, rather than requiring those fields to be duplicated inside the v7 wrapper. The same pass found that the revision-scoped package verifier required the changed broad structural audit but not the changed SQLite-owner source audit; rev0980 now requires both, and the structural package-policy oracle verifies that requirement.

## What this proves

Within a retained or explicitly advanced SQLite lineage, independent databases and explicit recovery epochs cannot alias retention candidate, page, or deletion-free-mark witnesses merely because their logical contents match. A future collector can require exact current lineage equality before treating a mark as candidate evidence.

## What this does not prove

The incarnation and recovery epoch live inside the database they describe. Restoring an exact whole-database image also restores both values. Rev0980 is therefore not external anti-rollback authority and does not detect an unreported exact-image rollback. A destructive retention feature still requires one of:

- an external monotonic anchor;
- a recovery workflow that always advances the epoch after restore/replacement; or
- a conservative rule that resets all mark age and collection eligibility whenever continuity is uncertain.

No trusted clock, grace consumption, quota choice, collection quarantine, restart collection state machine, user-visible loss preview, reclaim, or unlink is added.

## Next safe edge

Define the operator-visible database recovery workflow and trusted-time/rollback policy before exposing mark age as authority. Then model one deletion-free collection staging protocol that reacquires every causal, transient, process-live, store-writer, and exact-inode root; completely rehashes candidate bytes; moves them to a collection-specific quarantine; survives restart; re-proves policy and current lineage; and only then permits unlink under explicit retention and ENOSPC semantics.

## Validation

Exact rev0980 C++ source passed a clean GCC 14.2 Debug graph (532/532 configured build edges), all 259/259 registered tests in an uninterrupted serial replay in 123.72 seconds, and an independent 40/40 GCC product replay in 67.12 seconds. The finalized source audits passed 43/43 SQLite-owner checks and 372/372 structural authority checks. Focused exact-source suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 30 retention-mark, 640 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 334 SQLite-owner, 470 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 158 local-control, 87/87 observer, and 6/6 observer-race checks. A clean Clang 17 Debug product dependency graph completed 243/243 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 40/40 product tests passed serially in 122.76 seconds with leak detection and halt-on-error. Focused sanitizer proof passed the 640-check payload-store suite in 16.57 seconds at 514,388 KiB peak RSS, the 470-check folder-owner suite in 21.90 seconds at 1,467,012 KiB peak RSS, and the 158-check local-control suite in 1.12 seconds at 106,900 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0979 parent SHA-256 matched 5fc1ee63e991a261b9473f7a80887eb2b010e5d6167dc09405dba20fb779f58f and passed 41/41 wrapper-aware package checks. Validation excluded the divergent local-control prototype, vanished or interrupted build caches, source-divergent workers, the superseded v6-only SQLite audit oracle, duplicate validators, and every result not bound to the reconstructed schema-v7 source. The binary-aware source patch reconstructed all 16/16 changed active files and the complete 573-file projection byte-for-byte and by mode. The final active implementation projection contains 573 files / 26,745,576 bytes with SHA-256 c3b2f86e2a279e4114a546260c4010af75030ae5cf03657beb5371f55405248f.

# Bounded reconciliation history access audit — rev0999

## Product reason

AnonSync's first supported workflow is a Linux/headless multi-terabyte media
share. A four-terabyte payload can require 65,536 bounded 64 MiB response
windows. Rev0998 bounded payload-byte ownership, but each window still caused
complete retained-replica reconstruction on the requester, responder, and
receiver paths. With the 100,000-operation product frontier, that shape could
turn one large-file transfer into billions of unrelated operation-row decodes.
That is incompatible with the memory and latency discipline required to replace
Resilio Sync on a large media tree.

## Defect

Before rev0999, one continued reconciliation turn performed these history-wide
reads:

1. `make_request_or_throw()` called the complete SQLite snapshot owner merely to
   re-prove folder and local-actor identity.
2. `serve_request_frame_or_throw()` called that complete snapshot owner and then
   `evidence_page_or_throw()` reconstructed and sorted the complete retained
   model again to emit one bounded page.
3. `apply_response_or_throw()` reconstructed the complete local model merely to
   locate one same-path predecessor for content-defined reuse.

At 65,536 windows this admitted 262,144 complete model reconstructions before
counting terminal admission work. The problem scaled with total retained causal
history rather than the one active payload window.

## Retained C++ design

### Fixed owner identity cutpoint

`SyncReplicaSqliteIdentityCutpoint` transactionally re-attests the exact schema,
foreign-key mode, typed metadata row, folder, local actor, configured limits,
database incarnation, and recovery epoch. It decodes no operation, visible,
outbox, clock, or retention-pin row. Reconciliation request and response hot
paths use this fixed observation instead of `snapshot_or_throw()`.

Constructor-time complete replica reconstruction remains the cold authority. A
hot identity cutpoint does not become aggregate content proof.

### Primary-key evidence page

`evidence_page_or_throw()` now:

- reads and validates current typed metadata in one deferred transaction;
- rejects a stale expected evidence-set digest before operation-row access;
- validates a continuation cursor through one exact primary-key lookup;
- walks `sync_replica_operations` through
  `WHERE operation_id>? ORDER BY operation_id LIMIT ?`;
- binds the SQL limit to the requested page frontier plus one lookahead row;
- decodes each returned canonical operation through the existing strict row
  attestation; and
- commits only after the transaction retains snapshot authority.

It does not rebuild `SyncReplicaModel`, materialize all evidence operations, or
sort retained history in memory.

### Path-bounded predecessor reproof

Receiver-side content-defined reuse no longer searches a complete local
operation vector. Each named predecessor is re-proved through the existing
transactionally pinned exact-path cutpoint. The selected operation is copied
out of that cutpoint before its lifetime ends, then exact immutable payload
access and inode reproof proceed as before.

### Deliberate terminal boundary

Remote operation admission still reconstructs and validates the complete causal
model when a new operation is finally committed. Rev0999 removes that work from
every payload-progress turn; it does not silently weaken the terminal causal
admission boundary.

## Runtime and SQL-shape proof

The SQLite-owner regression populates 48 operations for identity proof and 72
operations for evidence paging, installs `sqlite3_trace_v2`, and requires:

- one metadata/schema/foreign-key identity read with no operation or visible
  projection;
- one primary-key range query for a first page;
- one exact cursor lookup plus one range query for a continuation;
- zero operation-row access for a stale source digest; and
- zero complete operation or visible projection in every bounded page case.

The multi-range content-defined service regression traces both peers. Its first
payload-progress turn must perform zero complete operation and visible
projections. Across the complete transfer the source may use only bounded
primary-key evidence pages. The receiver may use fixed identity and exact-path
reads; the only allowed complete reconstruction is the existing terminal remote
admission.

## Trust boundary and nonclaims

This is a hot-path scale correction, not a new hostile-local-database model.
Cold open still completely reconstructs and validates durable replica state.
Like the released targeted path and targeted publication cutpoints, bounded
reads assume the AnonSync-owned SQLite connection is the only cooperative
writer. They do not re-hash the entire operation table on every page and do not
claim protection from a noncooperating same-UID process that edits the database
behind the deployment singleton.

Rev0999 does not add cross-file chunk discovery, rename/move identity,
placeholder selective sync, Android lifecycle/storage adapters, quota or ENOSPC
qualification, public-route throughput proof, or completed multi-terabyte soak
evidence. It does not change reconciliation protocol generation 7.

## Adjacent audit/refactor

A competing unsealed cross-file-candidate prototype repeatedly rewrote the first
known rev0999 worktree and started a build against internally inconsistent
sources. That tree and its build results were excluded. The retained change was
reconstructed over exact sealed rev0998 bytes in a randomized authority.

The refactor also centralizes current owner-metadata reproof for identity,
targeted-path, and evidence-page readers and removes the now-unused
history-vector operation lookup helper from the reconciliation service.

## Validation

Exact rev0999 source passed a fresh GCC 14.2 Debug graph (551/551 configured build edges)
and a no-work bundled-SQLite re-attestation; all 282/282 registered tests were accounted
for, including the two final documentation-sensitive source audits, and an independent 47/47
product replay passed. Focused GCC proofs passed 380 SQLite-owner, 122 reconciliation-
service, and 536 folder-owner checks. Source audits passed 21/21 bounded-history-access,
34/34 direct-source-frame, 27/27 response-memory-shape, 30/30 targeted-path-cutpoint, and
503/503 structural-authority checks. A fresh Clang 17 Debug
AddressSanitizer/UndefinedBehaviorSanitizer product dependency graph completed 262/262 edges
across bounded resumptions and reached a no-work re-attestation; all 47/47 product tests
passed with leak detection and halt-on-error. Focused sanitizer proofs passed 380 SQLite-
owner, 122 reconciliation-service, and 536 folder-owner checks; the folder-owner proof
completed in 28.75 seconds at 1,689,024 KiB peak RSS, while the complete product lane peaked
at 1,692,312 KiB. Aggregate retained-log inspection found no compiler, linker,
AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic.
The exact rev0998 parent SHA-256 matched
dbc9b4f7fb972abd2ecfa10cabebeed6b5bba7c8c277d511bf2834d87bfd702f and passed 41/41 wrapper-
aware package checks. The binary-aware source patch reconstructed all 17/17 changed wrapper
paths, all 16/16 changed project paths, all 13/13 changed active paths, and the complete
610-file active projection byte-for-byte and mode-for-mode. The final active implementation
projection contains 610 files / 28,125,448 bytes with SHA-256
5110b2cce7e9f19917c9bf10a958fb22c4a42eee1affdadb64b5c88128153d68. Validation excluded
divergent unsealed rev0999 prototypes, an orphaned exclusion guard that named the live
authority, unrelated compiler/test lanes, vanished remount-era worktrees and build caches,
interrupted build chunks, and every result not re-proved from the reconstructed exact
source. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality
checks remain mandatory publication gates.

## Archive

AnonSync-rev0999-2026.08.05.02.52-primarykeypage-identitycutpoint-historycold-taaffeite.zip

Codename: `taaffeite`

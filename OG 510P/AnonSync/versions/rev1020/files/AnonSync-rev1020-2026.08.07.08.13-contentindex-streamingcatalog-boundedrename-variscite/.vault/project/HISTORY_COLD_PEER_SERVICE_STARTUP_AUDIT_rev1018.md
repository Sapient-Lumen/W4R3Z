# History-cold peer-service startup audit — rev1018

## Product question

AnonSync's first supported workflow is Linux/headless synchronization of media
trees measured in terabytes, with selective synchronization and delta transfer
as mandatory capabilities. Rev1017 added an owner-side process-resource time
series so memory could be measured rather than guessed. The first adjacent code
audit found a concrete startup multiplier before a larger sparse-tree run was
useful: several peer-facing services reconstructed the complete retained
replica or file-effect history immediately after their durable owners had
already performed the required cold reconstruction.

For a large share, that duplicated row decoding, canonical-operation ownership,
vector growth, payload ownership in the legacy file-effect path, digest work,
and peak resident memory at exactly the point where several share processes may
start together. It did not add authority. The service constructors needed only
stable folder/actor identity and persisted compatibility limits.

## Defect

`SyncReplicaSqliteOwner` intentionally remains an O(history) reference owner.
Its constructor performs a complete restore and re-attestation before the owner
is published. Rev1017 nevertheless constructed the network services as follows:

- `SyncReplicaDeliveryService` called `snapshot_or_throw()` again;
- `SyncReplicaReconciliationService` called `snapshot_or_throw()` again; and
- `SyncReplicaFileDeliveryService` indirectly repeated the replica snapshot and
  directly called the file-effect owner's complete `snapshot_or_throw()`.

The evidence and reconciliation services used only `folder_id`, `local_actor`,
and durable model limits. The file service used only the file-effect folder and
payload policy. Complete retained operation/effect vectors were therefore
pure startup waste.

## Correction

Rev1018 composes each service from a transaction-pinned bounded cutpoint:

- evidence delivery uses `SyncReplicaSqliteIdentityCutpoint`;
- reconciliation uses the same cutpoint for folder, actor, and model limits;
- file delivery inherits that bounded evidence construction; and
- file-effect compatibility uses the new
  `SyncReplicaFileEffectSqliteIdentityCutpoint`.

The replica cutpoint re-attests the exact trigger-free schema, foreign-key mode,
typed metadata row, folder/local actor, database lineage, and persisted limits
without decoding retained operations or projections.

The file-effect cutpoint re-attests the exact schema, rooted directory binding,
folder identity, persisted limits, and state generation inside one deferred
transaction. It does not read `sync_replica_file_effects` or any payload blob.
The same canonical metadata-row decoder now feeds both the bounded cutpoint and
the complete file-effect snapshot, removing a duplicated 24-column codec that
could otherwise drift across schema changes.

No wire protocol, durable schema, payload format, local control schema, or
selection policy changed.

## Executable four-terabyte shape

The existing product-labelled source-frame memory regression now creates an
exact logical four-terabyte replica tree:

- 64 distinct current file operations;
- 64 GiB per file; and
- exactly 4 TiB of logical file extent.

The fixture intentionally does not allocate or write 4 TiB of payload bytes.
Its purpose is to bind service startup to a large-file tree shape while a
SQLite authorizer provides the semantic memory fence.

Two independent negative controls install read-denial fences on
`sync_replica_operations` and `sync_replica_file_effects`. A complete replica
snapshot and a complete file-effect snapshot must each fail through its fence,
proving that the oracle would detect the historical paths. Under the same live
fences, all three peer-facing service constructors must succeed and preserve
the exact folder and actor identity.

The test also arms the process-wide allocation probe at 64 KiB while the three
services are constructed. The accepted implementation performs zero
allocations at or above that threshold. This is an executable constructor
frontier, not an estimate derived from source spelling.

## Adjacent audit and refactor

The first implementation added a second hand-written file-effect metadata
query. The audit rejected that duplication. Rev1018 instead introduces one
fixed `LoadedEffectMeta` decoder for the exact 24-column metadata row and uses
it from both the bounded identity cutpoint and complete snapshot restoration.
The complete snapshot still independently decodes, validates, and hashes every
retained effect after the shared metadata prefix.

The source audit also verifies that complete snapshots remain available and
that the negative controls call them. The correction is not allowed to make the
cold durable-owner proof disappear merely to make service construction look
small.

## Product benefit and nonclaims

This removes an immediate repeated O(history) memory and I/O multiplier from
peer-service composition. It is particularly valuable when multiple share
processes restart together, because each process now pays its durable owner's
cold reconstruction once rather than paying additional complete-history loads
for evidence, reconciliation, and file-effect service setup.

Rev1018 does **not** make complete AnonSync startup constant-memory. The replica
and file-effect owners are still documented O(history) correctness owners and
perform one complete cold reconstruction. The four-terabyte fixture is logical
metadata, not a completed sparse-tree service run, not a throughput result, and
not a measured whole-process RSS envelope. It does not cover page cache,
allocator arenas, SQLite cache policy, manifest recovery, concurrent shares,
network transfer, selective hydration, ENOSPC, Tor, I2P, or Android.

The adjacent rev1018 sparse-service gate now performs that real
`resources-watch` measurement against two `anonsync_sync run` processes over an
exact aggregate 4,399,120,252,928-byte logical tree. Its low measured envelope
removes the need for a speculative second projector in this revision. The
remaining owner reconstruction is still O(history), so denser and much larger
history fixtures remain future scale gates. Product priority now returns to
identity-preserving rename/move, complete directory semantics, understandable
conflicts, selective-sync operator surfaces, and controlled ENOSPC.

## Validation

`Exact rev1018 source passed a fresh GCC 14.2 Debug graph (578/578 configured build edges), all 310/310 registered tests, and an independent 56/56 product replay. Focused GCC proofs passed 22 history-cold source-frame/startup checks, 26 real sparse multi-terabyte process checks, 90/90 folder-observer checks, 6/6 observer-race checks, and 557 folder-owner checks. Source audits passed 19/19 history-cold startup checks, 18/18 sparse multi-terabyte checks, and 690/690 structural authority checks. A fresh Clang 17 ASan/UBSan product graph completed 286/286 edges and all 56/56 product tests passed with leak detection and halt-on-error. The exact rev1017 parent SHA-256 matched and passed 41/41 wrapper-aware package checks. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The obsolete predictable-path validator, its kill guard, interrupted caches, and divergent branches are excluded.`

## Intended archive

`AnonSync-rev1018-2026.08.07.02.31-historycold-sparsefourterabyte-memoryproof-danburite.zip`

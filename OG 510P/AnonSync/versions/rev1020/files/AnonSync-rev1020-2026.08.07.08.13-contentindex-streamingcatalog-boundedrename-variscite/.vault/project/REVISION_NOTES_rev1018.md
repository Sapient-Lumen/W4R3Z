# Revision notes — rev1018

## Product move

Rev1018 removes three repeated complete-history loads from peer-service
construction and then measures the resulting real process boundary with two
selective-sync services over an exact aggregate sparse logical extent of
4,399,120,252,928 bytes.

The first supported workflow remains Linux/headless synchronization of
multi-terabyte media trees. Selective synchronization and delta transfer are
mandatory. This revision makes startup composition history-cold and proves one
bounded sparse namespace/memory shape; it does not claim dense-media throughput
or complete product parity.

## C++ implementation

- `SyncReplicaDeliveryService` and
  `SyncReplicaReconciliationService` now use the bounded transaction-pinned
  `SyncReplicaSqliteIdentityCutpoint` rather than reloading complete retained
  operation history.
- `SyncReplicaFileDeliveryService` uses a bounded
  `SyncReplicaFileEffectSqliteIdentityCutpoint` rather than loading all retained
  file effects and payload ownership merely to check identity and policy.
- One exact 24-column file-effect metadata decoder feeds both the bounded
  cutpoint and the complete snapshot. The durable reference owner still
  reconstructs and hashes the full effect state.
- `SyncReplicaFolderTraversalSummary` now reports checked
  `metadata_only_regular_file_logical_bytes` from each individually classified
  regular file's no-follow `st_size` observation.
- `SyncReplicaFolderPassReport` now carries the exact traversal segment's
  directory enumeration count, largest component batch, and largest
  simultaneously retained component count.
- `anonsync_folder run`, `anonsync_sync once`, and share-create initial-pass
  JSON expose those exact diagnostics without another filesystem walk.

## Runtime proof

The constructor oracle retains its exact logical 4 TiB history shape: 64 files
at 64 GiB. SQLite authorizer fences reject complete operation/effect history
reads, while evidence, reconciliation, and file-delivery services construct
under the same fences with zero allocations at or above 64 KiB.

The new product process regression creates 4,097 sparse 512 MiB files in each
of two independent shares. A default metadata-only policy with one deeper
materialization rule forces all 8,194 files to be classified while spending
zero selected file bytes and zero payload-mutation bytes. The two passes report
4,096-name maximum batches and two directory enumeration passes per share.

A 24-sample, 75 ms resource series observes both real services. The focused GCC
run measured 16,280 KiB aggregate peak sampled PSS and 60,796 KiB summed
lifetime peak RSS. Release tripwires are 1 GiB and 1.5 GiB respectively.

## Adjacent audit/refactor

A divergent unsealed CPU/I/O prototype and prose not reconstructible from the
sealed rev1017 cutpoint were removed. The retained source is recorded in a
persistent Git authority as the exact parent, the reviewed history-cold startup
commit, and the sparse resource-gate commits.

The audit also rejected a cosmetic duplicate memory high-water field. Rev1017
already carries Linux `ru_maxrss`; rev1018 composes that lifetime signal with
sampled PSS rather than adding another near-synonym.

## Compatibility and limits

No durable database schema, reconciliation protocol, delivery protocol,
payload format, local control response schema, or selective-sync policy format
changed.

Sparse logical extent is not allocated blocks, dense I/O, page-cache pressure,
network throughput, delta-transfer throughput, or disk amplification. The
4,097-entry directory is not a million-file tree. PSS is sampled and can miss
between-point transients. The owners remain O(history) and still perform one complete cold reconstruction.

Identity-preserving rename/move, complete directories and empty directories,
human conflict handling, placeholder selective sync, automatic eviction,
best-effort retention collection, quota/ENOSPC behavior, Android adapters, and
live public Tor/I2P qualification remain open.

## Validation

`Exact rev1018 source passed a fresh GCC 14.2 Debug graph (578/578 configured build edges), all 310/310 registered tests, and an independent 56/56 product replay. Focused GCC proofs passed 22 history-cold source-frame/startup checks, 26 real sparse multi-terabyte process checks, 90/90 folder-observer checks, 6/6 observer-race checks, and 557 folder-owner checks. Source audits passed 19/19 history-cold startup checks, 18/18 sparse multi-terabyte checks, and 690/690 structural authority checks. A fresh Clang 17 ASan/UBSan product graph completed 286/286 edges and all 56/56 product tests passed with leak detection and halt-on-error. The exact rev1017 parent SHA-256 matched and passed 41/41 wrapper-aware package checks. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The obsolete predictable-path validator, its kill guard, interrupted caches, and divergent branches are excluded.`

## Intended archive

`AnonSync-rev1018-2026.08.07.02.31-historycold-sparsefourterabyte-memoryproof-danburite.zip`

Codename: `danburite`

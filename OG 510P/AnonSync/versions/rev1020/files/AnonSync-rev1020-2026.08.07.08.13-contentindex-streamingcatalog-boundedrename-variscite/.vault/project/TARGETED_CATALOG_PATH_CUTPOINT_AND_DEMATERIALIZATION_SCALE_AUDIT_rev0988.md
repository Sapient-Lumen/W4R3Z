# Rev0988 targeted catalog path cutpoint and dematerialization scale audit

## Product problem

Rev0987 made metadata-only selection physically meaningful: an exact selected
predecessor can be removed from the synchronized root while its causal evidence
and independently verified private payload remain retained. The safety
bracketing was intentionally conservative, but one part was catastrophically
mis-composed for the first supported multi-terabyte workflow.

For every metadata-only file candidate, the dematerialization path reloaded the
complete folder catalog during planning, immediately before unlink, and again
after unlink. A production pass may admit 4,096 remote effects while the catalog
may contain as many as 1,000,000 paths. The resulting upper shape was therefore
12,288 complete catalog projections in one pass, in addition to the pass-level
catalog observations. Every projection rebuilt the vector and owned strings for
all retained paths. The behavior was bounded only in the formal sense; it was
severely wasteful in time, allocation churn, and peak-memory pressure and was
incompatible with the stated large-media-tree direction.

## Retained correction

Rev0988 adds one internal `FolderCatalogPathCutpoint`. It is loaded in one
SQLite deferred read transaction and contains only:

- the exact current schema/folder/root/attestation identity;
- the persisted folder limits and catalog state generation;
- the selective-sync generation, absence-fence generation, and policy digest;
- zero or one catalog entry selected by the canonical-path primary key.

The exact entry query is:

```sql
SELECT canonical_path,value_kind,size_bytes,content_sha256,
       operation_id,source_snapshot_sha256,last_seen_generation
FROM main.sync_replica_folder_catalog_entries
WHERE canonical_path=?;
```

The metadata row and path row are therefore from one SQLite snapshot. Path,
value kind, size, digests, operation identity, and generation are validated by
the same `load_modern_catalog_entry_row_or_throw` decoder used by the complete
modern-catalog loader. That adjacent refactor removes a second independent copy
of the current entry codec and prevents the full and targeted paths from
silently drifting when the row contract changes.

The dematerialization owner now takes exactly three targeted catalog path
cutpoints for a successful removal:

1. planning reproof;
2. pre-unlink reproof; and
3. post-unlink reproof.

An already-absent path uses planning plus final reproof. Changed, untracked,
conflicted, or payload-unavailable paths still retain their existing fail-closed
behavior. The rooted content proof, private predecessor descriptor, causal
checks, atomic displacement, complete displaced-inode hash, and final rooted
absence proof are unchanged.

## What was deliberately not weakened

The optimization does not turn a cached path into durable authority. Every
cutpoint rechecks the current catalog identity, limits, selection generation,
selection digest, and exact path row inside one transaction. A policy or path
change invalidates the effect. The exact path row remains generation-bounded by
the current catalog metadata.

The path cutpoint is not a complete catalog snapshot and does not claim to
recompute the aggregate catalog digest or prove unrelated rows. Complete
catalog observations remain at the pass planning and terminal settlement
boundaries. Those expensive observations are still required to prove global
catalog contents, deletion inference, cursor settlement, and aggregate digest
integrity; rev0988 removes only their accidental multiplication by the number
of metadata-only effects.

No SQLite schema, wire protocol, on-disk payload format, or selective-sync
policy format changes in this revision.

## Runtime oracle and diagnostics

`SyncReplicaFolderConvergencePassReport` now exposes
`remote_targeted_catalog_path_cutpoint_count`, and both shipping convergence
JSON surfaces report it as `remote_targeted_catalog_path_cutpoints`.

The focused C++ regression attaches SQLite statement tracing to a batch of eight
materialized files, narrows the folder to metadata-only, and proves in one pass:

- all eight files are safely dematerialized;
- exactly 24 primary-key catalog reads occur, three per file;
- the report records the same 24 targeted cutpoints;
- complete catalog projection reads remain bounded independently of the eight
  effects; and
- all eight catalog mappings and causal operations remain retained while the
  rooted names are absent.

The earlier one-file regression also binds the exact three-cutpoint shape.
These are executable query-shape oracles, not performance benchmarks.

## Remaining scale seam

This correction removes the folder-catalog multiplier, not every O(history)
operation in the convergence owner. `SyncReplicaSqliteOwner` remains an explicit
O(history) reference owner. Successful dematerialization still reconstitutes
complete replica state while re-proving the causal target around each effect.
The next scaling correction should introduce a transactionally exact targeted
replica path/operation cutpoint, or a carefully ordered projection guard, without
weakening sole-visible and causal-supersession authority or holding a writer
transaction across unbounded filesystem work.

Likewise, each ordinary pass still performs complete catalog observations at
its global planning and terminal boundaries, and the sanitizer folder-owner
suite is still memory-heavy. Rev0988 is therefore a meaningful asymptotic
correction but not a claim that a million-path or multi-terabyte workload has
been qualified. Peak RSS, initial sync, catch-up, disk amplification, ENOSPC,
and route behavior still require measurement on the operator workload.

## Release proof

Exact rev0988 source passed the complete GCC 14.2 Debug graph in its 540-edge configured dependency state, including 261 exact-change rebuild edges and a no-work source re-attestation. The documentation-independent registry passed 266/266 tests; the finalized targeted-cutpoint and structural audits complete 268/268 registered-test accounting. The independent GCC product lane passed 43/43 tests in bounded exact-source invocations. Focused proofs passed 532 folder-owner checks, 52/52 selective-sync audit checks, 24/24 targeted catalog-cutpoint audit checks, and 425/425 structural authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 251/251 edges; all 43/43 product tests passed in bounded invocations with leak detection and halt-on-error. The direct sanitizer folder-owner proof passed 532 checks in 29.67 seconds at 1,668,096 KiB peak RSS. Aggregate inspection found no retained compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0987 parent SHA-256 matched 33680473e933ecf4e588eb24d8d90cf080002c256a2b4ed6408253424ded6d96 and passed 41/41 wrapper-aware package checks. The binary-aware patch reconstructed all 9/9 changed active files and the complete 592-file active projection byte-for-byte and mode-for-mode. That projection contains 27,537,575 bytes with SHA-256 d9d3383d821bb05d6c41b9610ec3cbe0bfaceec60ec0c968d4ea9fa430c759f9. The final wrapper directory and ZIP passed release-package verification, CRC integrity, canonical-path and no-symlink checks, and clean-extraction path/byte/type/mode equality.

The sealed archive identity is `AnonSync-rev0988-2026.08.04.06.00-targetedcatalog-pathcutpoint-projectionfence-celestite.zip`. The targeted cutpoint remains a
path-local optimization; it grants no aggregate-catalog or targeted-replica
authority beyond the boundaries described above.

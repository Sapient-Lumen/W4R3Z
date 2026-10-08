# AnonSync rev1020 revision notes

Rev1020 bounds the rev1019 regular-file rename planner for large namespaces.
One changed file no longer triggers a complete catalog materialization and a
complete retained-replica restore before rename planning. The catalog and
current-visible replica projections now carry startup-attested exact-content
indexes, and planning uses path-local and at-most-two-row cutpoints.

The catalog advances to schema v7 and the replica database advances to schema
v9. Exact prior schemas migrate inside writer transactions, preserve durable
causal and policy authority, advance one generation, and rebuild normalized
content projections. The direct v8-to-v9 regression proves restart equality and
a usable exact-content index. A forged normalized replica row is rejected when
it disagrees with its immutable active operation.

Single-path and rename-pair catalog publication now recompute canonical catalog
proofs as ordered streams rather than whole-catalog vectors. This removes
O(path count) retained row memory, but intentionally retains O(N) SQLite I/O for
the global catalog digest. An actual identity-preserving rename publication
also retains one O(N-visible) streamed integrity fence over the current visible
projection. Ordinary one-file planning is indexed and history-cold; rev1020 is
not a claim that every rename effect is constant-time or that a dense
million-file workload has been measured.

The adjacent audit corrected an exact migration-stage defect: v5-to-v6 catalog
migration had briefly created v7 metadata while recording schema version 6. The
retained implementation now creates and verifies the exact v6 selective-sync
schema before v6-to-v7 migration. It also preserves two-head displayed-candidate
adoption through a bounded two-operation conflict view without restoring
unrelated history.

No wire generation, payload format, delta-transfer behavior, selective-sync
rule, or causal rename shape changes. Directory/subtree moves, empty
directories, portable metadata, conflict UX, retention collection, ENOSPC,
Android adapters, and live public Tor/I2P qualification remain open.

Validation: `Exact rev1020 source passed a fresh GCC 14.2 Debug graph (573/573 configured build edges), all 312/312 registered tests, and an independent 56/56 product replay. Focused GCC suites passed network model 104/104 with 41 generated operations, SQLite owner 433/433, folder owner 562/562, and sync-once 114/114. Source audits passed bounded rename 23/23, identity-preserving rename 31/31, selective sync 52/52, targeted local publication 30/30, SQLite owner 43/43, and structural authority 705/705. The exact Clang 17 ASan/UBSan product graph completed 284/284 edges and reached a no-work state; all 56/56 product tests passed with leak detection and halt-on-error. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1019 parent SHA-256 matched 6598db7b72152953b02539f16338dbf04bea358b0318d26b5723bb641140829c and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 17/17 changed files. The active implementation projection contains 650 files / 29,625,955 bytes with SHA-256 3874720c5071b841920e6a3c3dadc71f8554c519a792b0eed89bebb78f4af833. Final wrapper-directory verification passed 32/32 checks, ZIP verification and CRC passed 41/41 checks, and clean extraction matched every path, byte, type, and mode.`

Archive: `AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite.zip`

Codename: `variscite`

See `BOUNDED_RENAME_CONTENT_INDEX_AND_STREAMING_CATALOG_AUDIT_rev1020.md`.

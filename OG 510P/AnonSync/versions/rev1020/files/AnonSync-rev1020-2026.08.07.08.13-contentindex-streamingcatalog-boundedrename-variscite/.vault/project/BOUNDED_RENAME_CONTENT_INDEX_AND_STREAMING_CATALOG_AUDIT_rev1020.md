# Bounded rename content index and streaming catalog audit — rev1020

## Product purpose

AnonSync's first supported workflow is Linux/headless synchronization of large
media trees measured in terabytes. Selective synchronization and delta transfer
are mandatory, but million-path trees also make namespace planning memory and
query shape part of correctness. Rev1019 introduced conservative
identity-preserving regular-file rename/move; its folder planner could still
load the complete catalog and restore the complete retained replica model for
one changed file. Repeating that work per file was quadratic in ordinary scan
turns and could dominate memory long before payload transfer did.

Rev1020 keeps the rev1019 causal operation shape and transport behavior. It
changes how one local file is planned, re-proved, and recorded.

## Startup-attested content indexes

The replica database advances from schema v8 to v9. The current-visible
projection now stores a normalized value kind, big-endian file size, and exact
SHA-256 digest, with an index ordered by that immutable file identity and then
canonical path. The catalog database advances from schema v6 to v7 with the
corresponding current catalog value columns and index.

Both indexes are durable projections, not independent authority. Every cold
owner open verifies exact schema, metadata, operations, catalog rows, projection
rows, counts, and canonical digests. Exact v8-to-v9 and v6-to-v7 migrations
rebuild the projection inside the existing writer transaction, advance one
state/catalog generation, and preserve causal evidence, database lineage,
selection policy, outbox state, retention pins, and current visible values.
Malformed or partially upgraded schemas fail closed.

A content query is forced through the named index and returns at most two rows.
No match, one exact active File, and ambiguity are distinct results. Every
returned row is re-bound to its immutable operation or catalog value before it
can influence planning. A forged normalized row therefore cannot manufacture a
rename candidate.

## Path-local one-file planning

The direct local-file path no longer starts by materializing the complete
catalog or complete retained replica model. It uses:

- one targeted catalog path cutpoint;
- one bounded catalog content cutpoint;
- one targeted replica path cutpoint;
- one bounded current-visible content cutpoint; and
- at most two exact active conflict operations when a displayed path is
  conflicted.

The two-operation conflict prefix preserves rev1019 behavior: a local
observation may adopt the exact already-displayed candidate without pretending
that two rows are the complete conflict set. Requested retained operations that
are already present in the sole or bounded-conflict view are borrowed from that
view instead of being decoded and copied twice.

Duplicate content remains conservative. Two matching current Files or two
matching absent catalog candidates produce ambiguity and ordinary
create/delete convergence. The index is acceleration only; it does not create
identity from content alone.

## Streaming publication proofs

Catalog publication previously loaded every catalog path into vectors to
recompute the canonical catalog digest, then loaded the staged result again.
Single-path and rename-pair publication now stream ordered rows through one
canonical accumulator. They retain only the exact path rows being changed plus
one current row at a time. This removes O(path count) retained row memory from
catalog commit.

The catalog digest is still a global authority. Therefore each catalog mutation
still performs one O(N) ordered SQLite read before publication and one O(N)
ordered read of the staged state. Rev1020 removes O(N) memory, not this O(N)
I/O. A future incremental authenticated catalog witness may remove that cost,
but is not introduced here.

The final identity-preserving replica pair also keeps a global corruption
fence. Before minting destination File and source Tombstone, it streams the
complete *current visible projection* one path at a time, recomputes the exact
visible-path count and accumulator, and compares them with durable metadata.
It does not decode retained operation history or allocate the whole projection.
This publication-only O(N-visible) pass prevents a deleted or malformed
projection row from turning duplicate content into false uniqueness.

Consequently the honest complexity claim is:

- ordinary one-file planning is path/content-indexed and history-cold;
- targeted prepare and commit do not reconstruct the complete model or catalog;
- catalog publication is O(N) I/O with O(1) row memory; and
- an actual identity-preserving rename publication is O(N-visible) integrity
  I/O with memory bounded by one path's conflict width.

This is not a dense million-file throughput measurement.

## Migration and corruption oracles

Focused regressions cover:

- exact schema-v8 reconstruction and v8-to-v9 migration;
- exact schema-v6-to-v7 catalog migration through the correct intermediate
  selective-sync schema;
- restart equality after migration;
- named-index use with `LIMIT 2`;
- absent, sole, and duplicate current-content results;
- forged normalized-value rejection against immutable operations;
- two-head displayed-candidate adoption without full history restore;
- streamed catalog digest equality for single-path and rename-pair commits; and
- fail-closed current-visible projection drift before rename publication.

An adjacent migration audit found a real intermediate-schema defect during this
revision: the v5-to-v6 catalog step briefly created the v7 metadata table while
claiming schema version 6. It now recreates the exact released v6 selective-sync
schema and digest first, then performs the v6-to-v7 content-index migration.

## Product and authority limits

Rev1020 does not change the wire protocol, payload layout, delta algorithm,
selective-sync policy, causal rename shape, or cross-database crash boundary. It
is regular-file planning and publication work, not directory/subtree moves,
empty-directory semantics, portable metadata, conflict-copy UX, retention
collection, quota/ENOSPC recovery, Android support, or live public Tor/I2P
qualification.

The catalog and replica remain separate SQLite authorities. The replica pair
and catalog pair are atomic independently, not one cross-database transaction.
The process can still crash after replica publication and before catalog
publication; ordinary restart inference remains the recovery mechanism.

The content index is not a cryptographic proof by itself. Cold owner
attestation, exact row-to-operation reproof, targeted cutpoints, and the final
streamed visible-projection witness remain load-bearing. Source spelling audits
are lexical hygiene only; compiler, runtime, sanitizer, reconstruction, and
package evidence remain necessary.

## Adjacent cloudtainer audit

The cloudtainer began near filesystem pressure and contained a divergent hidden
rev1020 prototype unrelated to this slice. Stale build/work/reconstruction trees
were removed, the divergent prototype was excluded, and the source authority
was reconstructed from the exact sealed rev1019 parent after a remount deleted
an unsealed first edit. Only the guarded Git authority and fresh validation
builds may supply release evidence.

## Validation scope

Exact rev1020 source passed a fresh GCC 14.2 Debug graph (573/573 configured build edges), all 312/312 registered tests, and an independent 56/56 product replay. Focused GCC suites passed network model 104/104 with 41 generated operations, SQLite owner 433/433, folder owner 562/562, and sync-once 114/114. Source audits passed bounded rename 23/23, identity-preserving rename 31/31, selective sync 52/52, targeted local publication 30/30, SQLite owner 43/43, and structural authority 705/705. The exact Clang 17 ASan/UBSan product graph completed 284/284 edges and reached a no-work state; all 56/56 product tests passed with leak detection and halt-on-error. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1019 parent SHA-256 matched 6598db7b72152953b02539f16338dbf04bea358b0318d26b5723bb641140829c and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 17/17 changed files. The active implementation projection contains 650 files / 29,625,955 bytes with SHA-256 3874720c5071b841920e6a3c3dadc71f8554c519a792b0eed89bebb78f4af833. Final wrapper-directory verification passed 32/32 checks, ZIP verification and CRC passed 41/41 checks, and clean extraction matched every path, byte, type, and mode.

Intended archive: `AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite.zip`

Codename: `variscite`

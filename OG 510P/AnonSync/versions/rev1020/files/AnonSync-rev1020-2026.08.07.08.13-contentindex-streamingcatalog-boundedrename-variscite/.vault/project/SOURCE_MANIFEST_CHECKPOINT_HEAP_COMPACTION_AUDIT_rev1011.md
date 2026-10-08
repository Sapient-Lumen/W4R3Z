# Source-manifest checkpoint heap-compaction audit — rev1011

## Product reason

AnonSync's first supported workflow is Linux/headless synchronization of media
trees measured in terabytes. Rev1010 made one exact source-side content-defined
manifest restart-durable, but its in-process checkpoint representation retained
each completed chunk digest as a 64-character `std::string`. The durable format
already stored those digests as 32 binary bytes, so the string representation
added allocator work without adding authority or information.

At the shipping 8,192-chunk frontier, a sealed-rev1010 allocation probe measured:

| operation after vector reserve | rev1010 allocations | rev1010 requested bytes | rev1011 allocations | rev1011 requested bytes |
|---|---:|---:|---:|---:|
| construct 8,192 checkpoint chunk records | 8,192 | 532,480 | 0 | 0 |
| copy the complete chunk vector | 8,193 | 860,160 | 1 | 327,680 |

These are allocator requests observed through the test executable's global
allocation boundary, not an RSS claim. Allocator metadata and fragmentation can
make the process cost larger. The 327,680-byte vector storage is unchanged
because both the old string-bearing record and the new fixed record are 40
bytes on the retained Linux ABI. Rev1011 removes the separate 65-byte allocation
behind every digest.

## Retained representation boundary

`SyncReplicaSourceManifestCheckpointChunk` now contains exactly:

- one 64-bit chunk extent; and
- one `std::array<std::uint8_t, 32>` SHA-256 value.

A compile-time 40-byte size fence and runtime maximum-shape allocation proof bind
that representation. Construction from hexadecimal text validates canonical
lowercase SHA-256 and decodes directly into the fixed array. Parsing reads the
32 durable bytes directly into the array. Serialization appends those bytes
directly. Copying 8,192 records therefore performs one vector allocation and no
per-digest allocation.

The ordinary reconciliation manifest still uses hexadecimal strings because
that is its existing canonical protocol representation. Hex conversion occurs
only at the boundary where a durable checkpoint is restored into the ordinary
in-memory projection or protocol manifest. On fresh completion, the source
projection's existing hexadecimal string is first decoded into the compact
checkpoint record and then moved—not copied—into the ordinary manifest.

## Exact wire compatibility

The checksum-framed source-manifest checkpoint remains
`anonsync:sync-replica-source-manifest-checkpoint:v2`. No field, byte order,
length, checksum domain, basename, store-generation rule, or publication rule
changed.

The focused C++ regression binds three exact byte images generated from the
sealed rev1010 implementation:

- active interior frontier: 845 bytes, SHA-256
  `7227966f72190f3f30fd2c3b78c5bd6fbc06568b65da3be6b2f34f067317834f`;
- complete two-chunk manifest: 990 bytes, SHA-256
  `cc5eb04387b25fd6b5cc7f28796d025f67c010a4363a87743cea1ec0cc996ea2`;
- maximum 8,192-chunk manifest: 328,581 bytes, SHA-256
  `c50edf7819caaf3c51c898d479262473df55c42ff99d8775a43a5f9532261106`.

Rev1011 must reproduce all three images exactly. This permits a rev1011 process
to consume a rev1010 checkpoint and a rev1010 process to consume a checkpoint
published by rev1011.

## Adjacent audit/refactor correction

The conversion review caught a subtle ownership regression in the first edit:
changing the final projection loop to `const` would have turned the established
`std::move(chunk.sha256)` into a copy. The retained loop remains mutable for the
fresh-completion path: it constructs the binary checkpoint record while the
hexadecimal digest is still present, then moves that same string into the
ordinary protocol manifest. Restore loops over immutable compact records and
allocates only the ordinary manifest strings that must exist afterward.

The focused codec test now instruments every global allocation. It proves:

- 8,192 fixed records can be constructed after `reserve()` with zero further
  allocations;
- copying the maximum vector makes exactly one 327,680-byte allocation;
- parsing the maximum wire image remains bounded well below one allocation per
  chunk; and
- invalid nonhex construction still fails closed.

## Authority and product nonclaims

This is a memory-shape refactor only. It does not change the rooted payload-store
lease, exact inode reproof, targeted causal lookup, publication cadence, restart
scheduler, source byte verification, wire protocol, or transfer authorization.

It also does **not** solve:

- the 131,072 32 MiB source-hash pulses required by a cold 4 TiB payload;
- the ordinary completed reconciliation manifest's hexadecimal strings;
- the O(chunk count) chunk-offset index;
- page-cache pressure, filesystem cache pressure, or measured whole-process RSS;
- a global, multi-file, or multi-share chunk index;
- rename/move identity, complete directory semantics, conflict UX, placeholders,
  Android lifecycle/storage integration, quota/ENOSPC policy, retention
  collection, or live public Tor/I2P qualification.

The next source-scale gate remains a sparse synthetic multi-terabyte measurement
of the ordinary completed manifest, offset index, page cache, checkpoint write
amplification, restart replay, and owner-turn latency. If the ordinary manifest
rather than this checkpoint dominates RSS, it should be paged or persisted under
an exact bounded authority instead of adding an unmeasured global index.

## Validation and release identity

Fresh GCC 14.2 Debug graph 563/563; GCC registry 298/298; GCC product 52/52; focused 30 checkpoint-codec, 45 chunker, 43 true-process restart, 5,001 protocol, 25 memory-shape, 20 terminal-state, 737 payload-store, 397 SQLite-owner, 536 folder-owner, 114 sync-once, 2,047 TLS, and 211 reconciliation-service checks; fresh Clang 17 ASan/UBSan product graph 274/274 and product 52/52 with leak detection and halt-on-error; dedicated heap-compaction audit 22/22, retained rev1010 checkpoint audit 36/36, structural authority audit 617/617, and exact rev1010 parent verification 41/41. Incremental, remount-lost, stale-validator, and transient aggregate TLS-EOF attempts are excluded.

Archive: `AnonSync-rev1011-2026.08.06.10.19-fixedwidthdigest-singleallocation-wirecompat-axinite.zip`

Codename: `axinite`

# Revision notes — rev1011

## Fixed-width durable source-manifest chunk records

Rev1011 removes one heap-backed hexadecimal string from every completed chunk in
the restart-durable source-manifest checkpoint. The durable v2 codec already
carried SHA-256 as 32 binary bytes; the retained C++ representation now matches
that format with a 40-byte extent-plus-digest record.

At the 8,192-chunk frontier, a sealed-rev1010 allocation probe observed 8,192
allocations and 532,480 requested bytes merely to construct records after the
vector had already been reserved. Copying the vector required 8,193 allocations
and 860,160 requested bytes. Rev1011 requires zero post-reserve allocations to
construct the records and one 327,680-byte allocation to copy the vector.

The checkpoint magic, v2 wire grammar, maximum encoded extent, checksum,
publication cadence, store identity, generation, rooted authority, and restart
semantics are unchanged. Focused regressions bind exact sealed-rev1010 active,
complete, and maximum-shape wire-image digests.

## Conversion boundary and adjacent refactor

Canonical lowercase hexadecimal is validated and decoded when ordinary source
manifest chunks enter checkpoint state. Parsing and serialization operate on
binary arrays without per-chunk heap allocation. Hexadecimal strings are rebuilt
only when a checkpoint is restored into the ordinary reconciliation manifest or
projection, where that protocol representation is still required.

The final source-projection loop deliberately remains mutable. It decodes the
existing digest into the compact checkpoint and then moves that same string into
the ordinary protocol manifest. An intermediate `const` refactor would have
silently converted the move to an 8,192-string copy and was rejected.

## Explicit limits

Rev1011 compacts only the optional restart checkpoint. It does not reduce cold
source hashing, the ordinary completed manifest's string storage, the chunk
offset index, or total page-cache cost. It does not add a global chunk index.
Selective placeholders, automatic eviction, rename/move identity, complete
directory semantics, conflict UI, Android, quota/ENOSPC qualification, retention
collection, and live public Tor/I2P qualification remain open.

## Validation and release identity

Fresh GCC 14.2 Debug graph 563/563; GCC registry 298/298; GCC product 52/52; focused 30 checkpoint-codec, 45 chunker, 43 true-process restart, 5,001 protocol, 25 memory-shape, 20 terminal-state, 737 payload-store, 397 SQLite-owner, 536 folder-owner, 114 sync-once, 2,047 TLS, and 211 reconciliation-service checks; fresh Clang 17 ASan/UBSan product graph 274/274 and product 52/52 with leak detection and halt-on-error; dedicated heap-compaction audit 22/22, retained rev1010 checkpoint audit 36/36, structural authority audit 617/617, and exact rev1010 parent verification 41/41. Incremental, remount-lost, stale-validator, and transient aggregate TLS-EOF attempts are excluded.

Archive: `AnonSync-rev1011-2026.08.06.10.19-fixedwidthdigest-singleallocation-wirecompat-axinite.zip`

Codename: `axinite`

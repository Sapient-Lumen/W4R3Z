# Fixed binary wire-manifest and shared digest codec audit — rev1013

## Product reason

AnonSync's first supported workflow is Linux/headless synchronization of media
trees measured in terabytes. Delta transfer and selective synchronization are
mandatory, and the owner has explicitly identified memory use as a product
risk. Rev1012 removed the resident string-backed source-manifest cache, but a
cache-cold first range still rebuilt 8,192 heap-backed digest strings before the
same generation-9 manifest could enter the response frame.

At the hard 8,192-chunk frontier, rev1012's focused allocator probe measured
that transient materialization as:

- one 327,680-byte `std::vector` allocation for 8,192 40-byte chunk objects;
- 8,192 allocations of 65 requested bytes for their 64-character SHA-256
  strings; and
- 8,193 allocations / 860,160 requested bytes in total.

That cost is bounded, but it is paid at a latency-sensitive cache-cold peer
boundary and is replicated by receive-side manifest construction. It is pure
representation overhead: the wire still carries the same 64 lowercase
hexadecimal characters for every chunk.

## Retained design

Rev1013 introduces one shared `Sha256DigestValue`:

- exactly 32 bytes;
- standard-layout and trivially copyable;
- no pointer, allocator, `std::string`, virtual dispatch, or hidden heap owner;
- canonical lowercase-hex construction and assignment;
- fixed binary construction for already-framed durable bytes;
- allocation-free comparison against lowercase hexadecimal text; and
- explicit binary, hexadecimal-string, framed-digest, and framed-wire output
  boundaries.

The type is now used by all three bounded source-manifest representations:

1. `SyncReplicaReconciliationDeltaChunk`, the generation-9 protocol object;
2. `SyncReplicaReconciliationCompactManifestChunk`, the process-retained
   cumulative cache; and
3. `SyncReplicaSourceManifestCheckpointChunk`, the checksum-framed restart
   checkpoint.

All three chunk records remain exactly 40 bytes: one 64-bit extent plus one
32-byte digest. The compact cache and protocol manifest can therefore copy or
materialize through one contiguous vector allocation. The checkpoint parser can
retain its existing 32 binary wire bytes without rebuilding text.

## Strict validity boundary

A protocol chunk can no longer contain malformed digest text and wait for a
later validator to notice. Construction and assignment first decode into a
local 32-byte value and publish only after all 64 input characters have been
proved canonical lowercase hexadecimal. Failure leaves the previous value
unchanged.

This changes an in-process API invariant, not the network or durable format.
Malformed peer bytes still fail while the parser constructs the typed chunk.
The ordinary manifest validator continues to prove canonical parameters,
nonzero bounded extents, chunk cardinality, and exact total coverage; digest
syntax is now guaranteed by the field type.

## Wire and durable compatibility

The reconciliation protocol remains generation 9. Serialization still emits an
8-byte length followed by the exact 64 lowercase hexadecimal characters, and
the semantic digest still hashes that same framing. The decoder borrows the
64-byte field from the frame and decodes it directly into the 32-byte value.

A deterministic rev1012 fixture is retained as a golden compatibility proof:

- request-frame SHA-256:
  `1e6ae4e901d86679e4219ad764dbb290d1fcb4a2f7520490f8a75b6045efab51`;
- response-frame SHA-256:
  `29304b77ca55367bbcd259c9119cdc916a2ca918fe0ae5836560a6a673fa8119`.

The source-manifest checkpoint remains magic/version v2 and retains the exact
sealed rev1010 active, complete, and 8,192-chunk byte images. Rev1013 removes
its third private hex/binary codec and routes construction, serialization, and
parsing through the shared value.

## Measured allocation boundary

The maximum-shape runtime probe now requires:

- parser-shaped construction of 8,192 wire chunks: one 327,680-byte vector
  allocation and zero digest allocations;
- compact-cache construction: one 327,680-byte vector allocation;
- compact-cache copy: one 327,680-byte vector allocation;
- compact-to-wire materialization: one 327,680-byte vector allocation; and
- numeric cumulative lookup across all 8,192 chunks: zero allocations.

Compared with rev1012 cache-cold materialization, this removes 8,192 allocator
calls and 532,480 requested bytes. It also removes the same per-digest owner
from receive-side typed manifest lifetime. These are allocator-request
measurements, not whole-process RSS or allocator-fragmentation measurements.

## Adjacent refactor

The audit found three implementations of the same SHA-256 text/binary
conversion: protocol/compact materialization, the compact cache, and the durable
checkpoint. Keeping all three would have made canonicality, diagnostics, and
future constant-time or parser changes drift independently. Rev1013 deletes the
compact and checkpoint copies and makes the shared value the only source of
fixed-width digest conversion for this source-manifest path.

This does not replace unrelated specialized digest codecs at TLS certificate,
SQLite resident-image, or other authority boundaries. Those formats have
different error, provider, or cryptographic requirements and are not changed by
this revision.

## Rejected alternatives

### Keep `std::string` on the public protocol object

This preserved easy mutation of intentionally invalid test fixtures but retained
8,192 ordinary heap owners in every complete typed manifest. A test convenience
is not a product reason to keep the allocation shape.

### Store either binary or invalid text in a variant

A draft compatibility wrapper could retain canonical digests as 32 bytes and
malformed test values as strings. It enlarged the public object, preserved a
hidden allocation-bearing state, and weakened the invariant that every live
chunk is valid. It was rejected.

### Change generation 9 to binary digests

Binary wire digests would save 32 bytes per chunk on the network, but would be a
protocol-generation change with compatibility and rollout consequences. The
measured problem here was process allocation churn. Rev1013 deliberately keeps
wire bytes unchanged.

### Page or persist the 327,680-byte sequence now

One maximum manifest remains bounded and small compared with a multi-terabyte
payload. The project still lacks target-scale whole-process RSS data showing
that one sequence dominates across actual concurrent shares. Paging or adding a
global multi-source index before that evidence would add durable and scheduler
authority prematurely.

## Remaining scale and product boundaries

Rev1013 does not make source-manifest memory constant. The hard frontier remains
8,192 chunks and 327,680 bytes per retained or materialized maximum sequence.
A cold 4 TiB source still requires 131,072 32 MiB hash pulses, and a successful
checkpoint may replay up to one 1 GiB interval. First source discovery,
receiver discovery, final publication, SQLite owners, full directory scans,
payload indexes, page cache, TLS frames, and allocator fragmentation still
contribute to whole-process RSS.

There is still no global, multi-file, or multi-share chunk database. The
revision does not solve identity-preserving rename/move, complete directory and
empty-directory semantics, conflict presentation, placeholders, automatic
selective-sync eviction, best-effort retention collection, quota/ENOSPC policy,
Android lifecycle and scoped storage, or live public Tor/I2P qualification.

The next source-scale gate remains measurement: sparse synthetic multi-terabyte
files and trees, concurrent shares, whole-process RSS, allocator fragmentation,
page-cache pressure, checkpoint write amplification, restart replay, pulse
throughput, ordinary-turn latency, complete scans, disk amplification,
high-latency routes, and controlled ENOSPC. If the remaining fixed sequence is
material at measured share counts, page or persist it. Otherwise product
priority should return to rename/move identity, directory semantics, conflicts,
and selective-sync user surfaces.

## Evidence boundary

The focused source audit is lexical hygiene, not semantic proof. Compile-time
layout assertions, allocator probes, exact wire-image hashes, checkpoint golden
images, full GCC and Clang sanitizer lanes, reconstruction, manifest, and
package verification remain load-bearing.

Validation: Exact rev1013 source passed a fresh GCC 14.2 Debug graph (567/567 configured build edges across bounded resumptions) and a no-work bundled-SQLite re-attestation; all 301/301 registered tests and an independent 53/53 product accounting passed. Focused GCC proofs passed 22 compact-manifest, 30 checkpoint-codec, 45 content-defined-chunker, 43 true-process restart, 5,004 reconciliation-protocol, 25 memory-shape, 10 source-frame-memory, 20 terminal-state, 737 payload-store, 397 SQLite-owner, 536 folder-owner, 114 sync-once, 2,047 TLS, and 211 reconciliation-service checks. A fresh Clang 17 ASan/UBSan product graph completed 278/278 edges and all 53/53 product tests passed with leak detection and halt-on-error; the additional payload-store sanitizer proof passed 737 checks. Source audits passed 30/30 fixed-binary-manifest, 29/29 compact-cache, 22/22 checkpoint-memory, 27/27 manifest-reference, and 635/635 structural-authority checks; the exact rev1012 parent passed 41/41 wrapper-aware package checks. Aggregate terminal-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The overwritten first authority, divergent controller branches, discarded caches, interrupted early registry, and pre-correction lexical-audit failure are excluded.

Archive: `AnonSync-rev1013-2026.08.06.16.45-fixedbinarymanifest-sharedcodec-singleallocation-scheelite.zip`

Codename: `scheelite`

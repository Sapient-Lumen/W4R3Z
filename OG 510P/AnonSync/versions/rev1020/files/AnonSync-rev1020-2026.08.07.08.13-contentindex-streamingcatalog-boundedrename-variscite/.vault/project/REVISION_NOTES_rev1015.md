# Revision notes — rev1015

## Fixed active-source digest records

Rev1015 completes the fixed-digest source-manifest conversion at the last
in-progress owner. `SyncReplicaFilePayloadStoreContentDefinedChunk` now contains
one 64-bit extent and one 32-byte `Sha256DigestValue`; the record is exactly 40
bytes and trivially copyable. The active projection, its durable checkpoint,
the completed checkpoint, the generation-9 protocol manifest, and the compact
cache copy fixed digest values rather than rebuilding owning digest strings.

At the 8,192-chunk maximum, one active projection retains one 327,680-byte
vector allocation rather than that vector plus 8,192 heap-backed 64-character
digest strings. In this GCC/libstdc++ toolchain the old boundary requested
860,160 bytes through 8,193 allocations. The retained boundary requests 327,680
bytes through one allocation.

## Allocation-free chunk completion

The adjacent hash refactor adds an allocation-free 32-byte terminal form to
`ResumableSha256`. Chunk completion builds the fixed digest directly from its
binary terminal value instead of creating a 64-character string and parsing it
back into binary. The fixed hexadecimal array and owning hexadecimal string APIs
now derive from the same binary terminal path.

The runtime oracle proves binary digest completion and fixed-record construction
perform no allocation after arming the allocator observer. It then proves 64
maximum active-source vectors retain exactly 64 large allocations and exactly
20 MiB of record storage. The equivalent prior requested shape was 52.5 MiB, so
the synthetic 64-source frontier removes 32.5 MiB of allocator requests and
524,288 per-digest heap owners.

## In-place checkpoint publication

The pending source-manifest checkpoint is now published through a mutable
caller-owned candidate. Typed lease or atomic-publication deferral retains the
same bounded vector for a later turn rather than copying all 8,192 fixed records
before every publication attempt. Exact store identity, successor generation,
encoded-record publication, committed-record parsing, lease reproof, and rooted
reproof remain mandatory.

## Terminal compact-cache release

A completed compact source manifest is now an active-transfer cache rather than
dormant process-lifetime state. After the terminal generation-9 frame is fully
assembled, all source descriptors are released, and the exact complete
checkpoint is durably re-proved, the service releases the resident compact
vector. Release requires the same operation id, canonical path, content digest,
size, and manifest digest; content equality alone is insufficient.

A duplicate request after a lost terminal response reloads the exact complete
checkpoint, reopens the immutable payload, and rehydrates the compact cache
without another source-manifest scan or source-byte hash. Filesystem-cold status
reports residency, retained capacity, exact durable availability, restorations,
and terminal releases.

## Compatibility and product boundary

Protocol generation remains 9. Checkpoint format remains v2. Network and durable
bytes, chunk boundaries, semantic manifest digests, structural digests, request
framing, response framing, and payload publication semantics are unchanged.

This is not a whole-daemon RSS result. SQLite caches, payload indexes, page
cache, TLS, descriptors, directory scans, watcher queues, allocator
fragmentation, and concurrent scheduler state are outside the fixture. One
active transfer may still retain one 327,680-byte O(chunk count) sequence, a
cold 4 TiB source still needs 131,072 32 MiB pulses, and a successful checkpoint
may replay one 1 GiB interval.

Identity-preserving rename/move, complete directory and empty-directory
semantics, conflict presentation, polished selective-sync surfaces, controlled
ENOSPC, Android, and live public Tor/I2P qualification remain open. Unless
whole-process concurrent-share measurement exposes another manifest bottleneck,
product priority should return to those ordinary file semantics.

Validation: Exact rev1015 source passed a fresh GCC 14.2 Debug graph (567/567 configured build
edges), a no-work bundled-SQLite re-attestation, independent 53/53 product tests, and
final 251/251 non-product accounting for all 304/304 registered tests. Focused GCC
proofs passed 86 resumable-SHA-256, 737 payload-store, 30 source-manifest-checkpoint, 35
compact-manifest, 16 source-frame-memory, and 215 reconciliation-service checks. Source
audits passed 19/19 active-source-memory, 22/22 terminal-cache, 22/22 checkpoint-memory,
and 659/659 structural-authority checks. A fresh Clang 17 ASan/UBSan product graph
completed 278/278 edges and all 53/53 product tests passed with leak detection and
halt-on-error. The exact rev1014 parent passed 41/41 wrapper-aware package checks.
Aggregate terminal-log inspection found no compiler, linker, AddressSanitizer,
UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic.

Archive: `AnonSync-rev1015-2026.08.06.20.55-activefixeddigest-terminalrelease-multishare-kornerupine.zip`

Codename: `kornerupine`

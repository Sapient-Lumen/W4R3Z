# Active source manifest fixed-digest and multi-share memory audit — rev1015

## Product reason

AnonSync's first supported workflow is Linux/headless synchronization of media
trees measured in terabytes. Delta transfer and selective synchronization are
mandatory, and memory growth across concurrent shares is a product constraint.
Rev1013 made the generation-9 wire manifest, completed compact cache, and
durable checkpoint use one fixed 32-byte SHA-256 value. Rev1014 removed the
publication-only copy of the completed compact manifest.

The in-progress source projection remained outside that correction. Its
`SyncReplicaFilePayloadStoreContentDefinedChunk` still owned each completed
chunk digest as a 64-character `std::string`. At the 8,192-chunk frontier the
vector itself requested 327,680 bytes, while 8,192 digest strings requested a
further 532,480 bytes in this toolchain: 8,193 retained allocations and 860,160
requested bytes for one active source. Copies into a durable checkpoint repeated
the same per-digest heap ownership.

## Retained correction

Rev1015 changes the active payload-store chunk record to the same fixed digest
representation already used by the wire and durable owners:

- one `std::uint64_t` chunk extent;
- one `Sha256DigestValue`, exactly 32 bytes;
- one exact 40-byte, standard-layout, trivially copyable record;
- no `std::string`, pointer, allocator, or hidden heap owner in the record; and
- lowercase hexadecimal materialization only at explicit text/reporting
  boundaries.

The payload-store accumulator, active restart checkpoint, completed checkpoint,
protocol manifest, and compact cache now transfer the fixed value directly.
There is no fixed-to-text-to-fixed round trip between these owners.

`ResumableSha256` also gains an allocation-free 32-byte terminal form. Chunk
completion now constructs `Sha256DigestValue` from those bytes rather than
calling `finish_hex()` and allocating a transient 64-character string. The
owning hexadecimal terminal API remains available for boundaries that actually
need text.

## Exact maximum shape

The focused runtime oracle binds the hard source shape:

- 8,192 completed chunks;
- 40 bytes per fixed chunk record;
- 327,680 bytes in one active source vector;
- zero digest-owned allocations after that vector reserve;
- allocation-free binary SHA-256 completion into one fixed chunk record; and
- 64 synthetic concurrent active-source vectors using exactly 64 large
  allocations and 20 MiB of retained record storage.

Under the previous string-backed representation, the same 64-source requested
shape was 52.5 MiB in this toolchain. Rev1015 removes 32.5 MiB of allocator
requests and 524,288 per-digest allocation owners from that synthetic frontier.
Those figures describe the manifest-record boundary, not a complete daemon RSS
measurement.

## Authority and compatibility

This is an in-process representation correction:

- reconciliation protocol generation remains 9;
- source-manifest checkpoint format remains v2;
- network digest fields remain 64 lowercase hexadecimal characters;
- durable checkpoint bytes remain fixed binary digests;
- chunk boundaries, semantic manifest digests, structural digests, request
  framing, response framing, and payload publication rules do not change; and
- malformed lowercase digest text still fails while entering the fixed digest
  type.

Every binary `Sha256DigestValue` bit pattern is a syntactically valid digest
value. Consequently the restored accumulator no longer performs a redundant
lowercase-text syntax check on an already-fixed value. Extent, count, rolling
chunker, whole-hash, current-chunk-hash, payload identity, and checkpoint
cutpoint validation remain unchanged.

## Adjacent refactor

The source preparation path previously converted the same digest through three
representations:

1. resumable SHA-256 words;
2. an owning lowercase hexadecimal string; and
3. a parsed fixed binary digest in the checkpoint/protocol layers.

Rev1015 makes binary completion the internal handoff. Hexadecimal text is now a
serialization concern rather than an intermediate ownership model. The
checkpoint chunk receives a fixed-digest constructor, and the reconciliation
service copies the 40-byte record directly through active restore, checkpoint
publication, completed projection, and compact-manifest construction.

This removes allocation churn as well as retained heap owners, while keeping one
canonical fixed digest implementation rather than creating another source-only
codec.

## Nonclaims and next edge

The 64-share fixture is an exact record-storage and allocator-boundary proof. It
is not a peer-service benchmark and does not include SQLite caches, payload-store
indexes, filesystem page cache, TLS buffers, complete directory scans, watcher
queues, allocator fragmentation outside this owner, active file descriptors, or
network backpressure. One source still retains one 327,680-byte O(chunk count)
sequence, and a compatibility caller may still materialize an owning manifest.

A cold 4 TiB source still requires 131,072 local 32 MiB hash pulses and may replay
one 1 GiB checkpoint interval. There is still no global, multi-file, or
multi-share chunk database. Whole-process RSS, concurrent service growth,
checkpoint write amplification, page-cache pressure, route latency, disk
amplification, and controlled ENOSPC remain measurement gates.

This revision does not solve identity-preserving rename/move, complete directory
and empty-directory semantics, conflict presentation, placeholders, automatic
selective-sync eviction, best-effort retention collection, quota policy,
Android lifecycle/scoped storage, or live public Tor/I2P qualification. Unless
whole-process measurement identifies another source-manifest bottleneck, product
priority should return to ordinary file semantics and selective-sync surfaces.

## Evidence boundary

The focused Python audit is lexical hygiene, not semantic proof. Compile-time
layout assertions, allocation probes, digest-vector equivalence, complete GCC
and Clang sanitizer lanes, source reconstruction, release manifest sealing, and
clean-extraction comparison remain load-bearing.

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

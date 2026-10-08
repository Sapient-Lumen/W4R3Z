# Content-defined delta and insertion resynchronization audit — rev0994

## Product reason

The first supported workflow is Linux/headless synchronization of selective,
multi-terabyte media trees. Delta transfer is mandatory. Rev0986–rev0993 used
canonical fixed boundaries: that preserved bounded memory and crash-safe range
resume, but a small insertion near the beginning of a large file shifted every
later absolute block. Unchanged bytes then ceased to match their former offsets
and could be retransmitted almost in full. That is product failure for large
mutable media and container files, not merely an optimization opportunity.

Rev0994 replaces the shipping fixed-boundary projection with one bounded
content-defined chunk path. It keeps the existing payload-before-operation,
durable-prefix, per-range, and final whole-file SHA-256 authorities. Boundary
hashes choose candidate cutpoints and local lookup opportunities; they never
admit bytes.

## Boundary engine

`SyncReplicaContentDefinedChunker` is a scalar streaming gear-hash state
machine. Its canonical parameters contain minimum, average, maximum, and maximum
chunk-count bounds. The implementation:

- emits no boundary before the minimum;
- uses a deterministic mask derived from the canonical average;
- forces a boundary at the maximum;
- rejects a chunk-count frontier before unbounded manifest growth; and
- owns no vector, payload buffer, pathname, descriptor, or allocator-backed
  chunk table.

The current protocol chooses a canonical average between 4 MiB and 1 GiB and
permits at most 8,192 chunks. The minimum possible chunk size at the largest
canonical average is 512 MiB, so the worst-case manifest frontier is exactly
4 TiB. Smaller files retain smaller average chunks and better resynchronization.
Peers do not select arbitrary geometry.

Gear-hash collision or boundary coincidence is not byte authority. Every chunk
record carries its exact size and SHA-256, and every completed payload is still
verified against the operation's whole-file SHA-256.

## Descriptor-rooted payload projection

The payload store exposes one content-defined manifest operation over an already
opened immutable payload capability. It streams the selected descriptor with
`pread`, computes each chunk SHA-256 and the whole-file SHA-256 in one pass,
checks the exact canonical regular-file observation after reading, and rejects
extent, count, or identity drift. The superseded fixed-block payload-store API
and projection were removed rather than retained as a second delta engine.

The manifest is acceleration, not namespace-health or retention authority. A
complete payload-store snapshot remains the only complete physical-namespace
health, capacity, transient-object, and inventory oracle.

## Protocol generation 6

Generation 6 carries one canonical variable-chunk manifest:

- canonical chunk parameters;
- ordered `{size_bytes, sha256}` records;
- a domain-separated digest binding content identity, total extent, parameters,
  chunk count, order, sizes, and digests; and
- the exact containing chunk offset and size for each ranged payload.

A cache-cold receiver receives the complete manifest. A same-process payload
continuation advertises the exact manifest digest and receives only the bounded
reference. A restarted receiver has no cache authority and receives the complete
manifest again. Ranges may not cross a content-defined chunk boundary. A full
chunk is compared with the retained manifest record before staging.

The generation change is intentional and incompatible with the superseded
fixed-boundary frames. An older peer must fail closed rather than reinterpret
variable geometry.

## Shifted predecessor reuse

The receiver retains at most one exact target manifest and one exact causal
predecessor manifest. Each cache includes cumulative chunk offsets. The
predecessor cache additionally keeps one digest-sorted vector of at most 8,192
indices.

For each target chunk, the receiver searches the predecessor index by SHA-256
and exact size. A matching predecessor chunk may begin at a different absolute
offset. Its descriptor bytes are copied from that predecessor offset and staged
at the target offset through the existing durable prefix owner. The receiver
still verifies range digests, chunk identity, final payload SHA-256, and causal
operation admission in the existing order.

The deterministic regression uses a 48 MiB predecessor, inserts 256 KiB near the
front, changes a distant region, and proves at least four shifted chunks and at
least 16 MiB are reused while exact final bytes and causal evidence converge. It
also exercises bounded pages, full-manifest bootstrap, reference continuations,
cache-cold restart behavior, and forged complete-chunk rejection.

## Memory boundary

The boundary detector is allocation-free. The durable payload projection owns
one vector of at most 8,192 chunk records. During one receiver transfer, the
bounded acceleration state is:

- one target manifest and one cumulative-offset vector;
- one predecessor manifest, one cumulative-offset vector, and one digest-order
  vector; and
- existing bounded response/range buffers and durable prefix state.

No structure grows with file bytes, tree path count, or the number of retained
payload objects. The source computes at most one selected-file manifest per
serve session and reuses it only while exact descriptor metadata and payload
identity remain unchanged.

This is a structural bound, not a measured target-scale peak-RSS result. The
48 MiB regression demonstrates shifted reuse semantics, not multi-terabyte
runtime or disk-amplification performance.

## Adjacent audit and refactor

The review removed the old fixed-block payload projection, protocol vocabulary,
service caches, counters, CLI fields, and focused audit identity from shipping
code. Historical rev0986/rev0992 records remain as provenance, but there is one
current delta implementation.

The current manifest-reference audit was rewritten around generation 6 rather
than weakening old lexical checks until they happened to pass. The rev0993
request-scoped source audit was also updated to ensure the content-defined
manifest is still bound to the current exact selected descriptor and does not
reintroduce a session-wide payload namespace owner.

## Nonclaims and next measurements

Rev0994 does not provide:

- a global cross-file or cross-payload chunk index;
- multilevel chunking for tiny edits within very large canonical chunks;
- compression or transport deduplication across peers;
- automatic selective-sync placeholders or private-payload eviction;
- identity-preserving rename or move;
- directory and empty-directory semantics;
- Android storage/lifecycle integration;
- quota or ENOSPC qualification; or
- a generated multi-terabyte peak-RSS, throughput, restart, and disk-amplification result.

The next product edge is measurement against a generated sparse multi-terabyte
Linux media-tree shape, including insertion-heavy large-file mutation. That
measurement should decide whether canonical chunk sizing, index representation,
range size, or cross-file discovery is the next real multiplier.

## Validation

Exact rev0994 source completed a fresh 540-edge GCC 14.2 Debug graph and a no-work bundled-SQLite re-attestation; all 273/273 registered tests and all 44/44 product tests were accounted for across bounded terminal shards. Focused GCC proofs passed 39 content-defined-chunker, 650 payload-store, 4,955 reconciliation-protocol, 113 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 31/31 content-defined-delta, 27/27 manifest-reference, 33/33 targeted-source-access, 52/52 selective-sync, and 458/458 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 256/256 edges; all 44/44 product tests and the same five focused suites passed with leak detection and halt-on-error. The sanitizer folder-owner proof passed 536 checks with 1,686,160 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0993 parent SHA-256 matched a9ac6bd2a95c56061d4ea836725d3e5691f117e2887d415b4bb82c9964540504 and passed 41/41 checks under its sealed wrapper-aware verifier. The binary-aware source patch reconstructed all 29/29 changed project paths, all 26/26 changed active paths, and the complete 601-file active projection byte-for-byte and mode-for-mode. The active projection contains 601 files / 27,831,652 bytes with SHA-256 ec5931b9b28566148ffd8d053d22d88a07549ac39b52d1e22dffb66db21e07e7. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality checks remain mandatory publication gates.

## Archive

AnonSync-rev0994-2026.08.04.17.13-contentdefined-shiftedreuse-boundedmanifest-kyanite.zip
kyanite

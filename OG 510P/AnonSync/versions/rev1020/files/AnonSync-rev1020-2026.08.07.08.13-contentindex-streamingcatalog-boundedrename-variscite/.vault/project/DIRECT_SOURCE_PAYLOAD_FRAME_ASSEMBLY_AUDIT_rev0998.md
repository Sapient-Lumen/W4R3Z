# Direct source payload-frame assembly audit — rev0998

## Product reason

Rev0997 removed the temporary canonical response body, transferred the final
frame into TLS continuation ownership, and kept receiver payloads borrowed from
that frame. The remaining source cutpoint still held every selected payload
range in `std::string` objects while allocating and filling the final response
frame. At the configured 64 MiB page frontier, that was a predictable second
payload-sized owner before OpenSSL or kernel buffering even began.

Multi-terabyte Linux media trees make that ownership shape product-critical.
Delta transfer cannot be called successful while one ordinary bounded response
needlessly doubles its payload memory at the source.

## Caller-owned exact range fill

`SyncReplicaFilePayloadStoreOpenedPayload` now exposes one exact
caller-owned-range operation. It reads with position-independent `pread`, caps
each syscall at `SSIZE_MAX`, hashes the bytes as they enter the destination,
re-proves the exact inode observation afterward, and returns the canonical
range SHA-256. A complete-file mismatch retains the existing process integrity
fault and throws the same typed payload-integrity error.

The compatibility `copy_range_or_throw` path allocates its result string and
then delegates to the same reader. There is one byte-reading implementation,
not a shipping fast path and a divergent legacy implementation.

## One-frame protocol assembly

The generation-7 protocol remains unchanged. A move-only frame assembly owner:

1. validates the request and bounded payload declarations;
2. projects the exact canonical body and frame sizes with checked arithmetic;
3. reserves one final frame;
4. appends metadata, fixed digest slots, and exact writable payload holes;
5. exposes each hole as `std::span<char>`;
6. commits one lowercase SHA-256 identity per filled range;
7. validates the complete response against the exact request and frame-backed
   bytes; and
8. writes the structural trailer digest before transferring the frame.

The builder contains no public callback, `std::function`, scatter/gather
lifetime, or payload-sized auxiliary owner. Uncommitted ranges, malformed
identities, duplicate commits, out-of-range access, extent drift, wire-size
drift, and byte/digest disagreement fail closed.

## Shipping service and TLS path

The reconciliation service now plans bounded payload metadata plus exact opened
payload indices and ranges. It sorts that plan canonically, creates one protocol
assembly, and fills each frame hole from the retained payload descriptor. Exact
payload-use leases and descriptors exist only through synchronous frame
completion. They are released before the result can enter TLS backpressure.

The TLS source path calls the direct frame API. The pre-existing owned service
API remains a named compatibility surface: it calls the direct path and then
decodes the canonical frame into owned payload strings. That differential is
intentional and executable; it is not the shipping path.

Public protocol-limit objects can narrow but cannot enlarge the fixed product
frontiers: at most 128 payload descriptors, 64 MiB of payload bytes per page,
and a 96 MiB response frame. Shipping TLS and real-process results expose the
number of direct frames, direct payload bytes, aggregate payload-page bytes at
frame reservation, maximum source staging, and maximum exact descriptors. The
oracles require zero aggregate page ownership, zero staging, and descriptor
fanout no greater than 128 for every emitted response.

## Deterministic memory proof

A product regression publishes an actual 64 MiB immutable payload, releases the
setup buffer, tags each observation generation, and observes every allocation at
or above 2 MiB. The shipping direct source must perform exactly one such
allocation and have exactly one such allocation live at once: the final frame.
The same request through the compatibility API must expose the expected two
simultaneously live owners: final frame plus owned decoded payload. This lower
threshold mechanically excludes a hidden four-MiB range staging allocation.

A second regression constructs a canonical 4 TiB extent with 4,096 one-GiB
content-defined chunks but transfers only one four-MiB range. It requires one
bounded frame allocation, one simultaneously live large allocation, and proves
that logical extent size does not drive resident payload ownership.

These are deterministic C++ heap-shape oracles, not complete operating-system
peak-RSS measurements.

## Adjacent audit/refactor

The byte reader was centralized before the direct path was retained. The new
span operation and the compatibility string operation share exact offset,
extent, hashing, stale-observation, and post-read reproof behavior. Syscall size
is bounded explicitly rather than relying on the current 64 MiB service limit.

Two divergent unsealed rev0998 implementations and pathname-based cleanup
actors were discovered during the run. The weaker range-staging branch, all
competing objects, all killed runs, and all vanished worktrees were excluded.
The retained source was reconstructed over the exact sealed rev0997 Git tree in
a neutral authority path before authoritative compilation. Only that frozen
source and clean builds derived from it are eligible for rev0998 evidence.

## Honest boundary

Rev0998 removes source payload strings and range staging beside the final frame.
It does not make the response frame streaming, reduce the configured 64 MiB
payload page itself, remove protocol validation hashes, eliminate OpenSSL or
kernel socket buffers, prove Tor/I2P throughput, or qualify multi-terabyte peak
RSS. These are not complete operating-system peak-RSS measurements. Metadata,
operation vectors, one bounded content-defined manifest, opened descriptor
objects, and the final frame remain resident during assembly.

It also does not add cross-file chunk discovery, rename/move identity, complete
directory semantics, placeholders, private-payload eviction, retention
collection, Android lifecycle/storage integration, or ENOSPC recovery.

## Next product edge

Use the now-single-source-frame path for measured direct, Tor, and I2P transfer
runs with 64 MiB windows, restart, controlled ENOSPC, and sparse synthetic
multi-terabyte trees. Measure RSS, page cache, read/write amplification,
throughput, and recovery. In parallel, extend content-defined local reuse from
the current target/predecessor scope to bounded cross-file discovery so media
renames and duplicated assets do not force network transfer.

## Validation

Exact rev0998 source passed a fresh GCC 14.2 Debug graph (551/551 configured build edges) and a no-work bundled-SQLite re-attestation; all 281/281 registered tests and an independent 47/47 product replay were accounted for from the exact source. Focused GCC proofs passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 652 payload-store, 39 content-defined-chunker, 98 network-model plus 41 generated-operation, 361 SQLite-owner, 536 folder-owner, 110 sync-once, 4,989 reconciliation-protocol, 6 response-frame-memory, 25 borrowed-memory-shape, 10 direct-source-frame, 117 reconciliation-service, 2,044 TLS-transport, and 162 local-control checks. Source audits passed 34/34 direct-source-frame, 19/19 response-frame-memory, 27/27 response-memory-shape, 33/33 targeted-source-access, and 496/496 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product dependency graph completed 262/262 edges; all 47/47 product tests passed with leak detection and halt-on-error. Focused sanitizer proofs passed 652 payload-store, 4,989 reconciliation-protocol, 10 direct-source-frame, 117 reconciliation-service, 2,044 TLS-transport, and 536 folder-owner checks; the folder-owner proof completed in 29.39 seconds at 1,692,128 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0997 parent SHA-256 matched 64125a2e82f1e9bb789c14abc2f94f5dbf55c667e6f61b92406b5fbd4389e6de and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 25/25 changed project paths, all 22/22 changed active paths, the one changed wrapper restart page, and the complete 609-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 609 files / 28,088,843 bytes with SHA-256 35acfcd7ff22a865d1321a5272b96af33dd6d138a21641178386a4ab746fbe41. Validation excluded two divergent unsealed rev0998 branches, pathname-based cleanup actors, vanished worktrees, interrupted aggregate CTest wrappers, and every result not bound to the final exact source.

## Archive

AnonSync-rev0998-2026.08.05.01.10-directsourceframe-zerostaging-fourterabyteproof-ulexite.zip
ulexite

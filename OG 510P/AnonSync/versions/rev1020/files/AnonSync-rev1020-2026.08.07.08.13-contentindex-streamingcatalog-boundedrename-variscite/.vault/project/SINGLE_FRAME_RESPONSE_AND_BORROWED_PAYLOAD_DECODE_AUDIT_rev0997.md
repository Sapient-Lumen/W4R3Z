# Single-frame response and borrowed payload decode audit — rev0997

## Product reason

Rev0996 made a 64 MiB grouped response reachable. The released receiver retained
the complete TLS frame and copied every payload field into owned strings before
sequential durable staging. Normal prefix staging then required another owned
record argument. Those copies were bounded but directly opposed the memory
contract required by multi-terabyte Linux media trees.

## Wire-compatible borrowed decode

Rev0997 keeps reconciliation protocol generation 7 unchanged. A request-bound
borrowed decoder structurally verifies the complete frame, parses response
metadata and operations into owned bounded objects, and represents each payload
byte field as an exact `std::string_view` into the caller-owned frame. The frame
must outlive the borrowed response, which the shipping TLS pull path guarantees
through application.

The decoder validates the borrowed response against the exact request once.
Generic owned decode remains a compatibility surface: it first validates the
borrowed views and only then materializes payload strings.

## Durable staging boundary

`SyncReplicaFilePayloadStore::stage_payload_prefix_or_throw` now accepts
`std::string_view`. The ordinary grouped-range path hashes, compares overlap,
and calls `pwrite` directly from the frame-backed view. A copy remains only for
bounded whole-payload insertion or the explicitly named legacy arbitrary-range
compatibility owner; neither creates another 64 MiB aggregate owner.

## Direct source frame integration

The source reserves one exact final frame and appends the canonical body directly.
Its frame-only shipping API avoids an unread semantic digest, while a separately
named with-digest API derives the digest from the resident body for compatibility
and memory-shape proof. The final frame then moves into TLS continuation storage,
and the response page vectors are released before backpressure.

## Deterministic allocation-shape regression

A product test constructs sixteen one-mebibyte payloads and observes allocations
at or above 512 KiB. It requires exactly one page-sized encode allocation, zero
page-sized borrowed-decode allocations, every view wholly inside the retained
frame, every corresponding owned payload string empty, unchanged canonical frame
bytes and semantic digest, and at least one owned allocation per payload in the
legacy decoder. The differential proves removed ownership rather than only
semantic equality.

## Honest memory claim

Rev0997 removes the source temporary body, copied TLS continuation, receiver
aggregate payload copy, and normal record-staging copy. It does not claim one total resident page. Source response payload objects and the final frame coexist
during encoding. OpenSSL and kernel socket buffers are outside the allocation
oracles. This is not measured 64 MiB or multi-terabyte peak RSS.

## Next product edge

Measure the remaining source two-owner cutpoint with 64 MiB and sparse synthetic
multi-terabyte shapes. Include restart, disk-write amplification, high-latency
direct/Tor/I2P routes, and controlled ENOSPC. Use the results to choose a
consuming or streaming source encoder, source response views, cross-file chunk
discovery, or another delta refinement. Rename/move identity and directory
semantics remain the next ordinary file-product surfaces.

## Validation

Exact rev0997 source passed a fresh 549-edge GCC 14.2 Debug graph and a no-work bundled-SQLite re-attestation; all 279/279 registered tests passed, and an independent 46/46 product replay passed. Focused GCC proofs passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 650 payload-store, 39 content-defined-chunker, 98 network-model plus 41 generated-operation, 361 SQLite-owner, 536 folder-owner, 110 sync-once, 4,967 reconciliation-protocol, 6 source-frame-memory, 25 borrowed-memory-shape, 117 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 19/19 direct-response-frame, 27/27 borrowed-response-memory, and 482/482 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 260/260 edges; all 46/46 product tests passed with leak detection and halt-on-error, and focused sanitizer proofs passed 650 payload-store, 4,967 reconciliation-protocol, 6 source-frame-memory, 25 borrowed-memory-shape, 117 reconciliation-service, and 2,044 TLS-transport checks. The sanitized 536-check folder-owner proof completed in 28.20 seconds at 1,688,636 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0996 parent SHA-256 matched f57105c8156a138decc394c4c25092b87d5df83f919b03c401e18a3fec75a007 and passed 41/41 wrapper-aware package checks. Its inherited stale visible goshenite/20.48 labels were corrected to the actual sealed petalite/20.52 identity already bound by lineage and release gate. The active implementation projection contains 607 files / 27,989,270 bytes with SHA-256 00840cfa9a06971c6d5e69784303b524a8158275624a7abe78b17b38027c8f5b. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality checks remain mandatory publication gates.

## Archive

AnonSync-rev0997-2026.08.04.22.41-singleframe-ownedtls-borrowedstaging-diaspore.zip
diaspore

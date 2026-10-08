# Direct response frame and owned TLS handoff audit — rev0997

## Product reason

Generation 7 can carry as much as 64 MiB of payload data in one grouped
response. A temporary canonical body, a final frame, a copied TLS continuation,
and the retained response payload page would make the configured bound multiply
inside one source turn. Multi-terabyte Linux media trees make that ownership
shape a product concern rather than a micro-optimization.

## Exact direct frame

The response encoder validates the semantic object, projects the exact canonical
body and payload byte counts with checked arithmetic, computes the final frame
size, reserves that frame once, and appends the body directly after the wire
header. Measured and emitted body and frame lengths are compared before return.
The structural digest is calculated over a view of the body already in the final
frame.

The shipping request-bound frame-only API does not derive an unused semantic
response digest. The separately named with-digest API retains compatibility for
independent callers and tests, deriving the semantic digest from the same body
view without rebuilding a body string.

Protocol generation, frame magic, body ordering, digest domains, limits, and
payload-before-operation semantics are unchanged.

## Owned TLS continuation

The borrowed TLS writer retains its explicit copy-before-reservation contract.
Rev0997 adds a by-value writer that moves the final frame allocation into the
same bounded, move-only continuation before stream reservation. The authenticated
serve path records compact disposition state, releases response operations,
payload strings, and metadata-only identifiers, then transfers the frame.

`response_frame_owned_handoffs` and
`reconciliation_response_frame_owned_handoffs` make accepted ownership transfer
observable. An already-expired deadline does not claim a handoff.

## Deterministic source allocation oracle

A product regression constructs one canonical 8 MiB whole-payload response
before arming allocation accounting. Encoding must reserve one allocation at
least as large as the final frame, make no materially larger allocation, remain
within final-frame bytes plus a 2 MiB auxiliary frontier, and round-trip exact
wire semantics. This is deterministic allocation-volume evidence, not an operating-system peak-RSS claim.

## Companion receiver correction

The companion borrowed-decode slice in
`SINGLE_FRAME_RESPONSE_AND_BORROWED_PAYLOAD_DECODE_AUDIT_rev0997.md` removes the
former receive-side frame-plus-owned-payload aggregate. The retained TLS frame
now backs validated payload views through normal durable prefix staging.

## Remaining memory frontier

At the source encoding cutpoint, response payload objects and the one final frame
still coexist. OpenSSL and kernel socket buffers are also outside the allocator
oracles. Rev0997 is therefore not streaming framing, not a one-page total RSS
claim, and not permission to raise the 64 MiB frontier.

The next experiment must measure 64 MiB and sparse synthetic multi-terabyte
shapes, disk amplification, restart, high-latency routes, and controlled ENOSPC.
A consuming/streaming source encoder should be selected only from those results.

## Validation

Exact rev0997 source passed a fresh 549-edge GCC 14.2 Debug graph and a no-work bundled-SQLite re-attestation; all 279/279 registered tests passed, and an independent 46/46 product replay passed. Focused GCC proofs passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 650 payload-store, 39 content-defined-chunker, 98 network-model plus 41 generated-operation, 361 SQLite-owner, 536 folder-owner, 110 sync-once, 4,967 reconciliation-protocol, 6 source-frame-memory, 25 borrowed-memory-shape, 117 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 19/19 direct-response-frame, 27/27 borrowed-response-memory, and 482/482 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 260/260 edges; all 46/46 product tests passed with leak detection and halt-on-error, and focused sanitizer proofs passed 650 payload-store, 4,967 reconciliation-protocol, 6 source-frame-memory, 25 borrowed-memory-shape, 117 reconciliation-service, and 2,044 TLS-transport checks. The sanitized 536-check folder-owner proof completed in 28.20 seconds at 1,688,636 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0996 parent SHA-256 matched f57105c8156a138decc394c4c25092b87d5df83f919b03c401e18a3fec75a007 and passed 41/41 wrapper-aware package checks. Its inherited stale visible goshenite/20.48 labels were corrected to the actual sealed petalite/20.52 identity already bound by lineage and release gate. The active implementation projection contains 607 files / 27,989,270 bytes with SHA-256 00840cfa9a06971c6d5e69784303b524a8158275624a7abe78b17b38027c8f5b. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality checks remain mandatory publication gates.

## Archive

AnonSync-rev0997-2026.08.04.22.41-singleframe-ownedtls-borrowedstaging-diaspore.zip
diaspore

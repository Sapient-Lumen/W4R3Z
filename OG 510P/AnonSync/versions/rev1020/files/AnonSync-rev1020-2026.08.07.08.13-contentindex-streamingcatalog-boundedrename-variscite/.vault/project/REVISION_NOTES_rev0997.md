# Revision notes — rev0997

## Summary

Rev0997 preserves reconciliation protocol generation 7 while removing avoidable
page-sized ownership from source framing, TLS handoff, receiver decoding, and
normal durable range staging.

## Source frame and TLS ownership

- Projects exact canonical body, payload, and final-frame sizes with checked
  arithmetic.
- Reserves one final frame and appends the canonical response body directly.
- The shipping request-bound frame encoder avoids both a temporary full body and
  an unread semantic digest.
- The compatibility with-digest encoder hashes the body already resident in the
  final frame instead of serializing it again.
- Moves request and response frames by value into bounded TLS continuation
  storage.
- Releases response operations, payload strings, and metadata-only IDs before
  waiting on response network backpressure.
- Exposes exact owned-frame handoff accounting through authenticated source and
  shipping JSON surfaces.

## Borrowed receiver and durable staging

- Adds a request-bound borrowed decoder whose payload byte fields are
  `std::string_view` instances into the caller-owned frame.
- Keeps owned payload strings empty through the shipping apply path.
- Validates the borrowed response against the exact request without generic-then-
  request duplicate payload hashing.
- Changes normal contiguous-prefix staging to borrow bytes through hashing,
  overlap comparison, and `pwrite`.
- Retains copies only for the bounded whole-payload insertion and named legacy
  arbitrary-range compatibility path.

## Deterministic memory-shape proof

- An 8 MiB source regression permits one final-frame allocation plus a 2 MiB
  auxiliary frontier and proves exact owned decode equality.
- A sixteen-payload 16 MiB regression requires exactly one page-sized encode
  allocation, zero page-sized borrowed-decode allocations, frame-contained
  payload views, unchanged wire/digest semantics, and the expected owned-decoder
  copy differential.

## Adjacent audit/refactor

- Removed the unused service-level `response_digest` field.
- Split frame-only and with-digest request-bound encoders so shipping does not
  pay an unread semantic hash while tests and independent callers retain it.
- Corrected TLS continuation audits to distinguish borrowed copy from owned
  transfer.
- Added focused source audits for both source/TLS ownership and borrowed receiver
  staging; release policy requires both.
- Corrected rev0996’s stale visible `goshenite`/20.48 handoff labels to the
  actual sealed `petalite`/20.52 package already bound by its lineage and release
  gate; the historical authority-incident record remains intact.

## Product boundary

The source response payload page and final frame still coexist at the encoding
cutpoint. OpenSSL and kernel socket buffers remain outside the allocation
oracles. Rev0997 is not measured 64 MiB or multi-terabyte peak RSS, streaming
framing, cross-file chunk discovery, rename/move identity, complete directory
semantics, Android support, retention collection, or ENOSPC qualification.

## Validation

Exact rev0997 source passed a fresh 549-edge GCC 14.2 Debug graph and a no-work bundled-SQLite re-attestation; all 279/279 registered tests passed, and an independent 46/46 product replay passed. Focused GCC proofs passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 650 payload-store, 39 content-defined-chunker, 98 network-model plus 41 generated-operation, 361 SQLite-owner, 536 folder-owner, 110 sync-once, 4,967 reconciliation-protocol, 6 source-frame-memory, 25 borrowed-memory-shape, 117 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 19/19 direct-response-frame, 27/27 borrowed-response-memory, and 482/482 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 260/260 edges; all 46/46 product tests passed with leak detection and halt-on-error, and focused sanitizer proofs passed 650 payload-store, 4,967 reconciliation-protocol, 6 source-frame-memory, 25 borrowed-memory-shape, 117 reconciliation-service, and 2,044 TLS-transport checks. The sanitized 536-check folder-owner proof completed in 28.20 seconds at 1,688,636 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0996 parent SHA-256 matched f57105c8156a138decc394c4c25092b87d5df83f919b03c401e18a3fec75a007 and passed 41/41 wrapper-aware package checks. Its inherited stale visible goshenite/20.48 labels were corrected to the actual sealed petalite/20.52 identity already bound by lineage and release gate. The active implementation projection contains 607 files / 27,989,270 bytes with SHA-256 00840cfa9a06971c6d5e69784303b524a8158275624a7abe78b17b38027c8f5b. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality checks remain mandatory publication gates.

## Archive

AnonSync-rev0997-2026.08.04.22.41-singleframe-ownedtls-borrowedstaging-diaspore.zip
diaspore

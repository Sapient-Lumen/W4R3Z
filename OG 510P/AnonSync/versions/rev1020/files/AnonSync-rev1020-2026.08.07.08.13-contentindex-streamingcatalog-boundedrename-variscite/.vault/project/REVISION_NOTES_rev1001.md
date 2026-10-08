# AnonSync rev1001 revision notes

## Summary

Rev1001 keeps reconciliation protocol generation 7 and converts cross-file
content-defined candidate hashing from one complete-file effect into a
process-local resumable projection with a hard 32 MiB per-apply frontier.
Completed source chunks become available for exact local reuse before the
source whole manifest finishes. A newly available local payload restarts an
otherwise exhausted current-visible search without requiring a causal-state
change.

## C++ changes

- Added move-only `SyncReplicaFilePayloadStoreContentDefinedProjection` state.
- Added bounded `advance_content_defined_projection_or_throw` over independently
  reopened exact payload descriptors.
- Centralized complete and bounded content-defined hashing in one
  `ContentDefinedDigestAccumulator`.
- Bound continuation to the expected content digest, exact size, canonical
  eleven-field POSIX observation, and exact chunking parameters.
- Clear unfinished projection state on any read or observation failure.
- Added one hard 32 MiB cross-file projection-hash budget per reconciliation
  apply invocation, independent of the wire page.
- Incrementally index completed chunks and reuse them before complete source
  manifestation.
- Require complete source whole-digest verification before caching a reusable
  source manifest.
- Restart an exhausted candidate sweep when the payload store's process-local
  durable-availability generation advances.
- Added unavailable-candidate, availability-restart, and projection-step
  counters through service, TLS, `anonsync_sync`, and `anonsync_replica` JSON.

## Runtime regressions

- Payload-store projection proceeds in five-byte steps across newly reopened
  descriptors and reproduces the canonical complete manifest exactly.
- New durable payload identities advance availability generation; duplicate
  insertion and replay do not.
- A 48 MiB decoy consumes two bounded projection turns.
- A matching 48 MiB renamed source is initially absent, later appears without a
  visible-state change, restarts the exhausted search, yields reusable chunks
  before whole-source completion, reduces network bytes, and publishes exact
  target bytes.

Focused GCC evidence before release sealing:

- payload-store: 674 checks;
- reconciliation service: 158 checks;
- TLS transport: 2,044 checks.

## Adjacent audit/refactor

The shared digest accumulator removes a second implementation of content-defined
boundary and digest segmentation. The audit also removed accidental coupling
between local projection work and the negotiated wire page. An early oracle
conflated cumulative and per-turn metrics; the retained test proves both
separately.

A concurrent process rewrote reviewed files during the first build. That source
and every derived build result were excluded. The retained authority was moved
to a nonce path and re-attested around focused builds.

## Product boundary

This is a latency and fairness correction for cold cross-file discovery. It does
not reduce the total bytes needed to reject every candidate, persist unfinished
projection across restart, create a durable/global chunk index, or make a
matched very-large local chunk copy resumable. At the four-terabyte ceiling,
adaptive chunks can still be large enough that the latter becomes a meaningful
next scheduling edge.

Rev1001 also does not add identity-preserving rename/move, full directory
semantics, Android support, placeholders, automatic payload eviction, polished
conflict handling, best-effort collection, ENOSPC qualification, or live public
Tor/I2P performance proof.

## Release cutpoint

Validation: `Exact rev1001 source passed a fresh GCC 14.2 Debug graph (551/551 configured build edges) and a no-work bundled-SQLite re-attestation; all 284/284 registered tests were accounted for, including both final documentation-sensitive audits, and an independent 47/47 product replay passed. Focused GCC proofs passed 677 payload-store, 158 reconciliation-service, 536 folder-owner, 397 SQLite-owner, and 2,044 TLS-transport checks. Source audits passed 32/32 bounded resumable projection, 22/22 inherited cross-file discovery, 31/31 content-defined delta, 27/27 manifest reference, and 521/521 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product dependency graph completed 262/262 edges and reached a no-work re-attestation; all 47/47 product tests were accounted for with leak detection and halt-on-error. Focused sanitizer proofs passed 677 payload-store, 158 reconciliation-service, and 536 folder-owner checks; the folder-owner proof completed in 32.10 seconds at 1,684,368 KiB peak RSS. Aggregate final-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1000 parent SHA-256 matched c68736ec03cd91298180b689a5c85228cdced06679e3b1fc836949017fd6d8c3 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 21/21 changed wrapper paths, all 20/20 changed project paths, all 17/17 changed active paths, and the complete 612-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 612 files / 28,276,868 bytes with SHA-256 9e3197543e4f453cd5bd17897304ab44c3733e08e510a496b391d56383ee3b9e. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excluded remount-vanished worktrees and caches, the divergent availability-only release branch, interrupted aggregate CTest wrappers, superseded lexical-audit failures, and generated Python bytecode removed before projection sealing.`

Archive: `AnonSync-rev1001-2026.08.05.08.49-boundedprojection-lateavailability-singleindex-chrysoprase.zip`

Codename: `chrysoprase`

# Revision notes — rev0998

## Summary

Rev0998 preserves reconciliation protocol generation 7 while removing the last
known payload-sized source copy beside one canonical response frame.

## Direct source frame assembly

- Adds a move-only protocol assembly owner with exact writable payload holes.
- Projects and cross-checks canonical body, payload, and final-frame sizes.
- Commits one exact chunk SHA-256 per range and validates frame-backed bytes
  against the complete request-bound response before writing the trailer.
- Rejects uncommitted ranges, duplicate commits, malformed digests, extent
  drift, and wire-size drift.
- Keeps the existing owned service API only as a compatibility wrapper over the
  direct frame path.

## Descriptor-to-frame payload transfer

- Adds caller-owned exact range fill to the opened immutable payload object.
- Reads with `pread`, hashes while filling, preserves descriptor position, and
  re-proves the exact inode observation.
- Retains typed complete-payload integrity failure behavior.
- Caps each read request at `SSIZE_MAX`.
- Refactors the compatibility string-returning range operation through the same
  exact reader.
- Releases exact payload descriptors and inode-use leases before TLS waiting.

## Memory and scale proof

- Publishes and serves an actual 64 MiB payload through the shipping path.
- Tags allocation observations and counts every allocation at or above 2 MiB.
- Requires exactly one such allocation and one simultaneously live large owner
  on the direct path: the final frame.
- Requires the compatibility API to expose two simultaneously live owners—frame
  plus decoded payload—without changing canonical bytes.
- Constructs a canonical 4 TiB extent while transferring one four-MiB range and
  requires one live large allocation, proving that logical extent does not
  become resident payload ownership.
- Fixes public product ceilings at 128 payload descriptors, 64 MiB of payload
  bytes per page, and a 96 MiB response frame; callers may only narrow them.
- Exposes and tests live direct-frame bytes, zero aggregate page ownership at
  reservation, zero source staging, and bounded descriptor fanout.
- Adds protocol assembly lifecycle and payload-store direct-fill regressions.

## Adjacent audit/refactor

- Centralizes direct and compatibility byte reads in one implementation.
- Updates the inherited rev0997 memory-shape audit to recognize the direct
  source path while preserving the named compatibility-copy boundary.
- Adds a dedicated rev0998 source audit and release-package requirements.
- Stops and excludes two divergent rev0998 branches, pathname-based cleanup
  actors, killed runs, and vanished worktrees from release authority.
- Reconstructs the retained direct-fill design over the exact sealed rev0997
  source in one neutral validation authority.

## Product boundary

Rev0998 is not streaming framing, TLS zero-copy, operating-system peak-RSS proof,
route throughput qualification, cross-file chunk discovery, rename/move
identity, full directory semantics, placeholder selective sync, retention
collection, Android support, or ENOSPC qualification. OpenSSL, kernel buffers,
metadata vectors, and one bounded content-defined manifest remain outside the
one-frame allocation claim.

## Validation

Exact rev0998 source passed a fresh GCC 14.2 Debug graph (551/551 configured build edges) and a no-work bundled-SQLite re-attestation; all 281/281 registered tests and an independent 47/47 product replay were accounted for from the exact source. Focused GCC proofs passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 652 payload-store, 39 content-defined-chunker, 98 network-model plus 41 generated-operation, 361 SQLite-owner, 536 folder-owner, 110 sync-once, 4,989 reconciliation-protocol, 6 response-frame-memory, 25 borrowed-memory-shape, 10 direct-source-frame, 117 reconciliation-service, 2,044 TLS-transport, and 162 local-control checks. Source audits passed 34/34 direct-source-frame, 19/19 response-frame-memory, 27/27 response-memory-shape, 33/33 targeted-source-access, and 496/496 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product dependency graph completed 262/262 edges; all 47/47 product tests passed with leak detection and halt-on-error. Focused sanitizer proofs passed 652 payload-store, 4,989 reconciliation-protocol, 10 direct-source-frame, 117 reconciliation-service, 2,044 TLS-transport, and 536 folder-owner checks; the folder-owner proof completed in 29.39 seconds at 1,692,128 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0997 parent SHA-256 matched 64125a2e82f1e9bb789c14abc2f94f5dbf55c667e6f61b92406b5fbd4389e6de and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 25/25 changed project paths, all 22/22 changed active paths, the one changed wrapper restart page, and the complete 609-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 609 files / 28,088,843 bytes with SHA-256 35acfcd7ff22a865d1321a5272b96af33dd6d138a21641178386a4ab746fbe41. Validation excluded two divergent unsealed rev0998 branches, pathname-based cleanup actors, vanished worktrees, interrupted aggregate CTest wrappers, and every result not bound to the final exact source.

## Archive

AnonSync-rev0998-2026.08.05.01.10-directsourceframe-zerostaging-fourterabyteproof-ulexite.zip
ulexite

# Revision notes — rev0994

## Summary

Rev0994 replaces the shipping fixed-boundary large-file delta seam with bounded
content-defined chunks. Small insertions or deletions can now resynchronize with
later unchanged predecessor content instead of invalidating every subsequent
absolute block.

## C++ changes

- Added an allocation-free deterministic gear-hash chunker with canonical
  minimum, average, maximum, and count limits.
- Added descriptor-rooted payload content-defined manifest projection with
  per-chunk SHA-256 and final whole-file SHA-256 reproof.
- Advanced reconciliation framing to generation 6.
- Added a bounded 8,192-record variable-chunk manifest and constant-size
  continuation reference.
- Added cumulative target and predecessor chunk-offset caches.
- Added digest-and-size predecessor lookup that permits a matching chunk to be
  copied from a different absolute offset.
- Preserved durable prefix staging, bounded wire ranges, payload-before-metadata
  ordering, and final whole-payload verification.
- Propagated source, target-cache, predecessor-index, and shifted-reuse counters
  through TLS and shipping JSON.
- Removed the superseded fixed-block payload projection and current shipping
  vocabulary rather than retaining two delta engines.

## Focused regression

The service regression mutates a deterministic 48 MiB payload by inserting
256 KiB near the beginning and editing a distant region. It proves at least four
shifted chunks and at least 16 MiB of exact predecessor content are reused,
while the final payload bytes and causal evidence match the source. It also
proves cache bootstrap/reference behavior and forged complete-chunk rejection.

The protocol regression constructs the maximum 8,192-record manifest shape and
proves the canonical frontier covers 4 TiB without allocating a 4 TiB file.

## Product boundary

This is the first insertion-resilient delta path, not the final large-file
performance model. Cross-file chunk discovery, multilevel delta, compression,
measured multi-terabyte peak RSS, controlled ENOSPC behavior, Android, rename and
move identity, directory semantics, placeholders, and automatic selective-sync
payload eviction remain open.

## Validation

Exact rev0994 source completed a fresh 540-edge GCC 14.2 Debug graph and a no-work bundled-SQLite re-attestation; all 273/273 registered tests and all 44/44 product tests were accounted for across bounded terminal shards. Focused GCC proofs passed 39 content-defined-chunker, 650 payload-store, 4,955 reconciliation-protocol, 113 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 31/31 content-defined-delta, 27/27 manifest-reference, 33/33 targeted-source-access, 52/52 selective-sync, and 458/458 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 256/256 edges; all 44/44 product tests and the same five focused suites passed with leak detection and halt-on-error. The sanitizer folder-owner proof passed 536 checks with 1,686,160 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0993 parent SHA-256 matched a9ac6bd2a95c56061d4ea836725d3e5691f117e2887d415b4bb82c9964540504 and passed 41/41 checks under its sealed wrapper-aware verifier. The binary-aware source patch reconstructed all 29/29 changed project paths, all 26/26 changed active paths, and the complete 601-file active projection byte-for-byte and mode-for-mode. The active projection contains 601 files / 27,831,652 bytes with SHA-256 ec5931b9b28566148ffd8d053d22d88a07549ac39b52d1e22dffb66db21e07e7. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality checks remain mandatory publication gates.

## Archive

AnonSync-rev0994-2026.08.04.17.13-contentdefined-shiftedreuse-boundedmanifest-kyanite.zip
kyanite

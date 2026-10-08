# Revision notes — rev0995

## Summary

Rev0995 removes a source-side per-range cumulative-index rebuild from the
content-defined delta path. One authenticated serve session now retains one
cohesive bounded manifest/index cache across valid continuations.

## C++ changes

- Added `CachedSourceContentDefinedManifest`, binding payload identity, exact
  rooted descriptor metadata, manifest digest, canonical manifest, and cumulative
  chunk offsets in one lifetime.
- Builds the source cumulative chunk index once after a cold manifest projection.
- Reuses the exact retained index for later chunk lookup in the same bound serve
  session.
- Resets the complete cache on source change rather than clearing parallel state.
- Rejects a stale cached-manifest reference before chunk lookup and before range
  copy.
- Added source-session counters for index builds, reuses, and lookups.
- Propagated those counters through authenticated TLS results and shipping JSON.

## Scale proof

At the 4 TiB payload frontier with 4 MiB wire ranges and 8,192 content-defined
chunks, the previous path admitted exactly 8,589,934,592 redundant cumulative
prefix additions and 68,727,865,344 bytes (64.0078125 GiB) of avoidable offset-
vector element traffic over 1,048,576 range turns.

The protocol regression records those exact values without allocating a 4 TiB
file. Focused service and TLS regressions prove one build and later reuse.

## Adjacent audit/refactor

- Updated manifest-reference and targeted-source lexical audits to follow the
  cohesive source cache rather than removed parallel fields.
- Added a dedicated source-index scale audit and bound the slice into the release
  verifier and structural authority audit.
- Excluded a divergent unsealed compact-binary-manifest prototype from source and
  validation authority.

## Product boundary

This removes one severe repeated-work multiplier. It does not remove the
1,048,576 request/response turns still required for a 4 TiB file at 4 MiB per
range. Bounded multi-range or byte-window framing is the next delta-transfer
product edge.

Rev0995 does not claim a completed multi-terabyte transfer, measured target-scale
RSS, cross-file chunk discovery, Android, rename/move identity, directory
semantics, placeholders, quota safety, or ENOSPC qualification.

## Validation

Exact rev0995 source passed a fresh 545-edge GCC 14.2 Debug graph and a no-work bundled-SQLite re-attestation; all 274/274 registered tests were accounted for across bounded terminal shards and an independent 44/44 product replay passed. Focused GCC proofs passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 650 payload-store, 39 content-defined-chunker, 98 network-model plus 41 generated-operation, 361 SQLite-owner, 536 folder-owner, 110 sync-once, 4,956 reconciliation-protocol, 115 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 18/18 source-chunk-index, 31/31 content-defined-delta, 27/27 manifest-reference, 33/33 targeted-source-access, 52/52 selective-sync, and 463/463 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 256/256 edges; all 44/44 product tests passed with leak detection and halt-on-error, and focused sanitizer proofs passed 650 payload-store, 39 content-defined-chunker, 4,956 reconciliation-protocol, 115 reconciliation-service, and 2,044 TLS-transport checks. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0994 parent SHA-256 matched cce60aea2ce146228f5163720b74b1ec666b3e56e204c5f155108d22f91ecd9a and passed 41/41 wrapper-aware package checks. The active implementation projection contains 602 files / 27,851,618 bytes with SHA-256 98fd496d786433027529c2628adc2a0f1e12c029300cb1084bd55804c965d7c1. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality checks remain mandatory publication gates.

## Archive

AnonSync-rev0995-2026.08.04.19.00-sourceindex-millionrange-framingfrontier-indicolite.zip
indicolite

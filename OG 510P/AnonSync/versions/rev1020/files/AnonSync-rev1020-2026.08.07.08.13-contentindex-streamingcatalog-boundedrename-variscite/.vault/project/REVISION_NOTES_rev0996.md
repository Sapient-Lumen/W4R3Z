# Revision notes — rev0996

## Summary

Rev0996 advances reconciliation to protocol generation 7 and replaces the
one-range-per-turn large-payload path with one bounded contiguous multi-range
window.

## C++ changes

- Allows several sorted, gap-free range records for one exact ranged payload.
- Binds one total size and one content-defined manifest digest across the group.
- Publishes a complete manifest only on the first cache-cold record and exact
  constant-size references thereafter.
- Binds continuation authority to the first requested offset and final range end.
- Emits ranges until the 128-record, 64 MiB page, 4 MiB record, chunk, or file
  frontier is reached.
- Performs one source cumulative-index lookup and then advances linearly through
  the retained index for the complete window.
- Consumes receiver ranges sequentially through the existing durable prefix and
  whole-file verification path.
- Skips later records already covered by an exact durable prefix or local
  predecessor reuse.
- Rejects overlap or gaps relative to the receiver's exact current prefix.
- Counts grouped windows, individual range records, and ranged bytes through the
  source session, authenticated TLS result, and shipping JSON surface.

## Exact scale result

At 4 TiB with the default 4 MiB record and 64 MiB page frontiers:

- one-range turns: 1,048,576;
- ranges per response window: 16;
- bounded-window turns: 65,536;
- turns avoided: 983,040.

This is exact frontier arithmetic, not measured throughput.

## Adjacent audit/refactor

- Replaced validator range-pointer vectors with scalar group state.
- Replaced receiver per-digest pointer vectors with contiguous `begin/count`
  spans into the immutable validated response.
- Stops before source payload open and manifest work when no page record or byte
  budget remains.
- Adds a deterministic zero-byte-frontier regression proving that a whole
  payload exhausting the page does not open, hash, index, or publish its ranged
  successor.
- Advances the TLS restart oracle from two one-range turns to one two-range turn
  and the real shipping process oracle from sixteen turns to one sixteen-range
  64 MiB window.
- Updated every current protocol-generation lexical oracle to generation 7.
- Added a dedicated multi-range source audit and release-package requirement.

## Product boundary

The configured page may now actually retain up to 64 MiB of payload data, and
encoding/TLS layers may add page-sized copies. Rev0996 does not claim target-scale
peak RSS, a completed multi-terabyte transfer, cross-file chunk discovery,
streaming frame publication, compression, Android, rename/move identity,
complete directory semantics, placeholders, quota safety, or ENOSPC
qualification.

## Validation

Exact rev0996 source passed a fresh 545-edge GCC 14.2 Debug graph and a no-work bundled-SQLite re-attestation; all 275/275 registered tests were accounted for across bounded terminal shards, and an independent 44/44 product replay passed. Focused GCC proofs passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 650 payload-store, 39 content-defined-chunker, 98 network-model plus 41 generated-operation, 361 SQLite-owner, 536 folder-owner, 110 sync-once, 4,960 reconciliation-protocol, 117 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 31/31 content-defined-delta, 18/18 source-chunk-index, 27/27 manifest-reference, 33/33 targeted-source-access, 52/52 selective-sync, 27/27 multi-range-window, and 472/472 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 256/256 edges; all 44/44 product tests passed with leak detection and halt-on-error, and focused sanitizer proofs passed 650 payload-store, 39 content-defined-chunker, 4,960 reconciliation-protocol, 117 reconciliation-service, and 2,044 TLS-transport checks. The sanitized 536-check folder-owner proof completed in 31.26 seconds at 1,694,252 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0995 parent SHA-256 matched 1129c9f66ba195ceda3f18b274ae58a997820ce332b44c39f9cfdf0fa033efc2 and passed 41/41 wrapper-aware package checks. The active implementation projection contains 603 files / 27,896,855 bytes with SHA-256 a42f7210b2c2109e990fef097fc26e87497cffe3770b4a1fe4b1de20f6432052. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality checks remain mandatory publication gates.

## Archive

AnonSync-rev0996-2026.08.04.20.52-multirangewindow-turncollapse-memoryfrontier-petalite.zip
petalite

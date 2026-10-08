# Revision notes — rev1000

## Summary

Rev1000 adds bounded current-visible cross-file content-defined chunk discovery
so a renamed, moved, duplicated, or regenerated media file can reuse locally
retained chunks even when it has no same-path causal predecessor.

## C++ implementation

- Adds a hard-capped current-visible primary-file page to the SQLite owner:
  64 paths, 4 MiB canonical bytes, and one lookahead row.
- Requires an exact visible-state digest and exact current-primary path cursor
  for continuation; stale source state returns before operation decoding.
- Keeps tombstones in path/byte accounting while returning only File candidates.
- Retains one bounded candidate page across apply turns so failed candidates do
  not repeatedly rescan the page tail.
- Hashes at most one plausible candidate payload per apply invocation.
- Keeps at most one selected cross-file manifest, offset vector, and
  digest-sorted chunk index for the current target manifest.
- Reopens the exact candidate operation for each bounded local range.
- Adds operator counters for candidate pages, paths, manifest scans/reuse,
  hashed bytes, matches, and index build/reuse through TLS and CLI JSON.
- Keeps reconciliation protocol generation 7 unchanged.

## Adjacent audit/refactor

Same-path predecessor reuse and cross-file reuse now share one exact local
chunk-copy and durable-staging boundary. The audit also found and removed a
bounded but wasteful quadratic page-tail rescan: one 64-entry page is moved into
process state and consumed once across turns.

The public page limits are hard ceilings rather than caller-adjustable defaults.

## Runtime proof

- SQLite owner: 397 focused checks.
- Reconciliation service: 144 focused checks.
- TLS transport: 2,044 focused checks.
- The cross-file regression uses one unrelated 48 MiB file, one 48 MiB renamed
  source, a shifted/edited target, and 4 MiB windows. It proves one SQL candidate
  page, two candidate hashes across separate turns, one match, local chunk
  reuse, lower network transfer, and exact final payload/operation convergence.

## Product boundary

This is a first-generation current-visible accelerator, not a global chunk
index. Candidate manifests are memory-bounded but require a complete candidate
byte read, so multi-terabyte hash latency remains an open performance question.
Rename/move identity, directory semantics, target-scale route/ENOSPC measurement,
Android, placeholders, and retention collection remain incomplete.

## Validation

Exact rev1000 source passed a fresh GCC 14.2 Debug graph (551/551 configured build edges) and a no-work bundled-SQLite re-attestation; all 283/283 registered tests were accounted for, including the two final documentation-sensitive source audits, and an independent 47/47 product replay passed. Focused GCC proofs passed 397 SQLite-owner, 144 reconciliation-service, 536 folder-owner, and 2,044 TLS-transport checks. Source audits passed 22/22 cross-file discovery, 31/31 content-defined delta, 27/27 manifest-reference, and 511/511 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product dependency graph completed 262/262 edges and reached a no-work re-attestation; all 47/47 product tests passed with leak detection and halt-on-error. Focused sanitizer proofs passed 397 SQLite-owner, 144 reconciliation-service, and 536 folder-owner checks; the folder-owner proof completed in 29.87 seconds at 1,690,840 KiB peak RSS, the reconciliation-service proof in 30.17 seconds at 774,444 KiB, and the SQLite-owner proof in 11.38 seconds at 777,440 KiB. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0999 parent SHA-256 matched 7b897c44e66870dd55e5df707d5d5e5180f60edbbe2baf4af431b861490cd3e0 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 20/20 changed wrapper paths, all 19/19 changed project paths, all 16/16 changed active paths, and the complete 611-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 611 files / 28,197,616 bytes with SHA-256 9653cca2703de4448b510a49c8321d95c72354716de08152bedaec8185197c05. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excluded remount-vanished worktrees and caches, timestamp-only CMake regeneration attempts, interrupted aggregate real-process harnesses, a divergent indexed cross-file prototype and its validators, unrelated build lanes, and a redundant terminated sanitizer rerun.

## Archive

`AnonSync-rev1000-2026.08.05.06.02-crossfilechunks-visiblepage-singlehash-hackmanite.zip`

Codename: `hackmanite`

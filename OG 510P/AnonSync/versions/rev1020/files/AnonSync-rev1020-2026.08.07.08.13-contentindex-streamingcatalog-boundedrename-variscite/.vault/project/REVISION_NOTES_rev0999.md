# Revision notes — rev0999

## Summary

Rev0999 keeps reconciliation protocol generation 7 while removing complete
retained-history reconstruction from every bounded large-file transfer window.

## C++ implementation

- Adds `SyncReplicaSqliteIdentityCutpoint`, a fixed transactionally pinned owner
  identity and limit observation with no operation or projection decoding.
- Centralizes current schema, foreign-key, metadata, and owner-identity reproof.
- Replaces evidence-page whole-model restore and in-memory sort with a bounded
  primary-key range query plus one lookahead row.
- Rejects stale source digests before cursor or operation-row access.
- Replaces receiver-side complete-history predecessor lookup with the existing
  exact-path SQLite cutpoint.
- Copies the predecessor operation out of its cutpoint before using it, avoiding
  a dangling observation lifetime.
- Retains complete causal reconstruction at final remote operation admission.

## Runtime proof

- SQLite-owner SQL traces prove fixed identity reads, bounded evidence ranges,
  exact cursor lookup, and stale-source early rejection without complete
  operation or visible projections.
- The multi-range shifted-predecessor regression proves its first progress turn
  is history-cold and that source windows remain primary-key bounded.
- Focused GCC results currently pass 380 SQLite-owner checks and 122
  reconciliation-service checks.

## Adjacent audit/refactor

A divergent unsealed cross-file prototype repeatedly rewrote the first rev0999
path. It was preserved only as forensic evidence and excluded. The retained
source was reconstructed from exact sealed rev0998 bytes in a randomized
working authority. The obsolete service history-vector lookup helper was
removed.

## Product boundary

Rev0999 is a scale prerequisite for multi-terabyte delta transfer, not completed
cross-file discovery, rename/move, Android support, target-scale soak evidence,
quota/ENOSPC behavior, or hostile same-UID database protection.

## Validation

Exact rev0999 source passed a fresh GCC 14.2 Debug graph (551/551 configured build edges)
and a no-work bundled-SQLite re-attestation; all 282/282 registered tests were accounted
for, including the two final documentation-sensitive source audits, and an independent 47/47
product replay passed. Focused GCC proofs passed 380 SQLite-owner, 122 reconciliation-
service, and 536 folder-owner checks. Source audits passed 21/21 bounded-history-access,
34/34 direct-source-frame, 27/27 response-memory-shape, 30/30 targeted-path-cutpoint, and
503/503 structural-authority checks. A fresh Clang 17 Debug
AddressSanitizer/UndefinedBehaviorSanitizer product dependency graph completed 262/262 edges
across bounded resumptions and reached a no-work re-attestation; all 47/47 product tests
passed with leak detection and halt-on-error. Focused sanitizer proofs passed 380 SQLite-
owner, 122 reconciliation-service, and 536 folder-owner checks; the folder-owner proof
completed in 28.75 seconds at 1,689,024 KiB peak RSS, while the complete product lane peaked
at 1,692,312 KiB. Aggregate retained-log inspection found no compiler, linker,
AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic.
The exact rev0998 parent SHA-256 matched
dbc9b4f7fb972abd2ecfa10cabebeed6b5bba7c8c277d511bf2834d87bfd702f and passed 41/41 wrapper-
aware package checks. The binary-aware source patch reconstructed all 17/17 changed wrapper
paths, all 16/16 changed project paths, all 13/13 changed active paths, and the complete
610-file active projection byte-for-byte and mode-for-mode. The final active implementation
projection contains 610 files / 28,125,448 bytes with SHA-256
5110b2cce7e9f19917c9bf10a958fb22c4a42eee1affdadb64b5c88128153d68. Validation excluded
divergent unsealed rev0999 prototypes, an orphaned exclusion guard that named the live
authority, unrelated compiler/test lanes, vanished remount-era worktrees and build caches,
interrupted build chunks, and every result not re-proved from the reconstructed exact
source. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality
checks remain mandatory publication gates.

## Archive

AnonSync-rev0999-2026.08.05.02.52-primarykeypage-identitycutpoint-historycold-taaffeite.zip

Codename: `taaffeite`

# Rev1000 audit

## Product defect

Content-defined reuse stopped at the same canonical path. A renamed, moved, duplicated, or regenerated large media file could already exist almost entirely in the receiver payload store and still be retransmitted because no causal predecessor edge connected the two paths.

## Correction

Rev1000 adds a hard-capped current-visible primary-key page: 64 visible paths, 4 MiB canonical operation bytes, and one lookahead. The receiver retains one page across bounded apply turns, hashes at most one plausible current-visible candidate per turn, keeps at most one match, and reopens exact immutable ranges through the existing payload capability. Final whole-payload SHA-256 and causal admission are unchanged.

## Adjacent refactor

Same-path and cross-file chunk reuse now share one local-copy and durable-staging helper. This also removed a bounded but quadratic page-tail rescan. Two inherited lexical audits were updated to follow that centralized authority instead of obsolete local spellings.

## Validation

- GCC graph: 551/551 edges and no-work re-attestation.
- GCC registry: 283/283; independent product accounting: 47/47.
- Clang ASan/UBSan graph: 262/262 edges and no-work re-attestation; product accounting: 47/47.
- Focused proofs: 397 SQLite-owner, 144 reconciliation-service, 536 folder-owner, and 2,044 TLS checks.
- Source audits: 22/22, 31/31, 27/27, and 511/511.
- Exact rev0999 parent and binary-aware reconstruction proof passed.

## Nonclaims

This is not a durable or global chunk index. One candidate hash may read a complete multi-terabyte file. Discovery covers current-visible files only, is process-local, and does not add identity-preserving rename/move, directory semantics, Android support, quota/ENOSPC qualification, or route-throughput proof.

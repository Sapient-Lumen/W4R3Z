# Rev0999 audit

## Defect

Generation-7 grouped delta windows bounded payload bytes but still reconstructed the complete retained replica model on request creation, source serving, and receiver predecessor selection. A maximum 4 TiB payload with 64 MiB windows permits 65,536 turns and therefore admitted up to 262,144 complete model reconstructions before terminal admission work.

## Correction

Rev0999 adds a fixed SQLite owner-identity cutpoint, rewrites evidence paging as a primary-key range capped at one page plus one lookahead, and re-proves one exact predecessor path instead of searching complete history. Complete causal reconstruction remains the deliberate terminal operation-admission boundary.

## Adjacent refactor

Current owner metadata reproof is centralized across identity, targeted-path, and evidence-page readers. The obsolete history-vector lookup helper is removed. SQL-trace regressions fail if bounded progress turns regain complete operation or visible projections.

## Validation

- GCC graph: 551/551 edges and no-work re-attestation.
- GCC registry: 282/282; independent product lane: 47/47.
- Clang ASan/UBSan product graph: 262/262 edges across bounded resumptions and no-work re-attestation; product lane: 47/47.
- Focused proofs: 380 SQLite-owner, 122 reconciliation-service, and 536 folder-owner checks under both ordinary and sanitizer builds.
- Source audits: 21/21, 34/34, 27/27, 30/30, and 503/503.
- Exact parent and binary-aware reconstruction proof passed.

## Nonclaims

This does not provide hostile same-UID database protection, cross-file chunk discovery, completed multi-terabyte soak evidence, rename/move identity, Android support, quota/ENOSPC qualification, or route-throughput proof.

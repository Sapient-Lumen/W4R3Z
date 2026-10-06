# ADR-0362: Removable-media local fallback post-detach reader-use ledger retention is typed and negative-tested

## Status

Accepted.

## Context

r504 closed the post-detach worker contract, r505 launch evidence, r506 recovery, r507 query projection, r508 export bundles, r509 tombstones, r510 denial receipts, r511 fresh-authority reissue, r512 fresh-authority consumption, r513 successor-index cutover, r514 checkpointing, r515 reader admission, r516 reader use, and r517 the reader-use ledger commit. The next lifecycle seam is retention: the lane must not avoid replay or double-spend risk by retaining raw observations forever, and it must not compact the ledger in a way that erases the proof needed to audit exhausted budgets and future denials.

## Decision

Add `spec/removable.media.local.post_detach.reader.use.ledger.retention.receipt.schema.json` with kind `removable.media.local.post_detach.reader.use.ledger.retention.receipt`, the canonical example `spec/examples/removable.media.local.post_detach.reader.use.ledger.retention.receipt.json`, and a red corpus under `spec/examples/invalid/removable-media/post-detach-reader-use-ledger-retention-receipt/`.

The ordinary B/C removable-media local fallback now records `typed-post-detach-reader-use-ledger-retention-positive-and-negative-fixture-guarded`, `sha256:f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8`, and `known-bad-post-detach-reader-use-ledger-retention-shapes-must-fail-validation` after the r517 reader-use ledger receipt. A reader-use ledger retention receipt binds one exact ledger root, one budget epoch, one successor subject, one debit record, one retention policy, one compaction commit, one audit summary, and one proof-carry-forward digest. It records `post-detach-reader-use-ledger-retention-bounded-redacted-and-auditable` and rejects missing ledger receipts, raw observation retention, raw receipt-payload retention, open-ended retention, compaction before ledger commit, missing audit summaries, missing proof carry-forward, rollback or forked compaction roots, raw locators, filenames, body/full-text, host identity, secret material, future queries that do not use the compacted root, result-before-ledger visibility, and offline-erasure overclaim.

## Consequences

- Reader-use ledger roots become bounded audit artifacts, not infinite raw observation logs.
- Compaction is allowed only after the ledger commit and only with digest-level proof carry-forward.
- Future denials and budget-exhaustion audits can use the compacted root without reopening raw entries.
- Ledger retention is fail-closed when it loses causality, redaction, or monotonicity.
- The post-detach checker-helper refactor now has shared positive-fixture validation used by both r517 and r518 checkers.

## Validation

`tools/check_removable_media_local_post_detach_reader_use_ledger_retention_receipt.py` validates the canonical fixture, proves the red corpus fails, and keeps `typed-post-detach-reader-use-ledger-retention-positive-and-negative-fixture-guarded` wired through the r517 ledger receipt and the existing removable-media post-detach chain.

Last updated: 2026-05-25r518

# ADR-0363: Removable-media local fallback post-detach reader-use ledger retention expiry is typed and negative-tested

## Status

Accepted.

## Context

r504 closed the post-detach worker contract, r505 launch evidence, r506 recovery, r507 query projection, r508 export bundles, r509 tombstones, r510 denial receipts, r511 fresh-authority reissue, r512 fresh-authority consumption, r513 successor-index cutover, r514 checkpointing, r515 reader admission, r516 reader use, r517 reader-use ledger commits, and r518 bounded reader-use ledger retention. The next lifecycle seam is expiry: a bounded retention receipt names an expiry timestamp, but without typed expiry evidence the implementation can silently extend retention, delete the proof carry-forward needed for denials, or keep serving new reads from an expired compacted root.

## Decision

Add `spec/removable.media.local.post_detach.reader.use.ledger.retention.expiry.receipt.schema.json` with kind `removable.media.local.post_detach.reader.use.ledger.retention.expiry.receipt`, the canonical example `spec/examples/removable.media.local.post_detach.reader.use.ledger.retention.expiry.receipt.json`, and a red corpus under `spec/examples/invalid/removable-media/post-detach-reader-use-ledger-retention-expiry-receipt/`.

The ordinary B/C removable-media local fallback now records `typed-post-detach-reader-use-ledger-retention-expiry-positive-and-negative-fixture-guarded`, `sha256:1919191919191919191919191919191919191919191919191919191919191919`, and `known-bad-post-detach-reader-use-ledger-retention-expiry-shapes-must-fail-validation` after the r518 reader-use ledger retention receipt. A reader-use ledger retention expiry receipt binds one exact r518 retention receipt, one compacted ledger root, one retention policy, one expiry trigger, one compare-and-swap expiry commit, one retained audit summary, and one retained proof-carry-forward digest. It records `post-detach-reader-use-ledger-retention-expiry-finalized-redacted-and-denial-auditable` and rejects missing retention receipts, expiry before the retention window end, silent extension, missing audit summary or proof carry-forward, expired roots used for new reads, future reader admission without fresh authority, rollback or forked expiry roots, raw locators, filenames, body/full text, host identity, secret material, unbounded post-expiry retention, and offline-erasure overclaim.

## Consequences

- Bounded ledger retention now has a typed terminal state instead of relying on a timestamp comment.
- Expiry preserves enough digest-level proof to audit exhausted budgets and denial decisions without retaining raw observations.
- Future post-expiry reads, exports, or rehydration attempts require denial or fresh authority instead of reusing stale compacted roots.
- The lane remains honest about offline copies: expiry finalizes live/query authority, not impossible erasure of already-exported evidence.
- The post-detach checker helper now has a shared `require_guardrail_contract` package validator used by r518 and r519 checkers.

## Validation

`tools/check_removable_media_local_post_detach_reader_use_ledger_retention_expiry_receipt.py` validates the canonical fixture, proves the red corpus fails, and keeps `typed-post-detach-reader-use-ledger-retention-expiry-positive-and-negative-fixture-guarded` wired through the r518 retention receipt and the existing removable-media post-detach chain.

Last updated: 2026-05-25r519

# ADR-0364: Removable-media local fallback post-detach reader-use ledger retention expiry enforcement is typed and negative-tested

## Status

Accepted.

## Context

r504 closed the post-detach worker contract, r505 launch evidence, r506 recovery, r507 query projection, r508 export bundles, r509 tombstones, r510 denial receipts, r511 fresh-authority reissue, r512 fresh-authority consumption, r513 successor-index cutover, r514 checkpointing, r515 reader admission, r516 reader use, r517 reader-use ledger commits, r518 bounded reader-use ledger retention, and r519 retention expiry. The next lifecycle seam is enforcement: r519 says expired compacted roots are denied or require fresh authority, but without a typed enforcement receipt the actual post-expiry attempt can become an ambiguous error, a silent success, or a support/debug side channel that exposes raw attempt handles.

## Decision

Add `spec/removable.media.local.post_detach.reader.use.ledger.retention.expiry.enforcement.receipt.schema.json` with kind `removable.media.local.post_detach.reader.use.ledger.retention.expiry.enforcement.receipt`, the canonical example `spec/examples/removable.media.local.post_detach.reader.use.ledger.retention.expiry.enforcement.receipt.json`, and a red corpus under `spec/examples/invalid/removable-media/post-detach-reader-use-ledger-retention-expiry-enforcement-receipt/`.

The ordinary B/C removable-media local fallback now records `typed-post-detach-reader-use-ledger-retention-expiry-enforcement-positive-and-negative-fixture-guarded`, `sha256:2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a`, and `known-bad-post-detach-reader-use-ledger-retention-expiry-enforcement-shapes-must-fail-validation` after the r519 reader-use ledger retention expiry receipt. A retention expiry enforcement receipt binds one exact r519 expiry receipt, one expired ledger root, one attempted root, one attempted handle digest, one denial receipt digest, one rate-limit debit, one monotonic enforcement sequence, and one redacted support projection. It records `post-detach-reader-use-ledger-retention-expiry-enforcement-denied-redacted-and-fresh-authority-gated` and rejects missing expiry receipts, expired roots accepted for new observation, post-expiry export or rehydration, missing fresh-authority requirement, missing rate-limit debit, non-monotonic enforcement sequences, rollback or forked enforcement roots, stale-root acceptance, raw handles, raw locators, untrusted filenames, host identity, body/full text, secret material, support raw-payload visibility, silent success, and unbounded retry windows.

## Consequences

- Post-expiry stale-root failures are auditable and user-explainable instead of silent or ambiguous.
- Expired compacted roots cannot produce new observations, exports, or rehydration without fresh authority.
- Support projections can explain the denial using digest-level proof carry-forward without exposing raw attempt state.
- The lane remains honest that expiry removes live/query authority, not offline copies that already left the host.
- The post-detach checker helper now has `require_absent_tokens` for cheap redaction-audit checks in newer guardrails.

## Validation

`tools/check_removable_media_local_post_detach_reader_use_ledger_retention_expiry_enforcement_receipt.py` validates the canonical fixture, proves the red corpus fails, and keeps `typed-post-detach-reader-use-ledger-retention-expiry-enforcement-positive-and-negative-fixture-guarded` wired through the r519 expiry receipt and the existing removable-media post-detach chain.

Last updated: 2026-05-25r520

# ADR-0356: Removable-media local fallback post-detach fresh authority consumption is typed and negative-tested

- Status: accepted
- Date: 2026-05-22
- Deciders: archive maintainers
- Consulted: `adrs/ADR-0355-removable-media-local-fallback-post-detach-fresh-authority-reissue-is-typed-and-negative-tested.md`, `adrs/ADR-0354-removable-media-local-fallback-post-detach-denial-receipts-are-typed-and-negative-tested.md`, `docs/293-attribute-indexed-metadata-and-live-queries.md`

## Context

ADR-0355 made renewed access after a tombstone-caused denial a fresh authority receipt rather than stale-handle replay. That still leaves a smaller but dangerous ambiguity: the fresh-authority receipt itself can become a reusable renewal token if the broker does not record exactly when it was consumed and which successor artifacts it minted.

## Decision

Add `spec/removable.media.local.post_detach.fresh.authority.consumption.receipt.schema.json` with kind `removable.media.local.post_detach.fresh.authority.consumption.receipt`, the canonical example `spec/examples/removable.media.local.post_detach.fresh.authority.consumption.receipt.json`, and a red corpus under `spec/examples/invalid/removable-media/post-detach-fresh-authority-consumption-receipt/`.

The ordinary B/C removable-media local fallback now records `typed-post-detach-fresh-authority-consumption-positive-and-negative-fixture-guarded`, `sha256:a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4`, and `known-bad-post-detach-fresh-authority-consumption-shapes-must-fail-validation` in the r511 fresh-authority receipt, r510 denial receipt, r509 revocation tombstone, r508 export bundle, r507 query projection, r506 recovery evidence, r504 post-detach contract backend evidence, canonical content import plan/receipt, and post-detach preopen map.

A fresh-authority consumption receipt is required before successor query, export, rehydration, remote-locator, or managed-copy authority becomes usable. It consumes the fresh lease once, binds exact successor artifacts, preserves the tombstone and denial evidence, and says explicitly that offline copies are not erased.

## Consequences

- Fresh authority is no longer a reusable renewal token.
- Successor authority becomes a one-shot apply step with a receipt, not just an issued lease.
- Brokers can detect double-spend/reuse attempts and fail closed.
- Support/debug surfaces can explain "new authority was consumed to mint these successor digests" without exposing raw handles, raw locators, filenames, host identity, body text, or receipt payloads.
- Negative fixtures make common consumption mistakes executable: missing fresh authority, lease reuse, double-spend, broad successor scope, pattern subjects, raw locator leakage, tombstone mutation, missing consumed marker, missing index update, secret material, and offline-erasure overclaim all fail validation.

## Alternatives considered

- **Let fresh-authority receipts stay reusable until expiry.** Rejected because the receipt would become an ambient renewal capability rather than an audited one-shot apply.
- **Put consumption state only in the query/export broker database.** Rejected because broker-local state without a receipt cannot be audited, exported safely, or rederived after crash/recovery.
- **Reuse the denial receipt as the consumption marker.** Rejected because denial and reissue-consumption are distinct facts with different redaction and successor-artifact semantics.

## Follow-up

- Teach query/export/rehydration brokers to emit `removable.media.local.post_detach.fresh.authority.consumption.receipt` before using a fresh-authority receipt.
- Add UX copy that says "new access was issued and consumed once" rather than "access was restored."
- Consider generalizing this as a one-shot lease-consumption pattern outside removable media after more lanes need it.

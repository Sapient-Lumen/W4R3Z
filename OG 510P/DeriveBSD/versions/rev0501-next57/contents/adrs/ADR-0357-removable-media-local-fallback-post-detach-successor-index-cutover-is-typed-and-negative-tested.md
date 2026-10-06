# ADR-0357: Removable-media local fallback post-detach successor index cutover is typed and negative-tested

- Status: accepted
- Date: 2026-05-23
- Deciders: archive maintainers
- Consulted: `adrs/ADR-0356-removable-media-local-fallback-post-detach-fresh-authority-consumption-is-typed-and-negative-tested.md`, `docs/293-attribute-indexed-metadata-and-live-queries.md`, `docs/765-removable-media-local-fallback-post-detach-denial-receipts-are-typed-and-negative-tested.md`

## Context

ADR-0356 made fresh authority one-shot and required a consumption receipt before successor query, export, rehydration, remote-locator, or managed-copy authority becomes usable. That still left the successor index update as a digest field rather than its own reviewed object. A broker could record consumption but then leave old handles live, activate both old and new index rows, fork successor rows, or roll the index back while the receipts still looked locally plausible.

## Decision

Add `spec/removable.media.local.post_detach.successor.index.cutover.receipt.schema.json` with kind `removable.media.local.post_detach.successor.index.cutover.receipt`, the canonical example `spec/examples/removable.media.local.post_detach.successor.index.cutover.receipt.json`, and a red corpus under `spec/examples/invalid/removable-media/post-detach-successor-index-cutover-receipt/`.

The ordinary B/C removable-media local fallback now records `typed-post-detach-successor-index-cutover-positive-and-negative-fixture-guarded`, `sha256:b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3b3`, and `known-bad-post-detach-successor-index-cutover-shapes-must-fail-validation` in the r512 consumption receipt and through the inherited post-detach chain.

A successor index cutover receipt is required after fresh-authority consumption and before successor authority is live. It proves that old tombstoned query/export/rehydration/managed-copy/remote-locator handles are terminal, that exact successor digests from the consumption receipt are the only live successor rows, that no dual-active window or rollback-to-old-index path exists, and that raw locators, filenames, host identity, full text, receipt bodies, recipient text, and secrets remain outside the projection.

## Consequences

- Consumption no longer hides an untyped index transition.
- Old and successor authority cannot both be live under a successful cutover claim.
- Successor rows cannot fork, widen to pattern subjects, or become orphaned from the consumption receipt.
- Support/debug surfaces can explain the cutover with digest and purpose summaries only.
- Negative fixtures make common cutover mistakes executable: missing consumption evidence, stale old handles, dual-active windows, orphan/forked successors, pattern subjects, raw locator or filename indexing, rollback, missing cutover markers, full-text indexing, secret material, and offline-erasure overclaim.

## Status

Accepted for the next implementation-shaped cut. Richer multi-successor policy, partial cutover repair, or cross-lane index compaction requires a later RFC and a separate artifact family.

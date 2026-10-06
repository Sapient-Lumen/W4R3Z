# ADR-0359: Removable-media local fallback post-detach reader admission is typed and negative-tested

- Status: accepted
- Date: 2026-05-24
- Deciders: archive maintainers
- Consulted: `adrs/ADR-0358-removable-media-local-fallback-post-detach-successor-index-checkpoint-is-typed-and-negative-tested.md`, `docs/293-attribute-indexed-metadata-and-live-queries.md`, `docs/769-removable-media-local-fallback-post-detach-successor-index-checkpoint-is-typed-and-negative-tested.md`

## Context

ADR-0358 introduced a monotonic successor-index checkpoint, but a checkpoint is only protective if every later reader proves it observed the fenced root before using query, export, rehydration, remote-locator, or managed-copy authority. Without a typed admission receipt, a broker can accidentally treat the checkpoint as passive documentation: it can read a stale root, accept a restored old-handle root, or use a broad/pattern scope and still leave no precise evidence of the mistake.

## Decision

Add `spec/removable.media.local.post_detach.reader.admission.receipt.schema.json` with kind `removable.media.local.post_detach.reader.admission.receipt`, the canonical example `spec/examples/removable.media.local.post_detach.reader.admission.receipt.json`, and a red corpus under `spec/examples/invalid/removable-media/post-detach-reader-admission-receipt/`.

The ordinary B/C removable-media local fallback now records `typed-post-detach-reader-admission-positive-and-negative-fixture-guarded`, `sha256:d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5`, and `known-bad-post-detach-reader-admission-shapes-must-fail-validation` after the r514 checkpoint receipt. A reader admission receipt binds the checkpoint digest, marker, sequence, accepted root, successor subject digest, and reader lease before any broker action. It records `post-detach-reader-admission-checkpoint-observed-and-stale-roots-denied` and rejects missing checkpoint evidence, below-floor roots, stale roots, restored old-handle roots, dual-active snapshots, broad reader scopes, live subscriptions, use-before-admission, raw locator/filename indexing, host identity, secret material, and offline-erasure overclaim.

## Consequences

- The r514 checkpoint becomes an active admission gate rather than background evidence.
- Query/export/rehydration readers must produce admission evidence before using successor authority.
- The admission receipt remains a digest-and-purpose summary; it does not expose raw paths, filenames, host identity, full text, receipt bodies, recipient text, live locators, or secrets.
- Negative fixtures make the common stale-reader mistakes executable and keep future broker adapters from quietly bypassing the checkpoint floor.

## Status

Accepted for the next implementation-shaped cut. Later multi-reader batching or witness-quorum work may compress admission receipts, but it must preserve exact checkpoint observation, exact successor subject binding, and redacted failure semantics.

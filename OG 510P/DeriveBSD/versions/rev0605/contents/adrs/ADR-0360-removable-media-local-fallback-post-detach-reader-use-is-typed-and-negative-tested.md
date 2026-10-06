# ADR-0360: Removable-media local fallback post-detach reader use is typed and negative-tested

- Status: accepted
- Date: 2026-05-24
- Deciders: archive maintainers
- Consulted: `adrs/ADR-0359-removable-media-local-fallback-post-detach-reader-admission-is-typed-and-negative-tested.md`, `docs/770-removable-media-local-fallback-post-detach-reader-admission-is-typed-and-negative-tested.md`, `docs/293-attribute-indexed-metadata-and-live-queries.md`

## Context

ADR-0359 made reader admission explicit, but admission is still not the same as use. A broker that proves checkpoint observation can still become a silent observation loop if each read is not separately budgeted, sequenced, redacted, and receipted before any result becomes visible. That creates a subtle authority leak: a one-time admission can behave like an unbounded subscription, support/debug tooling can replay the same lease, or result caches can expose raw fields while the receipt trail only says that admission happened.

## Decision

Add `spec/removable.media.local.post_detach.reader.use.receipt.schema.json` with kind `removable.media.local.post_detach.reader.use.receipt`, the canonical example `spec/examples/removable.media.local.post_detach.reader.use.receipt.json`, and a red corpus under `spec/examples/invalid/removable-media/post-detach-reader-use-receipt/`.

The ordinary B/C removable-media local fallback now records `typed-post-detach-reader-use-positive-and-negative-fixture-guarded`, `sha256:e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6`, and `known-bad-post-detach-reader-use-shapes-must-fail-validation` after the r515 reader-admission receipt. A reader-use receipt binds the reader-admission digest, checkpoint sequence, index root, successor subject digest, reader lease, nonce, idempotency key, use sequence, budget debit, and result projection before the observation result is exposed. It records `post-detach-reader-use-budgeted-sequenced-and-redacted` and rejects missing admission receipts, admission-as-use replay, non-debited results, exhausted budgets, double-spend/replay, broad scopes, live subscriptions, export/rehydration requests, raw locator/filename/body/full-text return, host identity, secret material, result visibility before receipt visibility, and offline-erasure overclaim.

## Consequences

- Reader admission remains an entry gate, not a reusable read token.
- Every admitted reader action consumes budget and leaves a redacted use receipt.
- Query/export/rehydration/support surfaces can inspect a use summary without receiving raw paths, filenames, host identity, body text, full text, raw receipt payloads, recipient text, live locators, or secrets.
- Negative fixtures make silent-observation, replay, and over-budget reader-use bugs executable.

## Status

Accepted for the next implementation-shaped cut. Later batching can aggregate reader-use receipts only if each admitted subject still has exact admission binding, use sequence, budget debit, redaction proof, and result digest evidence.

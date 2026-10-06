# ADR-0361: Removable-media local fallback post-detach reader-use ledger is typed and negative-tested

- Status: accepted
- Date: 2026-05-25
- Deciders: archive maintainers
- Consulted: `adrs/ADR-0360-removable-media-local-fallback-post-detach-reader-use-is-typed-and-negative-tested.md`, `docs/771-removable-media-local-fallback-post-detach-reader-use-is-typed-and-negative-tested.md`, `docs/293-attribute-indexed-metadata-and-live-queries.md`

## Context

ADR-0360 made each admitted reader use budgeted, sequenced, redacted, and receipt-visible before result visibility. That still leaves one lifecycle seam: a budget debit can be claimed by the use receipt while concurrent readers, restored ledgers, retry paths, or stale roots race around the durable ledger state. If the ledger root is not typed, compare-and-swap-bound, monotonic, and redacted, a reader-use receipt can become a local statement rather than the committed state transition that prevents double-spend and rollback.

## Decision

Add `spec/removable.media.local.post_detach.reader.use.ledger.receipt.schema.json` with kind `removable.media.local.post_detach.reader.use.ledger.receipt`, the canonical example `spec/examples/removable.media.local.post_detach.reader.use.ledger.receipt.json`, and a red corpus under `spec/examples/invalid/removable-media/post-detach-reader-use-ledger-receipt/`.

The ordinary B/C removable-media local fallback now records `typed-post-detach-reader-use-ledger-positive-and-negative-fixture-guarded`, `sha256:f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7`, and `known-bad-post-detach-reader-use-ledger-shapes-must-fail-validation` after the r516 reader-use receipt. A reader-use ledger receipt binds one reader-use receipt digest, one admission digest, one successor subject, one lease, one nonce/idempotency key, one prior ledger root, one compare-and-swap expected root, one debit record, one new ledger root, and one monotonic ledger sequence. It records `post-detach-reader-use-ledger-root-monotonic-and-committed` and rejects missing reader-use receipts, stale or unbound ledger roots, non-monotonic sequences, uncommitted debit, double-spend/replay, forked roots, rollback roots, live subscriptions, unbounded budgets, raw locator or filename indexing, full/body text indexing, host identity, secret material, result release before ledger commit, and offline-erasure overclaim.

## Consequences

- Reader-use receipts become preconditions for ledger commits, not substitutes for them.
- Reader budgets are protected by a durable compare-and-swap root rather than by per-result local claims.
- Replayed idempotency keys, restored roots, forked roots, and rollback roots remain fail-closed and auditable.
- Ledger projections are redacted observation summaries, not raw receipt or locator indexes.
- The new checker begins a small guardrail-helper refactor through `tools/removable_media_post_detach_guardrail_lib.py` while preserving historical checker behavior.

## Validation

`tools/check_removable_media_local_post_detach_reader_use_ledger_receipt.py` validates the canonical fixture, proves the red corpus fails, and keeps `typed-post-detach-reader-use-ledger-positive-and-negative-fixture-guarded` wired through the r516 reader-use receipt and the existing removable-media post-detach chain.

Last updated: 2026-05-25r517

# Removable-media local fallback post-detach reader-use ledger is typed and negative-tested

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability, reproducibility  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate, Bundles

r504 closed the worker contract, r505 closed launch evidence, r506 closed recovery evidence, r507 closed query projection, r508 closed redacted export bundles, r509 closed tombstones, r510 closed denial receipts, r511 closed fresh-authority reissue, r512 closed fresh-authority consumption, r513 closed successor-index cutover, r514 closed checkpointing, r515 closed reader admission, and r516 closed reader-use receipts. r517 closes the next seam: a reader-use receipt says the use was budgeted, but the budget ledger itself must be a monotonic committed artifact so concurrent brokers cannot double-spend, fork, roll back, or restore pre-debit observation budget.

See also:
- ADR: `adrs/ADR-0361-removable-media-local-fallback-post-detach-reader-use-ledger-is-typed-and-negative-tested.md`
- runtime schema: `spec/removable.media.local.post_detach.reader.use.ledger.receipt.schema.json`
- exact fixture schema: `spec/removable.media.local.post_detach.reader.use.ledger.receipt.fixture.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.reader.use.ledger.receipt.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-reader-use-ledger-receipt/`
- prior reader-use contract: `docs/771-removable-media-local-fallback-post-detach-reader-use-is-typed-and-negative-tested.md`
- metadata/query surface: `docs/293-attribute-indexed-metadata-and-live-queries.md`

## Decision

The ordinary B/C post-detach lane now carries:

- `typed-post-detach-reader-use-ledger-positive-and-negative-fixture-guarded`
- `sha256:f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7`
- `known-bad-post-detach-reader-use-ledger-shapes-must-fail-validation`

A `removable.media.local.post_detach.reader.use.ledger.receipt` is required after the r516 reader-use receipt and before the result release is treated as durable. The receipt records `post-detach-reader-use-ledger-root-monotonic-and-committed` and `reader-use-ledger-committed-before-result-release`. It binds the reader-use receipt digest `sha256:e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6e6`, the reader-admission digest `sha256:d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5`, the successor subject digest, reader lease digest, request nonce, idempotency key, budget epoch, prior ledger root, compare-and-swap expected root, debit record, new ledger root, monotonic ledger sequence, and redacted ledger projection.

## Evidence object shape

`spec/removable.media.local.post_detach.reader.use.ledger.receipt.schema.json` is now the r556 generic runtime schema; `spec/removable.media.local.post_detach.reader.use.ledger.receipt.fixture.schema.json` preserves the exact r517 literal fixture. The runtime schema requires these closed-world sections:

- `contract_binding`: joins the ledger to the r516 reader-use receipt and canonical content-import receipt;
- `reader_use_binding`: proves the ledger entry belongs to one exact reader-use receipt, sequence, lease, nonce, result digest, and projection digest;
- `ledger_precondition`: records the prior ledger root, minimum checkpoint sequence, observed index root, and compare-and-swap root while rejecting stale, dual-active, or untrusted-cache roots;
- `budget_debit_commit`: records the debit record, before/after budget state, debit-before-result ordering, double-spend denial, idempotency replay denial, and replay denial;
- `ledger_commit`: records the new ledger root, monotonic sequence, committed compare-and-swap result, single commit, fork denial, rollback denial, result-release-after-commit ordering, and ledger-root anchor;
- `concurrency_guard`: makes the single-committer compare-and-swap model explicit and denies live subscriptions or unbounded reader budgets;
- `projection_redaction`: keeps raw locators, untrusted filenames, host identity, full text, body text, recipient text, raw receipt payloads, and secrets out of ledger projections;
- `failure_policy`: fails closed on missing reader-use receipts, stale ledger roots, non-monotonic sequence, uncommitted debit, double-spend/replay, fork/rollback, live subscription, raw locator/filename/body/full-text indexing, host identity, secret material, result-before-ledger visibility, or offline-erasure overclaim.

## Red corpus

The reader-use ledger red corpus starts under `spec/examples/invalid/removable-media/post-detach-reader-use-ledger-receipt/` with:

- `missing-reader-use-receipt.json`
- `ledger-root-not-cas-bound.json`
- `stale-root-accepted.json`
- `non-monotonic-ledger-sequence.json`
- `debit-not-committed-before-result.json`
- `double-spend-accepted.json`
- `forked-ledger-root-accepted.json`
- `rollback-accepted.json`
- `replay-token-present.json`
- `raw-locator-indexed.json`
- `filename-indexed.json`
- `secret-material-present.json`
- `live-subscription-ledgered.json`
- `result-visible-before-ledger-commit.json`
- `unbounded-retention.json`

Each fixture is intentionally close to the canonical object and must fail validation.

## Audit/refactor note

While adding the r517 guardrail, the post-detach checker series was audited for repeated boilerplate. The archive now includes `tools/removable_media_post_detach_guardrail_lib.py`, a small shared helper for JSON loading, nested-field assertions, schema-validation errors, red-corpus checks, text-token checks, and hygiene-entry checks. The new r517 checker uses this helper. Historical r504-r516 checkers remain behavior-preserving direct scripts for now; future cleanup can migrate them one at a time without changing their contract semantics.

## What this changes in implementation terms

The first launcher/indexer prototype now has fourteen separate artifacts in this lane. The new final step says: no admitted reader result is durable merely because r516 emitted a use receipt. The ledger root must commit the debit first, and that commit must be monotonic, compare-and-swap-bound, redacted, and rollback/fork resistant.

The behavioral change is "no result release without a committed reader-use ledger root," not merely "no result without a reader-use receipt."

## Hygiene

`tools/check_removable_media_local_post_detach_reader_use_ledger_receipt.py` validates the positive reader-use ledger fixture, proves the red corpus fails, checks the r516 reader-use receipt points at the ledger contract, checks the broader post-detach chain carries `typed-post-detach-reader-use-ledger-positive-and-negative-fixture-guarded`, and verifies the checker helper refactor is discoverable.

Refactor follow-up in r518: the r517 checker now uses the shared `require_positive_fixture_valid` helper from `tools/removable_media_post_detach_guardrail_lib.py`, so positive-schema validation and red-corpus validation follow the same helper pattern as the retention checker.

Refactor follow-up in r556: the reader-use ledger receipt now follows the generic-runtime-schema-plus-exact-fixture-schema split. Dynamic receipt digests, IDs, schema paths, and sequence values validate through runtime patterns, while the historical r517 object remains locked by `spec/removable.media.local.post_detach.reader.use.ledger.receipt.fixture.schema.json`.

Last updated: 2026-06-10r556

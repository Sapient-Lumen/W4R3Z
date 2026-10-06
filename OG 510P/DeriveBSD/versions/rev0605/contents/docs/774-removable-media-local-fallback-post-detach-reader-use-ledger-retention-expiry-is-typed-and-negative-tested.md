# Removable-media local fallback post-detach reader-use ledger retention expiry is typed and negative-tested

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability, reproducibility  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate, Bundles

r504 through r518 made the removable-media post-detach lane increasingly executable: worker contract, launch evidence, recovery, query projection, export bundles, tombstones, denial receipts, fresh-authority reissue and consumption, successor-index cutover and checkpointing, reader admission, reader use, reader-use ledger commits, and bounded reader-use ledger retention. r519 closes the next seam: the r518 retention window has an expiry timestamp, but expiry itself must be a receipted state transition. Otherwise bounded retention can quietly become indefinite, old compacted roots can continue admitting reads, or cleanup can delete the digest proof needed to explain future denials.

See also:
- ADR: `adrs/ADR-0363-removable-media-local-fallback-post-detach-reader-use-ledger-retention-expiry-is-typed-and-negative-tested.md`
- runtime schema: `spec/removable.media.local.post_detach.reader.use.ledger.retention.expiry.receipt.schema.json`
- exact fixture schema: `spec/removable.media.local.post_detach.reader.use.ledger.retention.expiry.receipt.fixture.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.reader.use.ledger.retention.expiry.receipt.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-reader-use-ledger-retention-expiry-receipt/`
- prior retention contract: `docs/773-removable-media-local-fallback-post-detach-reader-use-ledger-retention-is-typed-and-negative-tested.md`
- metadata/query surface: `docs/293-attribute-indexed-metadata-and-live-queries.md`

## Decision

The ordinary B/C post-detach lane now carries:

- `typed-post-detach-reader-use-ledger-retention-expiry-positive-and-negative-fixture-guarded`
- `sha256:1919191919191919191919191919191919191919191919191919191919191919`
- `known-bad-post-detach-reader-use-ledger-retention-expiry-shapes-must-fail-validation`

A `removable.media.local.post_detach.reader.use.ledger.retention.expiry.receipt` is required after the r518 reader-use ledger retention receipt. It records `post-detach-reader-use-ledger-retention-expiry-finalized-redacted-and-denial-auditable` and `reader-use-ledger-retention-expiry-finalized-with-proof-carry-forward-no-silent-extension`. The receipt binds the r518 retention digest `sha256:f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8`, the compacted ledger root, the retention policy digest, the retention expiry instant, a clock-source digest, an expiry record, a monotonic expiry sequence, an expiry root anchor, the retained audit summary digest, and the retained proof-carry-forward digest.

## Evidence object shape

`spec/removable.media.local.post_detach.reader.use.ledger.retention.expiry.receipt.schema.json` is now the runtime contract: dynamic digests, ids, schema paths, timestamps, and sequence numbers are shape-checked through reusable `sha256Digest`, path, timestamp, and integer constraints. `spec/removable.media.local.post_detach.reader.use.ledger.retention.expiry.receipt.fixture.schema.json` keeps the exact r519 historical literals in an `allOf` fixture surface. The runtime schema requires these closed-world sections:

- `contract_binding`: joins the expiry receipt to the r518 retention receipt and canonical content-import receipt;
- `retention_binding`: proves the expiry event refers to one exact retention receipt, compacted root, audit summary, and proof carry-forward;
- `expiry_trigger`: records that expiry happened at or after the retention window end and that silent extension or operator override was not requested;
- `expiry_commit`: records the committed expiry root, monotonic sequence, compare-and-swap result, rollback denial, fork denial, and expiry anchor;
- `evidence_after_expiry`: preserves denial and budget-audit causality while keeping raw locators, filenames, body/full text, host identity, and secrets absent;
- `expiry_decision`: says post-expiry queries, exports, and rehydration are denied or require fresh authority;
- `failure_policy`: fails closed on missing retention receipts, early expiry, silent extension, missing proof carry-forward, stale root reuse, leaks, unbounded post-expiry retention, or offline-erasure overclaim.

## Red corpus

The reader-use ledger retention expiry red corpus starts under `spec/examples/invalid/removable-media/post-detach-reader-use-ledger-retention-expiry-receipt/` with:

- `audit-summary-deleted.json`
- `body-text-indexed.json`
- `expired-root-still-queryable.json`
- `expiry-before-retention-window-end.json`
- `filename-indexed.json`
- `forked-expiry-accepted.json`
- `full-text-indexed.json`
- `future-reader-admission-without-fresh-authority.json`
- `host-identity-present.json`
- `missing-proof-carry-forward.json`
- `missing-retention-receipt.json`
- `non-monotonic-expiry-sequence.json`
- `offline-erasure-claimed.json`
- `raw-locator-indexed.json`
- `rollback-accepted.json`
- `secret-material-present.json`
- `silent-extension-accepted.json`
- `silent-extension-requested.json`
- `stale-compacted-root-accepted.json`
- `unbounded-post-expiry-retention.json`

Each fixture is intentionally close to the canonical object and must fail validation.

## Audit/refactor note

r517 introduced `tools/removable_media_post_detach_guardrail_lib.py`; r518 added shared positive-fixture validation. r519 deepened that cleanup by adding `require_guardrail_contract`, a small package-level helper for the repeating validation sequence: positive fixture, exact red corpus, selected JSON joins, doc tokens, and hygiene wiring. r560 keeps that package helper but adds the production/fixture split: `require_positive_fixture_valid` validates the canonical object against the exact fixture schema before the generic runtime schema and red corpus are checked. Historical r504-r518 scripts are left semantically untouched.

## What this changes in implementation terms

The first launcher/indexer prototype now has a terminal state for bounded reader observation. A result can be read only after admission, use receipt, ledger commit, retention, and retention expiry handling. When the retention window closes, live/query authority cannot continue from the old compacted root; a broker must deny the attempt or require fresh authority. The receipt preserves digest-level audit proof without retaining raw paths, filenames, body text, host identity, or secret material.

The behavioral change is "no bounded retention without typed expiry or fresh-authority handling," not merely "retention has an expiry timestamp."

## Hygiene

`tools/check_removable_media_local_post_detach_reader_use_ledger_retention_expiry_receipt.py` validates the canonical positive fixture, proves the red corpus fails, checks chain wiring, and confirms the shared helper remains discoverable while `require_positive_fixture_valid` preserves exact r519 fixture history.

Last updated: 2026-06-10r560

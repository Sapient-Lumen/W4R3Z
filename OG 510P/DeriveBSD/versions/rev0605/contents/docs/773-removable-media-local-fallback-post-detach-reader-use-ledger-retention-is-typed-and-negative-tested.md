# Removable-media local fallback post-detach reader-use ledger retention is typed and negative-tested

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability, reproducibility  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate, Bundles

r504 through r517 made the removable-media post-detach lane increasingly executable: worker contract, launch evidence, recovery, query projection, export bundles, tombstones, denial receipts, fresh-authority reissue and consumption, successor-index cutover and checkpointing, reader admission, reader use, and reader-use ledger commits. r518 closes the next seam: a committed reader-use ledger still needs bounded, redacted, auditable retention semantics. Otherwise the implementation either keeps raw observation evidence forever or compacts away the proof needed to explain exhausted budgets and future denial decisions.

See also:
- ADR: `adrs/ADR-0362-removable-media-local-fallback-post-detach-reader-use-ledger-retention-is-typed-and-negative-tested.md`
- runtime schema: `spec/removable.media.local.post_detach.reader.use.ledger.retention.receipt.schema.json`
- exact fixture schema: `spec/removable.media.local.post_detach.reader.use.ledger.retention.receipt.fixture.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.reader.use.ledger.retention.receipt.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-reader-use-ledger-retention-receipt/`
- prior ledger contract: `docs/772-removable-media-local-fallback-post-detach-reader-use-ledger-is-typed-and-negative-tested.md`
- metadata/query surface: `docs/293-attribute-indexed-metadata-and-live-queries.md`

## Decision

The ordinary B/C post-detach lane now carries:

- `typed-post-detach-reader-use-ledger-retention-positive-and-negative-fixture-guarded`
- `sha256:f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8`
- `known-bad-post-detach-reader-use-ledger-retention-shapes-must-fail-validation`

A `removable.media.local.post_detach.reader.use.ledger.retention.receipt` is required after the r517 reader-use ledger receipt. It records `post-detach-reader-use-ledger-retention-bounded-redacted-and-auditable` and `reader-use-ledger-retention-compacted-after-commit-without-raw-observation`. The receipt binds the r517 ledger digest `sha256:f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7`, the ledger sequence and root, the budget epoch, successor subject, reader lease, debit record, result-release digest, retention policy digest, compaction record, compacted ledger root, audit summary digest, proof-carry-forward digest, and redacted support projection.

## Evidence object shape

`spec/removable.media.local.post_detach.reader.use.ledger.retention.receipt.schema.json` is now the generic runtime surface for this receipt. The exact historical r518 literals live in `spec/removable.media.local.post_detach.reader.use.ledger.retention.receipt.fixture.schema.json`, and the positive example validates against both. The runtime schema requires these closed-world sections:

- `contract_binding`: joins the retention receipt to the r517 reader-use ledger and canonical content-import receipt;
- `ledger_binding`: proves the retention event refers to one exact ledger root, sequence, budget epoch, successor subject, lease, debit record, and result release;
- `retention_window`: records a bounded operational audit window and denies raw observation retention, raw receipt-payload retention, unbounded retention, and pre-commit compaction;
- `compaction_commit`: records the compacted root, retention sequence, compare-and-swap result, single compaction, audit summary, proof carry-forward, rollback denial, fork denial, and compaction anchor;
- `evidence_preservation`: proves debit, tombstone-denial causality, admission-lease causality, and exhausted-budget auditability survive while raw locators, filenames, body/full text, host identity, and secrets remain absent;
- `retention_decision`: says future queries use the compacted root and that no offline-copy erasure is overclaimed;
- `failure_policy`: fails closed on missing ledger receipts, raw or unbounded retention, pre-commit compaction, missing audit summary or proof carry-forward, rollback/fork, leaks, non-compacted future queries, result-before-ledger visibility, or offline-erasure overclaim.

## Red corpus

The reader-use ledger retention red corpus starts under `spec/examples/invalid/removable-media/post-detach-reader-use-ledger-retention-receipt/` with:

- `body-text-indexed.json`
- `compaction-before-ledger-commit.json`
- `filename-indexed.json`
- `forked-compaction-accepted.json`
- `full-text-indexed.json`
- `future-query-without-compacted-root.json`
- `host-identity-present.json`
- `missing-audit-summary.json`
- `missing-reader-use-ledger-receipt.json`
- `offline-erasure-claimed.json`
- `proof-carry-forward-missing.json`
- `raw-locator-indexed.json`
- `raw-observation-retained.json`
- `raw-receipt-payload-retained.json`
- `result-visible-before-ledger-commit.json`
- `rollback-accepted.json`
- `secret-material-present.json`
- `unbounded-retention.json`

Each fixture is intentionally close to the canonical object and must fail validation.

## Audit/refactor note

r517 introduced `tools/removable_media_post_detach_guardrail_lib.py`. r518 deepened that cleanup by adding shared positive-fixture validation (`require_positive_fixture_valid`) and migrating the r517 checker to use it. r559 splits this r518 retention surface into a generic runtime schema plus exact fixture schema so future retention roots, digests, IDs, and sequence values can vary without losing the historical literal regression surface. The refactor remains deliberately small: it removes one p0 fixture-literal runtime schema without rewriting historical r504-r516 scripts or changing their contract semantics.

## What this changes in implementation terms

The first launcher/indexer prototype now has a bounded-reader-observation lifecycle. A result can be read only after admission, use receipt, ledger commit, and retention receipt. The retention receipt permits compaction only after the committed ledger root is carried forward into a redacted audit summary. It does not preserve raw paths, raw filenames, body text, host identity, or secret material just to make future denials explainable.

The behavioral change is "no ledger retention or compaction without a redacted proof-carry-forward receipt," not merely "no result release without a committed ledger."

## Hygiene

`tools/check_removable_media_local_post_detach_reader_use_ledger_retention_receipt.py` validates the positive retention fixture, proves the red corpus fails, checks the r517 ledger receipt points at the retention contract, checks the broader post-detach chain carries `typed-post-detach-reader-use-ledger-retention-positive-and-negative-fixture-guarded`, and verifies the helper refactor remains discoverable.
## r519 expiry handoff

r519 adds `typed-post-detach-reader-use-ledger-retention-expiry-positive-and-negative-fixture-guarded` after this retention receipt. The r518 bounded/compacted root is no longer a terminal live authority: after `retention_expires_at`, readers must observe the r519 expiry receipt and either deny stale use or require fresh authority.

Last updated: 2026-06-10r559

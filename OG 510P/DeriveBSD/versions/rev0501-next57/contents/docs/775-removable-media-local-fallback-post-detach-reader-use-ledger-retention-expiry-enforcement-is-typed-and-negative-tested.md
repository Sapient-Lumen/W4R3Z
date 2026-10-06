# Removable-media local fallback post-detach reader-use ledger retention expiry enforcement is typed and negative-tested

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability, reproducibility  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate, Bundles

r504 through r519 made the removable-media post-detach lane increasingly executable: worker contract, launch evidence, recovery, query projection, export bundles, tombstones, denial receipts, fresh-authority reissue and consumption, successor-index cutover and checkpointing, reader admission, reader use, reader-use ledger commits, bounded ledger retention, and retention expiry. r520 closes the next seam: r519 says expired compacted roots are denied-or-fresh-authority-only, but the actual denial/enforcement attempt must itself be receipted. Otherwise a stale reader can fail ambiguously, a broker can silently accept an expired root, or support tooling can reintroduce raw attempt handles while explaining the denial.

See also:
- ADR: `adrs/ADR-0364-removable-media-local-fallback-post-detach-reader-use-ledger-retention-expiry-enforcement-is-typed-and-negative-tested.md`
- schema: `spec/removable.media.local.post_detach.reader.use.ledger.retention.expiry.enforcement.receipt.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.reader.use.ledger.retention.expiry.enforcement.receipt.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-reader-use-ledger-retention-expiry-enforcement-receipt/`
- prior expiry contract: `docs/774-removable-media-local-fallback-post-detach-reader-use-ledger-retention-expiry-is-typed-and-negative-tested.md`
- metadata/query surface: `docs/293-attribute-indexed-metadata-and-live-queries.md`

## Decision

The ordinary B/C post-detach lane now carries:

- `typed-post-detach-reader-use-ledger-retention-expiry-enforcement-positive-and-negative-fixture-guarded`
- `sha256:2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a`
- `known-bad-post-detach-reader-use-ledger-retention-expiry-enforcement-shapes-must-fail-validation`

A `removable.media.local.post_detach.reader.use.ledger.retention.expiry.enforcement.receipt` is required when a query/export/rehydration path attempts to use an expired r519 compacted root without fresh authority. It records `post-detach-reader-use-ledger-retention-expiry-enforcement-denied-redacted-and-fresh-authority-gated` and `retention-expiry-enforcement-denies-expired-roots-before-new-observation`. The receipt binds the r519 expiry digest `sha256:1919191919191919191919191919191919191919191919191919191919191919`, the expired ledger root, retained audit summary digest, retained proof-carry-forward digest, attempted root digest, attempted handle digest, reader lease digest, denial receipt digest, rate-limit debit, monotonic enforcement sequence, and redacted support projection.

## Evidence object shape

`spec/removable.media.local.post_detach.reader.use.ledger.retention.expiry.enforcement.receipt.schema.json` requires these closed-world sections:

- `contract_binding`: joins the enforcement receipt to the r519 expiry receipt and canonical content-import receipt;
- `expiry_binding`: proves the attempt refers to one exact expired ledger root and retained proof carry-forward;
- `post_expiry_attempt`: records one stale-root attempt without raw handles, raw locators, filenames, host identity, or secret material;
- `enforcement_decision`: records denied-or-fresh-authority-only outcome, rate-limit debit, denial digest, monotonic sequence, rollback denial, fork denial, stale-root denial, and no export or rehydration;
- `evidence_after_enforcement`: preserves denial and budget-audit causality while keeping raw payloads and full-text surfaces absent;
- `failure_policy`: fails closed on missing expiry receipts, expired-root success, export/rehydration success, missing fresh-authority requirement, missing rate-limit debit, rollback/fork/stale-root acceptance, raw attempt leaks, and silent success.

## Red corpus

The reader-use ledger retention expiry enforcement red corpus starts under `spec/examples/invalid/removable-media/post-detach-reader-use-ledger-retention-expiry-enforcement-receipt/` with:

- `allow-export-after-expiry.json`
- `allow-new-observation.json`
- `allow-rehydration-after-expiry.json`
- `body-text-indexed.json`
- `forked-enforcement-accepted.json`
- `fresh-authority-not-required.json`
- `full-text-indexed.json`
- `host-identity-present.json`
- `missing-expiry-receipt.json`
- `missing-rate-limit-debit.json`
- `non-monotonic-enforcement-sequence.json`
- `raw-handle-present.json`
- `raw-locator-present.json`
- `rollback-accepted.json`
- `secret-material-present.json`
- `silent-success-without-denial.json`
- `stale-root-accepted.json`
- `support-raw-payload-visible.json`
- `unbounded-retry-window.json`
- `untrusted-filename-present.json`

Each fixture is intentionally close to the canonical object and must fail validation.

## Audit/refactor note

r517 introduced `tools/removable_media_post_detach_guardrail_lib.py`; r518 added shared positive-fixture validation; r519 added `require_guardrail_contract`. r520 adds `require_absent_tokens`, a tiny audit helper for canonical positive fixtures and support docs. The new checker uses it to keep example post-expiry enforcement evidence free of accidental raw path, locator, user, host, or secret samples. Historical guardrails are left semantically untouched.

## What this changes in implementation terms

Post-expiry behavior is now explicit: an expired compacted root is not merely "not accepted". A broker must emit a redacted enforcement receipt that explains the denial, preserves proof carry-forward, debits any retry/rate-limit budget, and points the user toward fresh authority. The receipt is useful to UX and support without turning expired-root attempts into a new query index.

The behavioral change is "no post-expiry denial without typed enforcement evidence," not merely "expired roots should fail."

## Hygiene

`tools/check_removable_media_local_post_detach_reader_use_ledger_retention_expiry_enforcement_receipt.py` validates the canonical positive fixture, proves the red corpus fails, checks chain wiring, and confirms the shared helper exposes `require_absent_tokens`.

Last updated: 2026-05-25r520

# ADR-0370: Removable-media local fallback post-detach rate-limit debit ledger and reader-use schema split are typed

## Status

Accepted.

## Context

r525 made denial cause selection executable, but the selected `debit` action still depended on fields embedded in the expiry-enforcement ledger and denial-selection receipt. That was good enough to prove the broker intended to debit, but it was not enough to prove the rate-limit ledger itself advanced exactly once, that idempotent replay did not double debit, or that support/debug views could not expose raw budget counters or ledger roots.

The live schema-refactor backlog also promoted `spec/removable.media.local.post_detach.reader.use.receipt.schema.json` as the next p0 post-detach const-heavy schema after the r525 contract split. Reader-use receipts are a production path, not only historical fixtures, so dynamic reader-use ids, digest joins, and schema paths need a runtime-shaped schema while the exact r516 example remains reviewable.

## Decision

Add a typed r526 rate-limit debit ledger and reader-use schema-split cut.

This cut adds:

- `spec/removable.media.local.post_detach.rate_limit.debit.ledger.receipt.schema.json` and `spec/examples/removable.media.local.post_detach.rate_limit.debit.ledger.receipt.json` as the typed ledger receipt for the r525 selected debit action;
- `spec/examples/invalid/removable-media/post-detach-rate-limit-debit-ledger-receipt/` as the red corpus for CAS mismatch, missing debit, non-advancing ledger root, policy digest drift, stale denial-selection binding, support-visible budget data, unbounded retry windows, and idempotent replay double debit;
- `tools/check_removable_media_local_post_detach_rate_limit_debit_ledger_receipt.py` as the semantic checker that recomputes source digests, joins the enforcement ledger to the denial-selection receipt, checks first-attempt debit versus idempotent replay no-debit behavior, and rejects the red corpus;
- `spec/removable.media.local.post_detach.reader.use.receipt.fixture.schema.json` as the exact historical r516 reader-use fixture schema;
- a rewritten `spec/removable.media.local.post_detach.reader.use.receipt.schema.json` as the generic runtime schema, preserving the closed-world reader-use safety envelope while allowing dynamic ids, digests, and schema paths through `$defs` and patterns;
- refreshed audit, backlog, hygiene, generated, and current-view surfaces showing the reader-use split as completed while retaining exact fixture evidence.

The new posture tokens are `post-detach-rate-limit-debit-ledger-positive-and-negative-fixture-guarded` and `post-detach-reader-use-generic-runtime-schema-plus-exact-fixture-split`.

## Consequences

- The selected rate-limit action is no longer only a scalar on the denial-selection receipt. It has a ledger receipt with subject, policy, window, CAS roots, idempotency key, retry posture, and support visibility.
- The first expired-root denial debits once; an idempotent replay returns the same denial and debits zero additional units.
- The rate-limit ledger CAS must use the prior root as the expected root, advance to a new root, and reject rollback/fork/stale-root acceptance.
- Support projection remains `support-safe-digest-only`; raw budget counts, ledger roots, subjects, and idempotency keys are not support-visible.
- The r516 reader-use example remains exact under the fixture schema, while production validation moves to a runtime-shaped schema.
- The schema refactor backlog records three completed production/fixture splits: r520 expiry enforcement, r504 post-detach contract, and r516 reader-use receipt.

## Validation

Run:

```text
python3 tools/check_removable_media_local_post_detach_rate_limit_debit_ledger_receipt.py
python3 tools/check_removable_media_local_post_detach_denial_selection_receipt.py
python3 tools/check_removable_media_local_post_detach_reader_use_receipt.py
python3 tools/check_cube_schema_audit_report.py
python3 tools/check_cube_schema_refactor_backlog.py
python3 tools/check_cube_hygiene_checkset_manifest.py
python3 tools/validate_spec_examples.py
python3 tools/lint_spec_schemas.py
python3 tools/check_schema_kind_matches_filename.py
python3 tools/check_generated_docs.py
python3 tools/check_version.py
```

`tools/check_removable_media_local_post_detach_rate_limit_debit_ledger_receipt.py` validates the positive debit ledger, recomputes source digests, proves first-attempt debit versus idempotent replay no-debit behavior, verifies rate-limit CAS/root joins, and rejects every red-corpus shape.

Last updated: 2026-05-30r526

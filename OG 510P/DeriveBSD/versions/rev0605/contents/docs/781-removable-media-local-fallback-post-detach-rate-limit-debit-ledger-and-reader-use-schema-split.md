# Removable-media local fallback post-detach rate-limit debit ledger and reader-use schema split

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability, reproducibility  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate, Bundles

r525 made denial-selection executable. r526 makes the selected rate-limit debit executable too, and it performs the next backlog-driven split by moving the r516 reader-use receipt into the runtime-schema plus exact-fixture pattern.

See also:

- ADR: `adrs/ADR-0370-removable-media-local-fallback-post-detach-rate-limit-debit-ledger-and-reader-use-schema-split-are-typed.md`
- rate-limit debit ledger schema: `spec/removable.media.local.post_detach.rate_limit.debit.ledger.receipt.schema.json`
- rate-limit debit ledger example: `spec/examples/removable.media.local.post_detach.rate_limit.debit.ledger.receipt.json`
- rate-limit debit ledger red corpus: `spec/examples/invalid/removable-media/post-detach-rate-limit-debit-ledger-receipt/`
- rate-limit debit checker: `tools/check_removable_media_local_post_detach_rate_limit_debit_ledger_receipt.py`
- runtime reader-use schema: `spec/removable.media.local.post_detach.reader.use.receipt.schema.json`
- exact reader-use fixture schema: `spec/removable.media.local.post_detach.reader.use.receipt.fixture.schema.json`
- current rate-limit view: `docs/current/removable-media-post-detach-rate-limit-debit-ledger.md`
- current schema-refactor view: `docs/current/cube-schema-refactor-backlog.md`

## Decision

The new r526 posture tokens are `post-detach-rate-limit-debit-ledger-positive-and-negative-fixture-guarded` and `post-detach-reader-use-generic-runtime-schema-plus-exact-fixture-split`.

The rate-limit debit ledger receipt is the execution bridge between the r525 denial-selection receipt and the rate-limit roots embedded in the r521 enforcement ledger. It records the debit subject, selected reason, policy/window binding, CAS roots, idempotency key, replay behavior, retry posture, support projection, and semantic joins.

The reader-use schema split is the second concrete migration from the r524 backlog. The exact r516 reader-use example is preserved under `spec/removable.media.local.post_detach.reader.use.receipt.fixture.schema.json`; the production schema keeps the closed-world safety fields but moves dynamic ids, digest joins, and schema paths into a runtime-shaped `$defs`/pattern contract.

## Debit ledger coverage

The r526 positive receipt covers the first `expired-root-denied-with-enforcement-ledger` attempt and the replay scenario `same-idempotency-key-replays-same-denial-without-double-debit`. It proves that:

- the first expired-root denial debits exactly one unit;
- the idempotent replay debits zero additional units;
- the CAS expected root equals the prior rate-limit root;
- the new rate-limit root advances from the prior root;
- rollback, fork, and stale-root acceptance remain false;
- retry guidance stays a bounded redacted window;
- support projection remains `support-safe-digest-only` and does not expose raw budget counts, ledger roots, subjects, or idempotency keys.

## Red corpus

The rate-limit debit ledger red corpus rejects:

- CAS expected-root mismatch;
- idempotent replay double debit;
- non-advancing ledger roots;
- missing debit;
- rate-limit policy digest drift;
- stale denial-selection binding;
- support-visible budget data;
- unbounded retry windows.

## Schema refactor result

The live schema audit now reports the reader-use runtime schema as runtime-shaped and records the exact historical reader-use fixture separately. The const-heavy count remains visible because fixture schemas still carry release history, but the open backlog shrinks again: the post-detach reader-use split is complete and the next p0 targets remain visible.

## Hygiene

Run:

```text
python3 tools/check_removable_media_local_post_detach_rate_limit_debit_ledger_receipt.py
python3 tools/check_removable_media_local_post_detach_denial_selection_receipt.py
python3 tools/check_removable_media_local_post_detach_reader_use_receipt.py
python3 tools/check_cube_schema_audit_report.py
python3 tools/check_cube_schema_refactor_backlog.py
python3 tools/check_cube_hygiene_checkset_manifest.py
python3 tools/hygiene.py --profile post-detach
python3 tools/hygiene.py --profile schema-cube-audit
```

Run the generic schema and generated-doc checks after touching schemas, examples, or docs:

```text
python3 tools/validate_spec_examples.py
python3 tools/lint_spec_schemas.py
python3 tools/check_schema_kind_matches_filename.py
python3 tools/check_generated_docs.py
```

Last updated: 2026-05-30r526

# Removable-media local fallback post-detach query-projection access and schema split

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability, reproducibility  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate, Bundles

r507 made query projection safe as a shape. r527 makes a concrete projection access safe as an execution event, and it performs the next backlog-driven split by moving the r507 query-projection schema into the runtime-schema plus exact-fixture pattern.

See also:

- ADR: `adrs/ADR-0371-removable-media-local-fallback-post-detach-query-projection-access-and-schema-split-are-typed.md`
- query-projection access schema: `spec/removable.media.local.post_detach.query.projection.access.receipt.schema.json`
- query-projection access example: `spec/examples/removable.media.local.post_detach.query.projection.access.receipt.json`
- query-projection access red corpus: `spec/examples/invalid/removable-media/post-detach-query-projection-access-receipt/`
- query-projection access checker: `tools/check_removable_media_local_post_detach_query_projection_access_receipt.py`
- runtime query-projection schema: `spec/removable.media.local.post_detach.query.projection.schema.json`
- exact query-projection fixture schema: `spec/removable.media.local.post_detach.query.projection.fixture.schema.json`
- current query-projection access view: `docs/current/removable-media-post-detach-query-projection-access.md`
- current schema-refactor view: `docs/current/cube-schema-refactor-backlog.md`

## Decision

The new r527 posture tokens are `post-detach-query-projection-access-positive-and-negative-fixture-guarded` and `post-detach-query-projection-generic-runtime-schema-plus-exact-fixture-split`.

The query-projection access receipt is the execution bridge between the r507 projection fixture and the r524–r526 denial/rate-limit surfaces. It records the request id, lease digest, requested and returned fields, tombstone check, support-safe decision, CAS-rooted access ledger, failure denial-selection join, and rate-limit debit join.

The query-projection schema split is the fourth concrete migration from the r524 backlog. The exact r507 query projection remains under `spec/removable.media.local.post_detach.query.projection.fixture.schema.json`; the production schema keeps the closed-world safety fields but moves dynamic ids, digest joins, and schema paths into a runtime-shaped `$defs`/pattern contract.

## Access receipt coverage

The r527 positive receipt proves that:

- projection access is lease-bound and single-query scoped;
- the lease digest matches the query projection fixture;
- tombstone status is checked before any projection becomes visible;
- returned fields are a subset of the allowlisted projection fields;
- live subscriptions and aggregate counts remain forbidden;
- raw payloads, body/full text, paths, filenames, device identifiers, and host identity remain invisible;
- failed projection access has a typed denial-selection path and rate-limit debit receipt path;
- the access ledger CAS expected root equals the prior root and the new root advances.

## Red corpus

The query-projection access red corpus rejects:

- aggregate counts enabled;
- access ledger root not advanced;
- body/full-text visibility;
- disallowed returned fields;
- live subscription requests;
- missing lease requirement;
- raw path visibility;
- stale projection digest binding;
- missing tombstone-before-projection check.

## Schema refactor result

The live schema audit now reports the query-projection runtime schema as runtime-shaped and records the exact historical query-projection fixture separately. The const-heavy count remains visible because fixture schemas still carry release history, but the open backlog shrinks again: the post-detach query-projection split is complete and the next p0 targets remain visible.

## Hygiene

Run:

```text
python3 tools/check_removable_media_local_post_detach_query_projection_access_receipt.py
python3 tools/check_removable_media_local_post_detach_query_projection.py
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

Last updated: 2026-05-30r527

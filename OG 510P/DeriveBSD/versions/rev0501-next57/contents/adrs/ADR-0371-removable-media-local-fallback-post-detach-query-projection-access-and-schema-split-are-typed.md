# ADR-0371: Removable-media local fallback post-detach query-projection access and schema split are typed

## Status

Accepted.

## Context

r507 made the post-detach query projection lease-bound, redacted, and negative-tested. That was enough to keep the projection from becoming an ambient metadata index, but it did not create an execution receipt for each projection access. A broker could still prove that a projection *shape* was safe without proving that a specific query request was lease-bound, tombstone-checked, allowlisted, access-ledger receipted, and connected to the denial/rate-limit path for failure cases.

The live schema-refactor backlog also promotes `spec/removable.media.local.post_detach.query.projection.schema.json` as the highest-priority p0 post-detach const-heavy schema. Query projection is now a production path, not only a historical fixture, so dynamic query ids, digest joins, and schema paths need a runtime-shaped schema while the exact r507 example remains reviewable.

## Decision

Add a typed r527 query-projection access and query-projection schema-split cut.

This cut adds:

- `spec/removable.media.local.post_detach.query.projection.access.receipt.schema.json` and `spec/examples/removable.media.local.post_detach.query.projection.access.receipt.json` as the typed access receipt for each support/debug projection read;
- `spec/examples/invalid/removable-media/post-detach-query-projection-access-receipt/` as the red corpus for missing lease checks, live subscriptions, aggregate counts, raw/body/path visibility, stale projection bindings, missing tombstone checks, non-advancing access roots, and disallowed returned fields;
- `tools/check_removable_media_local_post_detach_query_projection_access_receipt.py` as the semantic checker that recomputes source digests, verifies the query lease and allowed-field join, proves tombstone-before-projection ordering, checks the CAS-rooted access ledger, and rejects the red corpus;
- `spec/removable.media.local.post_detach.query.projection.fixture.schema.json` as the exact historical r507 query-projection fixture schema;
- a rewritten `spec/removable.media.local.post_detach.query.projection.schema.json` as the generic runtime schema, preserving the closed-world query-projection safety envelope while allowing dynamic ids, digests, and schema paths through `$defs` and patterns;
- refreshed audit, backlog, hygiene, generated, and current-view surfaces showing the query-projection split as completed while retaining exact fixture evidence.

The new posture tokens are `post-detach-query-projection-access-positive-and-negative-fixture-guarded` and `post-detach-query-projection-generic-runtime-schema-plus-exact-fixture-split`.

## Consequences

- Query projection visibility now has a per-access receipt, not only a static projection fixture.
- A projection access must be lease-bound, single-query scoped, tombstone-checked before visibility, and limited to allowlisted fields.
- Live subscriptions and aggregate counts remain forbidden in the first post-detach lane.
- Any failed projection access has a typed denial-selection path and a rate-limit debit receipt path rather than silent query failure.
- The access ledger CAS must use the prior root as the expected root, advance to a new root, and reject rollback/fork/stale-root acceptance.
- The r507 query-projection example remains exact under the fixture schema, while production validation moves to a runtime-shaped schema.
- The schema refactor backlog records four completed production/fixture splits: r520 expiry enforcement, r504 post-detach contract, r516 reader-use receipt, and r507 query projection.

## Validation

Run:

```text
python3 tools/check_removable_media_local_post_detach_query_projection_access_receipt.py
python3 tools/check_removable_media_local_post_detach_query_projection.py
python3 tools/check_cube_schema_audit_report.py
python3 tools/check_cube_schema_refactor_backlog.py
python3 tools/check_cube_hygiene_checkset_manifest.py
python3 tools/validate_spec_examples.py
python3 tools/lint_spec_schemas.py
python3 tools/check_schema_kind_matches_filename.py
python3 tools/check_generated_docs.py
python3 tools/check_version.py
```

`tools/check_removable_media_local_post_detach_query_projection_access_receipt.py` validates the positive access receipt, recomputes source digests, checks the allowed-field/lease/tombstone joins, proves access-ledger advancement, and rejects every red-corpus shape.

Last updated: 2026-05-30r527

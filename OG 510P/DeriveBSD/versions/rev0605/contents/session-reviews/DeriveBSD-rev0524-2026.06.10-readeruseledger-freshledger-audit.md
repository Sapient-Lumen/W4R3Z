# DeriveBSD rev0524 session audit — reader-use-ledger split and explicit fresh ledgers

## Risk-first target

This cut prioritized two risks that can block real forward progress in the cloudtainer:

1. `tools/hygiene.py --ledger` had a fresh-run ambiguity: the writer could merge existing passed rows from the target path even when the user did not ask for `--resume-ledger`. That made the resume cache too eager and could let stale partial evidence appear inside a nominally fresh run.
2. The highest open p0 schema-cube item, `spec/removable.media.local.post_detach.reader.use.ledger.receipt.schema.json`, was still an exact fixture-literal contract. That kept a budget/CAS ledger proof tied to the historical r517 object instead of allowing dynamic runtime digests, IDs, schema paths, and sequence values.

## Implementation changes

- Changed `tools/hygiene.py` so `write_ledger(..., preserve_existing_passed=False)` is the default. Existing passed rows are merged only when the explicit `--resume-ledger` path passes `preserve_existing_passed=True`.
- Extended `tools/check_cube_hygiene_run_ledger.py` with a regression that proves a fresh write to an existing ledger path records only the rows supplied by that invocation, while explicit resume still preserves current passed rows.
- Split `spec/removable.media.local.post_detach.reader.use.ledger.receipt.schema.json` into a generic runtime schema and `spec/removable.media.local.post_detach.reader.use.ledger.receipt.fixture.schema.json`.
- Updated `tools/check_removable_media_local_post_detach_reader_use_ledger_receipt.py` so the canonical positive object validates against both the runtime schema and the exact fixture schema.
- Regenerated `cube.schema.audit.report`, `cube.schema.refactor.backlog`, `cube.hygiene.checkset.manifest`, `cube.hygiene.run.ledger`, generated docs, and current docs.

## Cube-audit result

The schema cube now reports:

- `schemas_total: 450`
- `examples_total: 467`
- `const_heavy_schema_count: 25`
- `runtime_contract_shaped_schema_count: 35`
- `exact_fixture_schema_count: 12`
- `open_items: 13`
- `completed_items: 12`
- `audit_next_targets_count: 5`

The reader-use-ledger p0 item moved to completed. The next p0 target is `spec/removable.media.local.post_detach.fresh.authority.consumption.receipt.schema.json`.

## Validation evidence

- `release-critical`: 35/35 passed in `session-reviews/DeriveBSD-rev0524-2026.06.10-release-critical-hygiene-ledger.json`.
- `post-detach`: 39/39 passed in `session-reviews/DeriveBSD-rev0524-2026.06.10-post-detach-hygiene-ledger.json`.
- `schema-cube-audit`: 3/3 passed in `session-reviews/DeriveBSD-rev0524-2026.06.10-schema-cube-hygiene-ledger.json`.

The post-detach profile exceeded the outer command window twice, then resumed from the partial ledger. That intentionally exercised the r556 explicit-resume path instead of relying on a single long run.

## Remaining risk

The next highest-value refactor is fresh-authority consumption. It is still p0 and const-heavy. The next cloudtainer-hardening improvement should bind resume rows to a broader input-surface digest, not only the checker and wrapper bytes, so same-release edits to schemas/docs cannot be hidden by a previously passed row.

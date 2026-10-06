# Current cube schema audit

The live schema audit is `cube.schema.audit.report` for 2026-06-18r630. It counts the schema cube directly from the schema and example trees under `spec/` so const-heavy fixture-literal debt, runtime-contract shaped contracts, exact fixture schemas, and schema/example coverage remain visible. The r630 repository-snapshot admission repair keeps schema expansion frozen unless it directly unblocks the profile-A golden thread, removes misleading proof identity, or captures an observed real-host failure; package repository admission remains executable runtime evidence rather than a new schema family.

Current counts:

- schemas_total: 457
- examples_total: 469
- root_kind_schema_count: 377
- schemas_with_canonical_example_count: 436
- schemas_without_canonical_example_count: 21
- const_heavy_schema_count: 26
- runtime_contract_shaped_schema_count: 41
- exact_fixture_schema_count: 17
- dotted_kind_filename_mismatch_count: 0

Schema and canonical example:

- `spec/cube.schema.audit.report.schema.json`
- `spec/examples/cube.schema.audit.report.json`

Checker: `tools/check_cube_schema_audit_report.py`

Last updated: 2026-06-18r630

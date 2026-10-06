# Current cube schema refactor backlog

The live schema refactor backlog is `cube.schema.refactor.backlog` for 2026-06-18r630. It is generated from the schema audit so runtime-contract shaped schemas, const-heavy exact fixtures, duplicated fixture literals, and the `generic-runtime-schema-plus-exact-fixture-schema` refactor pattern stay visible without becoming doctrine-only churn. Under the r630 repository-snapshot admission gate, backlog work is subordinate to executable product progress; refactor only when it deletes surface, fixes proof identity, or unblocks a golden-thread step.

Current counts:

- items_total: 26
- open_items: 8
- completed_items: 18
- post_detach_items: 17
- highest_const_count: 201
- audit_next_targets_count: 0

Schema and canonical example:

- `spec/cube.schema.refactor.backlog.schema.json`
- `spec/examples/cube.schema.refactor.backlog.json`

Checker: `tools/check_cube_schema_refactor_backlog.py`

Last updated: 2026-06-18r630

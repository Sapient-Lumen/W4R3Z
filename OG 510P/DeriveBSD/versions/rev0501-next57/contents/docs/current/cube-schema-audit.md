# Current cube schema audit

The live schema audit is `cube.schema.audit.report` for 2026-05-30r533. It counts the schema cube directly from the schema and example trees under `spec/` so const-heavy fixture debt, runtime-contract shaped contracts, exact fixture schemas, and schema/example coverage remain visible.

Current counts:

```text
schemas_total: 443
examples_total: 462
const_heavy_schema_count: 21
runtime_contract_shaped_schema_count: 32
exact_fixture_schema_count: 10
dotted_kind_filename_mismatch_count: 0
```

The current refactor direction is still to split the highest-priority post-detach const-heavy schemas into generic runtime schemas plus exact historical fixture schemas. This is the active fixture-literal to runtime-contract migration path: old examples remain preserved as exact fixtures, while new production schemas allow dynamic ids, digests, timestamps, and broker outputs. r533 adds a terminal-closure successor-cutover receipt and completes the successor-index cutover runtime/fixture split.

Last updated: 2026-05-30r533

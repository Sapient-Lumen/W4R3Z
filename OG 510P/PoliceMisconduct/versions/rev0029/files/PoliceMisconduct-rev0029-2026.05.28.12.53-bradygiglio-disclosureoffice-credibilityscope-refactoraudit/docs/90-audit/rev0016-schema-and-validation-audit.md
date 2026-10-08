# Rev0016 schema and validation audit

The cube contains **93** schema files and **83** data JSON files in the audited base. Existing `make lint` is valuable and specific, but it is not yet universal JSON Schema enforcement.

The validator currently lives in `tools/validate_surfaces.py`, with **1524** lines and approximately **1114** quoted path/string references. That is workable now and brittle later.

## Recommendation

Split validation into module validators and add formal schema validation. Keep `make lint` as the single command, but let it call smaller checks.

## New audit surfaces

- `data/audit/rev0016_schema_coverage_rows.json`
- `SCHEMA-COVERAGE-AUDIT.json`
- `data/audit/rev0016_validator_structure_audit.json`

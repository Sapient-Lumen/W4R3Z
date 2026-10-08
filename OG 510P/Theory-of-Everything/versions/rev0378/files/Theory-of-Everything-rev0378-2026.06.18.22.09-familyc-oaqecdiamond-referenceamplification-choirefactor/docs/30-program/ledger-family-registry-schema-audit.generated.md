# Ledger-family registry schema audit (generated)

Generated from `LEDGER-FAMILY-REGISTRY.json` and `schemas/ledger-family-registry.schema.json`. Do not edit directly; run `make index` after changing registry fields.

- Registry revision: `rev0378`
- Registered layer families: `54`
- Registry envelope failures: `0`

## Required registry-row envelope

- `family_id`
- `introduced_revision`
- `ledger_files`
- `schema_files`
- `route_fields`
- `open_question_id`
- `cardinality_policy`
- `maximum_route_field_cardinality`
- `generated_summary`
- `audit_note`

## Audit rule

The ledger-family registry owns the route-support stack. Every family row must expose ledgers, schemas, route fields, an OQ gate, cardinality policy, generated summary path, and audit note. Missing registry metadata can hide a support layer from summaries, bindings, gates, or cardinality checks even when individual ledgers are valid.

# Schema coverage audit witnesses

This surface resolves `OQ-0226` by refusing to treat schema conformance as complete merely because the schemas that already exist pass. A schema audit can enforce public JSON contracts only when every root JSON surface is also inventoried as schema-backed, contract-only, or external-standard, with validator routing named explicitly.

## Practice / observation

`rev0331` made local JSON Schemas executable, but that left a second false-green seam: many root JSON surfaces had no local schema and no compact coverage row explaining whether they were intentionally contract-only, external-standard, or simply outside the coverage map. A green schema-conformance audit could therefore speak only for the surfaces already admitted to `SCHEMA_SURFACES`.

## Working synthesis

The current witness family is `schema_coverage_state` / `WVF-0131`. It distinguishes these allowed exact tokens:

- `root-json-inventoried`
- `schema-backed-classified`
- `contract-only-classified`
- `external-standard-classified`
- `validator-surface-linked`
- `coverage-gap-bounded`
- `mixed-schema-coverage`

`SCHEMA-COVERAGE-AUDIT.json` is generated from the root JSON inventory, the local schema/surface map, and admitted contract-only or external-standard validator routes. The audit fails if any root JSON surface is unclassified or names a missing validator.

## Audit surfaces

- `SCHEMA-COVERAGE-AUDIT.json`
- `docs/00-meta/schema-coverage-audit.md`
- `tools/schema_coverage_lib.py`
- `tools/gen_schema_coverage_audit.py`
- `tools/check_schema_coverage_audit_contract.py`
- `tools/check_schema_coverage_witness_contract.py`
- `schemas/schema-coverage-audit.schema.json`
- `tools/check_json_schema_surface_contract.py`
- `tools/check_schema_conformance_audit_contract.py`
- `tools/check_current_witness_receipt_slot.py`

## Forbidden machinery

The following names remain quarantined, not admitted as authority: `schema-coverage-court`, `schema-completeness-sovereign`, `contract-exemption-board`, `coverage-waiver-senate`, `schema-taxonomy-tribunal`, `public-surface-notary`, `validator-monopoly`, and `schema-backfill-authority`.

## Non-authority boundary

Schema coverage is an inventory and validator-routing witness. It can fail closed when a root JSON surface has no schema, no admitted contract-only validator, and no external-standard route. It does not certify semantic truth, canon sufficiency, legal status, release legitimacy, archive minimality, or continuation authority.

## Reopen trigger

Reopen through `OQ-0227` if schema coverage rows begin forcing all surfaces into local schemas, if contract-only classification becomes an exemption board, or if validator routing is treated as proof of public meaning rather than coverage evidence.

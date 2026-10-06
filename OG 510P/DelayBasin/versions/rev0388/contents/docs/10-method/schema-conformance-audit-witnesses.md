# Schema conformance audit witnesses

This surface resolves `OQ-0225` by refusing to let generated audits prove themselves through a green count alone. A generated audit may count as idempotence evidence only when its public JSON contract is separately checked for required keys, declared types, and constants against the paired surface.

## Practice / observation

`rev0330` shipped public JSON Schema files and a checker named `check_json_schema_surface_contract.py`, but the checker mostly verified that required keys existed. A schema could remain description-only for required public fields, or a surface value could drift across type boundaries, without producing a first-class conformance evidence surface.

## Working synthesis

The current witness family is `schema_conformance_state` / `WVF-0130`. It distinguishes these allowed exact tokens:

- `schema-required-checked`
- `schema-type-checked`
- `schema-const-checked`
- `schema-self-checked`
- `public-shape-bounded`
- `semantic-non-authoritative`
- `mixed-schema-conformance`

`SCHEMA-CONFORMANCE-AUDIT.json` is generated from the schema/surface pairs and records required-key, type, and const checks. Existing public schemas now carry type or const constraints for their required public fields instead of relying on description-only placeholders.

## Audit surfaces

- `SCHEMA-CONFORMANCE-AUDIT.json`
- `docs/00-meta/schema-conformance-audit.md`
- `tools/schema_conformance_lib.py`
- `tools/gen_schema_conformance_audit.py`
- `tools/check_schema_conformance_audit_contract.py`
- `tools/check_schema_conformance_witness_contract.py`
- `tools/check_json_schema_surface_contract.py`
- `tools/check_current_witness_receipt_slot.py`
- `schemas/schema-conformance-audit.schema.json`

## Forbidden machinery

The following names remain quarantined, not admitted as authority: `schema-conformance-court`, `type-sovereign`, `contract-adjudication-board`, `schema-waiver-senate`, `generated-audit-notary`, `public-shape-tribunal`, `validation-authority-court`, and `typed-surface-certifier`.

## Non-authority boundary

Schema conformance is a public-shape hygiene witness. It can fail closed when a declared public contract and a JSON surface disagree. It does not certify semantic truth, canon sufficiency, legal status, release legitimacy, archive minimality, or continuation authority.

## Reopen trigger

Reopen through `OQ-0226` if schema-conformance rows begin waiving source-surface review, if type correctness is treated as method truth, or if generated audit schemas become a contract-adjudication board rather than bounded public-shape evidence.

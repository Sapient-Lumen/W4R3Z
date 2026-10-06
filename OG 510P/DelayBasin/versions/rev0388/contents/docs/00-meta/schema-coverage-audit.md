# Schema coverage audit

This generated surface inventories every root JSON surface and records whether it is local-schema-backed, contract-only, or governed as an external-standard metadata surface.
It exists because schema conformance can be green while unclassified JSON surfaces remain outside the schema/contract coverage map.

## Non-authority boundary

This is not a schema-coverage-court, schema-completeness-sovereign, contract-exemption-board, coverage-waiver-senate, schema-taxonomy-tribunal, public-surface-notary, validator-monopoly, or schema-backfill-authority.
Schema coverage is an inventory and validator-routing witness only; it does not certify semantic truth, canon sufficiency, release legitimacy, legal status, minimality, or continuation authority.

## Counts

- Root JSON surfaces: `48`
- Schema-backed: `15`
- Contract-only: `30`
- External-standard: `3`
- Unclassified: `0`
- Failures: `0`

## Coverage rows
- `ALIAS-RETENTION-POLICY.json` — `contract-only`; schema `—`; validators `tools/check_alias_retention_policy_contract.py`; status `pass`
- `APPLICABILITY-LEDGER.json` — `contract-only`; schema `—`; validators `tools/check_applicability_witness_contract.py`; status `pass`
- `ARCHIVE-ECONOMY-AUDIT.json` — `contract-only`; schema `—`; validators `tools/check_archive_economy_audit_contract.py`; status `pass`
- `ASSUMPTION-LEDGER.json` — `contract-only`; schema `—`; validators `tools/check_assumption_witness_contract.py`; status `pass`
- `BASIS-PROVENANCE-AUDIT.json` — `schema-backed`; schema `schemas/basis-provenance-audit.schema.json`; validators `tools/check_json_schema_surface_contract.py`, `tools/check_schema_conformance_audit_contract.py`; status `pass`
- `CANARY-PROTOCOL.json` — `contract-only`; schema `—`; validators `tools/check_canary_protocol_contract.py`; status `pass`
- `CANARY-RUNS.json` — `contract-only`; schema `—`; validators `tools/check_canary_runs_contract.py`; status `pass`
- `CURRENT-RECEIPT.json` — `contract-only`; schema `—`; validators `tools/check_current_receipt_contract.py`; status `pass`
- `CURRENTNESS-CUE-AUDIT.json` — `schema-backed`; schema `schemas/currentness-cue-audit.schema.json`; validators `tools/check_json_schema_surface_contract.py`, `tools/check_schema_conformance_audit_contract.py`; status `pass`
- `DATACUBE-TRANSFER-LEDGER.json` — `contract-only`; schema `—`; validators `tools/check_transfer_ledger_contract.py`; status `pass`
- `FILE-MANIFEST.json` — `contract-only`; schema `—`; validators `tools/check_release_integrity_contract.py`; status `pass`
- `FIREBREAK-LEDGER.json` — `contract-only`; schema `—`; validators `tools/check_reasoning_firebreak_witness_contract.py`; status `pass`
- `FOLLOWTHROUGH-QUEUE.json` — `contract-only`; schema `—`; validators `tools/check_followthrough_witness_contract.py`; status `pass`
- `FOREIGN-PRESSURE-LEDGER.json` — `contract-only`; schema `—`; validators `tools/check_foreign_pressure_witness_contract.py`; status `pass`
- `FRONTIER-BACKLOG.json` — `contract-only`; schema `—`; validators `tools/check_frontier_backlog_contract.py`; status `pass`
- `HOT-SURFACE-COMPACTION-ORIGINALS.json` — `contract-only`; schema `—`; validators `tools/check_hot_surface_compaction_contract.py`; status `pass`
- `HOT-SURFACE-COMPACTION.json` — `contract-only`; schema `—`; validators `tools/check_hot_surface_compaction_contract.py`; status `pass`
- `LEDGER-AUDIT.json` — `contract-only`; schema `—`; validators `tools/check_ledger_audit_contract.py`; status `pass`
- `LEDGER-COLDSTORE.json` — `contract-only`; schema `—`; validators `tools/check_ledger_coldstore_roundtrip_contract.py`; status `pass`
- `LINK-INTEGRITY-POLICY.json` — `contract-only`; schema `—`; validators `tools/check_link_integrity_policy_contract.py`; status `pass`
- `LINT-IDEMPOTENCE-AUDIT.json` — `schema-backed`; schema `schemas/lint-idempotence-audit.schema.json`; validators `tools/check_json_schema_surface_contract.py`, `tools/check_schema_conformance_audit_contract.py`; status `pass`
- `OBLIGATION-LEDGER.json` — `contract-only`; schema `—`; validators `tools/check_obligation_witness_contract.py`; status `pass`
- `PACKAGE-IDENTITY-AUDIT.json` — `schema-backed`; schema `schemas/package-identity-audit.schema.json`; validators `tools/check_json_schema_surface_contract.py`, `tools/check_schema_conformance_audit_contract.py`; status `pass`
- `PATH-ALIAS-LEDGER.json` — `schema-backed`; schema `schemas/path-alias-ledger.schema.json`; validators `tools/check_json_schema_surface_contract.py`, `tools/check_schema_conformance_audit_contract.py`; status `pass`
- `RECEIPT-COLDSTORE.json` — `contract-only`; schema `—`; validators `tools/check_receipt_coldstore_roundtrip_contract.py`; status `pass`
- `REENTRY-CONTRACT.json` — `schema-backed`; schema `schemas/reentry-contract.schema.json`; validators `tools/check_json_schema_surface_contract.py`, `tools/check_schema_conformance_audit_contract.py`; status `pass`
- `REENTRY-SURFACE-CONFORMANCE.json` — `contract-only`; schema `—`; validators `tools/check_reentry_surface_contract.py`; status `pass`
- `RELEASE-MANIFEST.json` — `contract-only`; schema `—`; validators `tools/check_release_integrity_contract.py`; status `pass`
- `RELEASE-PROVENANCE.json` — `contract-only`; schema `—`; validators `tools/check_release_integrity_contract.py`, `tools/check_lint_idempotence_audit_contract.py`; status `pass`
- `RESOLUTION-LEDGER.json` — `contract-only`; schema `—`; validators `tools/check_resolution_witness_contract.py`; status `pass`
- `RETROSPECTIVE-QUEUE.json` — `contract-only`; schema `—`; validators `tools/check_retrospective_write_contract.py`; status `pass`
- `REVISION-RECEIPT.json` — `schema-backed`; schema `schemas/revision-receipt.schema.json`; validators `tools/check_json_schema_surface_contract.py`, `tools/check_schema_conformance_audit_contract.py`; status `pass`
- `SBOM.spdx.json` — `external-standard`; schema `—`; validators `tools/check_external_metadata_contract.py`; status `pass`
- `SCHEMA-CONFORMANCE-AUDIT.json` — `schema-backed`; schema `schemas/schema-conformance-audit.schema.json`; validators `tools/check_json_schema_surface_contract.py`, `tools/check_schema_conformance_audit_contract.py`; status `pass`
- `SCHEMA-COVERAGE-AUDIT.json` — `schema-backed`; schema `schemas/schema-coverage-audit.schema.json`; validators `tools/check_json_schema_surface_contract.py`, `tools/check_schema_conformance_audit_contract.py`; status `pass`
- `SELF-SUFFICIENCY-LEDGER.json` — `contract-only`; schema `—`; validators `tools/check_self_sufficiency_assay_contract.py`; status `pass`
- `SURFACE-STATUS.json` — `schema-backed`; schema `schemas/surface-status.schema.json`; validators `tools/check_json_schema_surface_contract.py`, `tools/check_schema_conformance_audit_contract.py`; status `pass`
- `VALIDATION-INDEX.json` — `schema-backed`; schema `schemas/validation-index.schema.json`; validators `tools/check_json_schema_surface_contract.py`, `tools/check_schema_conformance_audit_contract.py`; status `pass`
- `VALIDATION-TOOLCHAIN-MANIFEST.json` — `schema-backed`; schema `schemas/validation-toolchain-manifest.schema.json`; validators `tools/check_json_schema_surface_contract.py`, `tools/check_schema_conformance_audit_contract.py`; status `pass`
- `WITNESS-FAMILY-HANDLES.json` — `contract-only`; schema `—`; validators `tools/check_witness_family_handle_contract.py`; status `pass`
- `WITNESS-VOCABULARY.json` — `contract-only`; schema `—`; validators `tools/check_vocabulary_witness_contract.py`; status `pass`
- `codemeta.json` — `external-standard`; schema `—`; validators `tools/check_external_metadata_contract.py`; status `pass`
- `compact-surface-bundle.json` — `contract-only`; schema `—`; validators `tools/check_compact_surface_bundle_contract.py`; status `pass`
- `context-pack.json` — `schema-backed`; schema `schemas/context-pack.schema.json`; validators `tools/check_json_schema_surface_contract.py`, `tools/check_schema_conformance_audit_contract.py`; status `pass`
- `frontier-ticket.json` — `schema-backed`; schema `schemas/frontier-ticket.schema.json`; validators `tools/check_json_schema_surface_contract.py`, `tools/check_schema_conformance_audit_contract.py`; status `pass`
- `innovation-packet.json` — `schema-backed`; schema `schemas/innovation-packet.schema.json`; validators `tools/check_json_schema_surface_contract.py`, `tools/check_schema_conformance_audit_contract.py`; status `pass`
- `replay-capsule.json` — `contract-only`; schema `—`; validators `tools/check_replay_capsule_contract.py`; status `pass`
- `ro-crate-metadata.json` — `external-standard`; schema `—`; validators `tools/check_external_metadata_contract.py`; status `pass`

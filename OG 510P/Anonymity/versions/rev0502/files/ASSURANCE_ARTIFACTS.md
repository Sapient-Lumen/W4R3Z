# Assurance Artifacts

This is the grouped catalog of the archive's trust / integrity / drift / provenance surfaces.
Use it when you want the assurance surfaces as a set rather than discovering them piecemeal.

## Identity and bundle self-description

- `VERSION`
- `RELEASE_MANIFEST.json`
- `REVISION_RECEIPT.json`
- `ARCHIVE_INDEX.json`
- `MANIFEST.sha256`
- `MANIFEST.json`

## Publication boundary and decision posture

- `published/citation_heads.json`
- `published/PUBLIC_SURFACE.json`
- `release_queue/QUEUE_INDEX.json`
- `release_queue/LATEST_DECISION.json`
- `release_queue/DECISION_INDEX.json`

## Structural contracts and semantic invariants

- `schemas/`
- `reports/surface_schema_validation.json`
- `publishing/archive_invariants.json`
- `reports/archive_invariants.json`

## Integrity, completeness, pruning, and cross-surface agreement

- `reports/archive_surface_coherence.json`
- `reports/context_pack_contract.json`
- `reports/context_pack_budget.json`
- `reports/transient_surface_audit.json`
- `reports/manifest_sha256_verification.json`
- `reports/manifest_coverage_audit.json`

## Compared-bundle provenance and transfer memory

- `TRANSFER_SOURCES.json`
- `TRANSFER_SOURCES.md`
- `TRANSFER_INPUTS.sha256`
- `reports/transfer_source_receipt.json`
- `DATACUBE_TRANSFER_LEDGER.json`
- `DATACUBE_TRANSFER_LEDGER.md`

## Stage/gate and operator-navigation surfaces

- `CONTEXT_PACK.json`
- `START_HERE.md`
- `publishing/control_surfaces.json`
- `publishing/LIFECYCLE_GATES.md`
- `reports/lifecycle_gate_status.json`


Archive-budget and review-render hygiene now live in `publishing/archive_budget_policy.json` and `reports/archive_budget.json`.
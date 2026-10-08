# Session review rev0848

- Created: `2026-06-13T12:31:00Z`
- Output artifact: `EvidenceVault-rev0848-2026.06.13.12.52-builder-boundary-public-path-integrity-hardening.zip`
- Context: rev0848 overlay over rev0847; canonical rev0840 patch payloads unchanged.

## Focus

- material-builder subprocess target boundary hardening
- publication public_paths / PUBLIC_SURFACE consistency
- local rights reference coverage for LICENSES/licences/notices directories
- overlay-bundle self-integrity validator

## Substantive changes

### rebuild_indexes.py

Change: Added archive_python_script_path() and PY_MODULE_RE; material builders are now validated as safe module names and non-symlink archive-local scripts before subprocess execution.

Risk reduced: Prevents a symlinked or path-injected material builder from running host/cloudtainer code during release-critical rebuild refreshes.

### publish_queue_item.py

Change: Requires non-empty duplicate-free decision.public_paths and checks them against the PUBLIC_SURFACE snapshot/source manifest before writing public release records.

Risk reduced: Prevents a future rights-approved release record from claiming paths that were not actually digested into the public-surface snapshot.

### publication_rights_gate.py

Change: Recognizes local rights references under LICENSES/licences/notices/copyright path components even when the leaf filename is neutral.

Risk reduced: Prevents component-license links such as LICENSES/Apache-2.0.txt from bypassing the fresh local rights-reference scan.

### overlay checks

Change: Added validate_overlay_bundle_integrity_rev0848.py for exact overlay-manifest, patch hash, patch-chain, input artifact, and changed-file checks.

Risk reduced: Makes overlay artifact drift or stale self-description fail through a runnable validator instead of manual inspection only.

## New files

- `scripts/validate_publication_rights_gate_license_directory_reference_rev0848.py`
- `scripts/validate_publish_queue_item_public_path_consistency_rev0848.py`
- `scripts/validate_rebuild_indexes_material_builder_boundary_rev0848.py`
- `scripts/validate_overlay_bundle_integrity_rev0848.py`
- `AUDIT/PUBLICATION_RIGHTS_GATE_LICENSE_DIRECTORY_REFERENCE_REV0848.json`
- `AUDIT/PUBLICATION_RIGHTS_GATE_LICENSE_DIRECTORY_REFERENCE_REV0848.md`
- `AUDIT/PUBLISH_QUEUE_ITEM_PUBLIC_PATH_CONSISTENCY_REV0848.json`
- `AUDIT/PUBLISH_QUEUE_ITEM_PUBLIC_PATH_CONSISTENCY_REV0848.md`
- `AUDIT/REBUILD_INDEXES_MATERIAL_BUILDER_BOUNDARY_REV0848.json`
- `AUDIT/REBUILD_INDEXES_MATERIAL_BUILDER_BOUNDARY_REV0848.md`
- `AUDIT/OVERLAY_BUNDLE_INTEGRITY_REV0848.json`
- `AUDIT/OVERLAY_BUNDLE_INTEGRITY_REV0848.md`
- `VALIDATION/rev0848_targeted_validation.txt`
- `PATCHES/rev0847-to-rev0848-overlay.patch`
- `CHECKS/patch-bundle-identity-rev0848.json`
- `CHECKS/build-provenance-rev0848.intoto.json`

## Validation summary

Targeted validators pass; overlay-bundle self-integrity validator passes after manifest/check refresh; publication rights gate still refuses the overlay as expected.

## Rights status

publication_blocked; no license terms or notices inferred

## Known limits

- The overlay bundle is still not a full canonical tree; full make rebuild-indexes/make gate should run after applying the overlay stack to the complete canonical tree.
- The new public_paths consistency check validates record/snapshot consistency but cannot decide whether owner/legal approval is adequate.
- The overlay self-integrity validator checks extracted tree surfaces; external ZIP sidecar verification remains a packaging-time check.

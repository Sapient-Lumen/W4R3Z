# overlay-bundle self-integrity

- Revision: `rev0848`
- Created: `2026-06-13T12:31:00Z`
- Target: `CHECKS/overlay-manifest.json and CHECKS/*.sha256`
- Status: `passed_after_targeted_validation`

## Risk reduced

Overlay evidence can rot independently of canonical-tree validators; a stale manifest, patch hash list, or input-artifact path leak would make downstream application ambiguous.

## Changes observed

- Adds a runnable self-validator for overlay manifest exactness, sidecar hash, patch hashes, overlay-patch chain continuity, portable input-artifact names, and changed-file list cleanliness.
- Gives future sessions a first-pass integrity gate for the overlay artifact itself rather than relying only on manual packaging checks.

## Validator

- `scripts/validate_overlay_bundle_integrity_rev0848.py`

## Validator assertions

- overlay manifest exactly covers regular files except its self/sidecar pair
- CHECKS/patches.sha256 exactly covers PATCHES/*.patch and validates hashes
- overlay patch chain is contiguous through the current revision
- input-artifacts uses portable basenames, not cloudtainer-local paths
- changed-canonical-files has clean existing paths and current revision evidence

## Publication rights effect

None. Publication remains blocked pending owner-approved rights files and component license conclusions.

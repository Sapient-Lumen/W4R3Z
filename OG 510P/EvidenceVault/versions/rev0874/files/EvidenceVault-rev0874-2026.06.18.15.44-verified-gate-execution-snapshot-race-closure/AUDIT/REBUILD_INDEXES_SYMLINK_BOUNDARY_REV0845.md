# Rebuild Indexes Symlink Boundary Rev0845

- Status: `rebuild_indexes_symlink_boundary_validated_refreshed_with_atomic_output_checks`
- Revision context: `rev0845-audit-refreshed-in-rev0847-overlay`
- Purpose: Make rebuild_indexes.py fail closed on symlinked files/directories before generating digest/index surfaces.
- Risk reduced: INDEX/files.*, MANIFEST.sha256, release identity refreshes, and RO-Crate digested entities no longer silently hash host/cloudtainer files reachable through archive-internal symlinks.

- Changed/rebuild script: `scripts/rebuild_indexes.py`
- SHA-256: `df31735a8f0d6bbeec632094880ed2e6f218a57f623d01c522766f2422b12477`

## Dynamic cases

- clean fixture tree collects regular files deterministically
- symlinked file under the archive root is rejected before indexing
- sha256_file rejects symlink targets directly
- symlinked directory is rejected and not traversed

## Limits

- This validator probes helper behavior with fixtures; a full canonical rebuild should still run after applying the overlay patch.

## Validator

- Command: `/opt/pyvenv/bin/python3 scripts/validate_rebuild_indexes_symlink_boundary_rev0845.py`
- Return code: `0`
- Validator SHA-256: `a63cb7e9943d940be3418cfcd5c6546c850050d0a069fcd889c81ddc5d09de48`

```text
rebuild-indexes-symlink-boundary-rev0845: OK
```

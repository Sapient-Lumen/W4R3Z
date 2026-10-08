# Session review — rev0847

Created: `2026-06-13T09:27:16Z`

## Focus

This pass prioritized concrete failure modes over more registry surface: publication output redirection and partial generated-output writes.

## Main changes

1. `publish_queue_item.py` now rejects public-release output destinations outside `ROOT` and output paths that pass through symlinked parents before temporary files are created.
2. The final queue transition script is validated as an archive-local regular file before subprocess execution, and the child runs with `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUNBUFFERED=1`, and `cwd=ROOT`.
3. `rebuild_indexes.py` now writes `RELEASE_MANIFEST.json`, `ro-crate-metadata.json`, `RO_CRATE_PROFILE.md`, `INDEX/files.json`, `INDEX/files.csv`, and `MANIFEST.sha256` through fsynced same-directory temporary files and atomic replacement.

## New audits / validators

- `AUDIT/PUBLISH_QUEUE_ITEM_OUTPUT_BOUNDARY_REV0847.*`
- `scripts/validate_publish_queue_item_output_boundary_rev0847.py`
- `AUDIT/REBUILD_INDEXES_ATOMIC_OUTPUTS_REV0847.*`
- `scripts/validate_rebuild_indexes_atomic_outputs_rev0847.py`

## Rights status

Still publication-blocked. No license or notice text was invented, and no SPDX/RO-Crate rights conclusions were upgraded.

## Remaining high-priority work

Apply the overlay stack to the complete canonical tree, then run a full rebuild/gate. Once owner-approved root/component license and notice content exists, refresh the rights ledger, SPDX, RO-Crate, and publication gate together.

# Overlay absolute path reference audit rev0841

Created: 2026-06-12T15:06-04:00 America/New_York

Scope: overlay-artifact scan for cloudtainer-local absolute path references outside rev0841 self-report files.

Status: **cloudtainer_absolute_paths_still_present_in_overlay**

Files with matches: 4
Total matches: 2629

## Interpretation

- `CHECKS/input-artifacts.sha256` was normalized in rev0841 and no longer records `/mnt/data/...` input archive paths.
- The remaining high-volume source is the cumulative patch. It retains historical `/mnt/data` and `/home/oai` path references in patch headers/body. This audit records that risk; rev0841 does not rewrite the patch stream because doing so would change the validated payload.
- Future patch generation should prefer relative, source-controlled roots and should run this overlay audit before zipping.

## Matched files

### AUDIT/ABSOLUTE_PATH_REFERENCE_AUDIT.json — 2 matches

- line 4: `/mnt/data/...`
- line 5: `/home/oai/...`

### AUDIT/ABSOLUTE_PATH_REFERENCE_AUDIT.md — 2 matches

- line 3: `/mnt/data/...`
- line 3: `/home/oai/...`

### PATCHES/rev0826-to-rev0840-cumulative.patch — 2623 matches

- line 1: `/mnt/data/rev0826_base/EvidenceVault-rev0826/AUDIT/ABSOLUTE_PATH_REFERENCE_AUDIT.json`
- line 2: `/mnt/data/rev0826_base/EvidenceVault-rev0826/AUDIT/ABSOLUTE_PATH_REFERENCE_AUDIT.json`
- line 8: `/mnt/data/...`
- line 9: `/home/oai/...`
- line 25: `/mnt/data/rev0826_base/EvidenceVault-rev0826/AUDIT/ABSOLUTE_PATH_REFERENCE_AUDIT.md`

### PATCHES/rev0839-to-rev0840-incremental.patch — 2 matches

- line 19: `/mnt/data/...`
- line 19: `/home/oai/...`


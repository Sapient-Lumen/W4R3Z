# Public trace receipt relocation audit — REV0108

Status: `pass_with_blockers`  
Promotion allowed: `false`

Tests that v2 evaluation receipts are content-addressed: moving or renaming an accepted trace/provenance pair preserves the subject-set digest and selector entry if actual file hashes still match; tampered relocated files and old v1 receipts stay blocked.

## Cases

- `subject_set_stable_after_rename` = `True`
- `paths_differ_but_hashes_match` = `True`
- `selector_allows_original_matching_files` = `True`
- `selector_allows_relocated_matching_files` = `True`
- `selector_blocks_tampered_relocated_trace` = `True`
- `selector_blocks_v1_or_missing_subject_set` = `True`

## Errors

- none

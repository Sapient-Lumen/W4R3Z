# Public trace handoff archive audit — REV0114

Status: `pass_with_blockers`  
Promotion allowed: `false`

Audits a self-contained public-trace handoff archive: an accepted evaluation receipt plus selector-entry receipt can be zipped, extracted, moved, and replayed by relative paths and SHA-256 subject digests, while the archive also carries the verifier/evaluator/selector/replay toolpack and cold-reviewer wrapper by digest. Tampered files, missing tools, tool tampering, path escapes, and forged subject-set hashes stay blocked.

## Cases

- `selector_entry_fixture_opened` = `True`
- `direct_toolpacked_handoff_gate_passes` = `True`
- `toolpack_subject_set_verified` = `True`
- `extracted_archive_gate_passes` = `True`
- `archive_movement_preserves_subject_sets` = `True`
- `tampered_extracted_trace_blocks` = `True`
- `path_escape_manifest_blocks` = `True`
- `forged_handoff_subject_set_blocks` = `True`
- `forged_toolpack_subject_set_blocks` = `True`
- `missing_toolpack_subject_blocks` = `True`
- `tampered_toolpack_tool_blocks` = `True`

## Errors

- none

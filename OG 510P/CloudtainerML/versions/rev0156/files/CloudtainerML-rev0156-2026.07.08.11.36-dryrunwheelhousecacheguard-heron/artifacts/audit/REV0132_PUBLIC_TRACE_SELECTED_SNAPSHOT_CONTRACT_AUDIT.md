# Public trace selected-snapshot contract audit — REV0132

Status: `pass`  
Promotion allowed: `false`

## Checks

- preflight_selects_digest_verified_snapshot_path: `True`
- preflight_writes_runtime_capture_env: `True`
- preflight_records_selected_snapshot_in_json: `True`
- run_wrapper_sources_fresh_capture_env_after_preflight: `True`
- one_shot_sources_capture_env_after_preflight: `True`
- one_shot_requires_selected_local_snapshot: `True`
- one_shot_prefers_capture_model_export: `True`
- one_shot_still_forbids_download: `True`
- smoke_guards_selected_snapshot_contract: `True`

## Interpretation

The preflight must not only prove that a digest-verified snapshot exists. It must select a concrete local snapshot path and make the capture wrapper load that exact path. This prevents cache-resolution ambiguity from turning a hash check into evidence about the wrong bytes.

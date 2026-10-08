# Public trace loader-snapshot binding audit — REV0144

Status: `pass`  
Promotion allowed: `false`

## Checks

- capture_helper_has_explicit_loader_binding_flag: `True`
- capture_helper_computes_loader_binding_verified: `True`
- capture_helper_rejects_nonlocal_or_unbound_model_source: `True`
- capture_helper_public_provenance_requires_loader_binding: `True`
- capture_helper_serializes_loader_binding_receipt: `True`
- one_shot_passes_loader_binding_flag_to_capture: `True`
- one_shot_loads_capture_model_from_selected_snapshot_env: `True`
- one_shot_forbids_cap_model_drift_before_helper: `True`
- live_wrappers_run_loader_binding_audit: `True`
- selected_snapshot_audit_checks_loader_binding_or_smoke_does: `True`
- smoke_guards_loader_binding_contract: `True`
- run_packet_declares_loader_binding_contract: `True`
- run_packet_declares_loader_binding_required: `True`

## Interpretation

This closes a narrower gap than rev0132: the wrapper selects `LOCAL_SNAPSHOT_DIR`, and now the Python capture helper must independently refuse public promotion unless its own `--model` load source is that digest-verified local snapshot path.

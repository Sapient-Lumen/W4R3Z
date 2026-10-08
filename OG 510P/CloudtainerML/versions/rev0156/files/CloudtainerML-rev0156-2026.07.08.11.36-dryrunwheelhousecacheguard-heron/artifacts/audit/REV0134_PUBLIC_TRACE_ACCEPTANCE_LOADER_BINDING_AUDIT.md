# Public trace acceptance loader-binding audit — REV0134

Status: `pass`  
Promotion allowed: `false`

## Checks

- capture_helper_emits_digest_and_loader_binding_fields: `True`
- verifier_declares_public_loader_binding_field_list: `True`
- verifier_imports_pinned_expected_model_digest: `True`
- verifier_requires_manifest_loader_binding_fields: `True`
- verifier_requires_npz_loader_binding_fields: `True`
- verifier_requires_loader_source_equals_verified_snapshot_path: `True`
- verifier_requires_expected_and_observed_safetensors_sha: `True`
- npz_self_attestation_requires_loader_fields: `True`
- manifest_npz_crosscheck_includes_loader_fields: `True`
- wrappers_run_acceptance_loader_binding_audit: `True`
- smoke_guards_acceptance_loader_binding: `True`
- run_packet_declares_acceptance_loader_binding_contract: `True`
- run_packet_declares_acceptance_loader_binding_audit: `True`

## Interpretation

The live capture path can now refuse wrong loader sources before model import, but that is not sufficient. This audit ensures the downstream public-trace verifier rejects any trace/provenance pair that omits the selected-snapshot path, loader-binding boolean, and full pinned `model.safetensors` SHA-256 proof.

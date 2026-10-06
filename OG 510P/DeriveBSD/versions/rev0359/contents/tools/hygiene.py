#!/usr/bin/env python3
"""Run all lightweight archive hygiene checks.

This is a convenience wrapper so CI or humans can run a single command.

Usage:
  python3 tools/hygiene.py

Exit codes:
  0: all checks passed
  1: at least one check failed
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKS = [
    [sys.executable, str(ROOT / "tools" / "check_consistency.py")],
    [sys.executable, str(ROOT / "tools" / "lint_spec_schemas.py")],
    [sys.executable, str(ROOT / "tools" / "check_schema_kind_matches_filename.py")],
    [sys.executable, str(ROOT / "tools" / "validate_spec_examples.py")],
    [sys.executable, str(ROOT / "tools" / "check_discovery.py")],
    [sys.executable, str(ROOT / "tools" / "check_meta_doc_discoverability.py")],
    [sys.executable, str(ROOT / "tools" / "check_changelog_format.py")],
    [sys.executable, str(ROOT / "tools" / "check_changelog_artifact_mentions.py")],
    [sys.executable, str(ROOT / "tools" / "check_release_last_updated.py")],
    [sys.executable, str(ROOT / "tools" / "check_must_read_set.py")],
    [sys.executable, str(ROOT / "tools" / "check_doc_metadata.py")],
    [sys.executable, str(ROOT / "tools" / "check_doc_patterns.py")],
    [sys.executable, str(ROOT / "tools" / "check_diff_surface_registry.py")],
    [sys.executable, str(ROOT / "tools" / "check_diff_surface_registry_wiring.py")],
    [sys.executable, str(ROOT / "tools" / "check_diff_review_docs.py")],
    [sys.executable, str(ROOT / "tools" / "check_diff_wiring_risk_flags.py")],
    [sys.executable, str(ROOT / "tools" / "check_juicy_lesson_references.py")],
    [sys.executable, str(ROOT / "tools" / "check_risk_flag_registry.py")],
    [sys.executable, str(ROOT / "tools" / "check_risk_flag_typical_sources.py")],
    [sys.executable, str(ROOT / "tools" / "check_product_profiles.py")],
    [sys.executable, str(ROOT / "tools" / "check_profile_default_vocabulary.py")],
    [sys.executable, str(ROOT / "tools" / "check_remote_assistance_recording_posture.py")],
    [sys.executable, str(ROOT / "tools" / "check_operator_access_recording_posture.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_recording_posture.py")],
    [sys.executable, str(ROOT / "tools" / "check_destructive_reprovision_evidence_posture.py")],
    [sys.executable, str(ROOT / "tools" / "check_firmware_evidence_posture.py")],
    [sys.executable, str(ROOT / "tools" / "check_trust_bundle_apply_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_trust_bundle_apply_bundle_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_event_seal_bundle_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_event_journal_digest_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_restore_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_restore_bundle_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_support_session_bundle_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_operator_session_bundle_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_bundle_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_learn_net_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_access_posture_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_lifetime_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_locator_posture_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_secret_handoff_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_secret_handoff_authn_mode_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_secret_lifetime_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_secret_consumption_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_support_session_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_authority_join_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_lease_id_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_maintenance_trigger_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_support_trigger_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_access_model_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_human_share_access_model_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_organization_exposure_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_surface_continuity_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_diagnostic_artifact_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_notes_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_visible_indicator_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_revocation_affordance_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_return_path_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_management_return_binding_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_post_end_management_return_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_terminal_end_condition_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_current_stack_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_post_end_access_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_binding_hints_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_binding_hint_exactness_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_webhook_validation_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_validation_hint_webhook_only_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_endpoint_hint_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_url_hint_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_https_url_hint_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_path_prefix_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_path_prefix_uri_safe_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_local_service_hint_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_hostname_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_remote_locator_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_remote_locator_value_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_remote_locator_uri_hint_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_destination_hint_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_publish_session_tailnet_access_model_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_packet_capture_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_packet_capture_session_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_packet_capture_summary_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_packet_capture_selector_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_packet_capture_artifact_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_packet_capture_import_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_packet_capture_normalization_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_packet_capture_bundle_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_packet_capture_export_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_packet_capture_export_approval_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_packet_capture_export_transport_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_packet_capture_export_acceptance_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_packet_capture_export_destination_binding_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_packet_capture_export_recipient_digest_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_packet_capture_export_remote_object_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_packet_capture_export_remote_validator_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_packet_capture_export_remote_protection_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_packet_capture_export_remote_locator_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_packet_capture_export_reverification_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_packet_capture_export_digest_stability_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_store_gc_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_base_set_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_tree_mount_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_hw_support_matrix_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_hw_support_promotion_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_hw_support_qualification_receipt_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_hw_support_qualification_profile_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_hw_support_qualification_freshness_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_hw_support_qualification_status_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_hw_support_conditions_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_hw_support_qualification_target_scope_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_graphics_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_session_surface_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_uri_open_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_file_open_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_document_edit_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_working_copy_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_working_copy_save_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_reintegration_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_candidate_snapshot_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_candidate_supersession_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_candidate_same_origin_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_candidate_stale_target_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_candidate_stale_denial_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_candidate_retry_recovery_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_intent_role_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_role_binding_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_role_binding_diff_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_role_binding_event_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_role_binding_consent_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_role_binding_policy_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_role_binding_precondition_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_role_binding_import_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_role_binding_authority_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_role_binding_policy_profile_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_role_binding_policy_apply_window_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_role_binding_policy_instance_identity_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_role_binding_policy_denial_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_role_binding_denial_precedence_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_role_binding_policy_consumption_pointer_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_role_binding_policy_consumption_digest_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_role_binding_policy_consumption_binding_digest_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_role_binding_policy_consumption_diff_digest_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_role_binding_policy_consumption_previous_binding_digest_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_role_binding_policy_consumption_action_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_role_binding_policy_consumption_recovery_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_role_binding_policy_recovery_interpretation_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_support_bundle_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_support_bundle_import_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_safe_open_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_boot_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_reset_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_content_origin_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_strata_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_exec_integrity_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_keyless_identity_contract.py")],

    [sys.executable, str(ROOT / "tools" / "check_release_transparency_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_witness_policy_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_supplychain_verification_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_vulnerability_verification_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_attestation_admission_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_lease_authority_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_authority_budget_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_frontend_compile_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_derive_unit_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_fuzz_contract.py")],

    [sys.executable, str(ROOT / "tools" / "check_curated_references.py")],
    [sys.executable, str(ROOT / "tools" / "check_release_curated_references.py")],
    [sys.executable, str(ROOT / "tools" / "check_generated_docs.py")],
    [sys.executable, str(ROOT / "tools" / "check_risk_register.py")],
    [sys.executable, str(ROOT / "tools" / "check_open_questions_decisions.py")],
    [sys.executable, str(ROOT / "tools" / "check_microvm_example_plan_digests.py")],
    [sys.executable, str(ROOT / "tools" / "check_microvm_receipt_reason_requirements.py")],
    [sys.executable, str(ROOT / "tools" / "check_microvm_reason_code_registry.py")],



    [sys.executable, str(ROOT / "tools" / "check_spec_example_coverage.py")],
    [sys.executable, str(ROOT / "tools" / "check_version.py")],
]



def run(cmd: list[str]) -> int:
    print(f"==> {' '.join(cmd)}")
    p = subprocess.run(cmd, cwd=ROOT)
    return int(p.returncode)


def main() -> int:
    rc = 0
    for cmd in CHECKS:
        r = run(cmd)
        if r != 0:
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run all lightweight archive hygiene checks.

This is a convenience wrapper so CI or humans can run a single command.

Usage:
  python3 tools/hygiene.py
  python3 tools/hygiene.py --profile release-critical
  python3 tools/hygiene.py --profile post-detach

Exit codes:
  0: all checks passed
  1: at least one check failed or timed out
  2: ledger mode stopped cleanly before the selected profile completed
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import signal
import stat
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LEDGER_PARTIAL_EXIT_CODE = 2

CUBE_INPUT_FINGERPRINT_ROOTS = (
    "CHANGELOG.md",
    "README.md",
    "adrs",
    "docs",
    "fixtures",
    "rfcs",
    "spec",
    "tools",
)

CUBE_INPUT_FINGERPRINT_EXCLUDED_DIRS = {"__pycache__"}
CUBE_INPUT_FINGERPRINT_EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
CUBE_INPUT_FINGERPRINT_EXCLUDED_RELPATHS = {"spec/examples/cube.hygiene.run.ledger.json"}
_CUBE_INPUT_FINGERPRINT_CACHE: tuple[str, int] | None = None
_RUNNER_ENVIRONMENT_SHA256_CACHE: str | None = None

CHECKS = [
    [sys.executable, "-S", str(ROOT / "tools" / "check_consistency.py")],
    [sys.executable, str(ROOT / "tools" / "lint_spec_schemas.py")],
    [sys.executable, str(ROOT / "tools" / "check_schema_kind_matches_filename.py")],
    [sys.executable, str(ROOT / "tools" / "validate_spec_examples.py")],
    [sys.executable, str(ROOT / "tools" / "check_discovery.py")],
    [sys.executable, str(ROOT / "tools" / "check_meta_doc_discoverability.py")],
    [sys.executable, str(ROOT / "tools" / "check_changelog_format.py")],
    [sys.executable, str(ROOT / "tools" / "check_release_heading_uniqueness.py")],
    [sys.executable, str(ROOT / "tools" / "check_release_heading_order.py")],
    [sys.executable, str(ROOT / "tools" / "check_changelog_index_release_coverage.py")],
    [sys.executable, str(ROOT / "tools" / "check_index_front_matter_order.py")],
    [sys.executable, str(ROOT / "tools" / "check_doc_number_prefix_uniqueness.py")],
    [sys.executable, str(ROOT / "tools" / "check_markdown_h1_structure.py")],
    [sys.executable, str(ROOT / "tools" / "check_markdown_h2_heading_uniqueness.py")],
    [sys.executable, str(ROOT / "tools" / "check_markdown_inline_code_balance.py")],
    [sys.executable, str(ROOT / "tools" / "check_text_files_final_newline.py")],
    [sys.executable, str(ROOT / "tools" / "check_python_tool_executable_bits.py")],
    [sys.executable, str(ROOT / "tools" / "check_changelog_artifact_mentions.py")],
    [sys.executable, str(ROOT / "tools" / "check_hygiene_checkset_completeness.py")],
    [sys.executable, str(ROOT / "tools" / "check_frontdoor_budget.py")],
    [sys.executable, str(ROOT / "tools" / "check_canonical_json_digest_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_json_duplicate_key_rejection.py")],
    [sys.executable, str(ROOT / "tools" / "check_no_root_hygiene_log_dumps.py")],
    [sys.executable, str(ROOT / "tools" / "check_no_python_bytecode_artifacts.py")],
    [sys.executable, str(ROOT / "tools" / "check_cube_hygiene_run_ledger.py")],
    [sys.executable, str(ROOT / "tools" / "check_current_generated_surface_sync.py")],
    [sys.executable, str(ROOT / "tools" / "check_runtime_golden_thread.py")],
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
    [sys.executable, str(ROOT / "tools" / "check_breakglass_recording_activation_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_repair_outcome_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_method_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_bootstrap_join_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_bootstrap_sequence_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_bootstrap_actuation_boundary.py")],
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
    [sys.executable, str(ROOT / "tools" / "check_breakglass_adapter_detail_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_adapter_bundle_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_adapter_export_receipt_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_adapter_anchor_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_adapter_live_locator_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_adapter_payload_anchor_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_adapter_case_object_exactness_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_adapter_case_object_validator_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_adapter_case_object_remote_protection_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_adapter_case_object_remote_protection_exactness_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_adapter_case_object_remote_locator_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_adapter_case_object_reverification_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_uefi_var_set_bundle_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_fw_update_bundle_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_fw_inventory_diff_bundle_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_boot_bless_bundle_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_storage_scrub_bundle_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_time_sync_bundle_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_time_degraded_response_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_time_source_policy_profile_floors.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_vertical_slice.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_harness_run.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_prototype.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_safe_capture.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_freebsd_backend_plan.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_freebsd_backend_run.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_capsicum_worker_source.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_capsicum_worker_build.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_capsicum_worker_bridge.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_capsicum_worker_sha256_vectors.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_freebsd_host_smoke_runner.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_freebsd_host_proof_bundle.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_freebsd_host_proof_handoff.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_freebsd_host_proof_handoff_seal.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_freebsd_host_proof_sealed_importer.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_freebsd_host_proof_sealed_preflight.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_freebsd_host_proof_importer.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_freebsd_host_proof_import_audit.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_freebsd_host_proof_checked_import_gate.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_freebsd_host_proof_preflight.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_freebsd_host_proof_collect_import.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_freebsd_real_host_operator_packet.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fallback_freebsd_host_proof_work_order.py")],
    [sys.executable, str(ROOT / "tools" / "check_freebsd_real_host_proof_theatre_gate.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_fd_slot_policy_consistency.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_ingest_firstcut.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_fs_admission.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_mount_hardening.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_member_kind_floor.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_member_path_normalization.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_metadata_fidelity_floor.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_single_subject.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_regular_file_subject.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_present_device_scope.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_attach_receipt_hints.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_subject_capture.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_early_detach.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_worker_reset.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_preserved_capture.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_authoritative_store.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_single_object_projection.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_projection_digest_binding.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_preopened_delivery.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_broker_collected_output.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_single_declared_derivative_slot.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_empty_writeonly_derivative_slot.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_append_open_derivative_slot.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_capability_mode_entry.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_closed_world_descriptor_set.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_reviewed_process_launch.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_executable_identity.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_runtime_dependency_closure.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_credential_envelope.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_worker_lifecycle.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_resource_envelope.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_peer_interaction.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_ambient_input_envelope.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_network_egress.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_persistent_state.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_contract_closure.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_launch_evidence.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_recovery_evidence.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_query_projection.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_query_projection_access_receipt.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_export_bundle.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_export_bundle_access_receipt.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_export_bundle_deletion_receipt.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_terminal_closure_capsule.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_terminal_closure_access_receipt.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_terminal_closure_successor_authority_receipt.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_terminal_closure_successor_cutover_receipt.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_revocation_tombstone.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_denial_receipt.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_fresh_authority_receipt.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_fresh_authority_consumption_receipt.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_successor_index_cutover_receipt.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_successor_index_checkpoint_receipt.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_reader_admission_receipt.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_reader_use_receipt.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_reader_use_ledger_receipt.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_reader_use_ledger_retention_receipt.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_reader_use_ledger_retention_expiry_receipt.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_reader_use_ledger_retention_expiry_enforcement_receipt.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_runtime_state_machine.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_scenario_replay.py")],
    [sys.executable, str(ROOT / "tools" / "check_cube_schema_audit_report.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_transition_witness.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_denial_reason_registry.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_denial_selection_receipt.py")],
    [sys.executable, str(ROOT / "tools" / "check_removable_media_local_post_detach_rate_limit_debit_ledger_receipt.py")],
    [sys.executable, str(ROOT / "tools" / "check_cube_schema_refactor_backlog.py")],
    [sys.executable, str(ROOT / "tools" / "check_cube_hygiene_checkset_manifest.py")],
    [sys.executable, str(ROOT / "tools" / "check_crypto_compat_agent_projection_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_lease_snapshot_bundle_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_secret_bundle_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_pki_issue_bundle_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_attestation_bundle_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_attestation_reference_variance_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_attestation_reference_exception_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_attestation_reference_renewal_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_attestation_reference_selection_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_attestation_identity_provenance_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_attestation_action_verification_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_attestation_degraded_admission_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_attestation_rejected_override_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_attestation_verdict_projection_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_resumption_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_resumption_join_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_resumption_subject_binding_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_breakglass_resumption_temporal_contract.py")],
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
    [sys.executable, str(ROOT / "tools" / "check_net_publish_session_schema_classification.py")],
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
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_subject_exactness.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_grant_digest_join.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_single_delivery_exhaustion.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_effective_until.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_renewal_lineage.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_successor_scope.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_successor_payload_lineage.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_successor_payload_digest.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_successor_foreground.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_successor_delivery_mode.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_successor_rate_limit.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_successor_expires_at.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_constraints_closed_world.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_baseline_frozen.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_distinct_family_split.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_first_richer_rfc_target.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_finite_collection_autostop.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_snapshot_posture.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_manifest_posture.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_readonly_first.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_member_kind_floor.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_manifest_field_floor.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_manifest_order.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_manifest_digest.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_review_path_normalization.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_top_level_names.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_ancestor_closure.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_selected_roots.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_fresh_root.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_result_root_receipt.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_result_root_locator_posture.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_result_root_display_snapshot_continuity.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_result_root_handle_opacity.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_placement_hint_posture.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_profile_scope.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_artifact_family_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_example_joins.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_first_impl_aliasing.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_review_ui_path_compression.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_mime_posture.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_collection_filesystem_metadata_posture.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_datatransfer_finite_collection_current_stack_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_uri_open_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_file_open_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_document_edit_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_document_viewing_posture.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_sanitized_derivative_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_sanitized_ocr_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_sanitized_ocr_index_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_workstation_ocr_text_egress_boundary.py")],
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
    [sys.executable, str(ROOT / "tools" / "check_package_recipe_surface_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_package_recipe_step_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_cross_platform_identity_boundary.py")],
    [sys.executable, str(ROOT / "tools" / "check_derive_unit_contract.py")],
    [sys.executable, str(ROOT / "tools" / "check_fuzz_contract.py")],

    [sys.executable, str(ROOT / "tools" / "check_curated_references.py")],
    [sys.executable, str(ROOT / "tools" / "check_release_curated_references.py")],
    [sys.executable, str(ROOT / "tools" / "check_generated_docs.py")],
    [sys.executable, str(ROOT / "tools" / "check_generated_artifact_version_ids.py")],
    [sys.executable, str(ROOT / "tools" / "check_validation_logs_clean.py")],
    [sys.executable, str(ROOT / "tools" / "check_risk_register.py")],
    [sys.executable, str(ROOT / "tools" / "check_risk_register_heading_ids.py")],
    [sys.executable, str(ROOT / "tools" / "check_open_questions_decisions.py")],
    [sys.executable, str(ROOT / "tools" / "check_microvm_example_plan_digests.py")],
    [sys.executable, str(ROOT / "tools" / "check_microvm_receipt_reason_requirements.py")],
    [sys.executable, str(ROOT / "tools" / "check_microvm_reason_code_registry.py")],



    [sys.executable, str(ROOT / "tools" / "check_spec_example_coverage.py")],
    [sys.executable, str(ROOT / "tools" / "check_readme_latest_cut.py")],
    [sys.executable, str(ROOT / "tools" / "check_version.py")],
]



RELEASE_CRITICAL_STEMS = {
    "check_consistency",
    "check_schema_kind_matches_filename",
    "check_discovery",
    "check_meta_doc_discoverability",
    "check_changelog_format",
    "check_release_heading_uniqueness",
    "check_release_heading_order",
    "check_changelog_index_release_coverage",
    "check_index_front_matter_order",
    "check_doc_number_prefix_uniqueness",
    "check_markdown_h1_structure",
    "check_markdown_h2_heading_uniqueness",
    "check_markdown_inline_code_balance",
    "check_text_files_final_newline",
    "check_python_tool_executable_bits",
    "check_changelog_artifact_mentions",
    "check_hygiene_checkset_completeness",
    "check_frontdoor_budget",
    "check_canonical_json_digest_contract",
    "check_json_duplicate_key_rejection",
    "check_no_root_hygiene_log_dumps",
    "check_no_python_bytecode_artifacts",
    "check_cube_hygiene_run_ledger",
    "check_current_generated_surface_sync",
    "check_runtime_golden_thread",
    "check_removable_media_local_fallback_capsicum_worker_build",
    "check_removable_media_local_fallback_capsicum_worker_bridge",
    "check_removable_media_local_fallback_capsicum_worker_sha256_vectors",
    "check_removable_media_local_fallback_freebsd_host_smoke_runner",
    "check_removable_media_local_fallback_freebsd_host_proof_bundle",
    "check_removable_media_local_fallback_freebsd_host_proof_handoff",
    "check_removable_media_local_fallback_freebsd_host_proof_handoff_seal",
    "check_removable_media_local_fallback_freebsd_host_proof_sealed_importer",
    "check_removable_media_local_fallback_freebsd_host_proof_sealed_preflight",
    "check_removable_media_local_fallback_freebsd_host_proof_importer",
    "check_removable_media_local_fallback_freebsd_host_proof_import_audit",
    "check_removable_media_local_fallback_freebsd_host_proof_checked_import_gate",
    "check_removable_media_local_fallback_freebsd_host_proof_preflight",
    "check_removable_media_local_fallback_freebsd_host_proof_collect_import",
    "check_removable_media_local_fallback_freebsd_real_host_operator_packet",
    "check_removable_media_local_fallback_freebsd_host_proof_work_order",
    "check_freebsd_real_host_proof_theatre_gate",
    "check_removable_media_fd_slot_policy_consistency",
    "check_release_last_updated",
    "check_generated_docs",
    "check_generated_artifact_version_ids",
    "check_validation_logs_clean",
    "check_spec_example_coverage",
    "check_readme_latest_cut",
    "check_version",
}


def tool_name(cmd: list[str]) -> str:
    return Path(cmd[-1]).name


def profile_for_tool(name: str) -> str:
    stem = name[:-3] if name.endswith(".py") else name
    if name in {"lint_spec_schemas.py", "validate_spec_examples.py"} or stem in RELEASE_CRITICAL_STEMS:
        return "release-critical"
    if "post_detach" in name or "removable_media_local_fallback" in name or "removable_media_safe_capture" in name:
        return "post-detach"
    if stem.startswith("check_cube_") or stem in {"check_schema_kind_matches_filename"}:
        return "schema-cube-audit"
    if stem.startswith("check_doc_") or stem.startswith("check_markdown_") or stem in {
        "check_generated_docs",
        "check_discovery",
        "check_meta_doc_discoverability",
        "check_changelog_index_release_coverage",
        "check_spec_example_coverage",
    }:
        return "generated-surface"
    return "deep-contract"


def selected_checks(profile: str) -> list[list[str]]:
    if profile == "all":
        return CHECKS
    return [cmd for cmd in CHECKS if profile_for_tool(tool_name(cmd)) == profile]


def _sha256_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def _sha256_file(path: Path) -> str | None:
    try:
        return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _hygiene_wrapper_sha256() -> str | None:
    return _sha256_file(ROOT / "tools" / "hygiene.py")



def _iter_cube_input_files() -> list[Path]:
    """Return the deterministic source/evidence surface used to validate resume safety.

    Resume is meant to save cloudtainer work after an interruption, not to cache
    success across source, schema, example, fixture, tool, or documentation edits.
    The fingerprint deliberately excludes session-reviews and the canonical
    ledger example because ledger output would otherwise invalidate itself after
    every row.
    """
    paths: list[Path] = []
    for item in CUBE_INPUT_FINGERPRINT_ROOTS:
        root = ROOT / item
        if root.is_file():
            paths.append(root)
            continue
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT).as_posix()
            if rel in CUBE_INPUT_FINGERPRINT_EXCLUDED_RELPATHS:
                continue
            rel_parts = path.relative_to(ROOT).parts
            if any(part in CUBE_INPUT_FINGERPRINT_EXCLUDED_DIRS for part in rel_parts):
                continue
            if path.suffix in CUBE_INPUT_FINGERPRINT_EXCLUDED_SUFFIXES:
                continue
            paths.append(path)
    return sorted(paths, key=lambda p: p.relative_to(ROOT).as_posix())


def _runner_environment_scope() -> str:
    return "python-binary-version-platform-jsonschema"


def _python_executable_sha256(path: str | Path | None = None) -> str:
    """Hash interpreter bytes so equivalent launcher aliases share one identity."""
    executable = Path(path) if path is not None else Path(sys.executable)
    digest = hashlib.sha256()
    with executable.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _distribution_search_paths() -> list[str]:
    """Find package roots consistently even when the wrapper itself uses ``-S``."""
    import sysconfig

    candidates: set[Path] = set()
    for entry in sys.path:
        if entry:
            path = Path(entry)
            if path.name in {"site-packages", "dist-packages"}:
                candidates.add(path)
    for key in ("purelib", "platlib"):
        try:
            value = sysconfig.get_path(key)
        except (KeyError, TypeError):
            value = None
        if value:
            candidates.add(Path(value))

    # ``python -S`` suppresses virtual-environment prefix initialization on some
    # interpreters. Recover the venv package root from the launcher location
    # rather than allowing the proof fingerprint to change with the ``-S`` flag.
    executable_candidates = [Path(sys.executable)]
    try:
        executable_candidates.append(Path(sys.executable).resolve())
    except OSError:
        pass
    pyver = f"python{sys.version_info.major}.{sys.version_info.minor}"
    for executable in executable_candidates:
        for root in (executable.parent, executable.parent.parent):
            if not (root / "pyvenv.cfg").is_file():
                continue
            candidates.add(root / "lib" / pyver / "site-packages")
            candidates.add(root / "lib64" / pyver / "site-packages")

    return sorted(str(path) for path in candidates if path.is_dir())


def _installed_distribution_version(distribution_name: str) -> str:
    """Return an installed distribution version without depending on site import."""
    from importlib import metadata

    normalized = re.sub(r"[-_.]+", "-", distribution_name).lower()
    try:
        distributions = metadata.distributions(path=_distribution_search_paths())
        for distribution in distributions:
            observed_name = distribution.metadata.get("Name", "")
            if re.sub(r"[-_.]+", "-", observed_name).lower() == normalized:
                return distribution.version
    except Exception:  # noqa: BLE001
        pass
    return "unavailable"


def _runner_environment_material() -> dict[str, Any]:
    """Return the interpreter/package surface that makes resumed rows trustworthy.

    Checker source and cube input fingerprints catch repository edits, but a
    resumable ledger can also become stale when it is replayed under a different
    Python interpreter or jsonschema implementation. Bind resume evidence to the
    interpreter bytes rather than ``sys.executable`` so launcher aliases and the
    documented ``-S`` invocation do not invalidate otherwise identical proof.
    """
    import platform

    return {
        "python_executable_sha256": _python_executable_sha256(),
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "python_cache_tag": getattr(sys.implementation, "cache_tag", "unknown"),
        "platform_system": platform.system(),
        "platform_release": platform.release(),
        "platform_machine": platform.machine(),
        "jsonschema_version": _installed_distribution_version("jsonschema"),
    }


def _runner_environment_sha256() -> str:
    global _RUNNER_ENVIRONMENT_SHA256_CACHE
    if _RUNNER_ENVIRONMENT_SHA256_CACHE is None:
        material = json.dumps(_runner_environment_material(), sort_keys=True, separators=(",", ":"))
        _RUNNER_ENVIRONMENT_SHA256_CACHE = "sha256:" + hashlib.sha256(material.encode("utf-8")).hexdigest()
    return _RUNNER_ENVIRONMENT_SHA256_CACHE


def _cube_input_fingerprint_scope() -> str:
    return "source-docs-spec-tools-fixtures-no-session-reviews-or-ledger-output"


def _cube_input_fingerprint_pair() -> tuple[str, int]:
    global _CUBE_INPUT_FINGERPRINT_CACHE
    if _CUBE_INPUT_FINGERPRINT_CACHE is not None:
        return _CUBE_INPUT_FINGERPRINT_CACHE
    digest = hashlib.sha256()
    file_count = 0
    for path in _iter_cube_input_files():
        rel = path.relative_to(ROOT).as_posix()
        st = path.stat()
        mode = stat.S_IMODE(st.st_mode)
        content_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(mode).encode("ascii"))
        digest.update(b"\0")
        digest.update(content_digest.encode("ascii"))
        digest.update(b"\0")
        file_count += 1
    _CUBE_INPUT_FINGERPRINT_CACHE = ("sha256:" + digest.hexdigest(), file_count)
    return _CUBE_INPUT_FINGERPRINT_CACHE


def _cube_input_fingerprint_file_count() -> int:
    return _cube_input_fingerprint_pair()[1]


def _cube_input_sha256() -> str:
    return _cube_input_fingerprint_pair()[0]


def _line_count(value: str) -> int:
    if not value:
        return 0
    return value.count("\n") + (0 if value.endswith("\n") else 1)


def _version_id_token(version: str) -> str:
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})r(\d{3,})$", version)
    if not m:
        return version
    return f"{m.group(1)}{m.group(2)}{m.group(3)}-r{m.group(4)}"


def _top_version() -> str:
    import re

    changelog = ROOT / "CHANGELOG.md"
    text = changelog.read_text(encoding="utf-8", errors="replace") if changelog.exists() else ""
    match = re.search(r"^##\s+(\S+)\s*$", text, re.MULTILINE)
    return match.group(1) if match else "unknown"


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _run_budget_status(run_budget_seconds: float | None, run_started_perf: float | None, run_complete: bool, stopped_by_run_budget: bool) -> str:
    if run_budget_seconds is None:
        return "not-enforced"
    if stopped_by_run_budget:
        return "stopped-before-budget"
    if run_complete:
        return "completed-within-budget"
    if run_started_perf is not None and time.perf_counter() - run_started_perf >= run_budget_seconds:
        return "stopped-before-budget"
    return "within-budget"


def _check_budget_status(check_budget_limit: int | None, run_complete: bool, stopped_by_check_budget: bool) -> str:
    if check_budget_limit is None:
        return "not-enforced"
    if stopped_by_check_budget:
        return "stopped-before-check-budget"
    if run_complete:
        return "completed-within-check-budget"
    return "within-check-budget"


def _repo_arg(arg: str) -> str:
    if arg == sys.executable:
        return "python3"
    try:
        return Path(arg).resolve().relative_to(ROOT).as_posix()
    except Exception:  # noqa: BLE001
        return arg


def _child_max_rss_kib_best_effort() -> int | None:
    try:
        import resource
    except Exception:  # pragma: no cover - non-POSIX fallback
        return None
    try:
        return int(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
    except Exception:  # pragma: no cover
        return None



NO_SITE_PYTHON_CHECK_STEMS = {
    "check_consistency",
    "lint_spec_schemas",
    "check_schema_kind_matches_filename",
    "check_discovery",
    "check_meta_doc_discoverability",
    "check_changelog_format",
    "check_release_heading_uniqueness",
    "check_release_heading_order",
    "check_changelog_index_release_coverage",
    "check_index_front_matter_order",
    "check_doc_number_prefix_uniqueness",
    "check_markdown_h1_structure",
    "check_markdown_h2_heading_uniqueness",
    "check_markdown_inline_code_balance",
    "check_text_files_final_newline",
    "check_python_tool_executable_bits",
    "check_changelog_artifact_mentions",
    "check_hygiene_checkset_completeness",
    "check_frontdoor_budget",
    "check_canonical_json_digest_contract",
    "check_json_duplicate_key_rejection",
    "check_no_root_hygiene_log_dumps",
    "check_no_python_bytecode_artifacts",
    "check_release_last_updated",
    "check_removable_media_local_fallback_capsicum_worker_build",
    "check_removable_media_local_fallback_capsicum_worker_sha256_vectors",
    "check_removable_media_local_fallback_freebsd_host_smoke_runner",
    "check_removable_media_local_fallback_freebsd_host_proof_handoff",
    "check_removable_media_local_fallback_freebsd_host_proof_checked_import_gate",
    "check_removable_media_local_fallback_freebsd_host_proof_preflight",
    "check_removable_media_local_fallback_freebsd_host_proof_collect_import",
    "check_removable_media_local_fallback_freebsd_real_host_operator_packet",
    "check_removable_media_fd_slot_policy_consistency",
    "check_generated_docs",
    "check_generated_artifact_version_ids",
    "check_validation_logs_clean",
    "check_spec_example_coverage",
    "check_readme_latest_cut",
    "check_version",
}


def _should_disable_site_for_check(cmd: list[str]) -> bool:
    if not cmd or not Path(str(cmd[0])).name.startswith("python"):
        return False
    try:
        stem = Path(str(cmd[-1])).stem
    except Exception:  # noqa: BLE001
        return False
    return stem in NO_SITE_PYTHON_CHECK_STEMS


def child_env() -> dict[str, str]:
    """Run checks without emitting transient Python bytecode into the archive tree."""
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def child_cmd(cmd: list[str]) -> list[str]:
    """Invoke Python checks with bytecode disabled and skip site imports for pure stdlib checks.

    The release-critical wrapper can otherwise run a large parent plus a large
    child for simple checkers that do not need site packages.  `-S` keeps those
    children small while preserving normal site-package access for schema checks
    that need jsonschema.
    """
    actual = list(cmd)
    if actual and Path(actual[0]).name.startswith("python"):
        flags: list[str] = []
        if "-B" not in actual[1:3]:
            flags.append("-B")
        if _should_disable_site_for_check(cmd) and "-S" not in actual[1:4]:
            flags.append("-S")
        if flags:
            return [actual[0], *flags, *actual[1:]]
    return actual

def run(cmd: list[str]) -> int:
    actual_cmd = child_cmd(cmd)
    print(f"==> {' '.join(_repo_arg(str(part)) for part in actual_cmd)}", flush=True)
    p = subprocess.run(actual_cmd, cwd=ROOT, env=child_env())
    return int(p.returncode)


def _terminate_timed_out_process(proc: subprocess.Popen[Any], grace_seconds: float = 2.0) -> tuple[str, str]:
    """Terminate a timed-out checker and any descendants in its session.

    The ledger runner already avoids pipe-backed output capture, but a timed-out
    checker can still leave grandchildren running unless the wrapper owns a
    process boundary.  Start each check in a new session and kill the whole
    process group on timeout; fall back to the direct child only on platforms
    without process-group support.
    """
    if proc.poll() is not None:
        return "already-exited", "none"
    try:
        os.killpg(proc.pid, signal.SIGTERM)
        scope = "process-group"
    except Exception:  # noqa: BLE001
        proc.terminate()
        scope = "child-process"
    try:
        proc.wait(timeout=grace_seconds)
        return scope, "SIGTERM"
    except subprocess.TimeoutExpired:
        try:
            if scope == "process-group":
                os.killpg(proc.pid, signal.SIGKILL)
            else:
                proc.kill()
        except ProcessLookupError:
            pass
        try:
            proc.wait(timeout=grace_seconds)
            return scope, "SIGKILL"
        except subprocess.TimeoutExpired:
            # A wedged checker can become unkillable for a short window in a
            # constrained cloudtainer.  Do not let the ledger writer hang
            # forever while trying to reap it; record the cleanup ambiguity and
            # keep the partial ledger resumable.
            return scope, "SIGKILL-unreaped"


def run_for_ledger(cmd: list[str], timeout_seconds: float | None, selected_profile: str) -> dict[str, Any]:
    name = tool_name(cmd)
    started_at_utc = _utc_now()
    started = time.perf_counter()
    timed_out = False
    stdout = ""
    stderr = ""
    return_code = 0
    timeout_kill_scope = "not-needed"
    timeout_termination_signal: str | None = None
    timeout_grace_seconds: float | None = None
    process_group_isolated = True
    max_rss_before = _child_max_rss_kib_best_effort()

    actual_cmd = child_cmd(cmd)
    print(f"==> {' '.join(_repo_arg(str(part)) for part in actual_cmd)}", flush=True)
    # Spool child output to files instead of subprocess.PIPE.  A few checks run
    # nested probes; if a grandchild inherits a pipe fd, communicate() can wait
    # for EOF after the checked process has exited.  File-backed capture still
    # gives stable stdout/stderr digests without making the ledger writer depend
    # on pipe EOF from every descendant.  Each child is launched in its own
    # session so timeout cleanup can kill the complete process group instead of
    # leaking a checker grandchild in constrained cloudtainers.
    with tempfile.TemporaryDirectory(prefix="derivebsd-hygiene-output-") as td:
        stdout_path = Path(td) / "stdout"
        stderr_path = Path(td) / "stderr"
        with stdout_path.open("wb") as out_fh, stderr_path.open("wb") as err_fh:
            proc = subprocess.Popen(
                actual_cmd,
                cwd=ROOT,
                stdout=out_fh,
                stderr=err_fh,
                env=child_env(),
                start_new_session=True,
            )
            try:
                return_code = int(proc.wait(timeout=timeout_seconds))
            except subprocess.TimeoutExpired:
                timed_out = True
                return_code = 124
                timeout_grace_seconds = 2.0
                timeout_kill_scope, timeout_termination_signal = _terminate_timed_out_process(proc, timeout_grace_seconds)
                with stderr_path.open("ab") as err_fh2:
                    prefix = b"\n" if stderr_path.exists() and stderr_path.stat().st_size else b""
                    detail = (
                        f"TIMEOUT after {timeout_seconds} seconds; "
                        f"timeout_kill_scope={timeout_kill_scope}; "
                        f"timeout_termination_signal={timeout_termination_signal}"
                    )
                    err_fh2.write(prefix + detail.encode("utf-8"))
        stdout = stdout_path.read_bytes().decode("utf-8", errors="replace") if stdout_path.exists() else ""
        stderr = stderr_path.read_bytes().decode("utf-8", errors="replace") if stderr_path.exists() else ""

    elapsed = time.perf_counter() - started
    max_rss_after = _child_max_rss_kib_best_effort()
    cube_input_sha256 = _cube_input_sha256()
    cube_input_file_count = _cube_input_fingerprint_file_count()
    cube_input_scope = _cube_input_fingerprint_scope()
    status = "timed-out" if timed_out else ("passed" if return_code == 0 else "failed")
    terminated_by_signal = return_code < 0 and not timed_out
    signal_name = None
    if terminated_by_signal:
        try:
            signal_name = signal.Signals(-return_code).name
        except Exception:  # noqa: BLE001
            signal_name = f"SIGNAL_{-return_code}"
    failure_class = (
        "timed-out"
        if timed_out
        else ("terminated-by-signal" if terminated_by_signal else ("none" if return_code == 0 else "exit-nonzero"))
    )
    print(f"    {status} elapsed={elapsed:.3f}s rc={return_code}", flush=True)

    return {
        "tool": name,
        "profile": profile_for_tool(name),
        "selected_profile": selected_profile,
        "command": [_repo_arg(str(part)) for part in actual_cmd],
        "tool_sha256": _sha256_file(Path(cmd[-1])),
        "cube_input_sha256": cube_input_sha256,
        "cube_input_fingerprint_scope": cube_input_scope,
        "cube_input_file_count": cube_input_file_count,
        "runner_environment_sha256": _runner_environment_sha256(),
        "runner_environment_scope": _runner_environment_scope(),
        "status": status,
        "return_code": return_code,
        "failure_class": failure_class,
        "terminated_by_signal": terminated_by_signal,
        "signal_name": signal_name,
        "timed_out": timed_out,
        "timeout_seconds": timeout_seconds,
        "timeout_status": "timed-out" if timed_out else ("completed" if timeout_seconds is not None else "not-enforced"),
        "process_group_isolated": process_group_isolated,
        "timeout_kill_scope": timeout_kill_scope,
        "timeout_termination_signal": timeout_termination_signal,
        "timeout_grace_seconds": timeout_grace_seconds,
        "started_at_utc": started_at_utc,
        "finished_at_utc": _utc_now(),
        "elapsed_seconds": round(elapsed, 6),
        "stdout_sha256": _sha256_text(stdout),
        "stdout_bytes": len(stdout.encode("utf-8", errors="replace")),
        "stdout_lines": _line_count(stdout),
        "stderr_sha256": _sha256_text(stderr),
        "stderr_bytes": len(stderr.encode("utf-8", errors="replace")),
        "stderr_lines": _line_count(stderr),
        "child_max_rss_kib_best_effort": max_rss_after,
        "child_max_rss_kib_scope": "process-cumulative-children-high-water" if max_rss_after is not None else "unavailable",
        "child_max_rss_kib_before": max_rss_before,
    }



def _release_token(version: str) -> str:
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})r(\d+)$", version)
    if not m:
        return version
    return f"{m.group(1)}{m.group(2)}{m.group(3)}-r{m.group(4)}"

def _current_command_for_row(cmd: list[str]) -> list[str]:
    return [_repo_arg(str(part)) for part in child_cmd(cmd)]


def _row_matches_current_check(row: dict[str, Any], cmd: list[str], profile: str) -> bool:
    """Return true only when a passed row still matches the current checker.

    Earlier rev0513 work exposed a dangerous resume footgun: a passed row could
    be reused after the checker source changed, hiding a newly broken checker.
    The ledger now binds each row to the checker file digest and current command
    shape, so resume is a convenience rather than a stale-evidence cache.
    """
    if row.get("status") != "passed" or row.get("selected_profile") != profile:
        return False
    if row.get("tool") != tool_name(cmd):
        return False
    if row.get("command") != _current_command_for_row(cmd):
        return False
    current_digest = _sha256_file(Path(cmd[-1]))
    if not (isinstance(current_digest, str) and row.get("tool_sha256") == current_digest):
        return False
    return (
        row.get("cube_input_sha256") == _cube_input_sha256()
        and row.get("cube_input_fingerprint_scope") == _cube_input_fingerprint_scope()
        and row.get("cube_input_file_count") == _cube_input_fingerprint_file_count()
        and row.get("runner_environment_sha256") == _runner_environment_sha256()
        and row.get("runner_environment_scope") == _runner_environment_scope()
    )


def _ledger_wrapper_digest_matches(data: dict[str, Any]) -> bool:
    current = _hygiene_wrapper_sha256()
    return isinstance(current, str) and data.get("hygiene_wrapper_sha256") == current


def _ledger_cube_input_matches(data: dict[str, Any]) -> bool:
    current = _cube_input_sha256()
    return (
        isinstance(current, str)
        and data.get("cube_input_sha256") == current
        and data.get("cube_input_fingerprint_scope") == _cube_input_fingerprint_scope()
        and data.get("cube_input_file_count") == _cube_input_fingerprint_file_count()
    )


def _ledger_runner_environment_matches(data: dict[str, Any]) -> bool:
    return (
        data.get("runner_environment_sha256") == _runner_environment_sha256()
        and data.get("runner_environment_scope") == _runner_environment_scope()
    )


def _expected_ledger_id(profile: str) -> str:
    version = _top_version()
    return f"cube-hygiene-run-ledger-{_version_id_token(version)}-{profile}"


def _ledger_release_metadata_matches(data: dict[str, Any], profile: str) -> bool:
    """Return true only for ledgers generated for the current top release.

    Checker digests alone are not enough: rev0515 found that a prior-release
    green ledger could be merged forward when checker bytes happened not to
    change.  Resume must be same-release convenience, not cross-release evidence
    reuse.
    """
    return data.get("generated_for_version") == _top_version() and data.get("ledger_id") == _expected_ledger_id(profile)


def resume_records(path: Path, profile: str, checks: list[list[str]]) -> tuple[list[dict[str, Any]], str | None]:
    """Load still-current passed rows from an existing ledger.

    Only passed rows for the same selected profile, same command shape, same
    checker-file digest, and same hygiene-wrapper digest are reused.
    Failed/timed-out rows and stale passed rows are deliberately rerun. The
    returned records are ordered according to the current selected check list,
    so a resumed ledger remains directly comparable to a fresh run.
    """
    if not path.exists():
        return [], None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return [], None
    if data.get("kind") != "cube.hygiene.run.ledger" or data.get("selected_profile") != profile:
        return [], None
    if not _ledger_wrapper_digest_matches(data):
        return [], None
    if not _ledger_cube_input_matches(data):
        return [], None
    if not _ledger_runner_environment_matches(data):
        return [], None
    if not _ledger_release_metadata_matches(data, profile):
        return [], None
    rows_by_tool: dict[str, dict[str, Any]] = {}
    for row in data.get("results", []):
        if isinstance(row, dict) and isinstance(row.get("tool"), str):
            rows_by_tool[row["tool"]] = row
    ordered: list[dict[str, Any]] = []
    for cmd in checks:
        row = rows_by_tool.get(tool_name(cmd))
        if row is not None and _row_matches_current_check(row, cmd, profile):
            ordered.append(row)
    started_at = data.get("started_at_utc") if isinstance(data.get("started_at_utc"), str) else None
    return ordered, started_at


def merge_existing_passed_rows(
    path: Path,
    profile: str,
    checks: list[list[str]],
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Preserve only still-current passed rows when rewriting a ledger.

    This keeps the partial-ledger robustness from rev0504+ while avoiding stale
    checker or wrapper evidence: an existing passed row is retained only if the
    ledger wrapper digest, command, and checker source digest still match the
    current check list.
    """
    current_by_tool: dict[str, dict[str, Any]] = {}
    for row in records:
        tool = row.get("tool")
        if isinstance(tool, str):
            current_by_tool[tool] = row

    existing_passed_by_tool: dict[str, dict[str, Any]] = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            data = {}
        if (
            data.get("kind") == "cube.hygiene.run.ledger"
            and data.get("selected_profile") == profile
            and _ledger_wrapper_digest_matches(data)
            and _ledger_cube_input_matches(data)
            and _ledger_runner_environment_matches(data)
            and _ledger_release_metadata_matches(data, profile)
        ):
            rows_by_tool = {
                row["tool"]: row
                for row in data.get("results", [])
                if isinstance(row, dict) and isinstance(row.get("tool"), str)
            }
            for cmd in checks:
                row = rows_by_tool.get(tool_name(cmd))
                if row is not None and _row_matches_current_check(row, cmd, profile):
                    existing_passed_by_tool[row["tool"]] = row

    merged: list[dict[str, Any]] = []
    seen: set[str] = set()
    for cmd in checks:
        tool = tool_name(cmd)
        row = current_by_tool.get(tool) or existing_passed_by_tool.get(tool)
        if row is not None:
            merged.append(row)
            seen.add(tool)
    for row in records:
        tool = row.get("tool")
        if not isinstance(tool, str) or tool not in seen:
            merged.append(row)
    return merged

def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(text)
            tmp.flush()
            os.fsync(tmp.fileno())
        tmp_path.replace(path)
        try:
            dir_fd = os.open(path.parent, os.O_RDONLY)
        except OSError:
            return
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        if tmp_path is not None and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass



def _ledger_exit_code(records: list[dict[str, Any]], planned_checks_total: int) -> int:
    """Return the wrapper process exit code for a ledger-mode invocation.

    Budgeted chunks are useful only if callers cannot confuse them with a full
    green profile.  A completed all-passing ledger returns 0; any failed or
    timed-out checker returns 1; an otherwise clean partial ledger returns 2.
    """
    if any(row.get("status") in {"failed", "timed-out"} for row in records):
        return 1
    if len(records) != planned_checks_total:
        return LEDGER_PARTIAL_EXIT_CODE
    return 0

def write_ledger(
    path: Path,
    profile: str,
    timeout_seconds: float | None,
    records: list[dict[str, Any]],
    started_at_utc: str,
    planned_checks_total: int,
    checks: list[list[str]],
    *,
    preserve_existing_passed: bool = False,
    run_budget_seconds: float | None = None,
    run_started_perf: float | None = None,
    stopped_by_run_budget: bool = False,
    check_budget_limit: int | None = None,
    stopped_by_check_budget: bool = False,
) -> None:
    if preserve_existing_passed:
        records = merge_existing_passed_rows(path, profile, checks, records)
    counts = {
        "passed": sum(1 for r in records if r["status"] == "passed"),
        "failed": sum(1 for r in records if r["status"] == "failed"),
        "timed_out": sum(1 for r in records if r["status"] == "timed-out"),
    }
    version = _top_version()
    token = _version_id_token(version)
    checks_completed = len(records)
    run_complete = checks_completed == planned_checks_total
    run_budget_status = _run_budget_status(run_budget_seconds, run_started_perf, run_complete, stopped_by_run_budget)
    check_budget_status = _check_budget_status(check_budget_limit, run_complete, stopped_by_check_budget)
    payload = {
        "kind": "cube.hygiene.run.ledger",
        "schema_version": "1.0",
        "ledger_id": f"cube-hygiene-run-ledger-{token}-{profile}",
        "generated_for_version": version,
        "hygiene_wrapper": "tools/hygiene.py",
        "hygiene_wrapper_sha256": _hygiene_wrapper_sha256(),
        "cube_input_sha256": _cube_input_sha256(),
        "cube_input_fingerprint_scope": _cube_input_fingerprint_scope(),
        "cube_input_file_count": _cube_input_fingerprint_file_count(),
        "runner_environment_sha256": _runner_environment_sha256(),
        "runner_environment_scope": _runner_environment_scope(),
        "selected_profile": profile,
        "timeout_seconds": timeout_seconds,
        "run_budget_seconds": run_budget_seconds,
        "run_budget_status": run_budget_status,
        "check_budget_limit": check_budget_limit,
        "check_budget_status": check_budget_status,
        "started_at_utc": started_at_utc,
        "finished_at_utc": _utc_now(),
        "result": "passed" if run_complete and counts["failed"] == 0 and counts["timed_out"] == 0 else "failed",
        "checks_total": planned_checks_total,
        "checks_completed": checks_completed,
        "run_complete": run_complete,
        "counts": counts,
        "results": records,
    }
    atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--profile",
        choices=["all", "release-critical", "post-detach", "generated-surface", "schema-cube-audit", "deep-contract"],
        default="all",
        help="run a typed hygiene shard instead of the full wrapper",
    )
    ap.add_argument(
        "--ledger-json",
        "--ledger",
        dest="ledger_json",
        metavar="PATH",
        help="write a machine-readable run ledger with per-check status, elapsed time, output digests, and timeout state",
    )
    ap.add_argument(
        "--timeout-seconds",
        "--check-timeout-seconds",
        dest="timeout_seconds",
        type=float,
        default=None,
        help="per-check timeout used only while writing a ledger",
    )
    ap.add_argument(
        "--resume-ledger",
        action="store_true",
        help="when --ledger-json exists, keep passed rows for this profile and run only missing/failed/timed-out checks",
    )
    ap.add_argument(
        "--max-checks",
        type=int,
        default=None,
        help="ledger mode only: run at most this many not-yet-passed checks, then write a resumable partial ledger with check_budget_status",
    )
    ap.add_argument(
        "--max-run-seconds",
        type=float,
        default=None,
        help="ledger mode only: stop cleanly between checks after this many wrapper seconds so outer cloudtainer limits leave a resumable ledger",
    )
    args = ap.parse_args()

    rc = 0
    checks = selected_checks(args.profile)
    print(f"hygiene profile: {args.profile} ({len(checks)} checks)", flush=True)

    if args.ledger_json:
        ledger_path = Path(args.ledger_json)
        if args.resume_ledger:
            records, resumed_started_at = resume_records(ledger_path, args.profile, checks)
        else:
            records, resumed_started_at = [], None
        started_at = resumed_started_at or datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        run_started_perf = time.perf_counter()
        stopped_by_run_budget = False
        stopped_by_check_budget = False
        completed_tools = {str(row.get("tool")) for row in records if row.get("status") == "passed"}
        if records:
            print(f"resuming hygiene ledger with {len(records)} passed rows from {args.ledger_json}", flush=True)
        # Write a current-release partial ledger before the first child check.
        # This prevents --max-checks 0 or early interruption from leaving a stale
        # previous-release canonical ledger at the requested path.
        write_ledger(
            ledger_path,
            args.profile,
            args.timeout_seconds,
            records,
            started_at,
            len(checks),
            checks,
            preserve_existing_passed=args.resume_ledger,
            run_budget_seconds=args.max_run_seconds,
            run_started_perf=run_started_perf,
            stopped_by_run_budget=stopped_by_run_budget,
            check_budget_limit=args.max_checks,
            stopped_by_check_budget=stopped_by_check_budget,
        )
        executed_this_invocation = 0
        for cmd in checks:
            if tool_name(cmd) in completed_tools:
                print(f"==> {_repo_arg(str(cmd[-1]))} (resume: already passed)", flush=True)
                continue
            if args.max_run_seconds is not None and time.perf_counter() - run_started_perf >= args.max_run_seconds:
                stopped_by_run_budget = True
                print(f"ledger run budget reached after {executed_this_invocation} new checks; resume with --resume-ledger", flush=True)
                break
            if args.max_checks is not None and executed_this_invocation >= args.max_checks:
                stopped_by_check_budget = True
                print(f"ledger chunk limit reached after {executed_this_invocation} new checks; resume with --resume-ledger", flush=True)
                break
            record = run_for_ledger(cmd, args.timeout_seconds, args.profile)
            records.append(record)
            executed_this_invocation += 1
            if record["status"] != "passed":
                rc = 1
            # Rewrite after every check so an outer cloudtainer/CI timeout still
            # leaves partial structured evidence instead of only scrollback.
            write_ledger(
                ledger_path,
                args.profile,
                args.timeout_seconds,
                records,
                started_at,
                len(checks),
                checks,
                preserve_existing_passed=args.resume_ledger,
                run_budget_seconds=args.max_run_seconds,
                run_started_perf=run_started_perf,
                stopped_by_run_budget=stopped_by_run_budget,
                check_budget_limit=args.max_checks,
                stopped_by_check_budget=stopped_by_check_budget,
            )
        if stopped_by_run_budget or stopped_by_check_budget:
            write_ledger(
                ledger_path,
                args.profile,
                args.timeout_seconds,
                records,
                started_at,
                len(checks),
                checks,
                preserve_existing_passed=args.resume_ledger,
                run_budget_seconds=args.max_run_seconds,
                run_started_perf=run_started_perf,
                stopped_by_run_budget=stopped_by_run_budget,
                check_budget_limit=args.max_checks,
                stopped_by_check_budget=stopped_by_check_budget,
            )
        rc = _ledger_exit_code(records, len(checks))
        if rc == LEDGER_PARTIAL_EXIT_CODE:
            print("ledger run incomplete; returning 2 so partial evidence is not mistaken for a completed pass", flush=True)
        print(f"wrote hygiene ledger: {args.ledger_json}", flush=True)
        return rc

    for cmd in checks:
        r = run(cmd)
        if r != 0:
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

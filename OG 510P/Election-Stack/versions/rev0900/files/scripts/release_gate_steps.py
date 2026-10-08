#!/usr/bin/env python3
"""Canonical release-gate child-step inventory.

Keep the ordered child-step names here so the runner, doc-coverage
checker, and inventory self-check do not maintain parallel copies. The
final MANIFEST.sha256 step remains separate because it may be a check or
a write depending on the release-gate CLI flags.
"""

from __future__ import annotations

import sys
from pathlib import Path


CHECK_STEP_NAMES: tuple[str, ...] = (
    'gen_artifact_index.py',
    'check_index.py',
    'check_doc_number_collisions.py',
    'check_tracks.py',
    'check_adr_index.py',
    'gen_track_bundles.py',
    'gen_tombstone_index.py',
    'check_no_tombstone_refs.py',
    'gen_example_packets_index.py',
    'gen_external_sources_index.py',
    'check_doc_links.py',
    'check_doc_backtick_refs.py',
    'check_no_raw_urls_modern_docs.py',
    'check_no_forbidden_example_tlds.py',
    'check_no_cache_artifacts.py',
    'check_no_symlinks.py',
    'check_release_path_policy.py',
    'check_release_control_files.py',
    'check_release_builder_filesystem_policy.py',
    'check_manifest_verifier.py',
    'check_release_packaging_alignment.py',
    'check_release_zip_verifier.py',
    'check_release_safe_extractor.py',
    'check_release_zip_rebuild_from_extract.py',
    'check_tool_maturity_registry.py',
    'check_registries_readme.py',
    'check_registry_csv_integrity.py',
    'check_component_maturity.py',
    'check_pilot_readiness.py',
    'check_example_county_output_pack.py',
    'check_cdf_export_replay.py',
    'check_cdf_independent_replay_verifier.py',
    'check_ballot_accounting_reconciler.py',
    'check_election_event_log_reconciler.py',
    'check_mission_kernel_closeout_pack.py',
    'check_mission_kernel_live_workqueue.py',
    'check_mission_kernel_live_evidence_intake.py',
    'check_mission_kernel_evidence_submitter.py',
    'check_mission_kernel_full_drill_replay.py',
    'check_trust_recovery_playbook.py',
    'check_trust_recovery_output_pack.py',
    'check_human_review_handoff_playbook.py',
    'check_evidence_retention_disposition.py',
    'check_scenario_recovery_crosswalk.py',
    'check_human_review_output_pack.py',
    'check_evaluator_scoring_rubric.py',
    'check_synthetic_certification_boundaries.py',
    'check_example_county_evaluator_scorecard.py',
    'check_negative_control_fixtures.py',
    'check_release_maintainer_handoff.py',
    'check_release_go_no_go_pack.py',
    'check_local_pilot_intake_pack.py',
    'check_redaction_publication_pack.py',
    'check_accessibility_language_pack.py',
    'check_evidence_custody_provenance_pack.py',
    'check_independent_review_conflict_pack.py',
    'check_prep_evidence_ledgers.py',
    'check_pilot_operational_invariants.py',
    'check_envelope_kinds.py',
    'check_doc_envelope_kind_references.py',
    'check_envelope_payload_schemas.py',
    'check_attachment_requirements.py',
    'check_attachment_registry_integrity.py',
    'check_example_packets.py',
    'check_example_packets_public_artifact_lint.py',
    'check_no_hedging_in_public_templates.py',
    'check_example_packet_readmes.py',
    'check_example_payloads_against_schemas.py',
    'check_core_example_coverage.py',
    'check_example_ordering_conventions.py',
    'check_example_report_pins.py',
    'check_operator_smoke_coverage.py',
    'check_operator_tools_smoke.py',
    'check_measurement_tool_boundaries.py',
    'check_public_surface_pins_coverage.py',
    'check_packet_paths.py',
    'check_object_uri_alignment.py',
    'check_receipt_profiles.py',
    'check_publication_triggers.py',
    'check_election_milestones_registry.py',
    'check_drill_scenarios.py',
    'check_known_issues_registry.py',
    'check_catastrophe_classes_registry.py',
    'check_hazard_catastrophe_classes.py',
    'check_official_channels_registry.py',
    'check_discovery_pointer_coherence.py',
    'check_public_notice_type_coherence.py',
    'check_proof_obligations.py',
    'check_tombstones.py',
    'check_no_private_keys.py',
    'check_jcs_vectors.py',
    'check_observer_kit_jcs_mirror.py',
    'check_results_hash_vectors.py',
    'check_compact_context_vectors.py',
    'check_envelope_vectors.py',
    'check_version_consistency.py',
    'check_current_revision_fixture_sweep.py',
    'check_release_gate_doc_coverage.py',
    'check_release_gate_step_inventory.py',
    'check_release_gate_single_instance_lock.py',
    'check_platform_media_companion_tags.py',
    'check_recent_changelog_version_sequence.py',
    'check_voter_facing_surface_anchor_lock_coverage.py',
    'check_voter_facing_surface_structure_minimums.py',
    'gen_evidence_object_catalog.py',
    'check_verifier_problem_codes_registry.py',
    'check_surface_anomaly_codes_registry.py',
    'check_verifier_profiles_registry.py',
    'gen_verifier_profiles.py',
    'gen_verifier_problem_codes.py',
    'gen_surface_anomaly_codes.py',
    'check_packet_verification_report_linkage.py',
    'check_packet_verification_report_emit_packet.py',
    'check_signature_verifier_ed25519.py',
    'check_public_fingerprint_tool_safety.py',
    'check_publication_receipt_channel_digests.py',
    'check_retrievable_history_compaction.py',
    'check_size_budget.py',
    'validate_schemas.py',
    'gen_schema_catalog.py',
    'gen_public_surface_index.py',
    'check_voter_facing_public_answer_surfaces.py',
    'check_voter_facing_surface_triplets.py',
    'check_voter_facing_surface_range_references.py',
    'check_voter_facing_surface_entrypoint_coverage.py',
    'check_voter_facing_special_case_authority_minimums.py',
    'check_voter_facing_special_case_release_freshness.py',
    'check_voter_facing_special_case_direct_jurisdiction_anchors.py',
    'check_voter_facing_special_case_contactability.py',
    'check_voter_facing_special_case_responsible_office_specificity.py',
    'check_voter_facing_special_case_secure_channel_and_minimum_disclosure.py',
    'check_voter_facing_special_case_operability_now.py',
    'check_voter_facing_special_case_triplet_propagation.py',
    'check_voter_facing_special_case_freshness_current_state_conflict_propagation.py',
    'check_voter_facing_special_case_control_stack_reference_closure.py',
    'check_voter_facing_special_case_overview_stack_inheritance.py',
    'check_voter_facing_special_case_payload_review_window.py',
    'check_voter_facing_special_case_boundary_portability_checklists.py',
    'check_voter_facing_special_case_surface_doc_current_stack_pointer.py',
    'check_voter_facing_special_case_current_stack_range_labels.py',
    'check_voter_facing_special_case_official_routing_precedence.py',
    'check_voter_facing_special_case_current_state_visibility.py',
    'check_voter_facing_special_case_unresolved_conflict_stop.py',
    'check_voter_facing_special_case_nonoverlap.py',
    'check_voter_facing_special_case_fallback_escalation.py',
    'check_voter_facing_special_case_temporal_volatility.py',
    'check_recent_backticked_lockfile_citations.py',
    'check_external_sources_lockfile.py',
    'check_source_byte_receipt_pack.py',
    'check_source_byte_workpack_common.py',
    'check_source_byte_acquisition_queue.py',
    'check_source_byte_cache_batch_ingest.py',
    'check_source_byte_cache_intake_manifest.py',
    'check_source_byte_cache_batch_manifests.py',
    'check_source_byte_cache_batch_resume.py',
    'check_source_byte_cache_batch_status.py',
    'check_source_byte_batch_fetcher.py',
    'check_source_byte_batch_followup.py',
    'check_source_byte_batch_host_slices.py',
    'check_source_byte_dns_preflight.py',
    'check_source_byte_batch_attempt_workpacks.py',
    'check_source_byte_operator_workplan.py',
    'check_current_authority_review_cliff.py',
    'check_current_authority_report_consistency.py',
    'check_state_local_xref_quarantine.py',
    'check_adopter_authority_capture_pack.py',
    'check_adopter_capture_record_validator.py',
    'check_quarantined_source_public_surface_firewall.py',
    'check_track_a_pinned_sources.py',
    'check_unused_sources.py',
    'verify_external_sources_lock.py',
    'validate_artifact_refs.py',
)

MANIFEST_STEP_NAME = "build_manifest.py"


def step_path(root: Path, name: str) -> Path:
    """Return the absolute path for a release-gate child script name."""

    return root / "scripts" / name


def build_check_steps(root: Path, py: str | None = None) -> list[list[str]]:
    """Return subprocess commands for the ordered child checks."""

    python = py or sys.executable
    return [[python, str(step_path(root, name))] for name in CHECK_STEP_NAMES]


def build_manifest_step(root: Path, py: str | None = None, *, check: bool = True) -> list[str]:
    """Return the final manifest command; append --check unless writing."""

    python = py or sys.executable
    cmd = [python, str(step_path(root, MANIFEST_STEP_NAME))]
    if check:
        cmd.append("--check")
    return cmd

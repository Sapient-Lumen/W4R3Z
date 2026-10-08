# Crate Upgrade Pack Kit fixtures

This fixture pack freezes a first artifact vocabulary for **P-0514 Crate Upgrade Pack Kit**.

Artifacts:
- `upgrade-pack.schema.json`
- `upgrade-hazards.report.schema.json`
- `fixup-hints.receipt.schema.json`
- `migration-recipe.manifest.schema.json`
- `upgrade-check.report.schema.json`
- `upgrade-diff.report.schema.json`
- `hazard-class.policy.schema.json`
- `fixup-capability.receipt.schema.json`
- `lane-fidelity.report.schema.json`
- `hazard-authority.receipt.schema.json`
- `package-scope.report.schema.json`
- `source-lineage.receipt.schema.json`
- `hazard-arbitration.report.schema.json`
- `followthrough-state.report.schema.json`
- `import.receipt.schema.json`
- `fixup-posture.report.schema.json`
- `source-heads.report.schema.json`
- `pack-readiness.report.schema.json`
- `review-queue.report.schema.json`
- `cross-register-consistency.report.schema.json`
- `export-posture.report.schema.json`
- `publication-surface.manifest.schema.json`
- `redaction.receipt.schema.json`
- `deviation-ledger.receipt.schema.json`
- `warning-register.report.schema.json`
- `revalidation-window.policy.schema.json`
- `freshness-state.report.schema.json`
- `summary-claim.register.schema.json`
- `capture-context.receipt.schema.json`
- `baseline-state.receipt.schema.json`
- `coverage-matrix.report.schema.json`
- `lane-selection.receipt.schema.json`
- `config-basis.receipt.schema.json`
- `public-trace-path.report.schema.json`
- `durable-cue.report.schema.json`
- `review-provenance.report.schema.json`
- `session-honesty.report.schema.json`
- `replay-bridge.receipt.schema.json`
- `surface-authorship.report.schema.json`
- `omission-register.report.schema.json`

Scenario families:
- `renamed_api_fixup/`
- `feature_policy_shift/`
- `config_runtime_profile_shift/`
- `machine_fix_applies_but_manifest_feature_rename_remains/`
- `semver_green_but_behavior_review_required/`
- `workspace_recipe_checks_lib_lane_not_binary_lane/`

- `release_plz_semver_green_but_workspace_upgrade_lane_still_partial/`
- `source_fix_observed_but_manifest_docs_and_feature_recipe_remain/`
- `feature_flag_shift_is_upgrade_hazard_even_when_api_diff_is_green/`

- `github_release_note_imported_without_exact_tag_or_bytes_pin/`
- `semver_green_but_feature_policy_and_behavior_witness_still_conflict/`
- `docs_followthrough_completed_for_old_lane_but_rerequested_for_new_lane/`

- `cargo_semver_json_imported_but_summary_only_for_release_notes/`
- `cargo_fix_source_edits_observed_but_manifest_and_docs_followthrough_need_approval/`

- `latest_migration_guide_head_is_operational_but_not_citation_ready/`
- `pack_has_floating_import_conflict_and_active_docs_step_so_hold_not_freeze_ready/`
- `hold_pack_maps_to_explicit_review_queue_actions/`
- `freeze_ready_claim_fails_cross_register_consistency/`

- `private_workspace_pack_requires_redaction_before_public_export/`
- `public_redaction_receipt_allows_candidate_export/`
- `redaction_applied_without_receipt_fails_consistency/`
- `public_frozen_pack_exports_summary_and_exact_receipts_only/`
- `freeze_gap_temporarily_allowed_under_expiring_public_deviation/`
- `public_warning_register_tracks_blockers_and_deviation_links/`
- `material_change_triggers_define_revalidation_window/`
- `newer_revalidated_pack_supersedes_older_public_summary/`
- `public_summary_claims_trace_to_exact_receipts/`
- `mixed_synthesis_summary_claim_requires_fallback_and_warning_link/`
- `required_feature_bin_and_default_lib_are_distinct_matrix_cells/`
- `cargo_fix_import_claims_only_exact_feature_target_capture_context/`
- `published_extract_keeps_release_pair_baseline_exact/`
- `dirty_workspace_baseline_blocks_release_pair_claim/`
- `workspace_root_default_members_make_lane_selection_receipt_nonoptional/`
- `explicit_package_selection_overrides_workspace_defaults/`
- `workspace_patch_override_requires_config_basis_receipt/`
- `cargo_home_source_replacement_without_config_basis_fails_consistency/`
- `public_claim_routes_resolve_to_exported_receipts/`
- `public_trace_path_keeps_typed_fragment_miss_visible/`
- `blocking_public_warning_requires_durable_summary_cue/`
- `superseded_public_pack_keeps_replacement_cue_visible/`
- `independent_checker_closes_frozen_public_review_surface/`
- `same_author_self_review_blocks_freeze_without_explicit_deviation/`

- `same_lane_imports_share_single_session_family/`
- `mixed_session_synthesis_requires_warning_and_summary_disclosure/`
- `future_incompat_report_replayed_from_native_id_not_copied_attachment/`
- `native_storage_replay_claim_without_bridge_fails_consistency/`

- `semver_report_migration_guide_and_summary_stay_in_distinct_authorship_buckets/`
- `summary_native_import_claim_fails_authorship_consistency/`
- `public_summary_omits_local_only_context_but_register_keeps_exclusion_honest/`
- `blocking_known_hazard_left_out_of_public_summary_fails_omission_consistency/`

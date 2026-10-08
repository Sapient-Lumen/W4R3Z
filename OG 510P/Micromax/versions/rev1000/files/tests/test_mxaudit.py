from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_mxaudit_module():
    spec = importlib.util.spec_from_file_location(
        "micromax_test_mxaudit", ROOT / "tools" / "mxaudit.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mxaudit_json_reports_repeatable_structural_signals() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "mxaudit.py"), "--json", "--check", "--limit", "5"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    payload = json.loads(proc.stdout)

    assert payload["schema"] == "micromax.audit-metrics.v1"
    assert payload["project"] == "micromax"
    assert payload["rev"] > 0
    assert payload["checks"] == {"errors": [], "ok": True}

    assert payload["inventory"]["docs"]["files"] > 0
    assert payload["inventory"]["source"]["files"] > 0
    assert payload["inventory"]["tests"]["files"] > 0
    assert len(payload["python"]["top_files"]) == 5
    assert payload["python"]["parse_failures"] == []

    editor = payload["editor"]
    assert editor["found"] is True
    assert editor["path"] == "src/micromax_editor/editor.py"
    assert editor["method_count"] > 0
    assert editor["init_state_attributes"] > 0

    editor_trust = payload["editor_trust"]
    assert editor_trust["state_bound_discard_guard_present"] is True
    assert editor_trust["legacy_mutable_discard_flags_absent"] is True
    assert editor_trust["discard_commands_share_guard"] is True
    assert editor_trust["same_name_replacement_identity_present"] is True
    assert editor_trust["shared_initial_buffer_boundary_present"] is True
    assert editor_trust["failed_startup_remains_renderable"] is True
    assert editor_trust["headless_exit_uses_editor_quit_policy"] is True
    assert editor_trust["dirty_noninteractive_eof_is_nonzero"] is True
    assert editor_trust["trusted_and_restricted_journeys_present"] is True

    buffer_creation = payload["buffer_creation"]
    assert buffer_creation["unique_name_owner_present"] is True
    assert buffer_creation["strict_creation_guard_precedes_state_mutation"] is True
    assert buffer_creation["human_creation_routes_through_unique_owner"] is True
    assert buffer_creation["interactive_surface_present"] is True
    assert buffer_creation["script_creation_denial_present"] is True
    assert buffer_creation["focused_collision_regressions_present"] is True
    assert buffer_creation["runtime_registry_replacement_absent"] is True
    assert buffer_creation["mark_registry_replacement_absent"] is True
    assert buffer_creation["transactional_restore_preserves_registry_identity"] is True
    assert buffer_creation["mark_restores_preserve_registry_identity"] is True
    assert buffer_creation["direct_buffer_mutations_have_explicit_owners"] is True
    assert buffer_creation["direct_buffer_writes_have_explicit_owners"] is True
    assert [row["method"] for row in buffer_creation["direct_buffer_assignment_sites"]] == [
        "new_buffer",
        "_restore_buffer_identity",
        "rename_buffer",
    ]
    assert [row["method"] for row in buffer_creation["direct_buffer_deletion_sites"]] == [
        "_restore_buffer_identity",
        "close_buffer",
        "close_buffers",
    ]
    assert [row["method"] for row in buffer_creation["registry_assignment_sites"]] == [
        "__init__",
    ]
    assert [row["method"] for row in buffer_creation["insertion_call_sites"]] == [
        "_restore_macro_replay_snapshot",
    ]
    assert [row["method"] for row in buffer_creation["removal_call_sites"]] == [
        "rename_buffer",
    ]
    assert [row["method"] for row in buffer_creation["mark_registry_assignment_sites"]] == [
        "__init__",
    ]
    assert [row["method"] for row in buffer_creation["mark_insertion_call_sites"]] == [
        "_restore_mark_entries",
        "_restore_buffer_identity",
        "_restore_macro_replay_snapshot",
    ]
    assert [row["method"] for row in buffer_creation["mark_clear_call_sites"]] == [
        "_restore_mark_entries",
        "_restore_buffer_identity",
        "_restore_macro_replay_snapshot",
    ]

    snapshot = payload["plugin_runtime_snapshot"]
    assert snapshot["found"] is True
    assert snapshot["field_count"] == len(snapshot["fields"])
    assert "option_state" in snapshot["fields"]

    docs = payload["docs"]
    assert docs["installed_help_matches_pyproject"] is True
    assert docs["security_boundaries_installed"] is True
    assert docs["curated_entrypoints_match_current"] is True
    assert docs["curated_entrypoint_revs"]["docs/01-llm-start-here.md"] == payload["rev"]
    assert docs["curated_entrypoint_revs"]["docs/40-roadmap.md"] == payload["rev"]
    assert docs["curated_entrypoint_revs"]["docs/41-decisions-log.md"] == payload["rev"]
    assert docs["curated_entrypoint_revs"]["docs/43-worklist.md"] == payload["rev"]
    assert docs["revision_index_entries"] > 0

    effects = payload["effect_contracts"]
    assert effects["help_doc_path"] == "docs/33-effect-resource-contract.md"
    assert effects["help_doc_present"] is True
    assert effects["help_doc_installed"] is True
    assert effects["help_doc_matches_generated"] is True

    typecheck = payload["typecheck"]
    assert typecheck["covers_editor_package"] is True

    release = payload["release_hygiene"]
    assert release["shared_toolrun_present"] is True
    assert release["timely_runway_present"] is True
    assert release["timely_summary_incremental"] is True
    assert release["timely_summary_completion_honest"] is True
    assert release["full_suite_runway_present"] is True
    evidence_rows = release["release_suite_evidence_rows"]
    assert release["release_suite_evidence_present"] is bool(evidence_rows)
    assert len(evidence_rows) == len(release["release_suite_manifests"])
    assert release["release_suite_evidence_current_count"] == sum(
        1
        for row in evidence_rows
        if row["current"] is True and row["internally_consistent"] is True
    )
    assert release["release_suite_evidence_complete_current_count"] == sum(
        1
        for row in evidence_rows
        if row["current"] is True
        and row["internally_consistent"] is True
        and row["complete"] is True
    )
    assert release["release_suite_evidence_ok_current_count"] == sum(
        1
        for row in evidence_rows
        if row["current"] is True
        and row["internally_consistent"] is True
        and row["ok"] is True
        and not row["issues"]
    )
    for row in evidence_rows:
        assert row["path"] in release["release_suite_manifests"]
        assert row["issue_count"] == len(row["issues"])
        assert isinstance(row["batch_status_counts"], dict)
        assert isinstance(row["test_status_counts"], dict)
        assert isinstance(row["pytest_counts"], dict)
        assert row["test_batch_count"] >= 0
        assert row["test_file_count"] >= 0
    assert release["mkrevzip_provenance_present"] is True
    assert release["mkrevzip_verifier_present"] is True
    assert release["mkrevzip_revision_lineage_present"] is True
    assert release["package_input_report_ok"] is True
    assert release["package_input_issues"] == []
    assert "release/requirements-builder.txt" in release["lock_files"]
    assert release["package_input_policy_present"] is True
    assert release["hash_locked_builder_present"] is True
    assert release["hosted_attestation_present"] is True
    assert release["retained_attested_outputs_present"] is True

    runtime_group_policy = payload["runtime_group_policy"]
    assert runtime_group_policy["operation_error_class_present"] is True
    assert runtime_group_policy["narrow_group_snapshot_present"] is True
    assert runtime_group_policy["narrow_generation_snapshot_present"] is True
    assert runtime_group_policy["generation_cleanup_report_present"] is True
    assert runtime_group_policy["manager_retains_reports"] is True
    assert runtime_group_policy["manager_exposes_failure_rows"] is True
    assert runtime_group_policy["editor_exposes_cleanup_failure_rows"] is True
    assert runtime_group_policy["plugin_cleanup_command_present"] is True
    assert runtime_group_policy["plugin_cleanup_hostcall_present"] is True
    assert runtime_group_policy["plugin_cleanup_completion_present"] is True
    assert runtime_group_policy["unload_uses_cleanup_commit_guard"] is True
    assert runtime_group_policy["reload_uses_cleanup_commit_guard"] is True
    assert runtime_group_policy["reload_uses_retag_commit_guard"] is True
    assert runtime_group_policy["reload_uses_prestage_generation_guard"] is True
    assert runtime_group_policy["commit_guard_uses_narrow_group_snapshot"] is True
    assert runtime_group_policy["command_group_snapshot_present"] is True
    assert runtime_group_policy["action_keymap_timer_group_snapshots_present"] is True
    assert runtime_group_policy["hook_mark_group_snapshots_present"] is True
    assert runtime_group_policy["mark_owner_snapshot_present"] is True
    assert runtime_group_policy["hook_snapshots_clone_mutable_handlers"] is True
    assert runtime_group_policy["delayed_group_snapshots_present"] is True
    assert runtime_group_policy["runtime_group_snapshot_uses_touched_registry_surfaces"] is True
    assert runtime_group_policy["runtime_group_snapshot_uses_touched_delayed_surfaces"] is True
    assert runtime_group_policy["singleton_help_group_snapshots_present"] is True
    assert runtime_group_policy["runtime_group_snapshot_uses_touched_singleton_help_surfaces"] is True
    assert runtime_group_policy["commit_guard_passes_command_groups"] is True
    assert runtime_group_policy["loaded_cleanup_passes_command_group"] is True
    assert runtime_group_policy["commit_guard_avoids_full_registration_snapshot"] is True
    assert runtime_group_policy["generation_guard_uses_narrow_snapshot"] is True
    assert runtime_group_policy["generation_nonmacro_snapshots_present"] is True
    assert runtime_group_policy["generation_interaction_snapshot_present"] is True
    assert runtime_group_policy["recovery_owner_snapshot_present"] is True
    assert runtime_group_policy["pending_open_url_owner_snapshot_present"] is True
    assert runtime_group_policy["qreplace_owner_snapshot_present"] is True
    assert runtime_group_policy["qreplace_buffer_witness_present"] is True
    assert runtime_group_policy["clipboard_owner_snapshot_present"] is True
    assert runtime_group_policy["active_search_owner_snapshot_present"] is True
    assert runtime_group_policy["help_history_owner_snapshot_present"] is True
    assert runtime_group_policy["prompt_history_owner_snapshot_present"] is True
    assert runtime_group_policy["recent_files_owner_snapshot_present"] is True
    assert runtime_group_policy["palette_recent_owner_snapshot_present"] is True
    assert runtime_group_policy["generation_snapshot_uses_scoped_nonmacro_surfaces"] is True
    assert runtime_group_policy["generation_macro_snapshot_present"] is True
    assert runtime_group_policy["generation_snapshot_uses_scoped_macro_surface"] is True
    assert runtime_group_policy["scoped_generation_snapshot_avoids_broad_macro_restore"] is True
    assert runtime_group_policy["loaded_cleanup_restores_group_and_generation"] is True
    assert runtime_group_policy["plugin_callback_scoped_snapshot_present"] is True
    assert runtime_group_policy["plugin_callback_interaction_owner_present"] is True
    assert runtime_group_policy["option_state_owner_snapshot_present"] is True
    assert runtime_group_policy["plugin_callback_restore_uses_scoped_snapshots"] is True
    assert runtime_group_policy["editor_passes_plugin_identity_to_callback_snapshot"] is True
    assert runtime_group_policy["dictionary_snapshot_restores_word_authority"] is True
    assert runtime_group_policy["committed_plugin_wordlists_are_tombstoned"] is True
    assert runtime_group_policy["retired_direct_xts_reject_execution"] is True
    assert runtime_group_policy["retired_deferred_callbacks_reject_execution"] is True
    assert runtime_group_policy["retired_interactions_reject_response"] is True
    assert runtime_group_policy["retired_macros_reject_playback"] is True
    assert runtime_group_policy["qreplace_all_replacement_budget"] is True
    assert runtime_group_policy["timer_cancellation_releases_tasks"] is True
    assert runtime_group_policy["vm_hostcall_result_budget"] is True
    assert runtime_group_policy["stdlib_resource_contract_present"] is True
    assert runtime_group_policy["regex_hostcall_input_budget"] is True
    assert runtime_group_policy["regex_hostcall_timeout_worker"] is True
    assert runtime_group_policy["editor_model_dimension_budget"] is True
    assert runtime_group_policy["editor_query_input_budget"] is True
    assert runtime_group_policy["fs_read_preflight_byte_budget"] is True
    assert runtime_group_policy["fs_read_timeout_worker"] is True
    assert runtime_group_policy["editor_open_read_timeout_boundary"] is True
    assert runtime_group_policy["fs_list_timeout_worker"] is True
    assert runtime_group_policy["fs_stat_timeout_worker"] is True
    assert runtime_group_policy["editor_scan_row_budget"] is True
    assert runtime_group_policy["prompt_path_completion_scan_budget"] is True
    assert runtime_group_policy["prompt_path_completion_timeout_worker"] is True
    assert runtime_group_policy["editor_user_init_timeout_boundary"] is True
    assert runtime_group_policy["source_load_stat_timeout_boundary"] is True
    assert runtime_group_policy["editor_atomic_write_timeout_boundary"] is True
    assert runtime_group_policy["editor_save_freshness_timeout_boundary"] is True
    assert runtime_group_policy["editor_disk_state_cache_boundary"] is True
    assert runtime_group_policy["worker_result_frame_deadline_boundary"] is True
    assert runtime_group_policy["worker_start_deadline_boundary"] is True
    assert runtime_group_policy["filesystem_worker_result_drain_boundary"] is True
    assert runtime_group_policy["palette_recent_stat_batch_boundary"] is True
    assert runtime_group_policy["status_readonly_parsecursor_bounded"] is True
    assert runtime_group_policy["process_capture_pipe_owner_boundary"] is True
    assert runtime_group_policy["shell_output_timeout_budget"] is True
    assert runtime_group_policy["external_clipboard_process_budget"] is True
    assert runtime_group_policy["open_url_process_timeout_boundary"] is True
    assert runtime_group_policy["finite_worker_deadline_normalization"] is True
    assert runtime_group_policy["source_load_eval_budget"] is True
    assert runtime_group_policy["source_load_graph_budget"] is True
    assert runtime_group_policy["plugin_package_fingerprint_budgets"] is True
    assert runtime_group_policy["plugin_optional_meta_exists_contained"] is True
    assert runtime_group_policy["plugin_discovery_fingerprint_timeout_boundary"] is True
    assert runtime_group_policy["docs_catalog_scan_timeout_boundary"] is True
    assert runtime_group_policy["project_root_marker_batch_boundary"] is True
    assert runtime_group_policy["bounded_project_file_picker_boundary"] is True


def test_mxaudit_human_output_names_major_pressure_surfaces() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "mxaudit.py"), "--limit", "3"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "Micromax audit metrics" in proc.stdout
    assert "Structural hotspots:" in proc.stdout
    assert "Plugin lifecycle pressure:" in proc.stdout
    assert "RuntimeRegistrationSnapshot:" in proc.stdout
    assert "runtime cleanup guards:" in proc.stdout
    assert "group-snapshot=True" in proc.stdout
    assert "command-group=True" in proc.stdout
    assert "registry-groups=True" in proc.stdout
    assert "hook-mark-groups=True" in proc.stdout
    assert "mark-owner=True" in proc.stdout
    assert "hook-clones=True" in proc.stdout
    assert "delayed-groups=True" in proc.stdout
    assert "singleton-help=True" in proc.stdout
    assert "generation-snapshot=True" in proc.stdout
    assert "generation-rows=True" in proc.stdout
    assert "generation-macros=True" in proc.stdout
    assert "generation-interactions=True" in proc.stdout
    assert "open-url-owner=True" in proc.stdout
    assert "qreplace-owner=True" in proc.stdout
    assert "qreplace-buffer-witness=True" in proc.stdout
    assert "active-search-owner=True" in proc.stdout
    assert "recent-files-owner=True" in proc.stdout
    assert "palette-recent-owner=True" in proc.stdout
    assert "prompt-history-owner=True" in proc.stdout
    assert "callback-scope=True" in proc.stdout
    assert "callback-interaction-owner=True" in proc.stdout
    assert "option-owner=True" in proc.stdout
    assert "dictionary-provenance=True" in proc.stdout
    assert "wordlist-tombstones=True" in proc.stdout
    assert "retired-xt-guard=True" in proc.stdout
    assert "retired-callback-guard=True" in proc.stdout
    assert "retired-interaction-guard=True" in proc.stdout
    assert "retired-macro-guard=True" in proc.stdout
    assert "qreplace-all-budget=True" in proc.stdout
    assert "timer-release=True" in proc.stdout
    assert "hostcall-result-budget=True" in proc.stdout
    assert "stdlib-resource-contract=True" in proc.stdout
    assert "regex-input-budget=True" in proc.stdout
    assert "regex-timeout-worker=True" in proc.stdout
    assert "model-dim-budget=True" in proc.stdout
    assert "query-budget=True" in proc.stdout
    assert "fs-read-budget=True" in proc.stdout
    assert "fs-read-timeout=True" in proc.stdout
    assert "open-read-timeout=True" in proc.stdout
    assert "fs-list-timeout=True" in proc.stdout
    assert "fs-stat-timeout=True" in proc.stdout
    assert "scan-row-budget=True" in proc.stdout
    assert "path-completion-scan-budget=True" in proc.stdout
    assert "path-completion-timeout=True" in proc.stdout
    assert "user-init-timeout=True" in proc.stdout
    assert "source-stat-timeout=True" in proc.stdout
    assert "disk-state-cache=True" in proc.stdout
    assert "worker-start-deadline=True" in proc.stdout
    assert "palette-stat-batch=True" in proc.stdout
    assert "status-access-bounded=True" in proc.stdout
    assert "clipboard-process-budget=True" in proc.stdout
    assert "source-load-budget=True" in proc.stdout
    assert "package-budgets=True" in proc.stdout
    assert "plugin-meta-contained=True" in proc.stdout
    assert "plugin-discovery-timeout=True" in proc.stdout
    assert "docs-catalog-timeout=True" in proc.stdout
    assert "project-root-batch=True" in proc.stdout
    assert "project-file-picker=True" in proc.stdout
    assert "Editor trust boundaries:" in proc.stdout
    assert "discard-state-bound=True" in proc.stdout
    assert "legacy-sticky-absent=True" in proc.stdout
    assert "shared-discard-owner=True" in proc.stdout
    assert "same-name-identity=True" in proc.stdout
    assert "shared-startup=True" in proc.stdout
    assert "renderable-fallback=True" in proc.stdout
    assert "headless-safe-exit=True" in proc.stdout
    assert "dirty-eof-nonzero=True" in proc.stdout
    assert "journey-tests=True" in proc.stdout
    assert "buffer-no-clobber=True" in proc.stdout
    assert "unique-owner=True" in proc.stdout
    assert "human-routing=True" in proc.stdout
    assert "interactive-surface=True" in proc.stdout
    assert "script-denial=True" in proc.stdout
    assert "registry-stable=True" in proc.stdout
    assert "mark-registry-stable=True" in proc.stdout
    assert "mutation-owners=True" in proc.stdout
    assert "write-owners=True" in proc.stdout
    assert "Docs and release hygiene:" in proc.stdout
    assert "curated entrypoints current=True" in proc.stdout
    assert "shared tool-runner present=True" in proc.stdout
    assert "timely runway present=True" in proc.stdout
    assert "timely summary incremental=True" in proc.stdout
    assert "full-suite runway present=True" in proc.stdout
    assert "release-suite evidence current=" in proc.stdout
    assert "release manifest .artifacts/mxrelease-full-suite" in proc.stdout
    assert "mkrevzip provenance present=True" in proc.stdout
    assert "mkrevzip verifier present=True" in proc.stdout
    assert "mkrevzip lineage present=True" in proc.stdout
    assert "package-input policy present=True" in proc.stdout
    assert "hash-locked builder present=True" in proc.stdout
    assert "hosted attestation present=True" in proc.stdout


def test_timeout_boundary_audit_follows_one_local_alias_across_sinks(tmp_path: Path) -> None:
    mxaudit = _load_mxaudit_module()

    source = tmp_path / "boundary_sample.py"
    source.write_text(
        """
class Editor:
    def _save_buffer(self):
        write_timeout = effective_file_write_timeout_seconds(
            getattr(self, "vm", None)
        )
        plan_atomic_write_bounded(
            "target",
            timeout_seconds=write_timeout,
        )
        write_file_bytes(
            "target",
            b"payload",
            timeout_seconds=write_timeout,
        )
""".lstrip(),
        encoding="utf-8",
    )

    assert mxaudit._function_routes_call_result_to_keywords(
        source,
        class_name="Editor",
        function_name="_save_buffer",
        producer_name="effective_file_write_timeout_seconds",
        sink_names={"plan_atomic_write_bounded", "write_file_bytes"},
        keyword_name="timeout_seconds",
    )

    source.write_text(
        source.read_text(encoding="utf-8").replace(
            "timeout_seconds=write_timeout,\n        )\n",
            "timeout_seconds=1.0,\n        )\n",
            1,
        ),
        encoding="utf-8",
    )
    assert not mxaudit._function_routes_call_result_to_keywords(
        source,
        class_name="Editor",
        function_name="_save_buffer",
        producer_name="effective_file_write_timeout_seconds",
        sink_names={"plan_atomic_write_bounded", "write_file_bytes"},
        keyword_name="timeout_seconds",
    )


def test_function_docstring_audit_ignores_source_line_wrapping(tmp_path: Path) -> None:
    mxaudit = _load_mxaudit_module()

    source = tmp_path / "docstring_sample.py"
    source.write_text(
        '''\
def write_file_bytes():
    """Direct writes deliberately remain in-process even when a timeout is
    supplied, because killing one can leave the target partially written.
    """
''',
        encoding="utf-8",
    )

    assert mxaudit._function_docstring_contains(
        source,
        "write_file_bytes",
        "Direct writes",
        "remain in-process",
        "partially written",
    )

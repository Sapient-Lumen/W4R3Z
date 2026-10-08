from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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

    snapshot = payload["plugin_runtime_snapshot"]
    assert snapshot["found"] is True
    assert snapshot["field_count"] == len(snapshot["fields"])
    assert "option_state" in snapshot["fields"]

    docs = payload["docs"]
    assert docs["installed_help_matches_pyproject"] is True
    assert docs["security_boundaries_installed"] is True
    assert docs["revision_index_entries"] > 0

    typecheck = payload["typecheck"]
    assert typecheck["covers_editor_package"] is True

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
    assert runtime_group_policy["generation_snapshot_uses_scoped_nonmacro_surfaces"] is True
    assert runtime_group_policy["generation_macro_snapshot_present"] is True
    assert runtime_group_policy["generation_snapshot_uses_scoped_macro_surface"] is True
    assert runtime_group_policy["scoped_generation_snapshot_avoids_broad_macro_restore"] is True
    assert runtime_group_policy["loaded_cleanup_restores_group_and_generation"] is True
    assert runtime_group_policy["plugin_callback_scoped_snapshot_present"] is True
    assert runtime_group_policy["plugin_callback_restore_uses_scoped_snapshots"] is True
    assert runtime_group_policy["editor_passes_plugin_identity_to_callback_snapshot"] is True
    assert runtime_group_policy["dictionary_snapshot_restores_word_authority"] is True
    assert runtime_group_policy["committed_plugin_wordlists_are_tombstoned"] is True
    assert runtime_group_policy["retired_direct_xts_reject_execution"] is True
    assert runtime_group_policy["retired_deferred_callbacks_reject_execution"] is True
    assert runtime_group_policy["retired_interactions_reject_response"] is True
    assert runtime_group_policy["plugin_package_fingerprint_budgets"] is True


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
    assert "hook-clones=True" in proc.stdout
    assert "delayed-groups=True" in proc.stdout
    assert "singleton-help=True" in proc.stdout
    assert "generation-snapshot=True" in proc.stdout
    assert "generation-rows=True" in proc.stdout
    assert "generation-macros=True" in proc.stdout
    assert "generation-interactions=True" in proc.stdout
    assert "callback-scope=True" in proc.stdout
    assert "dictionary-provenance=True" in proc.stdout
    assert "wordlist-tombstones=True" in proc.stdout
    assert "retired-xt-guard=True" in proc.stdout
    assert "retired-callback-guard=True" in proc.stdout
    assert "retired-interaction-guard=True" in proc.stdout
    assert "package-budgets=True" in proc.stdout
    assert "Docs and release hygiene:" in proc.stdout

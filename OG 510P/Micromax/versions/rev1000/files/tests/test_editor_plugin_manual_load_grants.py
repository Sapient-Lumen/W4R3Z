from __future__ import annotations

import os

import pytest
from pathlib import Path

from micromax.vm import MicromaxError
from micromax_editor.startup import create_editor_runtime


def _plugin(root: Path, name: str, source: str) -> Path:
    plug = root / name
    plug.mkdir()
    (plug / "init.mx").write_text(source, encoding="utf-8")
    return plug


def test_restricted_plugin_reload_does_not_silently_load_available_candidate(tmp_path, monkeypatch) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "probe", ': probe-word "ran" ;\n')
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    ed.messages.clear()

    assert ed.exec_command_line("plugin reload probe") is False
    assert ed.messages == [
        "plugin reload: probe [available]",
        "  restricted workspace: use plugin load probe to approve and load",
    ]
    assert "probe" in pm.candidates
    assert "probe" not in pm.plugins
    with pytest.raises(MicromaxError):
        ed.vm.eval("use probe probe-word", filename="<restricted-reload-test>")


def test_restricted_plugin_load_records_session_grant_and_evaluates_one_candidate(tmp_path, monkeypatch) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "probe", ': probe-word "ran" ;\n')
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    ed.messages.clear()

    assert ed.exec_command_line("plugin load probe") is True
    assert ed.messages == ["plugin load: probe [loaded] · session grant"]
    assert "probe" in pm.plugins
    rows = pm.load_grant_rows()
    assert len(rows) == 1
    assert rows[0][:4] == ["probe", "active", "session", "user"]
    assert rows[0][5] == "command:plugin load probe"
    assert rows[0][7] == 1

    ed.vm.eval("use probe probe-word", filename="<restricted-load-test>")
    assert ed.vm.stack[-1] == "ran"


def test_restricted_plugin_grant_revocation_unloads_and_blocks_later_reload(tmp_path, monkeypatch) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "probe", ': probe-word "ran" ;\n')
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager

    assert ed.exec_command_line("plugin load probe") is True
    ed.messages.clear()
    assert ed.exec_command_line("plugin grants") is True
    assert ed.messages == ["plugin grants: 1 grant(s); probe [active, session, issuer:user]"]

    ed.messages.clear()
    assert ed.exec_command_line("plugin revoke probe") is True
    assert ed.messages == ["plugin revoke: probe [revoked, unloaded]"]
    assert "probe" not in pm.plugins
    assert pm.load_grant_rows()[0][1] == "revoked"

    ed.messages.clear()
    assert ed.exec_command_line("plugin reload probe") is False
    assert ed.messages == [
        "plugin reload: probe [available]",
        "  restricted workspace: use plugin load probe to approve and load",
    ]


def test_trusted_plugin_load_keeps_existing_available_candidate_recovery(tmp_path, monkeypatch) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "optional", ': optional-word "loaded" ;\n')
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="trusted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    pm.unload("optional")
    ed.messages.clear()

    assert ed.exec_command_line("plugin load optional") is True
    assert ed.messages == ["plugin load: optional [loaded]"]
    assert "optional" in pm.plugins
    assert pm.load_grant_rows() == []


def test_restricted_reload_rechecks_disk_before_trusting_existing_grant(tmp_path, monkeypatch) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = _plugin(root, "probe", ': probe-word "first" ;\n')
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    assert ed.exec_command_line("plugin load probe") is True

    (plug / "other.mx").write_text(': probe-word "second" ;\n', encoding="utf-8")
    (plug / "plugin.json").write_text('{"entry":"other.mx"}\n', encoding="utf-8")

    ed.messages.clear()
    assert ed.exec_command_line("plugin reload probe") is False
    assert ed.messages == [
        "plugin reload: probe [loaded]",
        "  restricted workspace: load grant is stale; use plugin load probe to approve reloads",
    ]
    assert pm.load_grant_rows()[0][1] == "active"
    assert pm.load_grant_rows(verify_disk=True)[0][1] == "stale"

    ed.vm.eval("use probe probe-word", filename="<stale-grant-test>")
    assert ed.vm.stack[-1] == "first"


def test_restricted_plugin_load_is_not_script_approvable_even_with_require_cap(tmp_path, monkeypatch) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "probe", ': probe-word "ran" ;\n')
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    assert ed.exec_command_line("set cap.fs-require true") is True
    ed.messages.clear()

    with ed.script_context(origin_id="script-loader"):
        assert ed.exec_command_line("plugin load probe") is False
    assert ed.messages == ["plugin load: disabled for scripts in restricted workspace"]
    assert "probe" in pm.candidates
    assert "probe" not in pm.plugins
    assert pm.load_grant_rows() == []


def test_plugin_grants_do_not_leak_to_scripts_without_plugin_read_cap(tmp_path, monkeypatch) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "probe", ': probe-word "ran" ;\n')
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    assert ed.exec_command_line("plugin load probe") is True
    ed.messages.clear()

    with ed.script_context(origin_id="script-viewer"):
        assert ed.plugin_load_grant_rows() == []
        assert ed.exec_command_line("plugin grants") is False
    assert ed.messages == ["plugin grants: hidden in script context (cap.plugin-read)"]

    assert ed.exec_command_line("set cap.plugin-read true") is True
    ed.messages.clear()
    with ed.script_context(origin_id="script-viewer"):
        assert ed.exec_command_line("plugin grants") is True
    assert ed.messages == ["plugin grants: 1 grant(s); probe [active, session, issuer:user]"]


def test_plugin_revoke_is_not_script_mutable(tmp_path, monkeypatch) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "probe", ': probe-word "ran" ;\n')
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    assert ed.exec_command_line("plugin load probe") is True
    assert ed.exec_command_line("set cap.plugin-read true") is True
    ed.messages.clear()

    with ed.script_context(origin_id="script-mutator"):
        assert ed.exec_command_line("plugin revoke probe") is False
    assert ed.messages == ["plugin revoke: disabled for scripts"]
    assert pm.load_grant_rows()[0][1] == "active"


def test_restricted_reload_rejects_same_entry_content_change_until_reapproved(tmp_path, monkeypatch) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = _plugin(root, "probe", ': probe-word "first" ;\n')
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    assert ed.exec_command_line("plugin load probe") is True

    (plug / "init.mx").write_text(': probe-word "second" ;\n', encoding="utf-8")
    ed.messages.clear()
    assert ed.exec_command_line("plugin reload probe") is False
    assert ed.messages == [
        "plugin reload: probe [loaded]",
        "  restricted workspace: load grant is stale; use plugin load probe to approve reloads",
    ]
    assert pm.load_grant_rows()[0][1] == "active"
    assert pm.load_grant_rows(verify_disk=True)[0][1] == "stale"
    ed.vm.eval("use probe probe-word", filename="<stale-content-test>")
    assert ed.vm.stack[-1] == "first"

    ed.messages.clear()
    assert ed.exec_command_line("plugin load probe") is True
    assert ed.messages == [
        "plugin load: probe [loaded] · replacement approved; run plugin reload probe"
    ]
    assert pm.load_grant_rows()[0][1] == "active"

    ed.messages.clear()
    assert ed.exec_command_line("plugin reload probe") is True
    assert ed.messages == ["plugin reload: probe [loaded]"]
    ed.vm.eval("use probe probe-word", filename="<reapproved-content-test>")
    assert ed.vm.stack[-1] == "second"


def test_restricted_reload_rejects_included_file_content_change(tmp_path, monkeypatch) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "probe"
    plug.mkdir()
    (plug / "init.mx").write_text('"part.mx" require\n', encoding="utf-8")
    (plug / "part.mx").write_text(': probe-word "first" ;\n', encoding="utf-8")
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    assert ed.exec_command_line("plugin load probe") is True
    before_digest = pm.load_grants["probe"].package_digest
    assert pm.load_grants["probe"].package_file_count == 2

    (plug / "part.mx").write_text(': probe-word "second" ;\n', encoding="utf-8")
    assert pm.load_grants["probe"].package_digest == before_digest
    assert pm.load_grant_rows()[0][1] == "active"
    assert pm.load_grant_rows(verify_disk=True)[0][1] == "stale"

    ed.messages.clear()
    assert ed.exec_command_line("plugin reload probe") is False
    assert ed.messages == [
        "plugin reload: probe [loaded]",
        "  restricted workspace: load grant is stale; use plugin load probe to approve reloads",
    ]
    ed.vm.eval("use probe probe-word", filename="<stale-include-test>")
    assert ed.vm.stack[-1] == "first"


def test_restricted_plugin_callback_uses_approved_snapshot_until_reload(tmp_path, monkeypatch) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "probe"
    plug.mkdir()
    (plug / "init.mx").write_text(
        ': run drop "helper.mx" include helper-msg "ed.msg" hostcall 1 ;\n'
        "' run \"cmdprobe\" \"include helper\" \"ed.cmd-add\" hostcall drop\n",
        encoding="utf-8",
    )
    (plug / "helper.mx").write_text(': helper-msg "first" ;\n', encoding="utf-8")
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    pm.package_fingerprint_timeout_seconds = 0
    assert ed.exec_command_line("plugin load probe") is True
    loaded_digest = pm.plugins["probe"].package_digest
    assert loaded_digest

    ed.messages.clear()
    assert ed.exec_command_line("cmdprobe") is True
    assert ed.messages[-1] == "first"

    (plug / "helper.mx").write_text(': helper-msg "second" ;\n', encoding="utf-8")
    assert pm.plugins["probe"].package_digest == loaded_digest
    assert pm.loaded_plugin_package_current(pm.plugins["probe"]) is False
    assert pm.loaded_plugin_package_authorized(
        pm.plugins["probe"],
        require_digest=True,
    ) is True

    # Disk drift does not alter the running generation.  Its deferred include
    # consumes the exact immutable package bytes approved at load time.
    ed.messages.clear()
    assert ed.exec_command_line("cmdprobe") is True
    assert ed.messages == ["first"]

    # Re-approval alone approves the new bytes for a future reload; it must not
    # silently turn an already-registered callback into a loader for changed files.
    ed.messages.clear()
    assert ed.exec_command_line("plugin load probe") is True
    assert ed.messages == [
        "plugin load: probe [loaded] · replacement approved; run plugin reload probe"
    ]
    assert pm.load_grant_rows()[0][1] == "active"
    assert pm.loaded_plugin_package_current(pm.plugins["probe"]) is False

    ed.messages.clear()
    assert ed.exec_command_line("cmdprobe") is True
    assert ed.messages == ["first"]
    assert "second" not in ed.messages

    ed.messages.clear()
    assert ed.exec_command_line("plugin reload probe") is True
    assert pm.loaded_plugin_package_current(pm.plugins["probe"]) is True

    ed.messages.clear()
    assert ed.exec_command_line("cmdprobe") is True
    assert ed.messages[-1] == "second"


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlink support required")
def test_restricted_callback_symlink_retarget_still_reads_approved_snapshot(
    tmp_path,
    monkeypatch,
) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "probe"
    plug.mkdir()
    (plug / "init.mx").write_text(
        ': run drop "helper.mx" include helper-msg "ed.msg" hostcall 1 ;\n'
        "' run \"cmdprobe\" \"include helper\" \"ed.cmd-add\" hostcall drop\n",
        encoding="utf-8",
    )
    helper = plug / "helper.mx"
    helper.write_text(': helper-msg "approved" ;\n', encoding="utf-8")
    outside = tmp_path / "outside.mx"
    outside.write_text(': helper-msg "unapproved-live-target" ;\n', encoding="utf-8")
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    pm.package_fingerprint_timeout_seconds = 0
    assert ed.exec_command_line("plugin load probe") is True

    helper.unlink()
    os.symlink(outside, helper)

    ed.messages.clear()
    assert ed.exec_command_line("cmdprobe") is True
    assert ed.messages == ["approved"]
    assert "unapproved-live-target" not in ed.messages


def test_direct_grant_revocation_withholds_future_callback_includes(tmp_path, monkeypatch) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "probe"
    plug.mkdir()
    (plug / "init.mx").write_text(
        ': run drop "helper.mx" include helper-msg "ed.msg" hostcall 1 ;\n'
        "' run \"cmdprobe\" \"include helper\" \"ed.cmd-add\" hostcall drop\n",
        encoding="utf-8",
    )
    (plug / "helper.mx").write_text(': helper-msg "first" ;\n', encoding="utf-8")
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    pm.package_fingerprint_timeout_seconds = 0
    assert ed.exec_command_line("plugin load probe") is True

    ed.messages.clear()
    assert ed.exec_command_line("cmdprobe") is True
    assert ed.messages[-1] == "first"
    assert pm.loaded_plugin_package_current(pm.plugins["probe"], require_digest=True) is True
    assert pm.loaded_plugin_package_authorized(pm.plugins["probe"], require_digest=True) is True

    # Interactive revoke now removes the runtime too.  Exercise the lower-level
    # grant API directly to pin fail-closed behavior for embedders that separate
    # the two transitions.
    assert pm.revoke_load_grant("probe") is True
    assert pm.loaded_plugin_package_current(pm.plugins["probe"], require_digest=True) is True
    assert pm.loaded_plugin_package_authorized(pm.plugins["probe"], require_digest=True) is False

    fingerprint_calls = 0
    original_fingerprint = pm._candidate_package_fingerprint

    def counted_fingerprint(candidate):
        nonlocal fingerprint_calls
        fingerprint_calls += 1
        return original_fingerprint(candidate)

    monkeypatch.setattr(pm, "_candidate_package_fingerprint", counted_fingerprint)
    ed.messages.clear()
    assert ed.exec_command_line("cmdprobe") is False
    assert any("load grant revoked" in str(msg) for msg in ed.messages)
    assert "first" not in ed.messages
    assert fingerprint_calls == 0

    ed.messages.clear()
    assert ed.exec_command_line("plugin load probe") is True
    assert ed.messages == [
        "plugin load: probe [loaded] · replacement approved; run plugin reload probe"
    ]
    assert pm.approved_package_snapshots["probe"] is pm.plugins["probe"].package_snapshot
    assert pm.loaded_plugin_package_authorized(pm.plugins["probe"], require_digest=True) is True
    ed.messages.clear()
    assert ed.exec_command_line("cmdprobe") is True
    assert ed.messages[-1] == "first"

def test_restricted_plugin_unload_removes_runtime_surface_and_revokes_grant(tmp_path, monkeypatch) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = root / "probe"
    plug.mkdir()
    (plug / "init.mx").write_text(
        ': run drop "helper.mx" include helper-msg "ed.msg" hostcall 1 ;\n'
        "' run \"cmdprobe\" \"include helper\" \"ed.cmd-add\" hostcall drop\n",
        encoding="utf-8",
    )
    (plug / "helper.mx").write_text(': helper-msg "first" ;\n', encoding="utf-8")
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    assert ed.exec_command_line("plugin load probe") is True
    assert ed.exec_command_line("cmdprobe") is True
    assert "probe" in pm.plugins
    assert pm.load_grant_rows()[0][1] == "active"

    ed.messages.clear()
    assert ed.exec_command_line("plugin unload probe") is True
    assert ed.messages == ["plugin unload: probe [unloaded]"]
    assert "probe" not in pm.plugins
    assert pm.load_grant_rows()[0][1] == "revoked"

    ed.messages.clear()
    assert ed.exec_command_line("cmdprobe") is False
    assert "first" not in ed.messages

    ed.messages.clear()
    assert ed.exec_command_line("plugin reload probe") is False
    assert ed.messages == [
        "plugin reload: probe [available]",
        "  restricted workspace: use plugin load probe to approve and load",
    ]


def test_plugin_unload_is_not_script_mutable(tmp_path, monkeypatch) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "probe", ': probe-word "ran" ;\n')
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    assert ed.exec_command_line("plugin load probe") is True
    ed.messages.clear()

    with ed.script_context(origin_id="script-unloader"):
        assert ed.exec_command_line("plugin unload probe") is False
    assert ed.messages == ["plugin unload: disabled for scripts"]
    assert "probe" in pm.plugins


def test_restricted_callback_without_source_load_does_not_fingerprint_package(
    tmp_path, monkeypatch
) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(
        root,
        "probe",
        ': run drop "ran" "ed.msg" hostcall 1 ;\n'
        "' run \"cmdprobe\" \"no source load\" \"ed.cmd-add\" hostcall drop\n",
    )
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    pm.package_fingerprint_timeout_seconds = 0
    assert ed.exec_command_line("plugin load probe") is True

    fingerprint_calls = 0
    original_fingerprint = pm._candidate_package_fingerprint

    def counted_fingerprint(candidate):
        nonlocal fingerprint_calls
        fingerprint_calls += 1
        return original_fingerprint(candidate)

    monkeypatch.setattr(pm, "_candidate_package_fingerprint", counted_fingerprint)
    ed.messages.clear()
    assert ed.exec_command_line("cmdprobe") is True
    assert ed.messages == ["ran"]
    assert fingerprint_calls == 0


def test_restricted_callback_performs_no_live_package_scan_for_multiple_source_reads(
    tmp_path, monkeypatch
) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = _plugin(
        root,
        "probe",
        ': run drop "a.mx" include "b.mx" include a-run b-run ;\n'
        "' run \"cmdprobe\" \"two source loads\" \"ed.cmd-add\" hostcall drop\n",
    )
    (plug / "a.mx").write_text(': a-run "a" "ed.msg" hostcall 1 ;\n', encoding="utf-8")
    (plug / "b.mx").write_text(': b-run "b" "ed.msg" hostcall 1 ;\n', encoding="utf-8")
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    pm.package_fingerprint_timeout_seconds = 0
    assert ed.exec_command_line("plugin load probe") is True

    fingerprint_calls = 0
    original_fingerprint = pm._candidate_package_fingerprint

    def counted_fingerprint(candidate):
        nonlocal fingerprint_calls
        fingerprint_calls += 1
        return original_fingerprint(candidate)

    monkeypatch.setattr(pm, "_candidate_package_fingerprint", counted_fingerprint)
    ed.messages.clear()
    assert ed.exec_command_line("cmdprobe") is True
    assert ed.messages == ["a", "b"]
    assert fingerprint_calls == 0


def test_restricted_failed_activation_revokes_the_uncommitted_grant(
    tmp_path, monkeypatch
) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "probe", "definitely-missing-word\n")
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    pm.package_fingerprint_timeout_seconds = 0
    ed.messages.clear()

    assert ed.exec_command_line("plugin load probe") is False
    assert "probe" not in pm.plugins
    assert pm.load_grant_rows()[0][1] == "revoked"
    assert ed.messages[-1] == "  session grant revoked because activation did not commit"



def test_plugin_revoke_cleanup_failure_keeps_runtime_and_grant_active(
    tmp_path,
    monkeypatch,
) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "probe", ': probe-word "ran" ;\n')
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    pm.package_fingerprint_timeout_seconds = 0
    assert ed.exec_command_line("plugin load probe") is True

    def fail_cleanup(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise MicromaxError("simulated runtime cleanup commit failure")

    monkeypatch.setattr(pm, "_cleanup_loaded_plugin_state_or_restore", fail_cleanup)

    ed.messages.clear()
    assert ed.exec_command_line("plugin revoke probe") is False
    assert "probe" in pm.plugins
    assert pm.load_grant_rows()[0][1] == "active"
    assert pm.approved_package_snapshots["probe"] is pm.plugins["probe"].package_snapshot
    assert ed.messages[0] == "plugin revoke: probe [loaded]"
    assert "cleanup failed" in ed.messages[1]
    assert "still loaded" in ed.messages[1]
    assert "grant unchanged" in ed.messages[1]


def test_plugin_revoke_does_not_execute_plugin_deinit(tmp_path, monkeypatch) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(
        root,
        "probe",
        ': deinit "deinit-ran" "ed.msg" hostcall -901 throw ;\n'
        ': probe-word "ran" ;\n',
    )
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    pm.package_fingerprint_timeout_seconds = 0
    assert ed.exec_command_line("plugin load probe") is True

    ed.messages.clear()
    assert ed.exec_command_line("plugin revoke probe") is True
    assert ed.messages == ["plugin revoke: probe [revoked, unloaded]"]
    assert "deinit-ran" not in ed.messages
    assert "probe" not in pm.plugins
    assert pm.load_grant_rows()[0][1] == "revoked"


def test_restricted_graceful_unload_uses_loaded_snapshot_after_disk_drift(
    tmp_path,
    monkeypatch,
) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = _plugin(
        root,
        "probe",
        ': deinit "helper.mx" include cleanup-msg "ed.msg" hostcall ;\n'
        ': probe-word "ran" ;\n',
    )
    helper = plug / "helper.mx"
    helper.write_text(': cleanup-msg "approved-cleanup" ;\n', encoding="utf-8")
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    pm.package_fingerprint_timeout_seconds = 0
    assert ed.exec_command_line("plugin load probe") is True

    helper.write_text(': cleanup-msg "changed-cleanup" ;\n', encoding="utf-8")
    ed.messages.clear()
    assert ed.exec_command_line("plugin unload probe") is True
    assert ed.messages == ["approved-cleanup", "plugin unload: probe [unloaded]"]
    assert "changed-cleanup" not in ed.messages
    assert "probe" not in pm.plugins
    assert pm.load_grant_rows()[0][1] == "revoked"


def test_restricted_reload_runs_each_generation_deinit_from_its_own_snapshot(
    tmp_path,
    monkeypatch,
) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = _plugin(
        root,
        "probe",
        ': deinit "helper.mx" include cleanup-msg "ed.msg" hostcall ;\n'
        ': probe-word "loaded" ;\n',
    )
    helper = plug / "helper.mx"
    helper.write_text(': cleanup-msg "old-cleanup" ;\n', encoding="utf-8")
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    pm.package_fingerprint_timeout_seconds = 0
    assert ed.exec_command_line("plugin load probe") is True
    first_generation = pm.plugins["probe"].generation

    helper.write_text(': cleanup-msg "new-cleanup" ;\n', encoding="utf-8")
    ed.messages.clear()
    assert ed.exec_command_line("plugin load probe") is True
    assert ed.messages == [
        "plugin load: probe [loaded] · replacement approved; run plugin reload probe"
    ]

    ed.messages.clear()
    assert ed.exec_command_line("plugin reload probe") is True
    assert ed.messages == ["old-cleanup", "plugin reload: probe [loaded]"]
    assert pm.plugins["probe"].generation > first_generation

    ed.messages.clear()
    assert ed.exec_command_line("plugin unload probe") is True
    assert ed.messages == ["new-cleanup", "plugin unload: probe [unloaded]"]


def test_retired_plugin_record_never_recovers_source_authority(
    tmp_path,
    monkeypatch,
) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "probe", ': probe-word "ran" ;\n')
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    pm.package_fingerprint_timeout_seconds = 0
    assert ed.exec_command_line("plugin load probe") is True
    retired = pm.plugins["probe"]

    # Keep the grant record active through the low-level manager unload.  Object
    # identity, not just matching name/root/digest fields, gates runtime authority.
    pm.unload("probe", run_deinit=False)
    denial = pm.loaded_plugin_source_load_denial(retired, require_digest=True)
    assert denial == "plugin source load denied: plugin generation is not loaded"


def test_prompt_grant_inventory_never_verifies_live_packages(
    tmp_path,
    monkeypatch,
) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    plug = _plugin(root, "probe", ': probe-word "ran" ;\n')
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    pm.package_fingerprint_timeout_seconds = 0
    assert ed.exec_command_line("plugin load probe") is True
    (plug / "init.mx").write_text(': probe-word "changed" ;\n', encoding="utf-8")

    def unexpected_fingerprint(_candidate):
        raise AssertionError("prompt inventory touched live plugin bytes")

    monkeypatch.setattr(pm, "_candidate_package_fingerprint", unexpected_fingerprint)
    assert ed.plugin_load_grant_rows()[0][1] == "active"
    row = ed._prompt_plugin_command_row("plugin grants", subcommand="grants")
    assert row[1] == "subcommand"
    assert "1 grant" in row[3]

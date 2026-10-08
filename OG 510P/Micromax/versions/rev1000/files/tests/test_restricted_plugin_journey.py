from __future__ import annotations

import json
from pathlib import Path

from micromax_editor.startup import create_editor_runtime


def _journey_plugin(root: Path) -> Path:
    plug = root / "probe"
    plug.mkdir()
    (plug / "plugin.json").write_text(
        json.dumps(
            {
                "name": "probe",
                "version": "1.0.0",
                "description": "restricted journey probe",
                "entry": "init.mx",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (plug / "init.mx").write_text(
        ': run drop "helper.mx" include helper-msg "ed.msg" hostcall 1 ;\n'
        "' run \"cmdprobe\" \"read package helper\" \"ed.cmd-add\" hostcall drop\n",
        encoding="utf-8",
    )
    (plug / "helper.mx").write_text(': helper-msg "first" ;\n', encoding="utf-8")
    return plug


def test_restricted_plugin_scan_approve_snapshot_reload_revoke_journey(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Pin the restricted plugin promise as one complete visible product loop."""

    root = tmp_path / "plugins"
    root.mkdir()
    plug = _journey_plugin(root)
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager
    # Package-worker mechanics have dedicated tests.  Keep this journey focused
    # on the user contract and capture the package inline.
    pm.package_fingerprint_timeout_seconds = 0

    # Restricted startup exposes inert metadata without evaluating source.
    assert "probe" in pm.candidates
    assert "probe" not in pm.plugins
    ed.messages.clear()
    assert ed.exec_command_line("plugin info probe") is True
    assert ed.messages[0] == "plugin info: probe [available, v1.0.0]"
    assert f"  root: {plug.resolve()}" in ed.messages
    assert "  desc: restricted journey probe" in ed.messages
    ed.messages.clear()
    assert ed.exec_command_line("cmdprobe") is False
    assert ed.messages == ["command: no such command: cmdprobe"]

    # Explicit approval activates exactly one captured package generation.
    ed.messages.clear()
    assert ed.exec_command_line("plugin load probe") is True
    assert ed.messages == ["plugin load: probe [loaded, v1.0.0] · session grant"]
    first = pm.plugins["probe"]
    assert first.package_snapshot is pm.approved_package_snapshots["probe"]
    assert pm.load_grant_rows()[0][1] == "active"

    # Registered surfaces carry visible plugin origin and source location.
    ed.messages.clear()
    assert ed.exec_command_line("showcmd cmdprobe") is True
    assert "read package helper" in ed.messages[-1]
    assert "[group plugin:probe]" in ed.messages[-1]
    assert f"defined at {plug / 'init.mx'}:" in ed.messages[-1]

    ed.messages.clear()
    assert ed.exec_command_line("cmdprobe") is True
    assert ed.messages == ["first"]

    # Changing disk cannot alter the already-approved runtime generation.  A
    # callback consumes the old immutable snapshot and performs no live package
    # fingerprint or recapture.
    (plug / "helper.mx").write_text(': helper-msg "second" ;\n', encoding="utf-8")

    def unexpected_live_package_access(_candidate):
        raise AssertionError("deferred callback touched the live plugin package")

    with monkeypatch.context() as m:
        m.setattr(pm, "_candidate_package_fingerprint", unexpected_live_package_access)
        m.setattr(pm, "_candidate_package_snapshot", unexpected_live_package_access)
        ed.messages.clear()
        assert ed.exec_command_line("cmdprobe") is True
        assert ed.messages == ["first"]

    # Reload is an explicit live-disk transition and refuses changed files until
    # the user approves their exact captured bytes.
    ed.messages.clear()
    assert ed.exec_command_line("plugin reload probe") is False
    assert ed.messages == [
        "plugin reload: probe [loaded, v1.0.0]",
        "  restricted workspace: load grant is stale; "
        "use plugin load probe to approve reloads",
    ]
    assert pm.load_grant_rows()[0][1] == "active"
    assert pm.load_grant_rows(verify_disk=True)[0][1] == "stale"

    ed.messages.clear()
    assert ed.exec_command_line("plugin load probe") is True
    assert ed.messages == [
        "plugin load: probe [loaded, v1.0.0] · "
        "replacement approved; run plugin reload probe"
    ]
    replacement = pm.approved_package_snapshots["probe"]
    assert replacement is not first.package_snapshot

    # Approval alone never retargets or partially disables the committed
    # generation.  Its callback continues to consume the old immutable bytes
    # until reload performs the explicit activation transition.
    ed.messages.clear()
    assert ed.exec_command_line("cmdprobe") is True
    assert ed.messages == ["first"]
    assert "second" not in ed.messages

    ed.messages.clear()
    assert ed.exec_command_line("plugin reload probe") is True
    assert ed.messages == ["plugin reload: probe [loaded, v1.0.0]"]
    second = pm.plugins["probe"]
    assert second.generation > first.generation
    assert second.package_snapshot is replacement

    ed.messages.clear()
    assert ed.exec_command_line("cmdprobe") is True
    assert ed.messages == ["second"]

    # Revocation is decisive: it skips plugin deinit, commits managed cleanup,
    # revokes the grant, and makes the registered command disappear.
    ed.messages.clear()
    assert ed.exec_command_line("plugin revoke probe") is True
    assert ed.messages == ["plugin revoke: probe [revoked, unloaded]"]
    assert "probe" not in pm.plugins
    assert pm.load_grant_rows()[0][1] == "revoked"
    assert ed.command_dispatcher.get("cmdprobe") is None
    retired = pm.retired_wordlist_rows("probe")
    assert retired and retired[-1][1] == "unload"

    ed.messages.clear()
    assert ed.exec_command_line("cmdprobe") is False
    assert ed.messages == ["command: no such command: cmdprobe"]

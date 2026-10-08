from __future__ import annotations

import os
from pathlib import Path

import pytest

from micromax.vm import MicromaxError
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugins import PluginManager


def _manager() -> tuple[Editor, PluginManager]:
    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    pm.plugin_discovery_timeout_seconds = 0
    return ed, pm


def _plugin(root: Path, source: str) -> Path:
    plug = root / "probe"
    plug.mkdir(parents=True)
    (plug / "plugin.json").write_text(
        '{"name":"probe","version":"1.0.0","entry":"init.mx"}\n',
        encoding="utf-8",
    )
    (plug / "init.mx").write_text(source, encoding="utf-8")
    return plug


def test_initial_grant_load_evaluates_the_approved_snapshot_not_later_disk(
    tmp_path: Path,
) -> None:
    root = tmp_path / "plugins"
    plug = _plugin(root, ': probe-word "approved" ;\n')

    ed, pm = _manager()
    pm.package_fingerprint_timeout_seconds = 0
    assert pm.scan_tree(root) == ["probe"]
    grant, snapshot = pm.grant_load_snapshot("probe")

    # Mutate both metadata and entry bytes after approval.  Activation must use
    # the captured generation, not reopen either live file.
    (plug / "plugin.json").write_text(
        '{"name":"probe","version":"9.9.9","entry":"other.mx"}\n',
        encoding="utf-8",
    )
    (plug / "init.mx").write_text(': probe-word "unapproved-init" ;\n', encoding="utf-8")
    (plug / "other.mx").write_text(': probe-word "unapproved-other" ;\n', encoding="utf-8")

    loaded = pm.load_available(
        "probe",
        grant=grant,
        package_snapshot=snapshot,
    )
    assert loaded.package_snapshot is snapshot
    assert loaded.meta["version"] == "1.0.0"
    ed.vm.eval("use probe probe-word", filename="<approved-snapshot-test>")
    assert ed.vm.stack[-1] == "approved"


def test_reload_consumes_retained_approval_even_if_disk_changes_again(
    tmp_path: Path,
) -> None:
    root = tmp_path / "plugins"
    plug = _plugin(root, ': probe-word "first" ;\n')

    ed, pm = _manager()
    pm.package_fingerprint_timeout_seconds = 0
    assert pm.scan_tree(root) == ["probe"]
    first_grant, first_snapshot = pm.grant_load_snapshot("probe")
    first = pm.load_available(
        "probe",
        grant=first_grant,
        package_snapshot=first_snapshot,
    )

    (plug / "init.mx").write_text(': probe-word "approved-second" ;\n', encoding="utf-8")
    second_grant, second_snapshot = pm.grant_load_snapshot("probe")
    assert second_snapshot is not first_snapshot

    # A later edit cannot retarget the manager's approved reload.  The editor's
    # user-facing reload command separately notices this drift and asks for a new
    # approval, but the manager never substitutes unchecked bytes.
    (plug / "init.mx").write_text(': probe-word "unapproved-third" ;\n', encoding="utf-8")
    second = pm.reload("probe", grant=second_grant)
    assert second.generation > first.generation
    assert second.package_snapshot is second_snapshot
    ed.vm.eval("use probe probe-word", filename="<approved-reload-test>")
    assert ed.vm.stack[-1] == "approved-second"
    assert pm.loaded_plugin_package_current(second, require_digest=True) is False



def test_revoked_grant_object_cannot_be_replayed_for_initial_load(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    _plugin(root, ': probe-word "approved" ;\n')

    _ed, pm = _manager()
    pm.package_fingerprint_timeout_seconds = 0
    assert pm.scan_tree(root) == ["probe"]
    stale_grant, snapshot = pm.grant_load_snapshot("probe")
    assert pm.revoke_load_grant("probe") is True

    with pytest.raises(MicromaxError, match="plugin load grant is stale: probe"):
        pm.load_available("probe", grant=stale_grant, package_snapshot=snapshot)
    assert "probe" not in pm.plugins


def test_superseded_grant_object_cannot_consume_new_approval(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    _plugin(root, ': probe-word "approved" ;\n')

    _ed, pm = _manager()
    pm.package_fingerprint_timeout_seconds = 0
    assert pm.scan_tree(root) == ["probe"]
    stale_grant, _stale_snapshot = pm.grant_load_snapshot("probe")
    current_grant, current_snapshot = pm.grant_load_snapshot("probe")
    assert current_grant is pm.load_grants["probe"]

    with pytest.raises(MicromaxError, match="plugin load grant is stale: probe"):
        pm.load_available("probe", grant=stale_grant, package_snapshot=current_snapshot)

    loaded = pm.load_available(
        "probe",
        grant=current_grant,
        package_snapshot=current_snapshot,
    )
    assert loaded.package_snapshot is current_snapshot


def test_revoked_grant_object_cannot_reload_or_recapture_disk(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "plugins"
    _plugin(root, ': probe-word "approved" ;\n')

    _ed, pm = _manager()
    pm.package_fingerprint_timeout_seconds = 0
    assert pm.scan_tree(root) == ["probe"]
    grant, snapshot = pm.grant_load_snapshot("probe")
    loaded = pm.load_available("probe", grant=grant, package_snapshot=snapshot)
    stale_grant = pm.load_grants["probe"]
    assert pm.revoke_load_grant("probe") is True

    def unexpected_capture(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("stale grant reached package recapture")

    monkeypatch.setattr(pm, "_candidate_package_snapshot", unexpected_capture)
    with pytest.raises(MicromaxError, match="plugin load grant is stale: probe"):
        pm.reload("probe", grant=stale_grant)
    assert pm.plugins["probe"] is loaded


def test_snapshot_source_resolution_normalizes_parent_segments(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    plug = _plugin(
        root,
        ': init "sub/../helper.mx" include ;\n'
        ': probe-word helper-word ;\n',
    )
    (plug / "sub").mkdir()
    (plug / "helper.mx").write_text(': helper-word "normalized" ;\n', encoding="utf-8")

    ed, pm = _manager()
    pm.package_fingerprint_timeout_seconds = 0
    assert pm.scan_tree(root) == ["probe"]
    grant, snapshot = pm.grant_load_snapshot("probe")
    pm.load_available("probe", grant=grant, package_snapshot=snapshot)

    ed.vm.eval("use probe probe-word", filename="<normalized-snapshot-path-test>")
    assert ed.vm.stack[-1] == "normalized"


def test_snapshot_retention_budget_fails_before_recording_grant(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    _plugin(root, ': probe-word "approved" ;\n')

    _ed, pm = _manager()
    pm.package_fingerprint_timeout_seconds = 0
    assert pm.scan_tree(root) == ["probe"]
    pm.package_snapshot_max_retained_bytes = 1

    with pytest.raises(MicromaxError, match="snapshot retention budget exceeded"):
        pm.grant_load_snapshot("probe")
    assert pm.load_grants == {}
    assert pm.approved_package_snapshots == {}


@pytest.mark.skipif(os.name != "posix", reason="large multiprocessing queue regression is POSIX-only")
def test_large_snapshot_worker_drains_result_before_join(tmp_path: Path) -> None:
    """A multi-MiB queue payload must not deadlock behind child join."""

    root = tmp_path / "plugins"
    plug = _plugin(root, ': probe-word "approved" ;\n')
    payload = b"x" * (600 * 1024)
    for index in range(4):
        (plug / f"payload-{index}.bin").write_bytes(payload)

    _ed, pm = _manager()
    assert pm.scan_tree(root) == ["probe"]
    pm.package_fingerprint_timeout_seconds = 15.0
    candidate = pm.candidates["probe"]

    snapshot = pm._candidate_package_snapshot(candidate)
    assert snapshot.total_bytes >= len(payload) * 4
    assert snapshot.file_count == 6
    assert snapshot.read_bytes(plug / "payload-3.bin") == payload

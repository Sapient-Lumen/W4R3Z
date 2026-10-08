from __future__ import annotations

import json
from pathlib import Path

from micromax_editor.startup import create_editor_runtime
from micromax_editor.workspace_trust import workspace_trust_policy


def _plugin(root: Path, name: str, source: str, *, meta: dict[str, object] | None = None) -> Path:
    plug = root / name
    plug.mkdir()
    (plug / "init.mx").write_text(source, encoding="utf-8")
    if meta is not None:
        (plug / "plugin.json").write_text(json.dumps(meta), encoding="utf-8")
    return plug


def test_workspace_trust_policy_names_automatic_code_loading_rules() -> None:
    trusted = workspace_trust_policy("trusted")
    restricted = workspace_trust_policy("restricted")

    assert trusted.auto_load_plugins is True
    assert trusted.auto_load_user_init is True
    assert restricted.auto_load_plugins is False
    assert restricted.auto_load_user_init is False
    assert restricted.model()["schema"] == "micromax.workspace-trust.v1"


def test_restricted_startup_scans_plugins_without_evaluating_source(tmp_path, monkeypatch) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "probe", ': init "plugin ran" "ed.msg" hostcall ;\n: probe-word "ran" ;\n')
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    pm = runtime.plugin_manager

    assert runtime.trust_policy.state == "restricted"
    assert "probe" in pm.candidates
    assert "probe" not in pm.plugins
    assert ed.plugin_inventory_rows() == [["probe", "available", "", "", 0]]
    assert "plugin ran" not in ed.messages
    try:
        ed.vm.eval("use probe probe-word", filename="<restricted-test>")
    except Exception as exc:
        assert "probe" in str(exc) or "word not found" in str(exc)
    else:  # pragma: no cover - defensive proof that source did not evaluate
        raise AssertionError("restricted startup evaluated plugin source")


def test_restricted_startup_does_not_load_user_init(tmp_path, monkeypatch) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    init = tmp_path / "init.mx"
    init.write_text(': from-init "loaded" ;\n', encoding="utf-8")
    monkeypatch.setenv("MICROMAX_INIT", str(init))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor

    assert "workspace restricted: user init not loaded" in ed.messages
    try:
        ed.vm.eval("from-init", filename="<restricted-init-test>")
    except Exception as exc:
        assert "from-init" in str(exc) or "word not found" in str(exc)
    else:  # pragma: no cover - defensive proof that user init did not evaluate
        raise AssertionError("restricted startup evaluated user init")


def test_trusted_startup_preserves_plugin_and_user_init_autoload(tmp_path, monkeypatch) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "probe", ': init "plugin ran" "ed.msg" hostcall ;\n: probe-word "ran" ;\n')
    init = tmp_path / "init.mx"
    init.write_text(': from-init "loaded" ;\n', encoding="utf-8")
    monkeypatch.setenv("MICROMAX_INIT", str(init))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="trusted")
    ed = runtime.editor

    assert runtime.trust_policy.state == "trusted"
    assert "probe" in runtime.plugin_manager.plugins
    assert "plugin ran" in ed.messages
    ed.vm.eval("use probe probe-word from-init", filename="<trusted-test>")
    assert ed.vm.stack[-2:] == ["ran", "loaded"]


def test_trust_state_hostcall_reports_startup_policy(tmp_path, monkeypatch) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    monkeypatch.setenv("MICROMAX_INIT", str(tmp_path / "missing-init.mx"))

    runtime = create_editor_runtime(plugins_root=root, workspace_trust="restricted")
    ed = runtime.editor
    ed.vm.eval("trust-state", filename="<trust-state-test>")
    model = ed.vm.stack.pop()

    assert model["schema"] == "micromax.workspace-trust.v1"
    assert model["state"] == "restricted"
    assert model["auto_load_plugins"] == 0
    assert model["auto_load_user_init"] == 0

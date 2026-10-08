from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)

    (proj / "macros" / "sig.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "sig",
                "steps": [
                    {"type": "Return", "value_expr": '"OK"', "out_var": "return_value"},
                ],
            }
        )
    )

    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "p",
                "macros": {"sig": "macros/sig.yaml"},
                "bindings": [
                    {
                        "keys": "Mod4+Shift+P",
                        "macro": "sig",
                        "description": "Run signature",
                    },
                    {
                        "keys": "Mod4+K",
                        "macro": "sig",
                        "description": "Scoped",
                        "when": {"class": "Firefox"},
                    },
                ],
            }
        )
    )
    return proj


def test_gen_wm_config_hyprland_emits_bindr_and_require_window(tmp_path: Path):
    proj = _make_project(tmp_path)

    result = runner.invoke(app, ["gen-wm-config", str(proj), "--wm", "hyprland"])
    assert result.exit_code == 0, result.output

    text = result.output
    assert "# VHK hyprland bindings" in text

    # Basic bind should be bindrd (release + description).
    assert "bindrd = SUPER SHIFT, P, Run signature, exec," in text

    # Scoped bind should include --require-window JSON selector.
    assert "bindrd = SUPER, K, Scoped, exec," in text
    assert "--require-window" in text
    assert '"class":"Firefox"' in text


def test_gen_wm_config_hyprland_via_bus_uses_emitter_and_payload_selector(tmp_path: Path, monkeypatch):
    proj = _make_project(tmp_path)

    runtime = tmp_path / "run"
    runtime.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime))

    result = runner.invoke(app, ["gen-wm-config", str(proj), "--wm", "hyprland", "--via-bus"])
    assert result.exit_code == 0, result.output

    text = result.output
    assert "vhk-emit" in text
    # Hyprland scoped binds should NOT use --require-window when using bus dispatch.
    assert "--require-window" not in text
    assert "require_window" in text
    assert "Firefox" in text


def test_run_require_window_skips_when_not_matching(tmp_path: Path, monkeypatch):
    proj = _make_project(tmp_path)

    import vhk.system.active_window as aw

    class FakeConn:
        def __init__(self, socket_path=None, timeout=2.0):
            pass

        def get_tree(self):
            # focused window is Chromium, not Firefox.
            return {
                "type": "root",
                "nodes": [
                    {
                        "type": "workspace",
                        "name": "1",
                        "nodes": [
                            {
                                "focused": True,
                                "window_properties": {"class": "Chromium", "title": "Chromium"},
                            }
                        ],
                        "floating_nodes": [],
                    }
                ],
                "floating_nodes": [],
            }

    monkeypatch.setenv("I3SOCK", "/tmp/fake.sock")
    monkeypatch.setattr(aw, "discover_socket_path", lambda: "/tmp/fake.sock")
    monkeypatch.setattr(aw, "I3Connection", FakeConn)

    selector = json.dumps({"class": "Firefox"})
    result = runner.invoke(app, ["run", str(proj), "sig", "--quiet", "--print-return", "--require-window", selector])
    assert result.exit_code == 0, result.output
    assert result.output == ""


def test_run_require_window_runs_when_matching(tmp_path: Path, monkeypatch):
    proj = _make_project(tmp_path)

    import vhk.system.active_window as aw

    class FakeConn:
        def __init__(self, socket_path=None, timeout=2.0):
            pass

        def get_tree(self):
            return {
                "type": "root",
                "nodes": [
                    {
                        "type": "workspace",
                        "name": "1",
                        "nodes": [
                            {
                                "focused": True,
                                "window_properties": {"class": "Firefox", "title": "Mozilla Firefox"},
                            }
                        ],
                        "floating_nodes": [],
                    }
                ],
                "floating_nodes": [],
            }

    monkeypatch.setenv("I3SOCK", "/tmp/fake.sock")
    monkeypatch.setattr(aw, "discover_socket_path", lambda: "/tmp/fake.sock")
    monkeypatch.setattr(aw, "I3Connection", FakeConn)

    selector = json.dumps({"class": "Firefox"})
    result = runner.invoke(app, ["run", str(proj), "sig", "--quiet", "--print-return", "--require-window", selector])
    assert result.exit_code == 0, result.output
    assert result.output == "OK"

from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.loader import load_project
from vhk.project.wm_bindings import build_wm_binding_manifest, default_wm_binding_key


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "proj space"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "macros" / "deploy.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "deploy",
                "group": "Release",
                "description": "Ship the current build",
                "steps": [{"type": "Return", "value": "ok"}],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj",
                "settings": {"event_log": False},
                "macros": {"deploy": "macros/deploy.yaml"},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return project_dir


def test_default_wm_binding_key_defaults() -> None:
    assert default_wm_binding_key("i3") == "$mod+Shift+p"
    assert default_wm_binding_key("sway") == "$mod+Shift+p"
    assert default_wm_binding_key("hyprland") == "$mainMod, P"


def test_build_wm_binding_manifest_for_i3_rofi_mode(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    manifest = build_wm_binding_manifest(
        project,
        wm="i3",
        launcher="rofi-mode",
        launcher_path=tmp_path / "bin" / "vhk-proj-palette",
        extra_modes=["drun"],
        mode_name="Project Macros",
    )
    assert manifest.wm == "i3"
    assert manifest.launcher == "rofi-mode"
    assert manifest.mode_name == "Project Macros"
    assert 'bindsym $mod+Shift+p exec --no-startup-id "rofi -show' in manifest.snippet
    assert "drun,Project Macros:" in manifest.snippet


def test_export_wm_bindings_cli_json_for_sway_palette_command(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    res = runner.invoke(
        app,
        [
            "export-wm-bindings",
            str(project_dir),
            "--wm",
            "sway",
            "--launcher",
            "palette-command",
            "--command",
            "python -m vhk.cli",
            "--json",
        ],
    )
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)
    assert payload["wm"] == "sway"
    assert payload["launcher"] == "palette-command"
    assert payload["key"] == "$mod+Shift+p"
    assert "python -m vhk.cli palette" in payload["command"]
    assert "bindsym $mod+Shift+p exec python -m vhk.cli palette" in payload["snippet"]


def test_export_wm_bindings_cli_hyprland_uwsm_stdout(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    res = runner.invoke(
        app,
        [
            "export-wm-bindings",
            str(project_dir),
            "--wm",
            "hyprland",
            "--launcher",
            "launcher-script",
            "--launcher-path",
            str(tmp_path / "bin" / "vhk-proj-palette"),
            "--uwsm-app",
        ],
    )
    assert res.exit_code == 0, res.output
    assert "bind = $mainMod, P, exec, uwsm app --" in res.output
    assert str(tmp_path / "bin" / "vhk-proj-palette") in res.output


def test_export_wm_bindings_cli_writes_file(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    out = tmp_path / "i3" / "vhk-proj.conf"
    res = runner.invoke(
        app,
        [
            "export-wm-bindings",
            str(project_dir),
            str(out),
            "--wm",
            "i3",
            "--launcher",
            "launcher-script",
            "--launcher-path",
            str(tmp_path / "bin" / "vhk-proj-palette"),
        ],
    )
    assert res.exit_code == 0, res.output
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "# VHK launcher for proj" in text
    assert "bindsym $mod+Shift+p exec --no-startup-id" in text

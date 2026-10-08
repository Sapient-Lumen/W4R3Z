from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.loader import load_project
from vhk.project.wm_includes import (
    build_wm_include_manifest,
    default_wm_bootstrap_glob,
    default_wm_include_dir,
    default_wm_include_install_path,
    wm_bootstrap_line,
)


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "proj space"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "macros" / "deploy.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "deploy",
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



def test_default_wm_include_install_path_honors_xdg_config_home(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    out = default_wm_include_install_path(
        project,
        wm="sway",
        kind="launcher-mode",
        env={"XDG_CONFIG_HOME": str(tmp_path / "cfg")},
    )
    assert out == tmp_path / "cfg" / "sway" / "vhk" / "vhk-proj-launcher-mode.conf"
    assert default_wm_include_dir("hyprland", env={"XDG_CONFIG_HOME": str(tmp_path / "cfg")}) == tmp_path / "cfg" / "hypr" / "vhk"
    assert default_wm_bootstrap_glob("i3", env={"XDG_CONFIG_HOME": str(tmp_path / "cfg")}) == tmp_path / "cfg" / "i3" / "vhk" / "*.conf"
    assert wm_bootstrap_line("hyprland", env={"XDG_CONFIG_HOME": str(tmp_path / "cfg")}) == f"source = {tmp_path / 'cfg' / 'hypr' / 'vhk' / '*.conf'}"
    from vhk.project.wm_includes import default_wm_parent_config_path
    assert default_wm_parent_config_path("sway", env={"XDG_CONFIG_HOME": str(tmp_path / "cfg")}) == tmp_path / "cfg" / "sway" / "config"



def test_build_wm_include_manifest_for_i3_binding_contains_bootstrap_line(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    manifest = build_wm_include_manifest(
        project,
        wm="i3",
        kind="binding",
        install_path=tmp_path / "cfg" / "i3" / "vhk" / "proj.conf",
        launcher="rofi-mode",
        launcher_path=tmp_path / "bin" / "vhk-proj-rofi",
        extra_modes=["drun"],
        mode_name="Project Macros",
    )
    assert manifest.wm == "i3"
    assert manifest.kind == "binding"
    assert manifest.bootstrap_line == f"include {tmp_path / 'cfg' / 'i3' / 'vhk' / '*.conf'}"
    assert 'bindsym $mod+Shift+p exec --no-startup-id "rofi -show' in manifest.snippet



def test_export_wm_include_cli_json_for_hyprland_launcher_mode(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    res = runner.invoke(
        app,
        [
            "export-wm-include",
            str(project_dir),
            "--wm",
            "hyprland",
            "--kind",
            "launcher-mode",
            "--mode-enter",
            "Mod4+Shift+o",
            "--launcher",
            "palette-command",
            "--command",
            "python -m vhk.cli",
            "--json",
        ],
    )
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)
    assert payload["wm"] == "hyprland"
    assert payload["kind"] == "launcher-mode"
    assert payload["bootstrap_line"].startswith("source = ")
    assert payload["install_path"].endswith("vhk-proj-launcher-mode.conf")
    assert "submap = vhk-launch, reset" in payload["snippet"]



def test_export_wm_include_cli_install_for_sway_writes_file_and_hint(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))
    res = runner.invoke(
        app,
        [
            "export-wm-include",
            str(project_dir),
            "--wm",
            "sway",
            "--kind",
            "binding",
            "--install",
            "--launcher",
            "palette-command",
            "--command",
            "python -m vhk.cli",
        ],
    )
    assert res.exit_code == 0, res.output
    out = tmp_path / "cfg" / "sway" / "vhk" / "vhk-proj-binding.conf"
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "bindsym $mod+Shift+p exec python -m vhk.cli palette" in text
    assert "include" in res.output
    assert "cfg/sway/vhk" in res.output



def test_export_wm_include_cli_requires_mode_enter_for_launcher_mode(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    res = runner.invoke(
        app,
        [
            "export-wm-include",
            str(project_dir),
            "--wm",
            "sway",
            "--kind",
            "launcher-mode",
        ],
    )
    assert res.exit_code == 1
    assert "--mode-enter is required" in res.output

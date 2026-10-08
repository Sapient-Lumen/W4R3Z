from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.loader import load_project
from vhk.project.wm_bundle import build_wm_bundle_manifest


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
                "icon": "system-run",
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



def test_build_wm_bundle_manifest_for_i3_rofi_bundle_dir(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    bundle_dir = tmp_path / "bundle"
    manifest = build_wm_bundle_manifest(
        project,
        wm="i3",
        kind="binding",
        launcher="rofi-mode",
        output_dir=bundle_dir,
        mode_name="Project Macros",
        extra_modes=["drun"],
    )
    assert manifest.root_dir == str(bundle_dir)
    assert manifest.helper_path == str(bundle_dir / "bin" / "vhk-proj-palette")
    assert manifest.include_path == str(bundle_dir / "config" / "i3" / "vhk" / "vhk-proj-binding.conf")
    assert manifest.bootstrap_path == str(bundle_dir / "BOOTSTRAP.txt")
    assert manifest.manifest_path == str(bundle_dir / "vhk-wm-bundle.json")
    assert manifest.reload_command == "i3-msg reload"
    assert manifest.launcher_command.startswith("rofi -show 'Project Macros' -modes")
    assert f"include {bundle_dir / 'config' / 'i3' / 'vhk' / '*.conf'}" == manifest.bootstrap_line



def test_export_wm_bundle_cli_writes_bundle_files(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    bundle_dir = tmp_path / "bundle out"
    res = runner.invoke(
        app,
        [
            "export-wm-bundle",
            str(project_dir),
            str(bundle_dir),
            "--wm",
            "hyprland",
            "--kind",
            "binding",
            "--launcher",
            "palette-command",
            "--command",
            "python -m vhk.cli",
        ],
    )
    assert res.exit_code == 0, res.output
    manifest_path = bundle_dir / "vhk-wm-bundle.json"
    bootstrap_path = bundle_dir / "BOOTSTRAP.txt"
    include_path = bundle_dir / "config" / "hypr" / "vhk" / "vhk-proj-binding.conf"
    support_doc = bundle_dir / "docs" / "VHK_PUBLIC_SUPPORT.md"
    support_json = bundle_dir / "docs" / "VHK_BUNDLE_SUPPORT.json"
    assert manifest_path.exists()
    assert bootstrap_path.exists()
    assert include_path.exists()
    assert support_doc.exists()
    assert support_json.exists()
    support_payload = json.loads(support_json.read_text(encoding="utf-8"))
    assert support_payload["flagship_lane_id"]
    assert "docs/VHK_RELEASE_LANES.md" in support_payload["docs"]
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["launcher"] == "palette-command"
    assert payload["helper_path"] is None
    assert payload["reload_command"] == "hyprctl reload"
    assert payload["support_summary_path"].endswith("/docs/VHK_PUBLIC_SUPPORT.md")
    assert payload["support_json_path"].endswith("/docs/VHK_BUNDLE_SUPPORT.json")
    assert "source =" in bootstrap_path.read_text(encoding="utf-8")
    assert "bind = $mainMod, P, exec, python -m vhk.cli palette" in include_path.read_text(encoding="utf-8")
    assert "VHK public support for proj" in support_doc.read_text(encoding="utf-8")
    assert "Reload with:" in res.output
    assert "hyprctl reload" in res.output



def test_export_wm_bundle_cli_install_writes_xdg_targets(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)
    monkeypatch.setenv("XDG_BIN_HOME", str(tmp_path / "bin"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))
    res = runner.invoke(
        app,
        [
            "export-wm-bundle",
            str(project_dir),
            "--wm",
            "sway",
            "--kind",
            "launcher-mode",
            "--mode-enter",
            "$mod+Shift+o",
            "--launcher",
            "rofi-mode",
            "--command",
            "python -m vhk.cli",
        ],
    )
    assert res.exit_code == 1
    assert "Need an output directory or --install" in res.output

    res = runner.invoke(
        app,
        [
            "export-wm-bundle",
            str(project_dir),
            "--wm",
            "sway",
            "--kind",
            "launcher-mode",
            "--mode-enter",
            "$mod+Shift+o",
            "--launcher",
            "rofi-mode",
            "--command",
            "python -m vhk.cli",
            "--install",
        ],
    )
    assert res.exit_code == 0, res.output
    helper = tmp_path / "bin" / "vhk-proj-palette"
    include_path = tmp_path / "cfg" / "sway" / "vhk" / "vhk-proj-launcher-mode.conf"
    assert helper.exists()
    assert helper.stat().st_mode & 0o111
    assert include_path.exists()
    normalized = " ".join(res.output.split())
    assert "include " in normalized
    assert str(tmp_path / "cfg" / "sway" / "vhk") in normalized
    assert str(tmp_path / "cfg" / "sway" / "config") in normalized
    assert "*.con" in res.output
    assert "swaymsg reload" in normalized



def test_export_wm_bundle_cli_json_manifest_for_bundle_dir(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    bundle_dir = tmp_path / "bundle"
    res = runner.invoke(
        app,
        [
            "export-wm-bundle",
            str(project_dir),
            str(bundle_dir),
            "--wm",
            "i3",
            "--launcher",
            "launcher-script",
            "--launcher-backend",
            "fuzzel",
            "--json",
        ],
    )
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)
    assert payload["wm"] == "i3"
    assert payload["launcher"] == "launcher-script"
    assert payload["helper_kind"] == "launcher-script"
    assert payload["helper_path"].endswith("/bin/vhk-proj-palette")
    assert payload["include_path"].endswith("/config/i3/vhk/vhk-proj-binding.conf")
    assert payload["manifest_path"].endswith("/vhk-wm-bundle.json")
    assert payload["reload_command"] == "i3-msg reload"
    assert payload["support_summary_path"].endswith("/docs/VHK_PUBLIC_SUPPORT.md")
    assert payload["support_json_path"].endswith("/docs/VHK_BUNDLE_SUPPORT.json")

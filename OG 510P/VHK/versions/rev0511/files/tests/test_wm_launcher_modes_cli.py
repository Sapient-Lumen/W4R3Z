from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.loader import load_project
from vhk.project.prompt_profiles import make_prompt_profile_store
from vhk.project.wm_bindings import build_wm_binding_manifest
from vhk.project.wm_launcher_modes import build_wm_launcher_mode_manifest


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
                "presets": [
                    {
                        "name": "prod",
                        "description": "Deploy to production",
                        "icon": "cloud-upload",
                        "vars": {"env": "prod"},
                        "prompt_form": {
                            "fields": [
                                {"name": "version", "label": "Version"},
                            ]
                        },
                    }
                ],
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


def test_build_wm_binding_manifest_quotes_i3_rofi_command_with_commas(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    manifest = build_wm_binding_manifest(
        project,
        wm="i3",
        launcher="rofi-mode",
        launcher_path=tmp_path / "bin" / "vhk-proj-palette",
        extra_modes=["drun"],
        mode_name="Project Macros",
    )
    assert 'bindsym $mod+Shift+p exec --no-startup-id "rofi -show' in manifest.snippet
    assert "drun,Project Macros:" in manifest.snippet
    assert manifest.command.startswith("rofi -show")



def test_build_wm_launcher_mode_manifest_for_i3_includes_launcher_and_entry_actions(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    project = load_project(project_dir)
    store = make_prompt_profile_store(project.root_dir, ".vhk/prompt_profiles.json")
    store.save_profile("macro:deploy:preset:prod", "release", {"version": "1.2.3"})

    manifest = build_wm_launcher_mode_manifest(
        project,
        wm="i3",
        mode_enter="$mod+Shift+o",
        launcher="rofi-mode",
        launcher_key="p",
        launcher_path=tmp_path / "bin" / "vhk-proj-rofi",
        rofi_mode_name="Project Macros",
        extra_modes=["drun"],
        entry_keys=("1", "2", "3"),
        max_entries=2,
        include_profile_actions=True,
    )

    assert manifest.mode_name == "vhk-launch"
    assert manifest.launcher_key == "p"
    assert len(manifest.actions) == 3
    assert manifest.actions[0].kind == "launcher"
    assert manifest.actions[1].entry_id == "deploy"
    assert manifest.actions[2].entry_id in {"deploy@prod", "deploy@prod#release"}
    assert 'bindsym $mod+Shift+o mode "vhk-launch"' in manifest.snippet
    assert 'bindsym --release p exec --no-startup-id "rofi -show' in manifest.snippet
    assert 'bindsym --release 1 exec --no-startup-id' in manifest.snippet
    assert '; mode "default"' in manifest.snippet



def test_export_wm_launcher_mode_cli_json_for_hyprland_uwsm(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    store = make_prompt_profile_store(project_dir, ".vhk/prompt_profiles.json")
    store.save_profile("macro:deploy:preset:prod", "release", {"version": "1.2.3"})

    res = runner.invoke(
        app,
        [
            "export-wm-launcher-mode",
            str(project_dir),
            "--wm",
            "hyprland",
            "--mode-enter",
            "Mod4+Shift+o",
            "--launcher",
            "palette-command",
            "--uwsm-app",
            "--profile-actions",
            "--entry-keys",
            "1,2",
            "--max-entries",
            "2",
            "--json",
            "--command",
            "python -m vhk.cli",
        ],
    )
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)
    assert payload["wm"] == "hyprland"
    assert payload["mode_enter"] == "Mod4+Shift+o"
    assert payload["launcher"] == "palette-command"
    assert payload["launcher_key"] == "p"
    assert payload["uwsm_app"] is True
    assert payload["actions"][0]["kind"] == "launcher"
    assert payload["actions"][0]["command"].startswith("uwsm app -- python -m vhk.cli palette")
    assert "submap = vhk-launch, reset" in payload["snippet"]
    assert "bindrd = , P, Open VHK palette, exec, uwsm app --" in payload["snippet"]



def test_export_wm_launcher_mode_cli_writes_file(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    out = tmp_path / "sway" / "vhk-launch.conf"
    res = runner.invoke(
        app,
        [
            "export-wm-launcher-mode",
            str(project_dir),
            str(out),
            "--wm",
            "sway",
            "--mode-enter",
            "$mod+Shift+o",
            "--launcher",
            "launcher-script",
            "--launcher-path",
            str(tmp_path / "bin" / "vhk-proj-palette"),
            "--entry-keys",
            "a,s",
            "--max-entries",
            "1",
        ],
    )
    assert res.exit_code == 0, res.output
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "mode \"vhk-launch\" {" in text
    assert "bindsym --release p exec" in text
    assert "bindsym --release a exec" in text

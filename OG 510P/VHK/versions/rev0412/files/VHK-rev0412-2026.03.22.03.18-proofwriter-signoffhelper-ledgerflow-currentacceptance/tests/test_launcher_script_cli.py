from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.core.runner import RunResult
from vhk.project.launcher_script import default_launcher_install_path, render_launcher_script
from vhk.project.loader import load_project
from vhk.project.prompt_profiles import make_prompt_profile_store


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



def test_default_launcher_install_path_honors_xdg_bin_home(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    project = load_project(project_dir)

    out = default_launcher_install_path(project, env={"XDG_BIN_HOME": str(tmp_path / "xdgbin")})
    assert out == tmp_path / "xdgbin" / "vhk-proj-palette"



def test_render_launcher_script_embeds_palette_entry_execution(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    project = load_project(project_dir)
    store = make_prompt_profile_store(project.root_dir, ".vhk/prompt_profiles.json")
    store.save_profile("macro:deploy:preset:prod", "release", {"version": "9.9.9"})

    text = render_launcher_script(
        project,
        command="vhk",
        launcher_backend="fuzzel",
        include_profile_actions=True,
        include_profile_management_actions=True,
        alpha=True,
    )

    assert 'VHK_COMMAND = ["vhk"]' in text
    assert f"PROJECT_DIR = '{project.root_dir}'" in text
    assert '"--entry-id"' in text or "'--entry-id'" in text
    assert 'DEFAULT_BACKEND = \'fuzzel\'' in text
    assert 'VHK_LAUNCHER_CMD' in text
    assert 'ROFI_RETV' in text
    assert 'search_terms' in text
    assert '--profile-management-actions' in text
    assert '--alpha' in text



def test_export_launcher_script_cli_install_writes_executable(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    env = {"XDG_BIN_HOME": str(tmp_path / "xdgbin")}

    res = runner.invoke(app, ["export-launcher-script", str(project_dir), "--install"], env=env)
    assert res.exit_code == 0, res.output

    out = tmp_path / "xdgbin" / "vhk-proj-palette"
    assert out.exists()
    assert out.stat().st_mode & 0o111
    text = out.read_text(encoding="utf-8")
    assert "#!/usr/bin/env python3" in text
    assert '"palette"' in text



def test_export_launcher_script_cli_stdout_can_include_profile_management(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["export-launcher-script", str(project_dir), "--profile-management-actions", "--launcher-backend", "tofi"])
    assert res.exit_code == 0, res.output
    assert "#!/usr/bin/env python3" in res.output
    assert "DEFAULT_BACKEND = 'tofi'" in res.output
    assert "--profile-management-actions" in res.output



def test_palette_entry_id_runs_selected_entry_directly(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)

    import vhk.cli as cli_mod

    seen: dict[str, object] = {}

    def fake_run(self, macro_name, initial_vars=None):
        seen["macro"] = macro_name
        seen["vars"] = dict(initial_vars or {})
        return RunResult(ok=True, vars={"return_value": "ok"}, event_log=None)

    monkeypatch.setattr(cli_mod.Runner, "run", fake_run)
    monkeypatch.setattr(cli_mod, "_apply_preset_prompt_overlay", lambda *args, **kwargs: {"env": "prod", "version": "1.2.3"})

    res = runner.invoke(app, ["palette", str(project_dir), "--entry-id", "deploy@prod"])
    assert res.exit_code == 0, res.output
    assert seen["macro"] == "deploy"
    assert seen["vars"] == {"env": "prod", "version": "1.2.3"}



def test_palette_entry_id_no_run_prints_selected_id(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["palette", str(project_dir), "--entry-id", "deploy@prod", "--no-run"])
    assert res.exit_code == 0, res.output
    assert res.output.strip() == "deploy@prod"



def test_launcher_script_can_print_palette_json(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["export-launcher-script", str(project_dir)])
    assert res.exit_code == 0, res.output
    assert "Usage: launcher" in res.output
    assert "--list" in res.output


def test_generated_launcher_script_outputs_rofi_rows_with_metadata(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    project = load_project(project_dir)
    script = tmp_path / "launcher.py"
    script.write_text(
        render_launcher_script(project, command=f"{sys.executable} -m vhk.cli", launcher_backend="rofi"),
        encoding="utf-8",
    )

    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path.cwd() / "src")
    env["ROFI_RETV"] = "0"
    proc = subprocess.run([sys.executable, str(script)], cwd=Path.cwd(), env=env, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert "\0prompt\x1fproj" in proc.stdout
    assert "\x1ficon\x1fcloud-upload" in proc.stdout
    assert "\x1finfo\x1fdeploy@prod" in proc.stdout
    assert "\x1fmeta\x1f" in proc.stdout



def test_generated_launcher_script_can_execute_rofi_selected_entry(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    project = load_project(project_dir)
    script = tmp_path / "launcher.py"
    script.write_text(
        render_launcher_script(project, command=f"{sys.executable} -m vhk.cli", launcher_backend="rofi", include_presets=False),
        encoding="utf-8",
    )

    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path.cwd() / "src")
    env["ROFI_RETV"] = "1"
    env["ROFI_INFO"] = "deploy"
    proc = subprocess.run([sys.executable, str(script)], cwd=Path.cwd(), env=env, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr + proc.stdout


def test_generated_launcher_script_can_print_support_about_and_json(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    project = load_project(project_dir)
    script = tmp_path / "launcher.py"
    script.write_text(
        render_launcher_script(project, command=f"{sys.executable} -m vhk.cli", launcher_backend="rofi"),
        encoding="utf-8",
    )

    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path.cwd() / "src")

    about = subprocess.run([sys.executable, str(script), "--about"], cwd=Path.cwd(), env=env, capture_output=True, text=True)
    assert about.returncode == 0, about.stderr
    assert "VHK support posture for proj" in about.stdout
    assert "support posture" in about.stdout.lower()
    assert "docs/VHK_PUBLIC_SUPPORT.md" in about.stdout
    assert "Flagship release lane:" in about.stdout
    assert "docs/VHK_RELEASE_LANES.md" in about.stdout
    assert "Flagship deploy style:" in about.stdout
    assert "docs/VHK_RELEASE_DEPLOYMENT.md" in about.stdout

    support_json = subprocess.run([sys.executable, str(script), "--support-json"], cwd=Path.cwd(), env=env, capture_output=True, text=True)
    assert support_json.returncode == 0, support_json.stderr
    payload = json.loads(support_json.stdout)
    assert payload["project"]["name"] == "proj"
    assert "headline" in payload
    assert payload["flagship_lane_id"]
    assert payload["release_lane_overview"]["lane_count"] >= 1
    assert payload["flagship_deploy_style"]
    assert payload["release_deploy_overview"]["lane_count"] >= 1

from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.loader import load_project
from vhk.project.rofi_mode import build_rofi_mode_manifest, default_rofi_mode_name


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


def test_default_rofi_mode_name_uses_project_slug(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    assert default_rofi_mode_name(project) == "vhk-proj"


def test_build_rofi_mode_manifest_can_include_extra_modes(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    manifest = build_rofi_mode_manifest(
        project,
        script_path=tmp_path / "vhk-proj-palette",
        mode_name="Project Macros",
        show_icons=True,
        extra_modes=["drun", "run"],
    )
    assert manifest.mode_name == "Project Macros"
    assert manifest.rofi_argv[:4] == ("rofi", "-show", "Project Macros", "-modes")
    assert manifest.rofi_argv[4] == f"drun,run,Project Macros:{tmp_path / 'vhk-proj-palette'}"
    assert manifest.rofi_argv[-1] == "-show-icons"
    assert "'Project Macros'" in manifest.command


def test_export_rofi_mode_requires_output_or_install(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    res = runner.invoke(app, ["export-rofi-mode", str(project_dir)])
    assert res.exit_code == 1
    assert "Need an output path or --install" in res.output


def test_export_rofi_mode_cli_writes_script_and_prints_command(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    out = tmp_path / "bin" / "vhk-proj-rofi"
    res = runner.invoke(
        app,
        [
            "export-rofi-mode",
            str(project_dir),
            str(out),
            "--mode-name",
            "Project Macros",
            "--extra-mode",
            "drun",
        ],
    )
    assert res.exit_code == 0, res.output
    assert out.exists()
    assert out.stat().st_mode & 0o111
    text = out.read_text(encoding="utf-8")
    assert "ROFI_RETV" in text
    assert "Wrote rofi mode launcher" in res.output
    normalized = " ".join(res.output.split())
    assert "rofi -show 'Project Macros' -modes" in normalized
    assert "drun,Project Macros:" in normalized
    assert str(out.parent) in normalized
    assert out.name in normalized


def test_export_rofi_mode_cli_json_manifest(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    out = tmp_path / "bin" / "vhk-proj-rofi"
    res = runner.invoke(
        app,
        ["export-rofi-mode", str(project_dir), str(out), "--json", "--no-show-icons"],
    )
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)
    assert payload["mode_name"] == "vhk-proj"
    assert payload["script_path"] == str(out)
    assert payload["rofi_argv"][:4] == ["rofi", "-show", "vhk-proj", "-modes"]
    assert payload["rofi_argv"][4] == f"vhk-proj:{out}"
    assert "-show-icons" not in payload["rofi_argv"]

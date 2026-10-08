from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.desktop_entry import (
    default_desktop_install_path,
    desktop_exec_quote_arg,
    render_desktop_entry,
)
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
    (project_dir / "macros" / "capture.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "capture",
                "description": "Take a screenshot",
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
                "macros": {
                    "capture": "macros/capture.yaml",
                    "deploy": "macros/deploy.yaml",
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return project_dir



def test_desktop_exec_quote_arg_handles_spaces_and_percent() -> None:
    assert desktop_exec_quote_arg("simple") == "simple"
    assert desktop_exec_quote_arg("hello world") == '"hello world"'
    assert desktop_exec_quote_arg("100%") == "100%%"



def test_render_desktop_entry_includes_palette_and_actions(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    project = load_project(project_dir)
    store = make_prompt_profile_store(project.root_dir, ".vhk/prompt_profiles.json")
    store.save_profile("macro:deploy:preset:prod", "release", {"version": "9.9.9"})

    text = render_desktop_entry(
        project,
        profile_store=store,
        alpha=True,
        max_actions=8,
    )

    assert "[Desktop Entry]" in text
    assert f'Exec=vhk palette "{project.root_dir}"' in text
    assert "Actions=" in text
    assert "[Desktop Action deploy-prod-release]" in text
    assert f'Exec=vhk run "{project.root_dir}" deploy --preset prod --prompt-profile release' in text
    assert "Icon=cloud-upload" in text
    assert "X-VHK-Project=proj" in text
    assert "X-VHK-Support-Headline=" in text
    assert "docs/VHK_PUBLIC_SUPPORT.md" in text
    assert "docs/VHK_RELEASE_LANES.md" in text
    assert "docs/VHK_RELEASE_DEPLOYMENT.md" in text
    assert "X-VHK-Release-Flagship=" in text
    assert "X-VHK-Release-Reference=" in text
    assert "X-VHK-Release-DeployStyle=" in text



def test_default_desktop_install_path_honors_xdg_data_home(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    project = load_project(project_dir)

    out = default_desktop_install_path(project, env={"XDG_DATA_HOME": str(tmp_path / "xdgdata")})
    assert out == tmp_path / "xdgdata" / "applications" / "vhk-proj.desktop"



def test_export_desktop_entry_cli_install_writes_file(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    env = {"XDG_DATA_HOME": str(tmp_path / "xdgdata")}

    res = runner.invoke(app, ["export-desktop-entry", str(project_dir), "--install"], env=env)
    assert res.exit_code == 0, res.output

    out = tmp_path / "xdgdata" / "applications" / "vhk-proj.desktop"
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "[Desktop Entry]" in text
    assert "Exec=vhk palette" in text



def test_export_desktop_entry_cli_stdout_can_disable_actions(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["export-desktop-entry", str(project_dir), "--no-actions", "--icon", ""]) 
    assert res.exit_code == 0, res.output
    assert "[Desktop Entry]" in res.output
    assert "Actions=" not in res.output
    assert "Icon=" not in res.output

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "reply.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "reply",
                "steps": [
                    {"type": "PromptForm", "title": "Reply", "fields": [{"name": "name", "label": "Name"}]},
                    {"type": "TypeText", "text": "Hello ${reply.name}"},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "macros" / "vision.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "vision",
                "steps": [
                    {"type": "WaitForImage", "needle_path": "assets/button.png", "timeout_ms": 5000},
                    {"type": "MouseClickAt", "x": 100, "y": 200},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj",
                "settings": {"desktop_backend": "wayland"},
                "bindings": [{"keys": "Mod4+V", "macro": "vision"}],
                "hotstrings": [{"trigger": ":reply", "macro": "reply"}],
                "bus_watchers": [{"name": "refresh", "event": "proj.refresh", "macro": "vision"}],
            },
            sort_keys=False,
        )
    )
    return project_dir



def test_gen_setup_pack_writes_docs_and_scripts(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = project_dir / "docs"
    scripts_dir = project_dir / "scripts"

    res = runner.invoke(app, ["gen-setup-pack", str(project_dir), "--no-session-check", "--quiet"])
    assert res.exit_code == 0, res.output

    guide = (docs_dir / "VHK_SETUP_GUIDE.md").read_text()
    matrix = (docs_dir / "VHK_SETUP_MATRIX.md").read_text()
    plan = json.loads((docs_dir / "VHK_SETUP_PLAN.json").read_text())
    apply_script = (scripts_dir / "vhk_apply_setup_recipes.sh").read_text()
    verify_script = (scripts_dir / "vhk_verify_setup_recipes.sh").read_text()
    package_script = (scripts_dir / "vhk_install_toolchain_packages.sh").read_text()

    assert "# VHK setup guide for proj" in guide
    assert "## Toolchain package bootstrap" in guide
    assert "## Setup recipes" in guide
    assert "scripts/vhk_apply_setup_recipes.sh" in guide
    assert "scripts/vhk_install_toolchain_packages.sh" in guide

    assert "# VHK setup recipe matrix for proj" in matrix
    assert "Runnable generator commands" in matrix
    assert "## Toolchain package groups" in matrix

    assert plan["project"]["name"] == "proj"
    assert plan["source_contract"] == "setup_recipes"
    assert plan["setup_summary"]["recipe_count"] >= 1
    assert plan["toolchain_packages"]["package_count"] >= 1
    assert any(item["id"] == "launcher-entrypoint-install" for item in plan["setup_recipes"])
    launcher_recipe = next(item for item in plan["setup_recipes"] if item["id"] == "launcher-entrypoint-install")
    assert any(cmd.startswith("vhk ") for cmd in launcher_recipe["generator_commands"])
    assert all("/tmp/" not in cmd for cmd in launcher_recipe["generator_commands"])

    assert apply_script.startswith("#!/usr/bin/env sh\n")
    assert 'RECIPE_FILTER="${RECIPE_FILTER:-all}"' in apply_script
    assert "launcher-entrypoint-install" in apply_script
    assert "vhk export-desktop-entry . ./build/vhk-project.desktop" in apply_script

    assert verify_script.startswith("#!/usr/bin/env sh\n")
    assert "Running VHK verification recipe commands" in verify_script

    assert package_script.startswith("#!/usr/bin/env sh\n")
    assert "RUN_INSTALL=" in package_script
    assert "Running VHK toolchain package bootstrap" in package_script
    assert "sudo apt-get install -y" in package_script



def test_gen_setup_pack_can_select_outputs_and_scripts_are_runnable(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = tmp_path / "setup-docs"
    scripts_dir = tmp_path / "setup-scripts"

    res = runner.invoke(
        app,
        [
            "gen-setup-pack",
            str(project_dir),
            "--out-dir",
            str(docs_dir),
            "--script-dir",
            str(scripts_dir),
            "--no-session-check",
            "--no-matrix",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    assert (docs_dir / "VHK_SETUP_GUIDE.md").exists()
    assert not (docs_dir / "VHK_SETUP_MATRIX.md").exists()
    assert (docs_dir / "VHK_SETUP_PLAN.json").exists()
    assert (scripts_dir / "vhk_apply_setup_recipes.sh").exists()
    assert (scripts_dir / "vhk_verify_setup_recipes.sh").exists()
    assert (scripts_dir / "vhk_install_toolchain_packages.sh").exists()

    proc = subprocess.run(
        ["sh", str(scripts_dir / "vhk_apply_setup_recipes.sh")],
        cwd=project_dir,
        env={"RECIPE_FILTER": "nonexistent"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "Running VHK generator recipe commands" in proc.stdout

    pkg_proc = subprocess.run(
        ["sh", str(scripts_dir / "vhk_install_toolchain_packages.sh")],
        cwd=project_dir,
        env={"PACKAGE_FILTER": "text-injection", "PACKAGE_MANAGER": "apt", "RUN_INSTALL": "0"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert pkg_proc.returncode == 0
    assert "Running VHK toolchain package bootstrap" in pkg_proc.stdout
    assert "Detected package manager: apt" in pkg_proc.stdout
    assert "dry-run" in pkg_proc.stdout

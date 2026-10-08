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


def test_gen_release_deploy_pack_writes_expected_artifacts(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = project_dir / "docs"
    scripts_dir = project_dir / "scripts"

    res = runner.invoke(app, ["gen-release-deploy-pack", str(project_dir), "--quiet"])
    assert res.exit_code == 0, res.output

    deploy_doc = (docs_dir / "VHK_RELEASE_DEPLOYMENT.md").read_text()
    snippets_doc = (docs_dir / "VHK_RELEASE_INSTALL_SNIPPETS.md").read_text()
    plan = json.loads((docs_dir / "VHK_RELEASE_DEPLOY_PLAN.json").read_text())
    refresh_script = (scripts_dir / "vhk_refresh_release_deploy.sh").read_text()

    assert "# VHK release deployment guide for proj" in deploy_doc
    assert "## Release-lane deployment choices" in deploy_doc
    assert "GNOME Wayland portal-first" in deploy_doc
    assert "Deploy style: `desktop-autostart`" in deploy_doc
    assert "wlroots-style Wayland remapper-first" in deploy_doc
    assert "Deploy style: `remapper-service`" in deploy_doc

    assert "# VHK release install snippets for proj" in snippets_doc
    assert "espanso service register" in snippets_doc
    assert "systemctl --user enable --now ydotoold-vhk-wlroots-wayland.service" in snippets_doc
    assert "vhk export-wm-bundle . ./build/release-lanes/x11-desktop/wm-bundle --wm i3 --kind binding --launcher rofi-mode --force" in snippets_doc

    assert plan["project"]["name"] == "proj"
    assert plan["source_contract"] == "release_deploy_pack"
    assert plan["deploy_summary"]["flagship_lane_id"] == "gnome-wayland"
    assert plan["deploy_summary"]["flagship_deploy_style"] == "desktop-autostart"

    lanes = {item["profile_id"]: item for item in plan["deploy_lanes"]}
    assert lanes["gnome-wayland"]["deploy_style"] == "desktop-autostart"
    assert any(item["path"].endswith("applications/vhk-proj-gnome-wayland.desktop") for item in lanes["gnome-wayland"]["artifact_subset"])
    assert "text-injection" in lanes["gnome-wayland"]["priority_package_group_ids"]
    assert lanes["x11-desktop"]["deploy_style"] == "wm-bundle"
    assert any("export-wm-bundle" in item.get("generator_command", "") for item in lanes["x11-desktop"]["artifact_subset"])
    assert lanes["wlroots-wayland"]["deploy_style"] == "remapper-service"
    assert any("gen-ydotoold-service" in item.get("generator_command", "") for item in lanes["wlroots-wayland"]["artifact_subset"])

    assert refresh_script.startswith("#!/usr/bin/env sh\n")
    assert "Collecting VHK release-deploy evidence" in refresh_script
    assert "vhk gen-release-deploy-pack . --force --quiet" in refresh_script


def test_gen_release_deploy_pack_can_limit_profiles_and_refresh_script_runs(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = tmp_path / "deploy-docs"
    scripts_dir = tmp_path / "deploy-scripts"

    res = runner.invoke(
        app,
        [
            "gen-release-deploy-pack",
            str(project_dir),
            "--out-dir",
            str(docs_dir),
            "--script-dir",
            str(scripts_dir),
            "--target-profile",
            "gnome-wayland",
            "--target-profile",
            "wlroots-wayland",
            "--no-snippets-doc",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    assert (docs_dir / "VHK_RELEASE_DEPLOYMENT.md").exists()
    assert not (docs_dir / "VHK_RELEASE_INSTALL_SNIPPETS.md").exists()
    assert (docs_dir / "VHK_RELEASE_DEPLOY_PLAN.json").exists()
    assert (scripts_dir / "vhk_refresh_release_deploy.sh").exists()

    plan = json.loads((docs_dir / "VHK_RELEASE_DEPLOY_PLAN.json").read_text())
    profile_ids = [item["profile_id"] for item in plan["deploy_lanes"]]
    assert profile_ids == ["gnome-wayland", "wlroots-wayland"]

    proc = subprocess.run(
        ["sh", str(scripts_dir / "vhk_refresh_release_deploy.sh")],
        cwd=project_dir,
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "Collecting VHK release-deploy evidence" in proc.stdout
    assert "Release-deploy refresh complete." in proc.stdout

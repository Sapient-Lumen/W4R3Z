from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.support_posture import summarize_support_posture


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


def test_summarize_support_posture_builds_release_deploy_overview_on_fresh_project(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    posture = summarize_support_posture(project_dir, prefer_cached=False)

    assert posture["release_lane_overview"]["lane_count"] >= 1
    assert posture["release_deploy_overview"]["lane_count"] >= 1
    assert posture["flagship_deploy_style"]


def test_gen_release_stage_pack_writes_expected_artifacts(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = project_dir / "docs"
    scripts_dir = project_dir / "scripts"
    build_dir = project_dir / "build" / "release-stage"

    res = runner.invoke(app, ["gen-release-stage-pack", str(project_dir), "--quiet"])
    assert res.exit_code == 0, res.output

    guide_doc = (docs_dir / "VHK_RELEASE_STAGE.md").read_text()
    matrix_doc = (docs_dir / "VHK_RELEASE_STAGE_MATRIX.md").read_text()
    plan = json.loads((docs_dir / "VHK_RELEASE_STAGE_PLAN.json").read_text())
    refresh_script = (scripts_dir / "vhk_refresh_release_stage.sh").read_text()

    assert "# VHK release staging guide for proj" in guide_doc
    assert "## Stage lanes" in guide_doc
    assert "GNOME Wayland portal-first" in guide_doc
    assert "wlroots-style Wayland remapper-first" in guide_doc

    assert "# VHK release stage matrix for proj" in matrix_doc
    assert "Install script:" in matrix_doc
    assert "Staged artifacts:" in matrix_doc

    assert plan["project"]["name"] == "proj"
    assert plan["source_contract"] == "release_stage_pack"
    assert plan["stage_summary"]["flagship_lane_id"] == "gnome-wayland"
    assert "wlroots-wayland" in plan["stage_summary"]["experimental_lane_ids"]

    lanes = {item["profile_id"]: item for item in plan["stage_lanes"]}
    assert lanes["gnome-wayland"]["deploy_style"] == "desktop-autostart"
    assert lanes["gnome-wayland"]["assemble_script_path"].endswith("/gnome-wayland/assemble_payload.sh")
    assert lanes["x11-desktop"]["deploy_style"] == "wm-bundle"
    assert lanes["wlroots-wayland"]["deploy_style"] == "remapper-service"
    assert any(
        "export-wm-bundle" in row.get("generator_command", "")
        for row in lanes["x11-desktop"]["artifact_manifest"]
    )

    assert refresh_script.startswith("#!/usr/bin/env sh\n")
    assert "Collecting VHK release-stage evidence" in refresh_script
    assert "vhk gen-release-stage-pack . --force --quiet" in refresh_script

    lane_root = build_dir / "gnome-wayland"
    assert (lane_root / "README.md").exists()
    assert (lane_root / "install.sh").exists()
    assert (lane_root / "verify.sh").exists()
    assert (lane_root / "assemble_payload.sh").exists()
    assert (lane_root / "vhk_release_stage.json").exists()
    assert (lane_root / "payload").exists()

    install_text = (lane_root / "install.sh").read_text()
    verify_text = (lane_root / "verify.sh").read_text()
    assemble_text = (lane_root / "assemble_payload.sh").read_text()
    readme_text = (lane_root / "README.md").read_text()

    assert "espanso service register" in install_text
    assert "vhk doctor --json" in verify_text
    assert "export-desktop-entry" in assemble_text
    assert "payload/" in readme_text


def test_gen_release_stage_pack_can_limit_profiles_and_refresh_script_runs(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = tmp_path / "stage-docs"
    scripts_dir = tmp_path / "stage-scripts"
    build_dir = tmp_path / "stage-build"

    res = runner.invoke(
        app,
        [
            "gen-release-stage-pack",
            str(project_dir),
            "--out-dir",
            str(docs_dir),
            "--script-dir",
            str(scripts_dir),
            "--build-dir",
            str(build_dir),
            "--target-profile",
            "gnome-wayland",
            "--target-profile",
            "wlroots-wayland",
            "--no-matrix-doc",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    assert (docs_dir / "VHK_RELEASE_STAGE.md").exists()
    assert not (docs_dir / "VHK_RELEASE_STAGE_MATRIX.md").exists()
    assert (docs_dir / "VHK_RELEASE_STAGE_PLAN.json").exists()
    assert (scripts_dir / "vhk_refresh_release_stage.sh").exists()
    assert (build_dir / "gnome-wayland").exists()
    assert (build_dir / "wlroots-wayland").exists()

    plan = json.loads((docs_dir / "VHK_RELEASE_STAGE_PLAN.json").read_text())
    profile_ids = [item["profile_id"] for item in plan["stage_lanes"]]
    assert profile_ids == ["gnome-wayland", "wlroots-wayland"]

    proc = subprocess.run(
        ["sh", str(scripts_dir / "vhk_refresh_release_stage.sh")],
        cwd=project_dir,
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "Collecting VHK release-stage evidence" in proc.stdout
    assert "Release-stage refresh complete." in proc.stdout

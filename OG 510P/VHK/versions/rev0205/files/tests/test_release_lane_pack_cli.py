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


def test_gen_release_lane_pack_writes_expected_artifacts(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = project_dir / "docs"
    scripts_dir = project_dir / "scripts"

    res = runner.invoke(app, ["gen-release-lane-pack", str(project_dir), "--quiet"])
    assert res.exit_code == 0, res.output

    lanes_doc = (docs_dir / "VHK_RELEASE_LANES.md").read_text()
    snippets_doc = (docs_dir / "VHK_RELEASE_SNIPPETS.md").read_text()
    plan = json.loads((docs_dir / "VHK_RELEASE_LANE_PLAN.json").read_text())
    refresh_script = (scripts_dir / "vhk_refresh_release_lanes.sh").read_text()

    assert "# VHK release lanes for proj" in lanes_doc
    assert "## Recommended release lanes" in lanes_doc
    assert "GNOME Wayland portal-first" in lanes_doc
    assert "Generic X11 desktop" in lanes_doc
    assert "Release level: `reference`" in lanes_doc

    assert "# VHK release snippets for proj" in snippets_doc
    assert "## Copy-ready public support snippets" in snippets_doc
    assert "Reference Linux lane: GNOME Wayland portal-first" in snippets_doc
    assert "Supported Linux lane: KDE Wayland portal-friendly" in snippets_doc
    assert "## Copy-ready support handoff snippets" in snippets_doc

    assert plan["project"]["name"] == "proj"
    assert plan["source_contract"] == "release_lane_pack"
    assert plan["release_summary"]["reference_lane_ids"] == ["gnome-wayland"]
    assert "kde-wayland" in plan["release_summary"]["supported_lane_ids"]
    assert "x11-desktop" in plan["release_summary"]["caveated_lane_ids"]

    lanes = {item["profile_id"]: item for item in plan["release_lanes"]}
    assert lanes["gnome-wayland"]["release_level"] == "reference"
    assert lanes["gnome-wayland"]["route_groups"][1]["primary_route_id"] == "portal-shortcuts-route"
    assert lanes["kde-wayland"]["release_level"] == "supported"
    assert lanes["wlroots-wayland"]["release_level"] == "experimental"

    assert refresh_script.startswith("#!/usr/bin/env sh\n")
    assert "Collecting VHK release-lane evidence" in refresh_script
    assert "vhk gen-release-lane-pack . --force --quiet" in refresh_script


def test_gen_release_lane_pack_can_limit_profiles_and_refresh_script_runs(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = tmp_path / "release-docs"
    scripts_dir = tmp_path / "release-scripts"

    res = runner.invoke(
        app,
        [
            "gen-release-lane-pack",
            str(project_dir),
            "--out-dir",
            str(docs_dir),
            "--script-dir",
            str(scripts_dir),
            "--target-profile",
            "x11-desktop",
            "--target-profile",
            "gnome-wayland",
            "--no-snippets-doc",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    assert (docs_dir / "VHK_RELEASE_LANES.md").exists()
    assert not (docs_dir / "VHK_RELEASE_SNIPPETS.md").exists()
    assert (docs_dir / "VHK_RELEASE_LANE_PLAN.json").exists()
    assert (scripts_dir / "vhk_refresh_release_lanes.sh").exists()

    plan = json.loads((docs_dir / "VHK_RELEASE_LANE_PLAN.json").read_text())
    profile_ids = [item["profile_id"] for item in plan["release_lanes"]]
    assert profile_ids == ["gnome-wayland", "x11-desktop"]

    proc = subprocess.run(
        ["sh", str(scripts_dir / "vhk_refresh_release_lanes.sh")],
        cwd=project_dir,
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "Collecting VHK release-lane evidence" in proc.stdout
    assert "Release-lane refresh complete." in proc.stdout

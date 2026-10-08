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


def test_gen_target_route_pack_writes_expected_artifacts(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = project_dir / "docs"
    scripts_dir = project_dir / "scripts"

    res = runner.invoke(app, ["gen-target-route-pack", str(project_dir), "--quiet"])
    assert res.exit_code == 0, res.output

    matrix_doc = (docs_dir / "VHK_TARGET_ROUTE_MATRIX.md").read_text()
    fixups_doc = (docs_dir / "VHK_TARGET_ROUTE_FIXUPS.md").read_text()
    plan = json.loads((docs_dir / "VHK_TARGET_ROUTE_PLAN.json").read_text())
    refresh_script = (scripts_dir / "vhk_compare_target_routes.sh").read_text()

    assert "# VHK target route matrix for proj" in matrix_doc
    assert "## Cross-profile route comparison" in matrix_doc
    assert "GNOME Wayland portal-first" in matrix_doc
    assert "wlroots-style Wayland remapper-first" in matrix_doc

    assert "# VHK target route fixups for proj" in fixups_doc
    assert "## Divergent groups that need explicit release decisions" in fixups_doc
    assert "`gnome-wayland` chooses `portal-shortcuts-route`" in fixups_doc
    assert "`wlroots-wayland` chooses `remapper-route`" in fixups_doc

    assert plan["project"]["name"] == "proj"
    assert plan["source_contract"] == "target_route_pack"
    assert plan["target_summary"]["profile_count"] == 4
    assert "trigger-entry" in plan["target_summary"]["divergent_groups"]
    assert "text-entry" in plan["target_summary"]["stable_groups"]

    profiles = {item["profile"]["id"]: item for item in plan["target_profiles"]}
    assert next(item for item in profiles["x11-desktop"]["reference_routes"] if item["selection_group"] == "trigger-entry")["route_id"] == "native-trigger-route"
    assert next(item for item in profiles["gnome-wayland"]["reference_routes"] if item["selection_group"] == "trigger-entry")["route_id"] == "portal-shortcuts-route"
    assert next(item for item in profiles["wlroots-wayland"]["reference_routes"] if item["selection_group"] == "trigger-entry")["route_id"] == "remapper-route"

    assert refresh_script.startswith("#!/usr/bin/env sh\n")
    assert "Collecting VHK target-route evidence" in refresh_script
    assert "vhk gen-target-route-pack . --force --quiet" in refresh_script


def test_gen_target_route_pack_can_limit_profiles_and_refresh_script_runs(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = tmp_path / "target-docs"
    scripts_dir = tmp_path / "target-scripts"

    res = runner.invoke(
        app,
        [
            "gen-target-route-pack",
            str(project_dir),
            "--out-dir",
            str(docs_dir),
            "--script-dir",
            str(scripts_dir),
            "--target-profile",
            "x11-desktop",
            "--target-profile",
            "wlroots-wayland",
            "--no-fixups-doc",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    assert (docs_dir / "VHK_TARGET_ROUTE_MATRIX.md").exists()
    assert not (docs_dir / "VHK_TARGET_ROUTE_FIXUPS.md").exists()
    assert (docs_dir / "VHK_TARGET_ROUTE_PLAN.json").exists()
    assert (scripts_dir / "vhk_compare_target_routes.sh").exists()

    plan = json.loads((docs_dir / "VHK_TARGET_ROUTE_PLAN.json").read_text())
    profile_ids = [item["profile"]["id"] for item in plan["target_profiles"]]
    assert profile_ids == ["x11-desktop", "wlroots-wayland"]

    proc = subprocess.run(
        ["sh", str(scripts_dir / "vhk_compare_target_routes.sh")],
        cwd=project_dir,
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "Collecting VHK target-route evidence" in proc.stdout
    assert "Target route comparison refresh complete." in proc.stdout

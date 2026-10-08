from __future__ import annotations

import json
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
                "presets": [{"name": "support", "vars": {"team": "support"}}],
                "steps": [
                    {
                        "type": "PromptForm",
                        "title": "Reply",
                        "fields": [{"name": "name", "label": "Name"}],
                    },
                    {"type": "TypeText", "text": "Hello ${reply.name}"},
                    {"type": "Return", "value": "ok"},
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



def test_gen_portability_pack_writes_expected_artifacts(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = project_dir / "docs"
    scripts_dir = project_dir / "scripts"

    res = runner.invoke(app, ["gen-portability-pack", str(project_dir), "--no-session-check", "--quiet"])
    assert res.exit_code == 0, res.output

    guide = (docs_dir / "VHK_PORTABILITY_GUIDE.md").read_text()
    rollout = (docs_dir / "VHK_TARGET_ROLLOUT.md").read_text()
    plan = json.loads((docs_dir / "VHK_PORTABILITY_PLAN.json").read_text())
    script = (scripts_dir / "vhk_review_portability.sh").read_text()

    assert "# VHK portability guide for proj" in guide
    assert "## Suggested target rollout" in guide
    assert "## Capability coverage hot spots" in guide
    assert "## Migration playbooks" in guide
    assert "## Core review commands" in guide
    assert "capability-agnostic" in guide

    assert "# VHK target rollout for proj" in rollout
    assert "## Baseline refresh" in rollout
    assert "## Rollout order" in rollout
    assert "## Capability proof points" in rollout
    assert "## Release-story handoff" in rollout

    assert plan["project"]["name"] == "proj"
    assert plan["target_rollout"]
    assert plan["environment_diffs"]
    assert plan["portability_playbooks"]
    assert plan["capability_coverage"]
    assert plan["portability_commands"]

    assert script.startswith("#!/usr/bin/env sh\n")
    assert "vhk doctor --json" in script
    assert "vhk validate . --json" in script
    assert "vhk plan-project . --json" in script
    assert "vhk gen-portability-pack . --out-dir" in script
    assert "docs/VHK_PORTABILITY_PLAN.json" in script



def test_gen_portability_pack_can_select_outputs(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = tmp_path / "portability-docs"
    scripts_dir = tmp_path / "portability-scripts"

    res = runner.invoke(
        app,
        [
            "gen-portability-pack",
            str(project_dir),
            "--out-dir",
            str(docs_dir),
            "--script-dir",
            str(scripts_dir),
            "--no-session-check",
            "--no-rollout",
            "--no-script",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    assert (docs_dir / "VHK_PORTABILITY_GUIDE.md").exists()
    assert (docs_dir / "VHK_PORTABILITY_PLAN.json").exists()
    assert not (docs_dir / "VHK_TARGET_ROLLOUT.md").exists()
    assert not (scripts_dir / "vhk_review_portability.sh").exists()

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



def test_gen_verification_pack_writes_expected_artifacts(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = project_dir / "docs"
    scripts_dir = project_dir / "scripts"

    res = runner.invoke(app, ["gen-verification-pack", str(project_dir), "--no-session-check", "--quiet"])
    assert res.exit_code == 0, res.output

    guide = (docs_dir / "VHK_VERIFICATION_GUIDE.md").read_text()
    checklist = (docs_dir / "VHK_RELEASE_CHECKLIST.md").read_text()
    plan = json.loads((docs_dir / "VHK_VERIFICATION_PLAN.json").read_text())
    script = (scripts_dir / "vhk_verify_release.sh").read_text()

    assert "# VHK verification guide for proj" in guide
    assert "## Surfaces that must be proven" in guide
    assert "## Installation seams to rehearse" in guide
    assert "## Shipping gates" in guide
    assert "## Suggested commands" in guide
    assert "capability-agnostic" in guide

    assert "# VHK release checklist for proj" in checklist
    assert "## Baseline refresh" in checklist
    assert "## Surface agreement" in checklist
    assert "## Install and rollback rehearsals" in checklist
    assert "## Shipping gates" in checklist
    assert "Regenerate `docs/VHK_VERIFICATION_PLAN.json` and `scripts/vhk_verify_release.sh`." in checklist

    assert plan["project"]["name"] == "proj"
    assert plan["deployable_surfaces"]
    assert plan["setup_recipes"]
    assert plan["verification_gates"]

    assert script.startswith("#!/usr/bin/env sh\n")
    assert "vhk doctor --json" in script
    assert "vhk validate . --json" in script
    assert "Manual acceptance checks to review" in script



def test_gen_verification_pack_can_select_outputs(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = tmp_path / "release-docs"
    scripts_dir = tmp_path / "release-scripts"

    res = runner.invoke(
        app,
        [
            "gen-verification-pack",
            str(project_dir),
            "--out-dir",
            str(docs_dir),
            "--script-dir",
            str(scripts_dir),
            "--no-session-check",
            "--no-checklist",
            "--no-script",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    assert (docs_dir / "VHK_VERIFICATION_GUIDE.md").exists()
    assert (docs_dir / "VHK_VERIFICATION_PLAN.json").exists()
    assert not (docs_dir / "VHK_RELEASE_CHECKLIST.md").exists()
    assert not (scripts_dir / "vhk_verify_release.sh").exists()

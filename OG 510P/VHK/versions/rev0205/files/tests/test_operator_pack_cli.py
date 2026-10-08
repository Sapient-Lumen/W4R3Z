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



def test_gen_operator_pack_writes_expected_artifacts(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    out_dir = project_dir / "docs"

    res = runner.invoke(app, ["gen-operator-pack", str(project_dir), "--no-session-check", "--quiet"])
    assert res.exit_code == 0, res.output

    guide = (out_dir / "VHK_OPERATOR_GUIDE.md").read_text()
    checklist = (out_dir / "VHK_DEPLOYMENT_CHECKLIST.md").read_text()
    plan = json.loads((out_dir / "VHK_OPERATOR_PLAN.json").read_text())

    assert "# VHK operator guide for proj" in guide
    assert "## Deployable surfaces" in guide
    assert "## Setup recipes" in guide
    assert "## Verification gates" in guide
    assert "## Borrowed product patterns" in guide
    assert "capability-agnostic" in guide

    assert "# VHK deployment checklist for proj" in checklist
    assert "## Baseline refresh" in checklist
    assert "## Install and rollback recipes" in checklist
    assert "## Shipping gates" in checklist
    assert "- [ ] Run `vhk doctor --json` on the target session." in checklist

    assert plan["project"]["name"] == "proj"
    assert plan["deployable_surfaces"]
    assert plan["setup_recipes"]
    assert plan["verification_gates"]



def test_gen_operator_pack_can_select_outputs(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    out_dir = tmp_path / "ops"

    res = runner.invoke(
        app,
        [
            "gen-operator-pack",
            str(project_dir),
            "--out-dir",
            str(out_dir),
            "--no-session-check",
            "--no-checklist",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    assert (out_dir / "VHK_OPERATOR_GUIDE.md").exists()
    assert (out_dir / "VHK_OPERATOR_PLAN.json").exists()
    assert not (out_dir / "VHK_DEPLOYMENT_CHECKLIST.md").exists()

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



def test_gen_design_pack_writes_expected_artifacts(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    out_dir = project_dir / "docs"

    res = runner.invoke(app, ["gen-design-pack", str(project_dir), "--no-session-check", "--quiet"])
    assert res.exit_code == 0, res.output

    brief = (out_dir / "VHK_DESIGN_BRIEF.md").read_text()
    contract = (out_dir / "VHK_RUNTIME_CONTRACT.md").read_text()
    plan = json.loads((out_dir / "VHK_DESIGN_PLAN.json").read_text())

    assert "# VHK design brief for proj" in brief
    assert "## Recommended stack profiles" in brief
    assert "## Runtime seams" in brief
    assert "## Ecosystem lessons carried into the design" in brief
    assert "## Immediate next moves" in brief

    assert "# VHK runtime contract for proj" in contract
    assert "## Layer ownership" in contract
    assert "## Toolchain boundary choices" in contract
    assert "## Release discipline" in contract

    assert plan["project"]["name"] == "proj"
    assert plan["stack_profiles"]
    assert plan["runtime_seams"]
    assert plan["ecosystem_lessons"]



def test_gen_design_pack_can_select_outputs(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    out_dir = tmp_path / "design"

    res = runner.invoke(
        app,
        [
            "gen-design-pack",
            str(project_dir),
            "--out-dir",
            str(out_dir),
            "--no-session-check",
            "--no-contract",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    assert (out_dir / "VHK_DESIGN_BRIEF.md").exists()
    assert (out_dir / "VHK_DESIGN_PLAN.json").exists()
    assert not (out_dir / "VHK_RUNTIME_CONTRACT.md").exists()

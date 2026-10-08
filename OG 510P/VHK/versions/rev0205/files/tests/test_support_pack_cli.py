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
                "settings": {"desktop_backend": "wayland", "log_dir": "logs"},
                "bindings": [{"keys": "Mod4+V", "macro": "vision"}],
                "hotstrings": [{"trigger": ":reply", "macro": "reply"}],
                "bus_watchers": [{"name": "refresh", "event": "proj.refresh", "macro": "vision"}],
            },
            sort_keys=False,
        )
    )
    return project_dir



def test_gen_support_pack_writes_expected_artifacts(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = project_dir / "docs"
    scripts_dir = project_dir / "scripts"

    res = runner.invoke(app, ["gen-support-pack", str(project_dir), "--no-session-check", "--quiet"])
    assert res.exit_code == 0, res.output

    guide = (docs_dir / "VHK_SUPPORT_GUIDE.md").read_text()
    checklist = (docs_dir / "VHK_SUPPORT_CHECKLIST.md").read_text()
    plan = json.loads((docs_dir / "VHK_SUPPORT_PLAN.json").read_text())
    script = (scripts_dir / "vhk_capture_support.sh").read_text()

    assert "# VHK support guide for proj" in guide
    assert "## Triage loop" in guide
    assert "## Evidence to attach" in guide
    assert "## Privacy review before sharing" in guide
    assert "capability-agnostic" in guide

    assert "# VHK support checklist for proj" in checklist
    assert "## Baseline refresh" in checklist
    assert "## Evidence to collect" in checklist
    assert "## Privacy review" in checklist
    assert "## Handoff" in checklist

    assert plan["project"]["name"] == "proj"
    assert plan["support_paths"]["log_dir"] == "logs"
    assert plan["support_artifacts"]
    assert plan["privacy_review"]
    assert plan["support_commands"]

    assert script.startswith("#!/usr/bin/env sh\n")
    assert "vhk doctor --json" in script
    assert "vhk validate . --json" in script
    assert "vhk plan-project . --json" in script
    assert "vhk report --project . --latest --json" in script
    assert "vhk trace --project . --latest --out" in script
    assert "vhk gen-capability-audit-pack . --out-dir \"$DEST/docs\"" in script
    assert "SUPPORT_INCLUDE_PROJECT_BUNDLE" in script
    assert any(item.get("id") == "installed-host-dossier-pack" for item in plan["support_artifacts"])
    dossier = next(item for item in plan["support_artifacts"] if item.get("id") == "installed-host-dossier-pack")
    assert "sh build/publish/<bundle>/dossier/redact_host_dossier.sh" in dossier["producer_commands"]
    assert "sh build/publish/<bundle>/dossier/archive_share_dossier.sh" in dossier["producer_commands"]
    assert any("share-safe dossier archive" in item for item in plan["privacy_review"])
    assert "vhk gen-host-dossier-pack . --force" in plan["support_commands"]
    assert "sh build/publish/<bundle>/dossier/redact_host_dossier.sh" in plan["support_commands"]
    assert "sh build/publish/<bundle>/dossier/archive_share_dossier.sh" in plan["support_commands"]



def test_gen_support_pack_can_select_outputs(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = tmp_path / "support-docs"
    scripts_dir = tmp_path / "support-scripts"

    res = runner.invoke(
        app,
        [
            "gen-support-pack",
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

    assert (docs_dir / "VHK_SUPPORT_GUIDE.md").exists()
    assert (docs_dir / "VHK_SUPPORT_PLAN.json").exists()
    assert not (docs_dir / "VHK_SUPPORT_CHECKLIST.md").exists()
    assert not (scripts_dir / "vhk_capture_support.sh").exists()

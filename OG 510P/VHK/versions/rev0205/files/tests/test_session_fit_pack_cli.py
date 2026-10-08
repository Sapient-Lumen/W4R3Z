from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml
from typer.testing import CliRunner

import vhk.cli as cli_mod
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
                "window_watchers": [{"name": "focus-sync", "event": "focus", "macro": "vision"}],
            },
            sort_keys=False,
        )
    )
    return project_dir



def test_gen_session_fit_pack_writes_expected_artifacts(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = project_dir / "docs"
    scripts_dir = project_dir / "scripts"

    capability_matrix = {
        "screen_capture": {"status": "ok", "recommended": "portal:Screenshot", "mechanisms": ["portal:Screenshot"], "notes": []},
        "text_injection": {"status": "limited", "recommended": None, "mechanisms": ["portal:RemoteDesktop(keyboard)"], "notes": ["interactive path"]},
        "pointer_injection": {"status": "missing", "recommended": None, "mechanisms": [], "notes": ["install helper"]},
        "global_hotkeys": {"status": "ok", "recommended": "portal:GlobalShortcuts", "mechanisms": ["portal:GlobalShortcuts"], "notes": []},
        "window_introspection": {"status": "limited", "recommended": "hyprctl", "mechanisms": ["hyprctl"], "notes": ["desktop specific"]},
    }
    monkeypatch.setattr(cli_mod, "_validation_session_capability_matrix", lambda: capability_matrix)

    res = runner.invoke(app, ["gen-session-fit-pack", str(project_dir), "--quiet"])
    assert res.exit_code == 0, res.output

    fit_doc = (docs_dir / "VHK_SESSION_FIT.md").read_text()
    fixups_doc = (docs_dir / "VHK_SESSION_FIXUPS.md").read_text()
    plan = json.loads((docs_dir / "VHK_SESSION_PLAN.json").read_text())
    review_script = (scripts_dir / "vhk_review_session_fit.sh").read_text()

    assert "# VHK session fit for proj" in fit_doc
    assert "## Required capability fit" in fit_doc
    assert "## Relevant bootstrap groups" in fit_doc

    assert "# VHK session fixups for proj" in fixups_doc
    assert "## Capability fixup lanes" in fixups_doc
    assert "pointer_injection" in fixups_doc

    assert plan["project"]["name"] == "proj"
    assert plan["source_contract"] == "session_fit"
    assert plan["session_summary"]["overall_status"] == "blocked"
    assert "pointer_injection" in plan["session_summary"]["blocked_capabilities"]
    assert any(group["capability"] == "pointer_injection" for group in plan["relevant_package_groups"])
    assert any(track["capability"] == "text_injection" and track["fit"] == "degraded" for track in plan["capability_tracks"])

    assert review_script.startswith("#!/usr/bin/env sh\n")
    assert "Collecting VHK session-fit evidence" in review_script
    assert "vhk doctor --json" in review_script



def test_gen_session_fit_pack_can_select_outputs_and_review_script_runs(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = tmp_path / "session-fit-docs"
    scripts_dir = tmp_path / "session-fit-scripts"

    res = runner.invoke(
        app,
        [
            "gen-session-fit-pack",
            str(project_dir),
            "--out-dir",
            str(docs_dir),
            "--script-dir",
            str(scripts_dir),
            "--no-session-check",
            "--no-fixups-doc",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    assert (docs_dir / "VHK_SESSION_FIT.md").exists()
    assert not (docs_dir / "VHK_SESSION_FIXUPS.md").exists()
    assert (docs_dir / "VHK_SESSION_PLAN.json").exists()
    assert (scripts_dir / "vhk_review_session_fit.sh").exists()

    proc = subprocess.run(
        ["sh", str(scripts_dir / "vhk_review_session_fit.sh")],
        cwd=project_dir,
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "Collecting VHK session-fit evidence" in proc.stdout
    assert "Session-fit refresh complete." in proc.stdout

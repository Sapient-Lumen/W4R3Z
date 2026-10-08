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
                "bus_watchers": [{"name": "refresh", "event": "proj.refresh", "macro": "vision"}],
            },
            sort_keys=False,
        )
    )
    return project_dir



def test_plan_project_includes_host_requirements(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    requirement_ids = {item["id"] for item in data["host_requirements"]}
    assert "text-surface-service" in requirement_ids
    assert "watcher-user-service" in requirement_ids
    assert "uinput-permissions" in requirement_ids
    assert "portal-global-shortcuts" in requirement_ids
    assert "portal-backend-config" in requirement_ids



def test_gen_host_contract_pack_writes_expected_artifacts(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = project_dir / "docs"
    scripts_dir = project_dir / "scripts"

    capability_matrix = {
        "screen_capture": {"status": "ok", "recommended": "portal:Screenshot", "mechanisms": ["portal:Screenshot"], "notes": [], "portal_backends": ["gnome"]},
        "text_injection": {"status": "limited", "recommended": None, "mechanisms": ["portal:RemoteDesktop(keyboard)"], "notes": ["interactive path"], "portal_backends": ["gnome"]},
        "pointer_injection": {"status": "missing", "recommended": None, "mechanisms": [], "notes": ["install helper"], "portal_backends": ["gnome"]},
        "global_hotkeys": {"status": "ok", "recommended": "portal:GlobalShortcuts", "mechanisms": ["portal:GlobalShortcuts"], "notes": [], "portal_backends": ["gnome"]},
        "input_capture": {"status": "limited", "recommended": None, "mechanisms": ["portal:InputCapture"], "notes": ["trigger-based"], "portal_backends": ["gnome"]},
    }
    host_snapshot = {
        "helpers": {
            "espanso": "/usr/bin/espanso",
            "ydotool": None,
            "keyd": None,
            "kanata": None,
            "kmonad": None,
            "xremap": None,
        },
        "uinput": {"can_write": False, "status": "permission_denied"},
        "ydotool_socket": {"status": "missing"},
        "xdg_portal_backend_config": {"status": "config_missing"},
    }
    monkeypatch.setattr(cli_mod, "_validation_session_capability_matrix", lambda: capability_matrix)
    monkeypatch.setattr(cli_mod, "_validation_host_contract_snapshot", lambda: host_snapshot)

    res = runner.invoke(app, ["gen-host-contract-pack", str(project_dir), "--quiet"])
    assert res.exit_code == 0, res.output

    req_doc = (docs_dir / "VHK_HOST_REQUIREMENTS.md").read_text()
    fix_doc = (docs_dir / "VHK_HOST_FIXUPS.md").read_text()
    plan = json.loads((docs_dir / "VHK_HOST_PLAN.json").read_text())
    review_script = (scripts_dir / "vhk_review_host_contract.sh").read_text()

    assert "# VHK host requirements for proj" in req_doc
    assert "## Service lifecycle requirements" in req_doc
    assert "## Permission requirements" in req_doc
    assert "## Portal and session requirements" in req_doc

    assert "# VHK host fixups for proj" in fix_doc
    assert "## Capability lanes" in fix_doc
    assert "pointer_injection" in fix_doc

    assert plan["project"]["name"] == "proj"
    assert plan["source_contract"] == "host_contract"
    assert plan["host_summary"]["overall_status"] == "blocked"
    assert "uinput-permissions" in plan["host_summary"]["blocked_requirements"]
    assert any(item["id"] == "portal-backend-config" and item["observed_status"] == "degraded" for item in plan["host_requirements"])
    assert any(item["id"] == "ydotool-daemon" and item["observed_status"] == "blocked" for item in plan["host_requirements"])

    assert review_script.startswith("#!/usr/bin/env sh\n")
    assert "Collecting VHK host-contract evidence" in review_script
    assert "vhk doctor --json" in review_script



def test_gen_host_contract_pack_can_select_outputs_and_review_script_runs(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = tmp_path / "host-docs"
    scripts_dir = tmp_path / "host-scripts"

    res = runner.invoke(
        app,
        [
            "gen-host-contract-pack",
            str(project_dir),
            "--out-dir",
            str(docs_dir),
            "--script-dir",
            str(scripts_dir),
            "--no-host-check",
            "--no-fixups-doc",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    assert (docs_dir / "VHK_HOST_REQUIREMENTS.md").exists()
    assert not (docs_dir / "VHK_HOST_FIXUPS.md").exists()
    assert (docs_dir / "VHK_HOST_PLAN.json").exists()
    assert (scripts_dir / "vhk_review_host_contract.sh").exists()

    proc = subprocess.run(
        ["sh", str(scripts_dir / "vhk_review_host_contract.sh")],
        cwd=project_dir,
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "Collecting VHK host-contract evidence" in proc.stdout
    assert "Host-contract refresh complete." in proc.stdout

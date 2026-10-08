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


def test_plan_project_includes_activation_routes(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["plan-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    route_ids = {item["id"] for item in data["activation_routes"]}
    assert "launcher-entrypoint" in route_ids
    assert "native-trigger-route" in route_ids
    assert "text-surface-route" in route_ids
    assert "watcher-service-route" in route_ids
    assert "helper-input-route" in route_ids


def test_gen_activation_pack_writes_expected_artifacts(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = project_dir / "docs"
    scripts_dir = project_dir / "scripts"

    capability_matrix = {
        "screen_capture": {"status": "ok", "recommended": "portal:Screenshot", "mechanisms": ["portal:Screenshot"], "notes": [], "portal_backends": ["gnome"]},
        "text_injection": {"status": "limited", "recommended": None, "mechanisms": ["portal:RemoteDesktop(keyboard)"], "notes": ["interactive path"], "portal_backends": ["gnome"]},
        "pointer_injection": {"status": "ok", "recommended": "ydotool", "mechanisms": ["ydotool"], "notes": [], "portal_backends": ["gnome"]},
        "global_hotkeys": {"status": "ok", "recommended": "portal:GlobalShortcuts", "mechanisms": ["portal:GlobalShortcuts"], "notes": [], "portal_backends": ["gnome"]},
        "input_capture": {"status": "limited", "recommended": None, "mechanisms": ["portal:InputCapture"], "notes": ["trigger-based"], "portal_backends": ["gnome"]},
    }
    host_snapshot = {
        "helpers": {
            "espanso": "/usr/bin/espanso",
            "ydotool": "/usr/bin/ydotool",
            "keyd": "/usr/bin/keyd",
            "kanata": None,
            "kmonad": None,
            "xremap": None,
        },
        "uinput": {"can_write": True, "status": "ok"},
        "input_event_access": {"status": "ok", "device_count": 2, "readable_count": 2, "readable_paths": ["/dev/input/event1"]},
        "user_groups": {"status": "ok", "group_names": ["input", "uinput"]},
        "ydotool_socket": {"status": "ok", "socket": "/run/user/1000/.ydotool_socket"},
        "xdg_portal_backend_config": {"status": "config_missing"},
        "service_units": {
            "user:espanso.service": {"unit": "espanso.service", "scope": "user", "status": "ok", "active_state": "active", "load_state": "loaded"},
            "user:vhk-busd.service": {"unit": "vhk-busd.service", "scope": "user", "status": "inactive", "active_state": "inactive", "load_state": "loaded"},
            "user:ydotoold.service": {"unit": "ydotoold.service", "scope": "user", "status": "ok", "active_state": "active", "load_state": "loaded"},
            "system:keyd.service": {"unit": "keyd.service", "scope": "system", "status": "ok", "active_state": "active", "load_state": "loaded"},
            "user:kanata.service": {"unit": "kanata.service", "scope": "user", "status": "unit_missing", "active_state": None, "load_state": "not-found"},
            "system:kanata.service": {"unit": "kanata.service", "scope": "system", "status": "unit_missing", "active_state": None, "load_state": "not-found"},
            "user:kmonad.service": {"unit": "kmonad.service", "scope": "user", "status": "unit_missing", "active_state": None, "load_state": "not-found"},
            "system:kmonad.service": {"unit": "kmonad.service", "scope": "system", "status": "unit_missing", "active_state": None, "load_state": "not-found"},
        },
    }
    monkeypatch.setattr(cli_mod, "_validation_session_capability_matrix", lambda: capability_matrix)
    monkeypatch.setattr(cli_mod, "_validation_live_readiness_snapshot", lambda requirements=None: host_snapshot)

    res = runner.invoke(app, ["gen-activation-pack", str(project_dir), "--quiet"])
    assert res.exit_code == 0, res.output

    routes_doc = (docs_dir / "VHK_ACTIVATION_ROUTES.md").read_text()
    fixups = (docs_dir / "VHK_ACTIVATION_FIXUPS.md").read_text()
    plan = json.loads((docs_dir / "VHK_ACTIVATION_PLAN.json").read_text())
    refresh_script = (scripts_dir / "vhk_review_activation_routes.sh").read_text()

    assert "# VHK activation routes for proj" in routes_doc
    assert "## Route matrix" in routes_doc
    assert "`launcher-entrypoint`" in routes_doc

    assert "# VHK activation fixups for proj" in fixups
    assert "## Degraded queue" in fixups
    assert "## Planned/manual review queue" in fixups

    assert plan["project"]["name"] == "proj"
    assert plan["source_contract"] == "activation_pack"
    assert plan["activation_summary"]["overall_status"] == "degraded"
    assert "watcher-service-route" in plan["activation_summary"]["degraded_routes"]
    assert any(item["id"] == "launcher-entrypoint" and item["route_status"] == "ready" for item in plan["activation_routes"])
    assert any(item["id"] == "text-surface-route" and item["route_status"] == "ready" for item in plan["activation_routes"])
    assert any(item["id"] == "native-trigger-route" and item["route_status"] == "planned" for item in plan["activation_routes"])

    assert refresh_script.startswith("#!/usr/bin/env sh\n")
    assert "Collecting VHK activation evidence" in refresh_script
    assert "vhk gen-activation-pack . --force --quiet" in refresh_script


def test_gen_activation_pack_can_select_outputs_and_refresh_script_runs(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = tmp_path / "activation-docs"
    scripts_dir = tmp_path / "activation-scripts"

    res = runner.invoke(
        app,
        [
            "gen-activation-pack",
            str(project_dir),
            "--out-dir",
            str(docs_dir),
            "--script-dir",
            str(scripts_dir),
            "--no-activation-check",
            "--no-fixups-doc",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    assert (docs_dir / "VHK_ACTIVATION_ROUTES.md").exists()
    assert not (docs_dir / "VHK_ACTIVATION_FIXUPS.md").exists()
    assert (docs_dir / "VHK_ACTIVATION_PLAN.json").exists()
    assert (scripts_dir / "vhk_review_activation_routes.sh").exists()

    proc = subprocess.run(
        ["sh", str(scripts_dir / "vhk_review_activation_routes.sh")],
        cwd=project_dir,
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "Collecting VHK activation evidence" in proc.stdout
    assert "Activation refresh complete." in proc.stdout

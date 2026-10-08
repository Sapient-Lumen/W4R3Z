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


def _capability_matrix() -> dict[str, object]:
    return {
        "screen_capture": {"status": "ok", "recommended": "portal:Screenshot", "mechanisms": ["portal:Screenshot"], "notes": [], "portal_backends": ["gnome"]},
        "text_injection": {"status": "limited", "recommended": None, "mechanisms": ["portal:RemoteDesktop(keyboard)"], "notes": ["interactive path"], "portal_backends": ["gnome"]},
        "pointer_injection": {"status": "ok", "recommended": "ydotool", "mechanisms": ["ydotool"], "notes": [], "portal_backends": ["gnome"]},
        "global_hotkeys": {"status": "ok", "recommended": "portal:GlobalShortcuts", "mechanisms": ["portal:GlobalShortcuts"], "notes": [], "portal_backends": ["gnome"]},
        "input_capture": {"status": "limited", "recommended": None, "mechanisms": ["portal:InputCapture"], "notes": ["trigger-based"], "portal_backends": ["gnome"]},
    }


def _host_snapshot() -> dict[str, object]:
    return {
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


def test_gen_route_selection_pack_writes_expected_artifacts(tmp_path: Path, monkeypatch) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = project_dir / "docs"
    scripts_dir = project_dir / "scripts"

    monkeypatch.setattr(cli_mod, "_validation_session_capability_matrix", _capability_matrix)
    monkeypatch.setattr(cli_mod, "_validation_live_readiness_snapshot", lambda requirements=None: _host_snapshot())

    res = runner.invoke(app, ["gen-route-selection-pack", str(project_dir), "--quiet"])
    assert res.exit_code == 0, res.output

    selection_doc = (docs_dir / "VHK_ROUTE_SELECTION.md").read_text()
    fixups_doc = (docs_dir / "VHK_ROUTE_FIXUPS.md").read_text()
    plan = json.loads((docs_dir / "VHK_ROUTE_PLAN.json").read_text())
    refresh_script = (scripts_dir / "vhk_review_route_selection.sh").read_text()

    assert "# VHK route selection for proj" in selection_doc
    assert "## Reference route set" in selection_doc
    assert "`trigger-entry` → `native-trigger-route`" in selection_doc
    assert "`input-edge` → `helper-input-route`" in selection_doc
    assert "pointer-injection__ydotool-daemon" in selection_doc

    assert "# VHK route selection fixups for proj" in fixups_doc
    assert "## Ready fallback routes worth promoting" in fixups_doc
    assert "`trigger-entry`: `remapper-route` is ready while primary `native-trigger-route` is `planned`" in fixups_doc

    assert plan["project"]["name"] == "proj"
    assert plan["source_contract"] == "route_selection_pack"
    assert plan["selection_summary"]["overall_status"] == "degraded"
    assert "trigger-entry" in plan["selection_summary"]["planned_primary_groups"]
    assert "event-plane" in plan["selection_summary"]["degraded_primary_groups"]
    assert any(item["selection_group"] == "trigger-entry" and item["route_id"] == "native-trigger-route" for item in plan["reference_routes"])
    assert any(item["selection_group"] == "universal-entry" and item["route_id"] == "launcher-entrypoint" for item in plan["reference_routes"])
    input_edge = next(item for item in plan["reference_routes"] if item["selection_group"] == "input-edge")
    assert input_edge["route_id"] == "helper-input-route"
    assert input_edge["preferred_bootstrap_filters"] == ["pointer-injection__ydotool-daemon"]
    assert any(item["selection_group"] == "trigger-entry" and item["fallback_route_id"] == "remapper-route" for item in plan["promotion_candidates"])

    assert refresh_script.startswith("#!/usr/bin/env sh\n")
    assert "Collecting VHK route-selection evidence" in refresh_script
    assert "vhk gen-route-selection-pack . --force --quiet" in refresh_script


def test_gen_route_selection_pack_can_select_outputs_and_refresh_script_runs(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    docs_dir = tmp_path / "route-docs"
    scripts_dir = tmp_path / "route-scripts"

    res = runner.invoke(
        app,
        [
            "gen-route-selection-pack",
            str(project_dir),
            "--out-dir",
            str(docs_dir),
            "--script-dir",
            str(scripts_dir),
            "--no-selection-check",
            "--no-fixups-doc",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    assert (docs_dir / "VHK_ROUTE_SELECTION.md").exists()
    assert not (docs_dir / "VHK_ROUTE_FIXUPS.md").exists()
    assert (docs_dir / "VHK_ROUTE_PLAN.json").exists()
    assert (scripts_dir / "vhk_review_route_selection.sh").exists()

    proc = subprocess.run(
        ["sh", str(scripts_dir / "vhk_review_route_selection.sh")],
        cwd=project_dir,
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "Collecting VHK route-selection evidence" in proc.stdout
    assert "Route selection refresh complete." in proc.stdout

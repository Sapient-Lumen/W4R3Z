from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.loader import load_project
from vhk.project.window_contracts import summarize_project_window_contract
from vhk.system.doctor import build_doctor_capability_matrix


runner = CliRunner()


def _write_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "main.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "main",
                "steps": [
                    {
                        "type": "WaitForWindow",
                        "selector": {"class": "mpv", "pid": 4242, "visible": True, "sticky": True},
                    },
                    {"type": "GetActiveWindow", "include_geometry": True, "require_geometry": True},
                    {"type": "GetWindowAtCursor", "include_geometry": True, "require_window": True},
                    {
                        "type": "GetWindowList",
                        "include_geometry": True,
                        "selector": {"fullscreen": True, "workspace": "2"},
                    },
                    {
                        "type": "WaitForWindowEvent",
                        "event": "title",
                        "raw_name": "windowtitlev2",
                        "selector": {"class": "mpv"},
                    },
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj",
                "bindings": [{"keys": "Mod4+M", "macro": "main", "when": {"workspace": "2"}}],
                "macros": {"main": "macros/main.yaml"},
            },
            sort_keys=False,
        )
    )
    return project_dir


def test_window_contract_summary_collects_state_geometry_and_pointer_requirements(tmp_path: Path) -> None:
    project_dir = _write_project(tmp_path)
    project = load_project(project_dir)

    contract = summarize_project_window_contract(project)

    assert contract["used"] is True
    assert contract["selector_site_count"] == 4
    assert contract["stateful_selector_count"] == 2
    assert contract["process_scoped_selector_count"] == 1
    assert contract["state_fields_used"] == ["fullscreen", "sticky", "visible"]
    assert contract["event_kinds_used"] == ["title"]
    assert contract["identity_fields_used"] == ["wm_class", "workspace"]
    assert contract["event_kinds_used"] == ["title"]
    assert contract["window_event_wait_count"] == 1
    assert contract["geometry_requested_count"] == 3
    assert contract["geometry_required_count"] == 1
    assert contract["pointer_window_count"] == 1
    assert contract["pointer_window_required_count"] == 1
    assert "stateful-window-selectors" in contract["dependency_tags"]
    assert "geometry-required" in contract["dependency_tags"]
    assert "pointer-window" in contract["dependency_tags"]
    assert "event-driven-window-hooks" in contract["dependency_tags"]


def test_plan_project_json_includes_window_contract(tmp_path: Path) -> None:
    project_dir = _write_project(tmp_path)

    result = runner.invoke(app, ["plan-project", str(project_dir), "--json", "--no-session-check"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)

    contract = data["window_contract"]
    assert contract["used"] is True
    assert contract["geometry_required_count"] == 1
    assert contract["pointer_window_count"] == 1
    assert contract["state_fields_used"] == ["fullscreen", "sticky", "visible"]
    assert contract["event_kinds_used"] == ["title"]


def test_validate_warns_when_session_lacks_window_state_contract(tmp_path: Path, monkeypatch) -> None:
    project_dir = _write_project(tmp_path)

    import vhk.cli as cli_mod

    monkeypatch.setattr(
        cli_mod,
        "_validation_session_capability_matrix",
        lambda: {
            "global_hotkeys": {"status": "ok", "mechanisms": ["x11-native"], "recommended": "x11-native", "notes": [], "portal_backends": []},
            "text_injection": {"status": "ok", "mechanisms": ["xdotool"], "recommended": "xdotool", "notes": [], "portal_backends": []},
            "screen_capture": {"status": "ok", "mechanisms": ["mss"], "recommended": "mss", "notes": [], "portal_backends": []},
            "pointer_injection": {"status": "ok", "mechanisms": ["xdotool"], "recommended": "xdotool", "notes": [], "portal_backends": []},
            "input_capture": {"status": "ok", "mechanisms": ["x11:RECORD"], "recommended": "x11:RECORD", "notes": [], "portal_backends": []},
            "window_introspection": {
                "status": "ok",
                "mechanisms": ["kdotool"],
                "recommended": "kdotool",
                "notes": [],
                "portal_backends": [],
                "window_contract_support": {
                    "selector_fields": ["title", "focused", "workspace", "class", "pid"],
                    "state_fields": ["fullscreen", "minimized"],
                    "geometry": True,
                    "process_scoping": True,
                    "pointer_window": "direct",
                    "event_kinds": ["focus"],
                    "notes": ["KDE/KWin via kdotool supports some windowstate properties, but sticky/hidden are still missing."],
                },
            },
        },
    )

    result = runner.invoke(app, ["validate", str(project_dir)])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)

    state_warnings = [item for item in data["warnings"] if item.get("code") == "SESSION_WINDOW_CONTRACT_STATE_FIELDS"]
    assert state_warnings
    assert state_warnings[0]["unsupported_state_fields"] == ["sticky", "visible"]


def test_doctor_window_contract_support_stays_backend_honest() -> None:
    matrix = build_doctor_capability_matrix(
        desktop_backend="wayland",
        helpers={"hyprctl": None, "kdotool": "/usr/bin/kdotool"},
        i3={"status": "not_available"},
        kdotool={"status": "ok"},
        screenshot=None,
        x11=None,
        wayland_protocols=None,
        uinput=None,
        ydotool_socket=None,
        xdg_portal_screenshot=None,
        xdg_portal_screencast=None,
        xdg_portal_input_capture=None,
        xdg_portal_backend_config=None,
        xdg_portal_global_shortcuts=None,
        xdg_portal_remote_desktop=None,
    )

    support = matrix["window_introspection"]["window_contract_support"]
    assert support["pointer_window"] == "direct"
    assert support["geometry"] is True
    assert "fullscreen" in support["state_fields"]
    assert "minimized" in support["state_fields"]
    assert "sticky" not in support["state_fields"]
    assert support["event_kinds"] == ["close", "focus", "geometry", "new", "title"]


def test_validate_warns_when_session_lacks_window_event_kinds(tmp_path: Path, monkeypatch) -> None:
    project_dir = _write_project(tmp_path)

    import vhk.cli as cli_mod

    monkeypatch.setattr(
        cli_mod,
        "_validation_session_capability_matrix",
        lambda: {
            "global_hotkeys": {"status": "ok", "mechanisms": ["x11-native"], "recommended": "x11-native", "notes": [], "portal_backends": []},
            "text_injection": {"status": "ok", "mechanisms": ["xdotool"], "recommended": "xdotool", "notes": [], "portal_backends": []},
            "screen_capture": {"status": "ok", "mechanisms": ["mss"], "recommended": "mss", "notes": [], "portal_backends": []},
            "pointer_injection": {"status": "ok", "mechanisms": ["xdotool"], "recommended": "xdotool", "notes": [], "portal_backends": []},
            "input_capture": {"status": "ok", "mechanisms": ["x11:RECORD"], "recommended": "x11:RECORD", "notes": [], "portal_backends": []},
            "window_introspection": {
                "status": "ok",
                "mechanisms": ["kdotool"],
                "recommended": "kdotool",
                "notes": [],
                "portal_backends": [],
                "window_contract_support": {
                    "selector_fields": ["title", "focused", "workspace", "class", "pid"],
                    "state_fields": ["fullscreen", "minimized"],
                    "geometry": True,
                    "process_scoping": True,
                    "pointer_window": "direct",
                    "event_kinds": ["focus"],
                    "notes": ["KDE/KWin via kdotool supports some windowstate properties, but sticky/hidden are still missing."],
                },
            },
        },
    )

    result = runner.invoke(app, ["validate", str(project_dir)])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)

    event_warnings = [item for item in data["warnings"] if item.get("code") == "SESSION_WINDOW_CONTRACT_EVENT_KINDS"]
    assert event_warnings
    assert event_warnings[0]["unsupported_event_kinds"] == ["title"]

from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.host_rehearsal_pack import build_host_rehearsal_plan, render_host_rehearsal_doc, render_host_rehearsal_handoff_readme


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "reply.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "reply",
                "steps": [
                    {"type": "TypeText", "text": "Hello"},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj",
                "settings": {"desktop_backend": "wayland", "bus_socket": "bus.sock"},
                "bindings": [{"keys": "Mod4+V", "macro": "reply"}],
                "bus_watchers": [{"name": "hotkeys", "event": "hotkey", "dispatch": True}],
            },
            sort_keys=False,
        )
    )
    return project_dir


def test_gen_host_rehearsal_pack_writes_docs_and_operability_scripts(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["gen-host-rehearsal-pack", str(project_dir), "--force", "--quiet"])
    assert res.exit_code == 0, res.output

    doc = (project_dir / "docs" / "VHK_HOST_REHEARSAL.md").read_text()
    plan = json.loads((project_dir / "docs" / "VHK_HOST_REHEARSAL_PLAN.json").read_text())
    script = (project_dir / "scripts" / "vhk_refresh_host_rehearsal_pack.sh").read_text()

    assert "# VHK host rehearsal pack for proj" in doc
    assert "## Rehearsal posture" in doc
    assert "## Session readiness evidence" in doc
    assert "## Validation tools" in doc
    assert "desktop-file-validate" in doc
    assert "gtk-launch" in doc

    story = dict(plan["host_rehearsal_story"])
    assert story["app_id"] == "io.visualhotkey.proj"
    assert story["command_name"] == "vhk-proj"
    assert story["bundle_kind"] == "project"
    assert story["service_mode"] == "socket-activated-busd"
    assert story["runner_mode"] == "bundle-state"
    assert story["desktop_file"] == "${XDG_DATA_HOME:-$HOME/.local/share}/applications/io.visualhotkey.proj.desktop"
    assert story["report_root"] == "${XDG_STATE_HOME:-$HOME/.local/state}/vhk/rehearsal/vhk-proj"
    assert story["report_json"] == "${XDG_STATE_HOME:-$HOME/.local/state}/vhk/rehearsal/vhk-proj/VHK_HOST_REHEARSAL_REPORT.json"
    assert story["service_units"]["socket"] == "vhk-busd-proj.socket"
    assert story["session_readiness_evidence"]["mode"] == "probe-and-unit-evidence"
    assert story["session_readiness_evidence"]["probe_path"] == "${XDG_CONFIG_HOME:-$HOME/.config}/vhk/vhk-proj/session-service/verify_session_readiness.sh"

    assert "vhk gen-host-rehearsal-pack . --force --quiet" in script
    assert "vhk gen-service-compose-pack . --force --quiet" in script

    root = project_dir / "build" / "publish" / "proj" / "rehearsal"
    assert (root / "README.md").exists()
    assert (root / "vhk_host_rehearsal_handoff.json").exists()
    assert (root / "install_reviewed_lane.sh").exists()
    assert (root / "status_reviewed_lane.sh").exists()
    assert (root / "report_reviewed_lane.sh").exists()
    assert (root / "logs_reviewed_lane.sh").exists()
    assert (root / "uninstall_reviewed_lane.sh").exists()
    assert (root / "rehearse_reviewed_lane.sh").exists()

    install_script = (root / "install_reviewed_lane.sh").read_text()
    status_script = (root / "status_reviewed_lane.sh").read_text()
    report_script = (root / "report_reviewed_lane.sh").read_text()
    logs_script = (root / "logs_reviewed_lane.sh").read_text()
    uninstall_script = (root / "uninstall_reviewed_lane.sh").read_text()
    smoke_script = (root / "rehearse_reviewed_lane.sh").read_text()

    assert 'sh "$PUBLISH_ROOT/native/assemble_native_app.sh"' in install_script
    assert 'sh "$PUBLISH_ROOT/native/install_xdg_local_app.sh"' in install_script
    assert 'sh "$PUBLISH_ROOT/service/install_user_session.sh"' in install_script
    assert 'Run report_reviewed_lane.sh next to capture one machine-readable rehearsal report.' in install_script
    assert "gtk-launch io.visualhotkey.proj" in install_script

    assert 'desktop-file-validate "$DESKTOP_FILE"' in status_script
    assert "gtk-launch probe id: io.visualhotkey.proj" in status_script
    assert "systemctl --user is-enabled vhk-busd-proj.socket" in status_script
    assert "systemctl --user show -p FragmentPath -p ActiveState -p SubState vhk-busd-proj.socket vhk-busd-proj.service" in status_script
    assert 'printf "%s\\n" "logs: sh ./logs_reviewed_lane.sh"' in status_script

    assert '"$LAUNCHER_LINK" --status-json > "$STATUS_JSON_CAPTURE" || true' in report_script
    assert 'systemd-analyze --user --man=no verify "$SYSTEMD_USER_DIR/vhk-busd-proj.socket" "$SYSTEMD_USER_DIR/vhk-busd-proj.service" > "$UNIT_VERIFY_TXT" 2>&1 || true' in report_script
    assert 'READINESS_PROBE="$SERVICE_PAYLOAD_DIR/verify_session_readiness.sh"' in report_script
    assert 'session_readiness_probe.txt' in report_script
    assert 'session_readiness_exit.txt' in report_script
    assert 'session_readiness_units.txt' in report_script
    assert 'Result -p UnitFileState -p FragmentPath -p ExecMainCode -p ExecMainStatus "vhk-busd-proj.socket" "vhk-busd-proj.service"' in report_script
    assert 'VHK_HOST_REHEARSAL_REPORT.json' in report_script
    assert '## Runtime health drift' in report_script
    assert '## Incident signature drift' in report_script
    assert '## Startup handoff drift' in report_script

    assert 'journalctl --user --no-pager -n "$LINES" -u vhk-busd-proj.socket -u vhk-busd-proj.service "$@"' in logs_script

    assert 'sh "$PUBLISH_ROOT/service/uninstall_user_session.sh"' in uninstall_script
    assert 'sh "$PUBLISH_ROOT/native/uninstall_xdg_local_app.sh"' in uninstall_script

    assert 'sh "$PUBLISH_ROOT/native/smoke_test_native_install.sh"' in smoke_script
    assert 'sh "$PUBLISH_ROOT/service/smoke_test_service_compose.sh"' in smoke_script
    assert 'VHK_SKIP_SYSTEMCTL=1 sh "$SCRIPT_DIR/install_reviewed_lane.sh"' in smoke_script
    assert 'XDG_STATE_HOME="$SMOKE_ROOT/state" VHK_BIN_HOME="$SMOKE_ROOT/bin" VHK_SKIP_SYSTEMCTL=1 sh "$SCRIPT_DIR/status_reviewed_lane.sh"' in smoke_script
    assert 'XDG_STATE_HOME="$SMOKE_ROOT/state" VHK_BIN_HOME="$SMOKE_ROOT/bin" VHK_SKIP_SYSTEMCTL=1 sh "$SCRIPT_DIR/report_reviewed_lane.sh"' in smoke_script
    assert 'test -f "$SMOKE_ROOT/state/vhk/rehearsal/vhk-proj/VHK_HOST_REHEARSAL_REPORT.json"' in smoke_script
    assert 'test -f "$SMOKE_ROOT/state/vhk/rehearsal/vhk-proj/session_readiness_probe.txt"' in smoke_script
    assert 'grep -q "session_readiness" "$SMOKE_ROOT/state/vhk/rehearsal/vhk-proj/VHK_HOST_REHEARSAL_REPORT.json"' in smoke_script
    assert 'test -x "$SMOKE_ROOT/bin/vhk-proj"' in smoke_script


def test_gen_host_rehearsal_pack_stage_target_keeps_profile_context(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(
        app,
        [
            "gen-host-rehearsal-pack",
            str(project_dir),
            "--bundle-target-profile",
            "gnome-wayland",
            "--app-id",
            "org.example.vhkdemo",
            "--python-cmd",
            "python3.12",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    plan = json.loads((project_dir / "docs" / "VHK_HOST_REHEARSAL_PLAN.json").read_text())
    story = dict(plan["host_rehearsal_story"])
    assert story["bundle_kind"] == "release-stage"
    assert story["bundle_profile_id"] == "gnome-wayland"
    assert story["app_id"] == "org.example.vhkdemo"
    assert story["python_cmd"] == "python3.12"

    root = project_dir / "build" / "publish" / "proj-gnome-wayland" / "rehearsal"
    manifest = json.loads((root / "vhk_host_rehearsal_handoff.json").read_text())
    assert manifest["bundle_profile_id"] == "gnome-wayland"
    assert manifest["command_name"] == "vhk-vhkdemo"
    assert manifest["report_json"] == "${XDG_STATE_HOME:-$HOME/.local/state}/vhk/rehearsal/vhk-vhkdemo/VHK_HOST_REHEARSAL_REPORT.json"
    assert manifest["service_units"]["socket"] == "vhk-busd-proj.socket"

    refresh = (root / "refresh_host_rehearsal_inputs.sh").read_text()
    assert "--bundle-target-profile gnome-wayland" in refresh

    status_script = (root / "status_reviewed_lane.sh").read_text()
    assert 'DESKTOP_FILE="$XDG_DATA_HOME/applications/org.example.vhkdemo.desktop"' in status_script
    assert 'BUNDLE_PATH="$APP_ROOT/share/vhk/project/proj-gnome-wayland.zip"' in status_script


def test_host_rehearsal_plan_can_render_current_host_truth(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    capability_matrix = {
        "screen_capture": {"status": "ok", "recommended": "portal:Screenshot", "mechanisms": ["portal:Screenshot"], "notes": [], "portal_backends": ["gnome"]},
        "text_injection": {"status": "limited", "recommended": None, "mechanisms": ["portal:RemoteDesktop(keyboard)"], "notes": ["interactive path"], "portal_backends": ["gnome"]},
        "pointer_injection": {"status": "ok", "recommended": "dotoolc", "mechanisms": ["dotoolc"], "notes": [], "portal_backends": ["gnome"]},
        "global_hotkeys": {"status": "ok", "recommended": "portal:GlobalShortcuts", "mechanisms": ["portal:GlobalShortcuts"], "notes": [], "portal_backends": ["gnome"]},
        "input_capture": {"status": "limited", "recommended": None, "mechanisms": ["portal:InputCapture"], "notes": ["trigger-based"], "portal_backends": ["gnome"]},
    }
    host_snapshot = {
        "helpers": {"espanso": "/usr/bin/espanso", "dotool": "/usr/bin/dotool", "dotoolc": "/usr/bin/dotoolc", "dotoold": "/usr/bin/dotoold", "ydotool": None},
        "uinput": {"can_write": False, "status": "permission_denied"},
        "ydotool_socket": {"status": "missing"},
        "xdg_portal_screenshot": {"status": "ok"},
        "xdg_portal_screencast": {"status": "ok"},
        "xdg_portal_global_shortcuts": {"status": "interface_missing"},
        "xdg_portal_remote_desktop": {"status": "interface_missing"},
        "xdg_portal_input_capture": {"status": "interface_missing"},
        "xdg_portal_backend_config": {"status": "config_missing"},
        "xdg_portal_backend_manifests": {
            "status": "ok_with_warnings",
            "xdg_current_desktop": "sway",
            "backends": [
                {"backend": "gtk", "manifest_path": "/usr/share/xdg-desktop-portal/portals/gtk.portal", "interfaces": ["org.freedesktop.impl.portal.RemoteDesktop"], "use_in": [], "matching_desktops": [], "usable_on_current_desktop": True},
                {"backend": "luminous", "manifest_path": "/usr/share/xdg-desktop-portal/portals/luminous.portal", "interfaces": ["org.freedesktop.impl.portal.Screenshot", "org.freedesktop.impl.portal.ScreenCast", "org.freedesktop.impl.portal.InputCapture"], "use_in": ["sway"], "matching_desktops": ["sway"], "usable_on_current_desktop": True},
            ],
            "parse_errors": [{"path": "/usr/share/xdg-desktop-portal/portals/broken.portal", "status": "parse_failed", "error": "boom"}],
        },
        "service_units": {"user:dotoold.service": {"unit": "dotoold.service", "scope": "user", "status": "ok", "active_state": "active", "load_state": "loaded"}},
    }

    plan = build_host_rehearsal_plan(
        project_dir,
        capability_matrix=capability_matrix,
        host_snapshot=host_snapshot,
    )
    doc = render_host_rehearsal_doc(plan)
    handoff = render_host_rehearsal_handoff_readme(plan)

    assert plan["portal_route_contract"]["status"] == "degraded"
    assert plan["host_truth"]["overall_status"] == "blocked"
    assert plan["host_truth"]["requirement_count"] >= 1
    assert len(plan["host_truth"]["blocked_requirements"]) >= 1
    assert "## Current host truth" in doc
    assert "## Observed host truth" in handoff
    assert "Portal route status" in handoff


def test_host_rehearsal_plan_surfaces_target_fit_contract(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    host_snapshot = {
        "helpers": {"espanso": "/usr/bin/espanso", "dotool": "/usr/bin/dotool", "dotoolc": "/usr/bin/dotoolc", "dotoold": "/usr/bin/dotoold", "ydotool": None},
        "uinput": {"can_write": False, "status": "permission_denied"},
        "ydotool_socket": {"status": "missing"},
        "xdg_portal_screenshot": {"status": "ok"},
        "xdg_portal_screencast": {"status": "ok"},
        "xdg_portal_global_shortcuts": {"status": "interface_missing"},
        "xdg_portal_remote_desktop": {"status": "interface_missing"},
        "xdg_portal_input_capture": {"status": "interface_missing"},
        "xdg_portal_backend_config": {"status": "config_missing"},
        "xdg_portal_backend_manifests": {"status": "ok_with_warnings", "xdg_current_desktop": "sway", "backends": []},
    }
    plan = build_host_rehearsal_plan(project_dir, host_snapshot=host_snapshot)
    doc = render_host_rehearsal_doc(plan)
    handoff = render_host_rehearsal_handoff_readme(plan)
    assert plan["target_fit_contract"]["profile_id"] == "gnome-wayland"
    assert plan["target_fit_contract"]["status"] == "drifted"
    assert "## Target lane fit" in doc
    assert "## Target lane fit" in handoff

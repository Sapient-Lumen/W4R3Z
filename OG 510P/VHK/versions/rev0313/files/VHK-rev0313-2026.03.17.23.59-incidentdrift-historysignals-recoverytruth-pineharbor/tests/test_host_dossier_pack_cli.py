from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.host_dossier_pack import build_host_dossier_plan, render_host_dossier_doc


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


def test_gen_host_dossier_pack_writes_docs_and_support_scripts(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["gen-host-dossier-pack", str(project_dir), "--force", "--quiet"])
    assert res.exit_code == 0, res.output

    doc = (project_dir / "docs" / "VHK_HOST_DOSSIER.md").read_text()
    plan = json.loads((project_dir / "docs" / "VHK_HOST_DOSSIER_PLAN.json").read_text())
    script = (project_dir / "scripts" / "vhk_refresh_host_dossier_pack.sh").read_text()

    assert "# VHK host dossier pack for proj" in doc
    assert "## Dossier posture" in doc
    assert "## Session readiness evidence" in doc
    assert "incident-signature" in doc
    assert "## What gets captured" in doc
    assert "loginctl show-session" in doc
    assert "redact_host_dossier.sh" in doc
    assert "archive_share_dossier.sh" in doc

    story = dict(plan["host_dossier_story"])
    assert story["app_id"] == "io.visualhotkey.proj"
    assert story["command_name"] == "vhk-proj"
    assert story["bundle_kind"] == "project"
    assert story["service_mode"] == "socket-activated-busd"
    assert story["dossier_root"] == "${XDG_STATE_HOME:-$HOME/.local/state}/vhk/dossier/vhk-proj"
    assert story["dossier_json"] == "${XDG_STATE_HOME:-$HOME/.local/state}/vhk/dossier/vhk-proj/VHK_HOST_DOSSIER.json"
    assert story["archive_path"] == "${XDG_STATE_HOME:-$HOME/.local/state}/vhk/dossier/vhk-proj/VHK_HOST_DOSSIER.zip"
    assert story["share_safe_archive"] == "${XDG_STATE_HOME:-$HOME/.local/state}/vhk/dossier/vhk-proj/VHK_HOST_DOSSIER.share.zip"
    assert story["share_safe_root"] == "${XDG_STATE_HOME:-$HOME/.local/state}/vhk/dossier/vhk-proj/share-safe"
    assert story["session_readiness_evidence"]["mode"] == "probe-and-unit-evidence"
    assert story["session_readiness_evidence"]["probe_path"] == "${XDG_CONFIG_HOME:-$HOME/.config}/vhk/vhk-proj/session-service/verify_session_readiness.sh"

    assert "vhk gen-host-rehearsal-pack . --force --quiet" in script
    assert "vhk gen-host-dossier-pack . --force --quiet" in script

    root = project_dir / "build" / "publish" / "proj" / "dossier"
    assert (root / "README.md").exists()
    assert (root / "vhk_host_dossier_handoff.json").exists()
    assert (root / "collect_host_dossier.sh").exists()
    assert (root / "redact_host_dossier.sh").exists()
    assert (root / "archive_host_dossier.sh").exists()
    assert (root / "archive_share_dossier.sh").exists()
    assert (root / "smoke_test_host_dossier.sh").exists()

    collect_script = (root / "collect_host_dossier.sh").read_text()
    redact_script = (root / "redact_host_dossier.sh").read_text()
    archive_script = (root / "archive_host_dossier.sh").read_text()
    share_archive_script = (root / "archive_share_dossier.sh").read_text()
    smoke_script = (root / "smoke_test_host_dossier.sh").read_text()

    assert '"$LAUNCHER_LINK" --home-json > "$APP_HOME_CAPTURE"' in collect_script
    assert '"$LAUNCHER_LINK" --status-json > "$STATUS_CAPTURE"' in collect_script
    assert 'sh "$PUBLISH_ROOT/rehearsal/report_reviewed_lane.sh"' in collect_script
    assert 'loginctl show-session "$XDG_SESSION_ID" -p Id -p Name -p Type -p Class -p State -p Desktop -p Active -p Remote -p Display' in collect_script
    assert 'systemctl --user show -p UnitPath --value > "$UNIT_PATH_CAPTURE"' in collect_script
    assert 'READINESS_PROBE="$SERVICE_PAYLOAD_DIR/verify_session_readiness.sh"' in collect_script
    assert 'session_readiness_probe.txt' in collect_script
    assert 'session_readiness_exit.txt' in collect_script
    assert 'session_readiness_units.txt' in collect_script
    assert 'Result -p UnitFileState -p FragmentPath -p ExecMainCode -p ExecMainStatus $JOURNAL_UNITS_RAW > "$UNIT_SHOW_CAPTURE"' in collect_script
    assert 'journalctl --user --no-pager -n "$DOSSIER_LINES"' in collect_script
    assert 'VHK_HOST_DOSSIER.json' in collect_script
    assert 'VHK_HOST_DOSSIER.md' in collect_script
    assert '## Runtime health drift' in collect_script
    assert 'Incident signature verdict' in collect_script
    assert 'Incident-signature drift verdict' in collect_script
    assert '## Startup handoff drift' in collect_script

    assert 'sh "$SCRIPT_DIR/collect_host_dossier.sh" >/dev/null' in archive_script
    assert 'VHK_HOST_DOSSIER.zip' in archive_script
    assert 'ZipFile(out, ' in archive_script

    assert 'sh "$SCRIPT_DIR/collect_host_dossier.sh" >/dev/null' in redact_script
    assert 'VHK_HOST_DOSSIER.share.json' in redact_script
    assert 'VHK_HOST_DOSSIER_REDACTION.json' in redact_script
    assert 'review_required' in redact_script
    assert '[REDACTED_SECRET]' in redact_script

    assert 'sh "$SCRIPT_DIR/redact_host_dossier.sh" >/dev/null' in share_archive_script
    assert 'VHK_HOST_DOSSIER.share.zip' in share_archive_script
    assert 'ZipFile(out, ' in share_archive_script

    assert 'sh "$PUBLISH_ROOT/rehearsal/install_reviewed_lane.sh"' in smoke_script
    assert 'VHK_SKIP_LOGINCTL=1 sh "$SCRIPT_DIR/collect_host_dossier.sh"' in smoke_script
    assert 'VHK_SKIP_LOGINCTL=1 sh "$SCRIPT_DIR/redact_host_dossier.sh"' in smoke_script
    assert 'VHK_SKIP_LOGINCTL=1 sh "$SCRIPT_DIR/archive_share_dossier.sh"' in smoke_script
    assert 'VHK_SKIP_LOGINCTL=1 sh "$SCRIPT_DIR/archive_host_dossier.sh"' in smoke_script
    assert 'test -f "$SMOKE_ROOT/state/vhk/dossier/vhk-proj/VHK_HOST_DOSSIER.json"' in smoke_script
    assert 'test -f "$SMOKE_ROOT/state/vhk/dossier/vhk-proj/captures/session_readiness_probe.txt"' in smoke_script
    assert 'grep -q "session_readiness" "$SMOKE_ROOT/state/vhk/dossier/vhk-proj/VHK_HOST_DOSSIER.json"' in smoke_script
    assert 'test -f "$SMOKE_ROOT/state/vhk/dossier/vhk-proj/share-safe/VHK_HOST_DOSSIER.share.json"' in smoke_script
    assert 'test -f "$SMOKE_ROOT/state/vhk/dossier/vhk-proj/VHK_HOST_DOSSIER.share.zip"' in smoke_script
    assert 'test -f "$SMOKE_ROOT/state/vhk/dossier/vhk-proj/VHK_HOST_DOSSIER.zip"' in smoke_script


def test_gen_host_dossier_pack_stage_target_keeps_profile_context(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(
        app,
        [
            "gen-host-dossier-pack",
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

    plan = json.loads((project_dir / "docs" / "VHK_HOST_DOSSIER_PLAN.json").read_text())
    story = dict(plan["host_dossier_story"])
    assert story["bundle_kind"] == "release-stage"
    assert story["bundle_profile_id"] == "gnome-wayland"
    assert story["app_id"] == "org.example.vhkdemo"

    root = project_dir / "build" / "publish" / "proj-gnome-wayland" / "dossier"
    manifest = json.loads((root / "vhk_host_dossier_handoff.json").read_text())
    assert manifest["bundle_profile_id"] == "gnome-wayland"
    assert manifest["command_name"] == "vhk-vhkdemo"
    assert manifest["dossier_json"] == "${XDG_STATE_HOME:-$HOME/.local/state}/vhk/dossier/vhk-vhkdemo/VHK_HOST_DOSSIER.json"

    refresh = (root / "refresh_host_dossier_inputs.sh").read_text()
    assert "--bundle-target-profile gnome-wayland" in refresh

    collect_script = (root / "collect_host_dossier.sh").read_text()
    assert 'LAUNCHER_LINK="$VHK_BIN_HOME/vhk-vhkdemo"' in collect_script


def test_host_dossier_plan_can_render_current_host_truth(tmp_path: Path) -> None:
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

    plan = build_host_dossier_plan(
        project_dir,
        capability_matrix=capability_matrix,
        host_snapshot=host_snapshot,
    )
    doc = render_host_dossier_doc(plan)

    assert plan["portal_route_contract"]["status"] == "degraded"
    assert plan["host_truth"]["overall_status"] == "blocked"
    assert plan["host_truth"]["requirement_count"] >= 1
    assert len(plan["host_truth"]["blocked_requirements"]) >= 1
    assert plan["target_fit_contract"]["status"] == "drifted"
    assert plan["target_fit_contract"]["profile_id"] == "gnome-wayland"
    assert "## Current host truth" in doc
    assert "## Target lane fit" in doc
    assert "Portal route status" in doc

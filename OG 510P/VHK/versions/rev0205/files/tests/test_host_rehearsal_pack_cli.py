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
    assert 'VHK_HOST_REHEARSAL_REPORT.json' in report_script

    assert 'journalctl --user --no-pager -n "$LINES" -u vhk-busd-proj.socket -u vhk-busd-proj.service "$@"' in logs_script

    assert 'sh "$PUBLISH_ROOT/service/uninstall_user_session.sh"' in uninstall_script
    assert 'sh "$PUBLISH_ROOT/native/uninstall_xdg_local_app.sh"' in uninstall_script

    assert 'sh "$PUBLISH_ROOT/native/smoke_test_native_install.sh"' in smoke_script
    assert 'sh "$PUBLISH_ROOT/service/smoke_test_service_compose.sh"' in smoke_script
    assert 'VHK_SKIP_SYSTEMCTL=1 sh "$SCRIPT_DIR/install_reviewed_lane.sh"' in smoke_script
    assert 'XDG_STATE_HOME="$SMOKE_ROOT/state" VHK_BIN_HOME="$SMOKE_ROOT/bin" VHK_SKIP_SYSTEMCTL=1 sh "$SCRIPT_DIR/status_reviewed_lane.sh"' in smoke_script
    assert 'XDG_STATE_HOME="$SMOKE_ROOT/state" VHK_BIN_HOME="$SMOKE_ROOT/bin" VHK_SKIP_SYSTEMCTL=1 sh "$SCRIPT_DIR/report_reviewed_lane.sh"' in smoke_script
    assert 'test -f "$SMOKE_ROOT/state/vhk/rehearsal/vhk-proj/VHK_HOST_REHEARSAL_REPORT.json"' in smoke_script
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

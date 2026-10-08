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


def test_gen_service_compose_pack_writes_docs_units_and_bridge(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["gen-service-compose-pack", str(project_dir), "--force", "--quiet"])
    assert res.exit_code == 0, res.output

    doc = (project_dir / "docs" / "VHK_SERVICE_COMPOSE.md").read_text()
    plan = json.loads((project_dir / "docs" / "VHK_SERVICE_COMPOSE_PLAN.json").read_text())
    script = (project_dir / "scripts" / "vhk_refresh_service_compose_pack.sh").read_text()

    assert "# VHK service composition pack for proj" in doc
    assert "## Service posture" in doc
    assert "Runner mode" in doc
    assert "## Adjacent helper services to review" in doc

    story = dict(plan["service_compose_story"])
    assert story["service_mode"] == "socket-activated-busd"
    assert story["autostart_mode"] == "systemctl-bridge"
    assert story["runner_mode"] == "bundle-state"
    assert story["watchers"] == ["hotkeys"]
    assert story["environment_exports"]["VHK_PROJECT_ROOT"] == str(project_dir.resolve())
    assert story["environment_exports"]["PATH"] == "${HOME}/.local/bin:$PATH"
    assert story["environment_exports"]["VHK_SERVICE_BUNDLE_NAME"] == "proj.zip"

    assert "vhk gen-service-compose-pack . --force --quiet" in script
    assert "vhk gen-native-install-pack . --force --quiet" in script

    service_root = project_dir / "build" / "publish" / "proj" / "service"
    assert (service_root / "README.md").exists()
    assert (service_root / "vhk_service_compose_handoff.json").exists()
    assert (service_root / "install_user_session.sh").exists()
    assert (service_root / "uninstall_user_session.sh").exists()
    assert (service_root / "smoke_test_service_compose.sh").exists()
    assert (service_root / "materialize_bundle_root.sh").exists()
    assert (service_root / "run_bundle_busd.sh").exists()

    service_unit = (service_root / "systemd-user" / "vhk-busd-proj.service").read_text()
    socket_unit = (service_root / "systemd-user" / "vhk-busd-proj.socket").read_text()
    env_conf = (service_root / "environment.d" / "80-vhk-vhk-proj.conf").read_text()
    autostart = (service_root / "autostart" / "vhk-busd-proj.desktop").read_text()
    materialize_script = (service_root / "materialize_bundle_root.sh").read_text()
    run_script = (service_root / "run_bundle_busd.sh").read_text()

    assert "PartOf=graphical-session.target" in service_unit
    assert "After=graphical-session-pre.target" in service_unit
    assert "ConfigurationDirectory=vhk/vhk-proj/session-service" in service_unit
    assert "StateDirectory=vhk/vhk-proj/session-service" in service_unit
    assert "CacheDirectory=vhk/vhk-proj/session-service" in service_unit
    assert "ExecStart=/usr/bin/env sh -lc '$CONFIGURATION_DIRECTORY/run_bundle_busd.sh'" in service_unit

    assert "ListenDatagram=" in socket_unit
    assert "bus.sock" in socket_unit
    assert "WantedBy=graphical-session.target" in socket_unit

    assert f"VHK_PROJECT_ROOT={project_dir.resolve()}" in env_conf
    assert "PATH=${HOME}/.local/bin:$PATH" in env_conf
    assert "VHK_SERVICE_RUNNER_MODE=bundle-state" in env_conf
    assert "VHK_BUNDLE_PATH=${XDG_DATA_HOME:-$HOME/.local/share}/vhk/apps/vhk-proj/share/vhk/project/proj.zip" in env_conf

    assert "Exec=/usr/bin/env sh -lc 'systemctl --user start vhk-busd-proj.socket" in autostart
    assert "TryExec=systemctl" in autostart

    assert 'materialize-bundle "$BUNDLE_PATH" "$TARGET_ROOT" --json' in materialize_script
    assert 'TARGET_ROOT="$STATE_DIRECTORY/project"' in materialize_script
    assert 'exec $VHK_CMD busd "$PROJECT_ROOT" --watcher hotkeys' in run_script

    install_script = (service_root / "install_user_session.sh").read_text()
    assert 'SYSTEMD_USER_DIR="$XDG_CONFIG_HOME/systemd/user"' in install_script
    assert 'SERVICE_PAYLOAD_DIR="$XDG_CONFIG_HOME/vhk/vhk-proj/session-service"' in install_script
    assert 'cp "$SCRIPT_DIR/systemd-user/vhk-busd-proj.socket" "$SYSTEMD_USER_DIR/vhk-busd-proj.socket"' in install_script
    assert 'cp "$SCRIPT_DIR/materialize_bundle_root.sh" "$SERVICE_PAYLOAD_DIR/materialize_bundle_root.sh"' in install_script
    assert 'systemctl --user add-wants graphical-session.target vhk-busd-proj.socket' in install_script

    smoke_script = (service_root / "smoke_test_service_compose.sh").read_text()
    assert 'VHK_SKIP_SYSTEMCTL=1 sh "$SCRIPT_DIR/install_user_session.sh"' in smoke_script
    assert 'test -x "$SMOKE_ROOT/config/vhk/vhk-proj/session-service/materialize_bundle_root.sh"' in smoke_script
    assert 'grep -q "run_bundle_busd.sh" "$SMOKE_ROOT/config/systemd/user/vhk-busd-proj.service"' in smoke_script



def test_gen_service_compose_pack_stage_target_keeps_profile_context(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(
        app,
        [
            "gen-service-compose-pack",
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

    plan = json.loads((project_dir / "docs" / "VHK_SERVICE_COMPOSE_PLAN.json").read_text())
    story = dict(plan["service_compose_story"])
    assert story["bundle_kind"] == "release-stage"
    assert story["bundle_profile_id"] == "gnome-wayland"
    assert story["app_id"] == "org.example.vhkdemo"
    assert story["python_cmd"] == "python3.12"

    service_root = project_dir / "build" / "publish" / "proj-gnome-wayland" / "service"
    manifest = json.loads((service_root / "vhk_service_compose_handoff.json").read_text())
    assert manifest["bundle_profile_id"] == "gnome-wayland"
    assert manifest["service_mode"] == "socket-activated-busd"
    assert manifest["runner_mode"] == "bundle-state"

    refresh = (service_root / "refresh_service_compose_inputs.sh").read_text()
    assert "--bundle-target-profile gnome-wayland" in refresh

    env_conf = (service_root / "environment.d" / f"80-vhk-{manifest['command_name']}.conf").read_text()
    assert "VHK_BUNDLE_PROFILE=gnome-wayland" in env_conf

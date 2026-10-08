from __future__ import annotations

from pathlib import Path

from vhk.project.i3_x11_flagship_stack_bridge_pack import (
    FLAGSHIP_STACK_BRIDGE_KIND,
    build_i3_x11_flagship_stack_bridge_pack,
    render_i3_x11_flagship_stack_autostart_desktop,
    render_i3_x11_flagship_stack_start_user_session,
    render_i3_x11_flagship_stack_sync_session_activation_env,
    render_i3_x11_flagship_stack_verify_session_readiness,
    render_i3_x11_flagship_stack_verify_session_targets,
    render_i3_x11_flagship_stack_verify_startup_handoff,
)


def test_build_i3_x11_flagship_stack_bridge_pack_reuses_startup_bridge_contract() -> None:
    pack = build_i3_x11_flagship_stack_bridge_pack(
        project_dir=Path("/tmp/demo"),
        unit_base="vhk-busd-demo",
        watcher_names=["hotkeys"],
        bus_socket_path="%t/vhk-demo.sock",
    )

    assert pack["pack_kind"] == FLAGSHIP_STACK_BRIDGE_KIND
    contract = pack["startup_bridge_contract"]
    story = pack["service_compose_story"]
    assert contract["window_manager"] == "i3"
    assert contract["desktop_backend"] == "x11"
    assert story["unit_base"] == "vhk-busd-demo"
    assert story["service_mode"] == "socket-activated-busd"
    assert story["bus_socket_path"] == "%t/vhk-demo.sock"
    assert story["session_readiness_policy"]["display_any_of"] == ["DISPLAY"]
    assert story["startup_handoff_policy"]["primary_owner"] == "graphical-session.target"
    assert pack["startup_bridge_summary"]["fallback_startup_owner"] == "xdg-autostart"


def test_render_i3_x11_flagship_stack_bridge_scripts_emit_explicit_session_bridge_contract() -> None:
    pack = build_i3_x11_flagship_stack_bridge_pack(
        project_dir=Path("/tmp/demo"),
        unit_base="vhk-busd-demo",
        watcher_names=["hotkeys"],
        bus_socket_path="%t/vhk-demo.sock",
    )

    sync_script = render_i3_x11_flagship_stack_sync_session_activation_env(pack)
    readiness_script = render_i3_x11_flagship_stack_verify_session_readiness(pack)
    target_script = render_i3_x11_flagship_stack_verify_session_targets(pack)
    startup_script = render_i3_x11_flagship_stack_verify_startup_handoff(pack)
    start_script = render_i3_x11_flagship_stack_start_user_session(pack)
    autostart_desktop = render_i3_x11_flagship_stack_autostart_desktop(pack)

    assert 'dbus-update-activation-environment --systemd $VARS' in sync_script
    assert 'systemctl --user import-environment $VARS' in sync_script
    assert '== VHK session readiness probe ==' in readiness_script
    assert 'DISPLAY_VARS="DISPLAY"' in readiness_script
    assert 'graphical-session target: inactive' in readiness_script
    assert 'systemctl --user show "$SERVICE_UNIT" -p LoadState -p ActiveState -p PartOf -p BindsTo -p After' in target_script
    assert 'warning: both an autostart bridge and an enabled user unit are present' in startup_script
    assert 'sync_session_activation_env.sh' in start_script
    assert 'verify_session_readiness.sh' in start_script
    assert 'systemctl --user start "$UNIT_NAME"' in start_script
    assert 'sync_session_activation_env.sh' in autostart_desktop
    assert 'verify_session_readiness.sh' in autostart_desktop
    assert 'systemctl --user start vhk-busd-demo.socket' in autostart_desktop

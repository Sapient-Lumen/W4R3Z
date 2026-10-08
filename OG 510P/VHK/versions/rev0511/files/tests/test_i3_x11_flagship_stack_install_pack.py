from __future__ import annotations

from pathlib import Path
import subprocess

from vhk.project.i3_x11_flagship_stack_bridge_pack import build_i3_x11_flagship_stack_bridge_pack
from vhk.project.i3_x11_flagship_stack_install_pack import (
    FLAGSHIP_STACK_INSTALL_KIND,
    build_i3_x11_flagship_stack_install_pack,
    render_i3_x11_flagship_stack_install_user_session,
    render_i3_x11_flagship_stack_repair_user_session,
    render_i3_x11_flagship_stack_smoke_install,
    render_i3_x11_flagship_stack_uninstall_user_session,
    render_i3_x11_flagship_stack_verify_user_session,
    render_i3_x11_flagship_stack_verify_user_session_json,
)


def _build_pack() -> dict:
    bridge_pack = build_i3_x11_flagship_stack_bridge_pack(
        project_dir=Path('/tmp/demo'),
        unit_base='vhk-busd-demo',
        watcher_names=['hotkeys'],
        bus_socket_path='%t/vhk-demo.sock',
    )
    return build_i3_x11_flagship_stack_install_pack(project_dir=Path('/tmp/demo'), stack_bridge_pack=bridge_pack)


def test_build_i3_x11_flagship_stack_install_pack_exposes_xdg_install_story() -> None:
    pack = _build_pack()

    assert pack['pack_kind'] == FLAGSHIP_STACK_INSTALL_KIND
    story = pack['install_story']
    assert story['unit_base'] == 'vhk-busd-demo'
    assert story['payload_rel'] == 'vhk/vhk-busd-demo/session-service'
    assert story['i3_include_rel'] == 'i3/vhk/vhk-busd-demo.conf'
    assert story['default_enable_user_unit'] is True
    assert story['default_install_autostart_bridge'] is False
    assert story['default_install_i3_include'] is True
    assert pack['install_summary']['payload_rel'] == 'vhk/vhk-busd-demo/session-service'
    assert pack['install_summary']['post_install_helpers']['verify_user_session_json'] == 'verify_user_session_json.sh'
    assert pack['install_summary']['post_install_helpers']['repair_user_session'] == 'repair_user_session.sh'


def test_render_i3_x11_flagship_stack_install_scripts_copy_and_rehearse_stack() -> None:
    pack = _build_pack()

    install_script = render_i3_x11_flagship_stack_install_user_session(pack)
    verify_json_script = render_i3_x11_flagship_stack_verify_user_session_json(pack)
    verify_script = render_i3_x11_flagship_stack_verify_user_session(pack)
    repair_script = render_i3_x11_flagship_stack_repair_user_session(pack)
    uninstall_script = render_i3_x11_flagship_stack_uninstall_user_session(pack)
    smoke_script = render_i3_x11_flagship_stack_smoke_install(pack)

    assert 'PAYLOAD_DIR="$XDG_CONFIG_HOME/vhk/vhk-busd-demo/session-service"' in install_script
    assert 'I3_INCLUDE_PATH="$XDG_CONFIG_HOME/i3/vhk/vhk-busd-demo.conf"' in install_script
    assert 'cp "$SCRIPT_DIR/bin/"*.sh "$PAYLOAD_DIR/"' in install_script
    assert 'cp "$SCRIPT_DIR/control-plane.json" "$PAYLOAD_DIR/control-plane.json"' in install_script
    assert 'cp "$SCRIPT_DIR/i3/vhk-busd.conf" "$I3_INCLUDE_PATH"' in install_script
    assert 'VHK_INSTALL_AUTOSTART_BRIDGE' in install_script
    assert 'systemctl --user enable --now vhk-busd-demo.socket' in install_script
    assert '"stack_kind": "vhk.i3_x11.flagship_user_session_install_verdict"' in verify_json_script
    assert 'runtime_startable_now' in verify_json_script
    assert 'verify_user_session_json.sh' in verify_script
    assert 'install_user_session.sh' in repair_script
    assert 'start_user_session.sh' in repair_script
    assert 'rm -f "$I3_INCLUDE_PATH"' in uninstall_script
    assert 'rm -rf "$PAYLOAD_DIR"' in uninstall_script
    assert 'VHK_SKIP_SYSTEMCTL=1 sh "$SCRIPT_DIR/install_user_session.sh"' in smoke_script
    assert 'verify_user_session_json.sh' in smoke_script
    assert 'repair_user_session.sh' in smoke_script
    assert 'test -f "$SMOKE_ROOT/config/i3/vhk/vhk-busd-demo.conf"' in smoke_script
    assert 'test -f "$SMOKE_ROOT/config/vhk/vhk-busd-demo/session-service/control-plane.json"' in smoke_script
    assert 'VHK_INSTALL_AUTOSTART_BRIDGE=1 sh "$SCRIPT_DIR/install_user_session.sh"' in smoke_script


def test_rendered_i3_x11_flagship_stack_install_scripts_parse_as_shell() -> None:
    pack = _build_pack()
    for script in [
        render_i3_x11_flagship_stack_install_user_session(pack),
        render_i3_x11_flagship_stack_verify_user_session_json(pack),
        render_i3_x11_flagship_stack_verify_user_session(pack),
        render_i3_x11_flagship_stack_repair_user_session(pack),
        render_i3_x11_flagship_stack_uninstall_user_session(pack),
        render_i3_x11_flagship_stack_smoke_install(pack),
    ]:
        proc = subprocess.run(['sh', '-n'], input=script, text=True, capture_output=True)
        assert proc.returncode == 0, proc.stderr

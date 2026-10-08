from __future__ import annotations

import json
import subprocess
from pathlib import Path

from vhk.project.i3_x11_flagship_stack_bridge_pack import build_i3_x11_flagship_stack_bridge_pack
from vhk.project.i3_x11_flagship_stack_install_pack import build_i3_x11_flagship_stack_install_pack
from vhk.project.i3_x11_flagship_stack_install_handoff import (
    FLAGSHIP_STACK_INSTALL_HANDOFF_KIND,
    build_i3_x11_flagship_stack_install_handoff,
    render_i3_x11_flagship_stack_install_lane_ticket,
    render_i3_x11_flagship_stack_install_lane_ticket_json,
)


def _build_pack() -> dict:
    bridge_pack = build_i3_x11_flagship_stack_bridge_pack(
        project_dir=Path('/tmp/demo'),
        unit_base='vhk-busd-demo',
        watcher_names=['hotkeys'],
        bus_socket_path='%t/vhk-demo.sock',
    )
    install_pack = build_i3_x11_flagship_stack_install_pack(project_dir=Path('/tmp/demo'), stack_bridge_pack=bridge_pack)
    return build_i3_x11_flagship_stack_install_handoff(project_dir=Path('/tmp/demo'), stack_install_pack=install_pack)


def test_build_i3_x11_flagship_stack_install_handoff_exposes_statuses() -> None:
    pack = _build_pack()
    assert pack['pack_kind'] == FLAGSHIP_STACK_INSTALL_HANDOFF_KIND
    summary = pack['handoff_summary']
    assert summary['helper_json'] == 'install_lane_ticket_json.sh'
    assert summary['helper_text'] == 'install_lane_ticket.sh'
    assert summary['status_ids'] == ['install_not_deployed', 'repair_required', 'start_recommended', 'active']
    assert summary['recommended_surface_order'][0] == 'install_lane_ticket_json.sh'


def test_render_i3_x11_flagship_stack_install_handoff_scripts_parse_as_shell() -> None:
    pack = _build_pack()
    for script in [
        render_i3_x11_flagship_stack_install_lane_ticket_json(pack),
        render_i3_x11_flagship_stack_install_lane_ticket(pack),
    ]:
        proc = subprocess.run(['sh', '-n'], input=script, text=True, capture_output=True)
        assert proc.returncode == 0, proc.stderr


def _write_verify_helper(root: Path, payload: dict) -> None:
    verify = root / 'verify_user_session_json.sh'
    verify.write_text(
        "#!/usr/bin/env sh\n"
        "set -eu\n"
        "python3 - <<'PY'\n"
        "import json\n"
        + f"payload = {repr(payload)}\n"
        + "print(json.dumps(payload, indent=2, sort_keys=False))\n"
        + "PY\n",
        encoding='utf-8',
    )
    verify.chmod(0o755)
    verify_text = root / 'verify_user_session.sh'
    verify_text.write_text('#!/usr/bin/env sh\nset -eu\nprintf "%s\\n" "verify"\n', encoding='utf-8')
    verify_text.chmod(0o755)


def _base_verdict() -> dict:
    return {
        'schema_version': 1,
        'stack_kind': 'vhk.i3_x11.flagship_user_session_install_verdict',
        'install_complete': False,
        'runtime_startable_now': False,
        'runtime_active_now': False,
        'paths': {
            'payload_dir': '/tmp/demo-payload',
            'service_unit': '/tmp/service',
            'socket_unit': '/tmp/socket',
            'i3_include': '/tmp/i3.conf',
            'autostart_desktop': '/tmp/vhk.desktop',
        },
        'artifacts': {
            'payload_present': False,
            'service_present': False,
            'socket_present': False,
            'i3_include_present': False,
            'autostart_present': False,
            'sync_helper_present': False,
            'start_helper_present': False,
            'readiness_helper_present': False,
            'targets_helper_present': False,
            'handoff_helper_present': False,
        },
        'session': {
            'readiness_ok': False,
            'targets_ok': False,
            'startup_handoff_ok': False,
        },
        'systemd_user': {
            'available': False,
            'enabled_state': 'unknown',
            'active_state': 'inactive',
        },
        'warnings': [],
        'summary': 'demo',
    }


def test_install_lane_ticket_json_distinguishes_not_deployed_repair_and_start() -> None:
    root = Path('/tmp') / 'vhk_install_handoff_test'
    if root.exists():
        subprocess.run(['rm', '-rf', str(root)], check=False)
    root.mkdir(parents=True)
    bin_dir = root / 'bin'
    bin_dir.mkdir()
    pack = _build_pack()
    helper_json = bin_dir / 'install_lane_ticket_json.sh'
    helper_json.write_text(render_i3_x11_flagship_stack_install_lane_ticket_json(pack), encoding='utf-8')
    helper_json.chmod(0o755)
    helper_text = bin_dir / 'install_lane_ticket.sh'
    helper_text.write_text(render_i3_x11_flagship_stack_install_lane_ticket(pack), encoding='utf-8')
    helper_text.chmod(0o755)

    verdict = _base_verdict()
    _write_verify_helper(root, verdict)
    res = subprocess.run([str(helper_json)], cwd=str(bin_dir), capture_output=True, text=True, check=False)
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert payload['status_id'] == 'install_not_deployed'
    assert payload['recommended']['command'] == './install_user_session.sh'

    verdict = _base_verdict()
    verdict['artifacts']['payload_present'] = True
    verdict['artifacts']['service_present'] = True
    verdict['warnings'] = ['missing_start_helper']
    _write_verify_helper(root, verdict)
    res = subprocess.run([str(helper_json)], cwd=str(bin_dir), capture_output=True, text=True, check=False)
    payload = json.loads(res.stdout)
    assert payload['status_id'] == 'repair_required'
    assert payload['recommended']['command'] == './repair_user_session.sh'

    verdict = _base_verdict()
    verdict['install_complete'] = True
    verdict['runtime_startable_now'] = True
    verdict['artifacts'].update({
        'payload_present': True,
        'service_present': True,
        'socket_present': True,
        'i3_include_present': True,
        'sync_helper_present': True,
        'start_helper_present': True,
        'readiness_helper_present': True,
        'targets_helper_present': True,
        'handoff_helper_present': True,
    })
    verdict['session'] = {'readiness_ok': True, 'targets_ok': True, 'startup_handoff_ok': True}
    _write_verify_helper(root, verdict)
    res = subprocess.run([str(helper_json)], cwd=str(bin_dir), capture_output=True, text=True, check=False)
    payload = json.loads(res.stdout)
    assert payload['status_id'] == 'start_recommended'
    assert payload['recommended']['command'] == '/tmp/demo-payload/start_user_session.sh'

    verdict['runtime_active_now'] = True
    _write_verify_helper(root, verdict)
    res = subprocess.run([str(helper_json)], cwd=str(bin_dir), capture_output=True, text=True, check=False)
    payload = json.loads(res.stdout)
    assert payload['status_id'] == 'active'

    text_res = subprocess.run([str(helper_text)], cwd=str(bin_dir), capture_output=True, text=True, check=False)
    assert text_res.returncode == 0, text_res.stderr
    assert 'status_id: active' in text_res.stdout

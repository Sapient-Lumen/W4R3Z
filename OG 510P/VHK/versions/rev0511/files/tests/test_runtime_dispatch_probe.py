from __future__ import annotations

import threading
import time
from pathlib import Path

import yaml

from vhk.core.bus_watchers import run_bus_daemon
from vhk.project.loader import load_project
from vhk.project.runtime_contract import summarize_project_runtime_contract_from_root
from vhk.project.runtime_dispatch_probe import (
    allocate_runtime_dispatch_probe_ack_path,
    is_allowed_runtime_dispatch_probe_ack_path,
    probe_runtime_dispatch_path,
    summarize_runtime_dispatch_probe,
)
from vhk.system.event_bus import get_bus_socket_path


def _write_project(tmp_path: Path) -> Path:
    proj = tmp_path / 'proj'
    (proj / 'macros').mkdir(parents=True)
    (proj / 'project.yaml').write_text(yaml.safe_dump({
        'name': 'p',
        'settings': {'event_log': False},
        'bus_watchers': [{'name': 'hotkeys', 'event': 'hotkey', 'macro': 'noop'}],
        'macros': {'noop': 'macros/noop.yaml'},
    }))
    (proj / 'macros' / 'noop.yaml').write_text(yaml.safe_dump({'name': 'noop', 'steps': []}))
    return proj


def test_runtime_dispatch_probe_path_guard_accepts_runtime_probe_roots(tmp_path: Path, monkeypatch):
    proj = _write_project(tmp_path)
    runtime = tmp_path / 'run'
    runtime.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv('XDG_RUNTIME_DIR', str(runtime))

    probe_id, ack_path = allocate_runtime_dispatch_probe_ack_path(project_root=proj, xdg_runtime_dir=str(runtime))
    assert probe_id
    assert is_allowed_runtime_dispatch_probe_ack_path(ack_path, project_root=proj, xdg_runtime_dir=str(runtime)) is True
    assert is_allowed_runtime_dispatch_probe_ack_path(proj / 'not-allowed.json', project_root=proj, xdg_runtime_dir=str(runtime)) is False


def test_runtime_dispatch_probe_round_trip_reports_ok(tmp_path: Path, monkeypatch):
    proj = _write_project(tmp_path)
    project = load_project(proj)
    runtime = tmp_path / 'run'
    runtime.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv('XDG_RUNTIME_DIR', str(runtime))
    monkeypatch.setenv('DISPLAY', ':0')
    monkeypatch.setenv('XAUTHORITY', '/tmp/live.Xauthority')
    monkeypatch.setenv('DBUS_SESSION_BUS_ADDRESS', 'unix:path=/run/user/1000/bus')
    monkeypatch.setenv('I3SOCK', '/run/user/1000/i3/ipc.sock')

    sock = get_bus_socket_path(proj, configured=project.settings.bus_socket)
    out = {'stats': None, 'exc': None}

    def daemon():
        try:
            out['stats'] = run_bus_daemon(project, max_events=1)
        except Exception as exc:
            out['exc'] = exc

    t = threading.Thread(target=daemon, daemon=True)
    t.start()
    deadline = time.time() + 2
    while not sock.exists() and time.time() < deadline:
        time.sleep(0.01)

    payload = probe_runtime_dispatch_path(project_root=proj, bus_socket=sock, xdg_runtime_dir=str(runtime), timeout_s=0.75)
    expected_contract = summarize_project_runtime_contract_from_root(proj)
    summary = summarize_runtime_dispatch_probe(shell_env={
        'DISPLAY': ':0',
        'XAUTHORITY': '/tmp/live.Xauthority',
        'XDG_RUNTIME_DIR': str(runtime),
        'DBUS_SESSION_BUS_ADDRESS': 'unix:path=/run/user/1000/bus',
        'I3SOCK': '/run/user/1000/i3/ipc.sock',
    }, probe_payload=payload, expected_watchers=['hotkeys'], expected_runtime_contract=expected_contract)

    t.join(timeout=2)
    assert out['exc'] is None
    assert payload['status'] == 'ok'
    assert payload['ack']['received_event'] == 'vhk.runtime.probe'
    assert summary['status'] == 'ok'
    assert summary['env_in_sync'] is True
    assert summary['desktop_session_contract_in_sync'] is True
    assert summary['daemon_desktop_session_contract_status']['status'] == 'in_sync'
    assert summary['watchers_in_sync'] is True
    assert summary['runtime_contract_in_sync'] is True
    assert summary['daemon_watchers'] == ['hotkeys']
    assert summary['daemon_runtime_contract_digest'] == expected_contract['digest']
    assert payload['ack']['runtime_contract']['digest'] == expected_contract['digest']
    assert payload['ack']['runtime_state']['runtime_epoch_id']
    assert summary['daemon_runtime_epoch_id'] == payload['ack']['runtime_state']['runtime_epoch_id']
    assert summary['daemon_reload_count'] == 0
    assert summary['ack_pid'] is not None



def test_runtime_dispatch_probe_summary_reports_expected_watcher_drift():
    summary = summarize_runtime_dispatch_probe(
        shell_env={
            'DISPLAY': ':0',
            'XAUTHORITY': '/tmp/live.Xauthority',
            'XDG_RUNTIME_DIR': '/run/user/1000',
            'DBUS_SESSION_BUS_ADDRESS': 'unix:path=/run/user/1000/bus',
            'I3SOCK': '/run/user/1000/i3/ipc.sock',
        },
        probe_payload={
            'status': 'ok',
            'probe_id': 'abc',
            'event_name': 'vhk.runtime.probe',
            'roundtrip_latency_ms': 12.5,
            'ack': {
                'pid': 4242,
                'watchers': ['clipboard'],
                'environment': {
                    'DISPLAY': ':0',
                    'XAUTHORITY': '/tmp/live.Xauthority',
                    'XDG_RUNTIME_DIR': '/run/user/1000',
                    'DBUS_SESSION_BUS_ADDRESS': 'unix:path=/run/user/1000/bus',
                    'I3SOCK': '/run/user/1000/i3/ipc.sock',
                },
            },
        },
        expected_watchers=['hotkeys'],
    )

    assert summary['status'] == 'ok'
    assert summary['env_in_sync'] is True
    assert summary['watchers_in_sync'] is False
    assert summary['missing_expected_watchers'] == ['hotkeys']
    assert summary['daemon_watchers'] == ['clipboard']
    assert 'missing watchers: hotkeys' in summary['summary']


def test_runtime_dispatch_probe_summary_reports_runtime_contract_drift():
    summary = summarize_runtime_dispatch_probe(
        shell_env={
            'DISPLAY': ':0',
            'XAUTHORITY': '/tmp/live.Xauthority',
            'XDG_RUNTIME_DIR': '/run/user/1000',
            'DBUS_SESSION_BUS_ADDRESS': 'unix:path=/run/user/1000/bus',
            'I3SOCK': '/run/user/1000/i3/ipc.sock',
        },
        probe_payload={
            'status': 'ok',
            'probe_id': 'abc',
            'event_name': 'vhk.runtime.probe',
            'roundtrip_latency_ms': 12.5,
            'ack': {
                'pid': 4242,
                'watchers': ['hotkeys'],
                'runtime_contract': {'digest': 'daemon-digest'},
                'environment': {
                    'DISPLAY': ':0',
                    'XAUTHORITY': '/tmp/live.Xauthority',
                    'XDG_RUNTIME_DIR': '/run/user/1000',
                    'DBUS_SESSION_BUS_ADDRESS': 'unix:path=/run/user/1000/bus',
                    'I3SOCK': '/run/user/1000/i3/ipc.sock',
                },
            },
        },
        expected_watchers=['hotkeys'],
        expected_runtime_contract={'digest': 'disk-digest'},
    )

    assert summary['status'] == 'ok'
    assert summary['env_in_sync'] is True
    assert summary['watchers_in_sync'] is True
    assert summary['runtime_contract_in_sync'] is False
    assert summary['expected_runtime_contract_digest'] == 'disk-digest'
    assert summary['daemon_runtime_contract_digest'] == 'daemon-digest'
    assert 'runtime contract digest drift' in summary['summary']

def test_runtime_dispatch_probe_summary_reports_daemon_desktop_session_drift():
    summary = summarize_runtime_dispatch_probe(
        shell_env={
            'DISPLAY': ':0',
            'XAUTHORITY': '/tmp/live.Xauthority',
            'XDG_RUNTIME_DIR': '/run/user/1000',
            'DBUS_SESSION_BUS_ADDRESS': 'unix:path=/run/user/1000/bus',
            'I3SOCK': '/run/user/1000/i3/ipc.sock',
            'XDG_SESSION_TYPE': 'x11',
            'XDG_CURRENT_DESKTOP': 'i3',
        },
        probe_payload={
            'status': 'ok',
            'probe_id': 'abc',
            'event_name': 'vhk.runtime.probe',
            'roundtrip_latency_ms': 12.5,
            'ack': {
                'pid': 4242,
                'watchers': ['hotkeys'],
                'environment': {
                    'DISPLAY': ':0',
                    'XAUTHORITY': '/tmp/live.Xauthority',
                    'XDG_RUNTIME_DIR': '/run/user/1000',
                    'DBUS_SESSION_BUS_ADDRESS': 'unix:path=/run/user/1000/bus',
                    'I3SOCK': '/run/user/1000/i3/ipc.sock',
                },
                'desktop_session_contract': {
                    'display': ':0',
                    'xauthority': '/tmp/live.Xauthority',
                    'i3sock': '/run/user/1000/i3/ipc.sock',
                    'session_type': 'x11',
                    'current_desktop': 'openbox',
                },
            },
        },
        expected_watchers=['hotkeys'],
    )

    assert summary['status'] == 'ok'
    assert summary['env_in_sync'] is True
    assert summary['desktop_session_contract_in_sync'] is False
    assert summary['daemon_desktop_session_contract_status']['status'] == 'drifted'
    assert 'XDG_CURRENT_DESKTOP changed since latest healthy replay' in summary['daemon_desktop_session_contract_status']['reasons']
    assert summary['daemon_desktop_session_contract']['current_desktop'] == 'openbox'
    assert 'daemon desktop session drift:' in summary['summary']



def test_runtime_dispatch_probe_summary_reports_over_budget_latency():
    summary = summarize_runtime_dispatch_probe(
        shell_env={
            'DISPLAY': ':0',
            'XAUTHORITY': '/tmp/live.Xauthority',
            'XDG_RUNTIME_DIR': '/run/user/1000',
            'DBUS_SESSION_BUS_ADDRESS': 'unix:path=/run/user/1000/bus',
            'I3SOCK': '/run/user/1000/i3/ipc.sock',
        },
        probe_payload={
            'status': 'ok',
            'probe_id': 'abc',
            'event_name': 'vhk.runtime.probe',
            'roundtrip_latency_ms': 91.4,
            'ack': {
                'pid': 4242,
                'watchers': ['hotkeys'],
                'runtime_contract': {'digest': 'disk-digest'},
                'environment': {
                    'DISPLAY': ':0',
                    'XAUTHORITY': '/tmp/live.Xauthority',
                    'XDG_RUNTIME_DIR': '/run/user/1000',
                    'DBUS_SESSION_BUS_ADDRESS': 'unix:path=/run/user/1000/bus',
                    'I3SOCK': '/run/user/1000/i3/ipc.sock',
                },
            },
        },
        expected_watchers=['hotkeys'],
        expected_runtime_contract={'digest': 'disk-digest'},
    )

    assert summary['status'] == 'ok'
    assert summary['watchers_in_sync'] is True
    assert summary['runtime_contract_in_sync'] is True
    assert summary['latency_status'] == 'over_budget'
    assert summary['latency_within_budget'] is False
    assert summary['latency_budget_ms'] == 60.0
    assert 'warm-path probe latency over budget: 91.4ms > 60ms' in summary['summary']

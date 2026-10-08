from vhk.project.desktop_session_contract import summarize_desktop_session_contract
from vhk.project.runtime_reload_receipt import summarize_runtime_reload_receipt


def test_runtime_reload_receipt_reports_observed_reload_and_sync():
    current_session = summarize_desktop_session_contract({
        'DISPLAY': ':1',
        'XAUTHORITY': '/tmp/auth',
        'I3SOCK': '/tmp/i3.sock',
        'XDG_SESSION_TYPE': 'x11',
        'XDG_CURRENT_DESKTOP': 'i3',
    })
    receipt = summarize_runtime_reload_receipt(
        before_probe={
            'status': 'ok',
            'ack': {
                'pid': 100,
                'runtime_contract': {'digest': 'old-digest'},
                'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
                'desktop_session_contract': current_session,
            },
        },
        after_probe={
            'status': 'ok',
            'ack': {
                'pid': 100,
                'runtime_contract': {'digest': 'new-digest'},
                'runtime_state': {'runtime_epoch_id': 'epoch-b', 'reload_count': 1, 'last_reload_reason': 'bus:vhk.reload'},
                'desktop_session_contract': current_session,
            },
        },
        expected_runtime_contract={'digest': 'new-digest'},
        current_desktop_session_contract=current_session,
        reload_command='./bin/reload_runtime_json.sh',
        restart_runtime_command='systemctl --user restart vhk-busd.service',
        inspect_runtime_command='./bin/check_runtime_json.sh',
        emit_status='ok',
    )

    assert receipt['status'] == 'reload_observed_and_in_sync'
    assert receipt['ok'] is True
    assert receipt['runtime_epoch_changed'] is True
    assert receipt['reload_count_increased'] is True
    assert receipt['runtime_contract_in_sync'] is True
    assert receipt['after_desktop_session_contract_in_sync'] is True
    assert receipt['last_reload_reason'] == 'bus:vhk.reload'
    assert receipt['recommended_followup'] is None


def test_runtime_reload_receipt_reports_contract_sync_even_without_epoch_change():
    current_session = summarize_desktop_session_contract({
        'DISPLAY': ':1',
        'XAUTHORITY': '/tmp/auth',
        'I3SOCK': '/tmp/i3.sock',
        'XDG_SESSION_TYPE': 'x11',
        'XDG_CURRENT_DESKTOP': 'i3',
    })
    receipt = summarize_runtime_reload_receipt(
        before_probe={
            'status': 'ok',
            'ack': {
                'pid': 100,
                'runtime_contract': {'digest': 'old-digest'},
                'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
                'desktop_session_contract': current_session,
            },
        },
        after_probe={
            'status': 'ok',
            'ack': {
                'pid': 100,
                'runtime_contract': {'digest': 'new-digest'},
                'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
                'desktop_session_contract': current_session,
            },
        },
        expected_runtime_contract={'digest': 'new-digest'},
        current_desktop_session_contract=current_session,
        emit_status='ok',
    )

    assert receipt['status'] == 'contract_in_sync_after_reload'
    assert receipt['ok'] is True
    assert receipt['reload_observed'] is False
    assert receipt['runtime_contract_in_sync'] is True
    assert receipt['after_desktop_session_contract_in_sync'] is True


def test_runtime_reload_receipt_reports_daemon_desktop_session_drift_even_after_contract_sync():
    current_session = summarize_desktop_session_contract({
        'DISPLAY': ':1',
        'XAUTHORITY': '/tmp/auth-a',
        'I3SOCK': '/tmp/i3-a.sock',
        'XDG_SESSION_TYPE': 'x11',
        'XDG_CURRENT_DESKTOP': 'i3',
    })
    stale_daemon_session = summarize_desktop_session_contract({
        'DISPLAY': ':2',
        'XAUTHORITY': '/tmp/auth-b',
        'I3SOCK': '/tmp/i3-b.sock',
        'XDG_SESSION_TYPE': 'x11',
        'XDG_CURRENT_DESKTOP': 'openbox',
    })
    receipt = summarize_runtime_reload_receipt(
        before_probe={
            'status': 'ok',
            'ack': {
                'pid': 100,
                'runtime_contract': {'digest': 'old-digest'},
                'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
                'desktop_session_contract': stale_daemon_session,
            },
        },
        after_probe={
            'status': 'ok',
            'ack': {
                'pid': 100,
                'runtime_contract': {'digest': 'new-digest'},
                'runtime_state': {'runtime_epoch_id': 'epoch-b', 'reload_count': 1},
                'desktop_session_contract': stale_daemon_session,
            },
        },
        expected_runtime_contract={'digest': 'new-digest'},
        current_desktop_session_contract=current_session,
        reload_command='./bin/reload_runtime_json.sh',
        restart_runtime_command='systemctl --user restart vhk-busd.service',
        inspect_runtime_command='./bin/check_runtime_json.sh',
        emit_status='ok',
    )

    assert receipt['status'] == 'reload_observed_but_daemon_desktop_session_drift'
    assert receipt['ok'] is False
    assert receipt['runtime_contract_in_sync'] is True
    assert receipt['after_desktop_session_contract_in_sync'] is False
    assert receipt['after_daemon_desktop_session_contract_status']['status'] == 'drifted'
    assert 'DISPLAY changed since latest healthy replay' in receipt['after_daemon_desktop_session_contract_status']['reasons']
    assert receipt['recommended_followup']['id'] == 'restart_runtime_for_daemon_desktop_session'
    assert receipt['recommended_followup']['route_id'] == 'daemon_desktop_session_then_restart'
    assert receipt['recommended_followup']['command'] == 'systemctl --user restart vhk-busd.service'


def test_runtime_reload_receipt_reports_emit_failure():
    receipt = summarize_runtime_reload_receipt(
        before_probe={'status': 'ok', 'ack': {'runtime_contract': {'digest': 'old'}}},
        after_probe={'status': 'ok', 'ack': {'runtime_contract': {'digest': 'old'}}},
        expected_runtime_contract={'digest': 'new'},
        inspect_runtime_command='./bin/check_runtime_json.sh',
        emit_status='emit_failed',
        emit_error='socket missing',
    )

    assert receipt['status'] == 'reload_emit_failed'
    assert receipt['ok'] is False
    assert receipt['emit_error'] == 'socket missing'
    assert receipt['recommended_followup']['id'] == 'inspect_runtime_reload_path'
    assert receipt['recommended_followup']['command'] == './bin/check_runtime_json.sh'

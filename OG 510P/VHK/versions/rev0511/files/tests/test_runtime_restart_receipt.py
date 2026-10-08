from vhk.project.runtime_restart_receipt import summarize_runtime_restart_receipt


def test_runtime_restart_receipt_reports_fresh_ready_runtime():
    receipt = summarize_runtime_restart_receipt(
        before_probe={'status': 'ok', 'ack': {'pid': 100, 'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0}}},
        after_probe={'status': 'ok', 'ack': {'pid': 200, 'runtime_state': {'runtime_epoch_id': 'epoch-b', 'reload_count': 0}}},
        after_summary={'status': 'ok', 'ok': True, 'runtime_contract_in_sync': True, 'watchers_in_sync': True, 'desktop_session_contract_in_sync': True},
        restart_command='./bin/restart_runtime_json.sh',
        sync_activation_environment_command='dbus-update-activation-environment --systemd DISPLAY XAUTHORITY DBUS_SESSION_BUS_ADDRESS XDG_RUNTIME_DIR I3SOCK',
        inspect_runtime_command='./bin/check_runtime_json.sh',
        reload_runtime_command='./bin/reload_runtime_json.sh',
        sync_status='ok',
        restart_status='ok',
    )
    assert receipt['status'] == 'restart_observed_and_runtime_ready'
    assert receipt['ok'] is True
    assert receipt['runtime_epoch_changed'] is True
    assert receipt['pid_changed'] is True
    assert receipt['restart_observed'] is True
    assert receipt['recommended_followup'] is None


def test_runtime_restart_receipt_reports_daemon_desktop_session_drift_after_restart():
    receipt = summarize_runtime_restart_receipt(
        before_probe={'status': 'ok', 'ack': {'pid': 100, 'runtime_state': {'runtime_epoch_id': 'epoch-a'}}},
        after_probe={'status': 'ok', 'ack': {'pid': 200, 'runtime_state': {'runtime_epoch_id': 'epoch-b'}}},
        after_summary={'status': 'ok', 'ok': False, 'runtime_contract_in_sync': True, 'watchers_in_sync': True, 'desktop_session_contract_in_sync': False, 'daemon_desktop_session_contract_status': {'status': 'drifted', 'reasons': ['DISPLAY changed since latest healthy replay']}},
        restart_command='./bin/restart_runtime_json.sh',
        inspect_runtime_command='./bin/check_runtime_json.sh',
        sync_status='failed',
        sync_error='unable to talk to session bus',
        restart_status='ok',
    )
    assert receipt['status'] == 'restart_completed_but_daemon_desktop_session_drift'
    assert receipt['ok'] is False
    assert receipt['after_desktop_session_contract_in_sync'] is False
    assert receipt['after_daemon_desktop_session_contract_status']['status'] == 'drifted'
    assert receipt['recommended_followup']['id'] == 'inspect_runtime_session_attachment'
    assert receipt['recommended_followup']['command'] == './bin/check_runtime_json.sh'
    assert receipt['sync_status'] == 'failed'


def test_runtime_restart_receipt_recommends_reload_for_stale_runtime_contract():
    receipt = summarize_runtime_restart_receipt(
        before_probe={'status': 'ok', 'ack': {'pid': 100, 'runtime_state': {'runtime_epoch_id': 'epoch-a'}}},
        after_probe={'status': 'ok', 'ack': {'pid': 200, 'runtime_state': {'runtime_epoch_id': 'epoch-b'}}},
        after_summary={'status': 'ok', 'ok': False, 'runtime_contract_in_sync': False, 'watchers_in_sync': True, 'desktop_session_contract_in_sync': True},
        restart_command='./bin/restart_runtime_json.sh',
        inspect_runtime_command='./bin/check_runtime_json.sh',
        reload_runtime_command='./bin/reload_runtime_json.sh',
        restart_status='ok',
    )
    assert receipt['status'] == 'restart_completed_but_runtime_contract_stale'
    assert receipt['recommended_followup']['id'] == 'reload_runtime_for_project_contract'
    assert receipt['recommended_followup']['command'] == './bin/reload_runtime_json.sh'

from vhk.project.runtime_reload_receipt import summarize_runtime_reload_receipt


def test_runtime_reload_receipt_reports_observed_reload_and_sync():
    receipt = summarize_runtime_reload_receipt(
        before_probe={
            'status': 'ok',
            'ack': {
                'pid': 100,
                'runtime_contract': {'digest': 'old-digest'},
                'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
            },
        },
        after_probe={
            'status': 'ok',
            'ack': {
                'pid': 100,
                'runtime_contract': {'digest': 'new-digest'},
                'runtime_state': {'runtime_epoch_id': 'epoch-b', 'reload_count': 1, 'last_reload_reason': 'bus:vhk.reload'},
            },
        },
        expected_runtime_contract={'digest': 'new-digest'},
        reload_command='./bin/reload_runtime_json.sh',
        emit_status='ok',
    )

    assert receipt['status'] == 'reload_observed_and_in_sync'
    assert receipt['ok'] is True
    assert receipt['runtime_epoch_changed'] is True
    assert receipt['reload_count_increased'] is True
    assert receipt['runtime_contract_in_sync'] is True
    assert receipt['last_reload_reason'] == 'bus:vhk.reload'


def test_runtime_reload_receipt_reports_contract_sync_even_without_epoch_change():
    receipt = summarize_runtime_reload_receipt(
        before_probe={
            'status': 'ok',
            'ack': {
                'pid': 100,
                'runtime_contract': {'digest': 'old-digest'},
                'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
            },
        },
        after_probe={
            'status': 'ok',
            'ack': {
                'pid': 100,
                'runtime_contract': {'digest': 'new-digest'},
                'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
            },
        },
        expected_runtime_contract={'digest': 'new-digest'},
        emit_status='ok',
    )

    assert receipt['status'] == 'contract_in_sync_after_reload'
    assert receipt['ok'] is True
    assert receipt['reload_observed'] is False
    assert receipt['runtime_contract_in_sync'] is True


def test_runtime_reload_receipt_reports_emit_failure():
    receipt = summarize_runtime_reload_receipt(
        before_probe={'status': 'ok', 'ack': {'runtime_contract': {'digest': 'old'}}},
        after_probe={'status': 'ok', 'ack': {'runtime_contract': {'digest': 'old'}}},
        expected_runtime_contract={'digest': 'new'},
        emit_status='emit_failed',
        emit_error='socket missing',
    )

    assert receipt['status'] == 'reload_emit_failed'
    assert receipt['ok'] is False
    assert receipt['emit_error'] == 'socket missing'

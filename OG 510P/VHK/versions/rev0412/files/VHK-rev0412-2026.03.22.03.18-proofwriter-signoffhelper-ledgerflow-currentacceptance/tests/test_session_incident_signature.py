from __future__ import annotations

from vhk.project.session_incident_signature import summarize_session_incident_signature


def test_incident_signature_reports_clean_session_skip() -> None:
    payload = summarize_session_incident_signature(
        service_mode='socket-activated-busd',
        expected_units=['vhk-busd-proj.service'],
        units=[{'unit': 'vhk-busd-proj.service', 'active_state': 'inactive', 'sub_state': 'dead', 'condition_result': 'no', 'result': 'condition'}],
        readiness_runtime={'verdict': 'not_ready'},
        runtime_health={'verdict': 'skipped_not_ready'},
        journal_entries=[{'MESSAGE': "vhk-busd-proj.service: Skipped due to 'exec-condition'."}],
        journal_available=True,
    )
    assert payload['verdict'] == 'clean_session_skip'
    assert 'session was not ready yet' in payload['summary']


def test_incident_signature_reports_start_limit_churn() -> None:
    payload = summarize_session_incident_signature(
        service_mode='socket-activated-busd',
        expected_units=['vhk-busd-proj.service'],
        units=[{'unit': 'vhk-busd-proj.service', 'active_state': 'failed', 'sub_state': 'failed', 'result': 'start-limit-hit'}],
        readiness_runtime={'verdict': 'ready'},
        runtime_health={'verdict': 'degraded_restart_churn'},
        journal_entries=[{'MESSAGE': 'vhk-busd-proj.service: Start request repeated too quickly.'}],
        journal_available=True,
    )
    assert payload['verdict'] == 'start_limit_churn'
    assert 'restart churn' in payload['summary']


def test_incident_signature_reports_service_failure() -> None:
    payload = summarize_session_incident_signature(
        service_mode='socket-activated-busd',
        expected_units=['vhk-busd-proj.service'],
        units=[{'unit': 'vhk-busd-proj.service', 'active_state': 'failed', 'sub_state': 'failed', 'result': 'exit-code'}],
        readiness_runtime={'verdict': 'ready'},
        runtime_health={'verdict': 'degraded_failed'},
        journal_entries=[{'MESSAGE': 'vhk-busd-proj.service: Main process exited, code=exited, status=1/FAILURE'}],
        journal_available=True,
    )
    assert payload['verdict'] == 'service_failure'
    assert 'real service/process failure' in payload['summary']


def test_incident_signature_reports_healthy_no_recent_incident() -> None:
    payload = summarize_session_incident_signature(
        service_mode='socket-activated-busd',
        expected_units=['vhk-busd-proj.socket'],
        units=[{'unit': 'vhk-busd-proj.socket', 'active_state': 'active', 'sub_state': 'listening', 'result': 'success'}],
        readiness_runtime={'verdict': 'ready'},
        runtime_health={'verdict': 'healthy'},
        journal_entries=[],
        journal_available=False,
    )
    assert payload['verdict'] == 'healthy_no_recent_incident'

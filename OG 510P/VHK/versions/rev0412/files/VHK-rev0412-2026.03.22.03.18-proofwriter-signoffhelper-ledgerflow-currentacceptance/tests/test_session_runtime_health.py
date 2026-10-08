from __future__ import annotations

from vhk.project.session_runtime_health import summarize_session_runtime_health


def test_runtime_health_reports_no_owned_service_for_environment_only_lane() -> None:
    payload = summarize_session_runtime_health(
        service_mode='environment-only',
        expected_units=[],
        units=[],
        readiness_runtime={'verdict': 'ready'},
        systemctl_available=True,
    )
    assert payload['verdict'] == 'no_owned_service'
    assert 'does not ship a VHK-owned long-lived user service' in payload['summary']


def test_runtime_health_reports_skipped_when_readiness_not_ready() -> None:
    payload = summarize_session_runtime_health(
        service_mode='socket-activated-busd',
        expected_units=['vhk-busd-proj.socket', 'vhk-busd-proj.service'],
        units=[
            {
                'unit': 'vhk-busd-proj.socket',
                'load_state': 'loaded',
                'active_state': 'inactive',
                'sub_state': 'dead',
                'result': 'success',
                'condition_result': '',
                'n_restarts': '0',
                'query_ok': True,
            }
        ],
        readiness_runtime={'verdict': 'not_ready'},
        systemctl_available=True,
    )
    assert payload['verdict'] == 'skipped_not_ready'
    assert payload['readiness_verdict'] == 'not_ready'


def test_runtime_health_reports_restart_churn_from_start_limit() -> None:
    payload = summarize_session_runtime_health(
        service_mode='socket-activated-busd',
        expected_units=['vhk-busd-proj.service'],
        units=[
            {
                'unit': 'vhk-busd-proj.service',
                'load_state': 'loaded',
                'active_state': 'failed',
                'sub_state': 'failed',
                'result': 'start-limit-hit',
                'condition_result': '',
                'n_restarts': '7',
                'query_ok': True,
            }
        ],
        readiness_runtime={'verdict': 'ready'},
        systemctl_available=True,
    )
    assert payload['verdict'] == 'degraded_restart_churn'
    assert payload['counts']['restart_churn_unit_count'] == 1
    assert payload['counts']['start_limit_unit_count'] == 1
    assert 'start-limit pressure' in payload['summary']


def test_runtime_health_reports_healthy_for_active_socket_lane() -> None:
    payload = summarize_session_runtime_health(
        service_mode='socket-activated-busd',
        expected_units=['vhk-busd-proj.socket', 'vhk-busd-proj.service'],
        units=[
            {
                'unit': 'vhk-busd-proj.socket',
                'load_state': 'loaded',
                'active_state': 'active',
                'sub_state': 'listening',
                'result': 'success',
                'condition_result': '',
                'n_restarts': '0',
                'query_ok': True,
            },
            {
                'unit': 'vhk-busd-proj.service',
                'load_state': 'loaded',
                'active_state': 'inactive',
                'sub_state': 'dead',
                'result': 'success',
                'condition_result': '',
                'n_restarts': '0',
                'query_ok': True,
            },
        ],
        readiness_runtime={'verdict': 'ready'},
        systemctl_available=True,
    )
    assert payload['verdict'] == 'healthy'
    assert payload['counts']['healthy_unit_count'] >= 1

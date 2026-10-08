from __future__ import annotations

from vhk.project.session_runtime_health_drift import summarize_session_runtime_health_drift


def test_runtime_health_drift_reports_first_snapshot() -> None:
    payload = summarize_session_runtime_health_drift({'verdict': 'healthy', 'readiness_verdict': 'ready'}, [])
    assert payload['verdict'] == 'first_snapshot'
    assert payload['current_verdict'] == 'healthy'


def test_runtime_health_drift_reports_recovered_healthy() -> None:
    payload = summarize_session_runtime_health_drift(
        {'verdict': 'healthy', 'readiness_verdict': 'ready'},
        [{'verdict': 'degraded_restart_churn', 'readiness_verdict': 'ready'}],
    )
    assert payload['verdict'] == 'recovered_healthy'
    assert payload['previous_verdict'] == 'degraded_restart_churn'


def test_runtime_health_drift_reports_chronic_restart_churn() -> None:
    payload = summarize_session_runtime_health_drift(
        {'verdict': 'degraded_restart_churn', 'readiness_verdict': 'ready'},
        [{'verdict': 'degraded_restart_churn', 'readiness_verdict': 'ready'}],
    )
    assert payload['verdict'] == 'chronic_restart_churn'
    assert 'restart churn' in payload['summary']


def test_runtime_health_drift_reports_flapping_health() -> None:
    payload = summarize_session_runtime_health_drift(
        {'verdict': 'stopped', 'readiness_verdict': 'ready'},
        [
            {'verdict': 'healthy', 'readiness_verdict': 'ready'},
            {'verdict': 'degraded_failed', 'readiness_verdict': 'ready'},
            {'verdict': 'degraded_restart_churn', 'readiness_verdict': 'ready'},
        ],
    )
    assert payload['verdict'] == 'flapping_health'
    assert payload['distinct_recent_verdict_count'] >= 3

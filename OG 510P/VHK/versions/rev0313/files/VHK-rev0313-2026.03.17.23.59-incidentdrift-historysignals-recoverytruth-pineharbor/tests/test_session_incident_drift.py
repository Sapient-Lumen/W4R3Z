from __future__ import annotations

from vhk.project.session_incident_drift import summarize_session_incident_drift


def test_incident_drift_reports_chronic_start_limit() -> None:
    payload = summarize_session_incident_drift(
        {
            'verdict': 'start_limit_churn',
            'readiness_verdict': 'ready',
            'runtime_health_verdict': 'degraded_restart_churn',
        },
        previous_history=[
            {'verdict': 'start_limit_churn', 'readiness_verdict': 'ready', 'runtime_health_verdict': 'degraded_restart_churn'},
        ],
    )
    assert payload['verdict'] == 'chronic_start_limit'
    assert 'start-limit' in payload['summary'] or 'restart-churn' in payload['summary']


def test_incident_drift_reports_recovered_to_quiet() -> None:
    payload = summarize_session_incident_drift(
        {
            'verdict': 'healthy_no_recent_incident',
            'readiness_verdict': 'ready',
            'runtime_health_verdict': 'healthy',
        },
        previous_history=[
            {'verdict': 'service_failure', 'readiness_verdict': 'ready', 'runtime_health_verdict': 'degraded_failed'},
        ],
    )
    assert payload['verdict'] == 'recovered_to_quiet'
    assert 'quiet no-recent-incident posture' in payload['summary']


def test_incident_drift_reports_changed_skip_mode() -> None:
    payload = summarize_session_incident_drift(
        {
            'verdict': 'condition_skip',
            'readiness_verdict': 'not_ready',
            'runtime_health_verdict': 'skipped_not_ready',
        },
        previous_history=[
            {'verdict': 'clean_session_skip', 'readiness_verdict': 'not_ready', 'runtime_health_verdict': 'skipped_not_ready'},
        ],
    )
    assert payload['verdict'] == 'changed_skip_mode'
    assert 'skip mode changed' in payload['summary']

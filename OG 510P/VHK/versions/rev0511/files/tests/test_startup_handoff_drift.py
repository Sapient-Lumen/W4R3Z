from __future__ import annotations

from vhk.project.startup_handoff_drift import summarize_startup_handoff_drift


def test_startup_handoff_drift_reports_first_snapshot() -> None:
    payload = summarize_startup_handoff_drift({'verdict': 'primary_user_unit_owner'}, [])
    assert payload['verdict'] == 'first_snapshot'
    assert payload['current_verdict'] == 'primary_user_unit_owner'


def test_startup_handoff_drift_reports_stable() -> None:
    payload = summarize_startup_handoff_drift(
        {'verdict': 'primary_user_unit_owner'},
        [{'verdict': 'primary_user_unit_owner'}, {'verdict': 'primary_user_unit_owner'}],
    )
    assert payload['verdict'] == 'stable'
    assert payload['previous_verdict'] == 'primary_user_unit_owner'


def test_startup_handoff_drift_reports_chronic_duplicate_risk() -> None:
    payload = summarize_startup_handoff_drift(
        {'verdict': 'duplicate_start_risk'},
        [{'verdict': 'duplicate_start_risk'}],
    )
    assert payload['verdict'] == 'chronic_duplicate_risk'
    assert 'duplicate-start risk' in payload['summary']


def test_startup_handoff_drift_reports_flapping_owners() -> None:
    payload = summarize_startup_handoff_drift(
        {'verdict': 'fallback_autostart_owner'},
        [
            {'verdict': 'primary_user_unit_owner'},
            {'verdict': 'duplicate_start_risk'},
            {'verdict': 'no_startup_owner'},
        ],
    )
    assert payload['verdict'] == 'flapping_owners'
    assert payload['distinct_recent_verdict_count'] >= 3

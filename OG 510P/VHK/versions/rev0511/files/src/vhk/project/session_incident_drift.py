from __future__ import annotations

from collections import Counter
from typing import Any, Mapping

_QUIET_VERDICTS = {
    'healthy_no_recent_incident',
    'stopped_no_recent_incident',
    'no_owned_service',
}

_SKIP_VERDICTS = {
    'clean_session_skip',
    'condition_skip',
}

_HARD_INCIDENT_VERDICTS = {
    'start_limit_churn',
    'service_failure',
    'missing_unit',
    'probe_error',
}


def _coerce_snapshot(snapshot: Mapping[str, Any] | None) -> dict[str, Any]:
    row = dict(snapshot or {})
    return {
        'generated_at': str(row.get('generated_at') or '').strip(),
        'generated_at_epoch': row.get('generated_at_epoch'),
        'verdict': str(row.get('verdict') or 'unavailable').strip() or 'unavailable',
        'summary': str(row.get('summary') or '').strip(),
        'readiness_verdict': str(row.get('readiness_verdict') or '').strip(),
        'runtime_health_verdict': str(row.get('runtime_health_verdict') or '').strip(),
        'journal_entry_count': int(row.get('journal_entry_count') or 0),
    }


def summarize_session_incident_drift(
    current_snapshot: Mapping[str, Any] | None,
    previous_history: list[Mapping[str, Any]] | None = None,
    *,
    history_limit: int = 12,
) -> dict[str, Any]:
    current = _coerce_snapshot(current_snapshot)
    previous = [_coerce_snapshot(item) for item in list(previous_history or []) if isinstance(item, Mapping)]
    if history_limit > 0 and len(previous) > history_limit:
        previous = previous[-history_limit:]
    prior = [item for item in previous if item.get('verdict')]
    prior_last = prior[-1] if prior else None
    recent = [*prior[-3:], current] if prior else [current]
    recent_verdicts = [str(item.get('verdict') or 'unavailable') for item in recent]
    distinct_recent_verdicts = list(dict.fromkeys(recent_verdicts))
    current_verdict = str(current.get('verdict') or 'unavailable')
    verdict_counter = Counter(recent_verdicts)

    if current_verdict == 'unavailable':
        verdict = 'unavailable'
    elif not prior_last:
        verdict = 'first_snapshot'
    elif len(distinct_recent_verdicts) >= 3:
        verdict = 'flapping_incidents'
    elif current_verdict == 'start_limit_churn' and verdict_counter.get('start_limit_churn', 0) >= 2:
        verdict = 'chronic_start_limit'
    elif current_verdict == 'service_failure' and verdict_counter.get('service_failure', 0) >= 2:
        verdict = 'chronic_service_failure'
    elif current_verdict == 'missing_unit' and verdict_counter.get('missing_unit', 0) >= 2:
        verdict = 'chronic_missing_unit'
    elif current_verdict == 'probe_error' and verdict_counter.get('probe_error', 0) >= 2:
        verdict = 'chronic_probe_error'
    elif current_verdict == str(prior_last.get('verdict') or ''):
        verdict = 'stable'
    elif current_verdict in _QUIET_VERDICTS and str(prior_last.get('verdict') or '') not in _QUIET_VERDICTS:
        verdict = 'recovered_to_quiet'
    elif str(prior_last.get('verdict') or '') in _QUIET_VERDICTS and current_verdict not in _QUIET_VERDICTS:
        verdict = 'drifted_from_quiet'
    elif current_verdict in _SKIP_VERDICTS and str(prior_last.get('verdict') or '') in _SKIP_VERDICTS:
        verdict = 'changed_skip_mode'
    elif current_verdict in _HARD_INCIDENT_VERDICTS and str(prior_last.get('verdict') or '') in _HARD_INCIDENT_VERDICTS:
        verdict = 'changed_incident_mode'
    else:
        verdict = 'changed_recently'

    summary_headline = {
        'first_snapshot': 'This is the first incident-signature snapshot for the installed lane, so there is no older incident history to compare yet.',
        'stable': 'Recent installed-lane snapshots keep showing the same incident signature verdict.',
        'changed_recently': 'The incident signature changed relative to the previous installed-lane snapshot.',
        'recovered_to_quiet': 'The installed lane moved back to a quiet no-recent-incident posture after a stronger or more explicit earlier incident.',
        'drifted_from_quiet': 'The installed lane drifted away from a quiet no-recent-incident posture into a stronger recent incident signature.',
        'changed_skip_mode': 'The installed lane still looks skipped, but the skip mode changed across recent snapshots.',
        'changed_incident_mode': 'The installed lane stayed incident-shaped, but the dominant incident class changed across recent snapshots.',
        'chronic_start_limit': 'Recent installed-lane snapshots keep showing start-limit or restart-churn incidents instead of settling down.',
        'chronic_service_failure': 'Recent installed-lane snapshots keep showing real service-failure incidents instead of settling down.',
        'chronic_missing_unit': 'Recent installed-lane snapshots keep showing missing-unit incidents rather than a restored owned lane.',
        'chronic_probe_error': 'Recent installed-lane snapshots keep showing readiness/probe-error incidents rather than a restored owned lane.',
        'flapping_incidents': 'Recent installed-lane snapshots show multiple different incident signatures, which suggests the lane is flapping between incident classes.',
        'unavailable': 'Incident-signature drift could not be established from the available installed-lane history.',
    }.get(verdict, 'Incident-signature drift summary unavailable.')

    reasons = [summary_headline]
    if prior_last:
        reasons.append(f"Previous verdict: {prior_last.get('verdict') or 'unknown'}.")
    reasons.append(f"Current verdict: {current_verdict}.")
    if current.get('readiness_verdict'):
        reasons.append(f"Current readiness verdict: {current.get('readiness_verdict')}.")
    if current.get('runtime_health_verdict'):
        reasons.append(f"Current runtime health verdict: {current.get('runtime_health_verdict')}.")
    if recent_verdicts:
        reasons.append('Recent verdicts: ' + ' -> '.join(recent_verdicts) + '.')

    return {
        'verdict': verdict,
        'summary': ' '.join(piece for piece in reasons if piece).strip(),
        'previous_verdict': prior_last.get('verdict') if prior_last else None,
        'current_verdict': current_verdict,
        'recent_verdicts': recent_verdicts,
        'recent_snapshot_count': len(recent),
        'history_sample_count': len(prior),
        'distinct_recent_verdict_count': len(distinct_recent_verdicts),
    }


def known_session_incident_drift_verdicts() -> list[str]:
    return [
        'first_snapshot',
        'stable',
        'changed_recently',
        'recovered_to_quiet',
        'drifted_from_quiet',
        'changed_skip_mode',
        'changed_incident_mode',
        'chronic_start_limit',
        'chronic_service_failure',
        'chronic_missing_unit',
        'chronic_probe_error',
        'flapping_incidents',
        'unavailable',
    ]

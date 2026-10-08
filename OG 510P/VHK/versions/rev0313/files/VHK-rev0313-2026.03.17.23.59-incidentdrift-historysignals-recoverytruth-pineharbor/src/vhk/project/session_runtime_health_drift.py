from __future__ import annotations

from collections import Counter
from typing import Any, Mapping

_DEGRADED_VERDICTS = {
    'degraded_restart_churn',
    'degraded_failed',
    'degraded_probe_error',
    'degraded_unit_missing',
}


def _coerce_snapshot(snapshot: Mapping[str, Any] | None) -> dict[str, Any]:
    row = dict(snapshot or {})
    counts = dict(row.get('counts') or {}) if isinstance(row.get('counts'), Mapping) else {}
    return {
        'generated_at': str(row.get('generated_at') or '').strip(),
        'generated_at_epoch': row.get('generated_at_epoch'),
        'verdict': str(row.get('verdict') or 'unavailable').strip() or 'unavailable',
        'summary': str(row.get('summary') or '').strip(),
        'readiness_verdict': str(row.get('readiness_verdict') or '').strip(),
        'healthy_unit_count': int(counts.get('healthy_unit_count') or row.get('healthy_unit_count') or 0),
        'failed_unit_count': int(counts.get('failed_unit_count') or row.get('failed_unit_count') or 0),
        'restart_churn_unit_count': int(counts.get('restart_churn_unit_count') or row.get('restart_churn_unit_count') or 0),
        'missing_unit_count': int(counts.get('missing_unit_count') or row.get('missing_unit_count') or 0),
    }


def summarize_session_runtime_health_drift(
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
    current_recent_count = verdict_counter.get(current_verdict, 0)

    if current_verdict == 'unavailable':
        verdict = 'unavailable'
    elif not prior_last:
        verdict = 'first_snapshot'
    elif len(distinct_recent_verdicts) >= 3:
        verdict = 'flapping_health'
    elif current_verdict == 'degraded_restart_churn' and verdict_counter.get('degraded_restart_churn', 0) >= 2:
        verdict = 'chronic_restart_churn'
    elif current_verdict == 'degraded_failed' and verdict_counter.get('degraded_failed', 0) >= 2:
        verdict = 'chronic_failed'
    elif current_verdict in {'stopped', 'degraded_unit_missing', 'no_owned_service'} and current_recent_count >= 2:
        verdict = 'chronic_inactive_or_missing'
    elif current_verdict == str(prior_last.get('verdict') or ''):
        verdict = 'stable'
    elif current_verdict == 'healthy' and str(prior_last.get('verdict') or '') != 'healthy':
        verdict = 'recovered_healthy'
    elif str(prior_last.get('verdict') or '') == 'healthy' and current_verdict != 'healthy':
        verdict = 'drifted_from_healthy'
    elif current_verdict in _DEGRADED_VERDICTS and str(prior_last.get('verdict') or '') in _DEGRADED_VERDICTS:
        verdict = 'changed_degraded_mode'
    else:
        verdict = 'changed_recently'

    summary_headline = {
        'first_snapshot': 'This is the first runtime-health snapshot for the installed lane, so there is no older health history to compare yet.',
        'stable': 'Runtime health looks stable across the recent installed-lane snapshots.',
        'changed_recently': 'Runtime health changed relative to the previous installed-lane snapshot.',
        'recovered_healthy': 'Runtime health moved back to a healthy owned-lane state after a weaker or degraded previous snapshot.',
        'drifted_from_healthy': 'Runtime health drifted away from a previously healthy owned-lane state in the most recent comparison.',
        'changed_degraded_mode': 'Runtime health stayed degraded, but the degradation mode changed between recent snapshots.',
        'chronic_restart_churn': 'Recent installed-lane snapshots keep showing restart churn or start-limit pressure rather than a recovered steady state.',
        'chronic_failed': 'Recent installed-lane snapshots keep showing failed user-unit state rather than a recovered steady state.',
        'chronic_inactive_or_missing': 'Recent installed-lane snapshots keep showing inactive, missing, or no-owned-service runtime states rather than a live healthy lane.',
        'flapping_health': 'Recent installed-lane snapshots show multiple different runtime-health verdicts, which suggests the lane is flapping between health states.',
        'unavailable': 'Runtime-health drift could not be established from the available installed-lane history.',
    }.get(verdict, 'Runtime-health drift summary unavailable.')

    reasons = [summary_headline]
    if prior_last:
        reasons.append(f"Previous verdict: {prior_last.get('verdict') or 'unknown'}.")
    reasons.append(f"Current verdict: {current_verdict}.")
    if current.get('readiness_verdict'):
        reasons.append(f"Current readiness verdict: {current.get('readiness_verdict')}.")
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


def known_session_runtime_health_drift_verdicts() -> list[str]:
    return [
        'first_snapshot',
        'stable',
        'changed_recently',
        'recovered_healthy',
        'drifted_from_healthy',
        'changed_degraded_mode',
        'chronic_restart_churn',
        'chronic_failed',
        'chronic_inactive_or_missing',
        'flapping_health',
        'unavailable',
    ]

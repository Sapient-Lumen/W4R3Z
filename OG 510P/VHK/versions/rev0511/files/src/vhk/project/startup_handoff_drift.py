from __future__ import annotations

from collections import Counter
from typing import Any, Mapping


_MISSING_OWNER_VERDICTS = {
    'no_startup_owner',
    'masked_no_owner',
    'autostart_hidden_no_owner',
    'autostart_tryexec_missing',
}


def _coerce_snapshot(snapshot: Mapping[str, Any] | None) -> dict[str, Any]:
    row = dict(snapshot or {})
    counts = dict(row.get('counts') or {}) if isinstance(row.get('counts'), Mapping) else {}
    return {
        'generated_at': str(row.get('generated_at') or '').strip(),
        'generated_at_epoch': row.get('generated_at_epoch'),
        'verdict': str(row.get('verdict') or 'unavailable').strip() or 'unavailable',
        'summary': str(row.get('summary') or '').strip(),
        'enabled_unit_count': int(counts.get('enabled_unit_count') or row.get('enabled_unit_count') or 0),
        'masked_unit_count': int(counts.get('masked_unit_count') or row.get('masked_unit_count') or 0),
        'autostart_state': str(((row.get('autostart') or {}) if isinstance(row.get('autostart'), Mapping) else {}).get('state') or row.get('autostart_state') or '').strip(),
        'autostart_effective': bool((((row.get('autostart') or {}) if isinstance(row.get('autostart'), Mapping) else {}).get('effective')) if isinstance(row.get('autostart'), Mapping) else row.get('autostart_effective')),
    }


def summarize_startup_handoff_drift(
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
    current_recent_count = sum(1 for item in recent if str(item.get('verdict') or '') == current_verdict)
    verdict_counter = Counter(recent_verdicts)

    if current_verdict == 'unavailable':
        verdict = 'unavailable'
    elif not prior_last:
        verdict = 'first_snapshot'
    elif len(distinct_recent_verdicts) >= 3:
        verdict = 'flapping_owners'
    elif current_verdict == 'duplicate_start_risk' and verdict_counter.get('duplicate_start_risk', 0) >= 2:
        verdict = 'chronic_duplicate_risk'
    elif current_verdict in _MISSING_OWNER_VERDICTS and current_recent_count >= 2:
        verdict = 'chronic_missing_owner'
    elif current_verdict == prior_last.get('verdict'):
        verdict = 'stable'
    elif current_verdict == 'primary_user_unit_owner' and prior_last.get('verdict') != 'primary_user_unit_owner':
        verdict = 'recovered_to_primary'
    elif prior_last.get('verdict') == 'primary_user_unit_owner' and current_verdict != 'primary_user_unit_owner':
        verdict = 'drifted_from_primary'
    else:
        verdict = 'changed_recently'

    summary_headline = {
        'first_snapshot': 'This is the first startup-handoff snapshot for the installed lane, so there is no older owner history to compare yet.',
        'stable': 'Startup ownership looks stable across the recent installed-lane snapshots.',
        'changed_recently': 'Startup ownership changed relative to the previous installed-lane snapshot.',
        'recovered_to_primary': 'Startup ownership moved back to a primary VHK user-unit owner after a weaker or conflicting previous state.',
        'drifted_from_primary': 'Startup ownership drifted away from a primary VHK user-unit owner in the most recent comparison.',
        'chronic_duplicate_risk': 'Recent installed-lane snapshots keep showing duplicate-start risk rather than a one-owner startup path.',
        'chronic_missing_owner': 'Recent installed-lane snapshots keep showing no effective startup owner for the reviewed lane.',
        'flapping_owners': 'Recent installed-lane snapshots show multiple different startup-owner verdicts, which suggests the lane is flapping between owners or startup states.',
        'unavailable': 'Startup-owner drift could not be established from the available installed-lane history.',
    }.get(verdict, 'Startup-owner drift summary unavailable.')

    reasons = [summary_headline]
    if prior_last:
        reasons.append(f"Previous verdict: {prior_last.get('verdict') or 'unknown'}.")
    reasons.append(f"Current verdict: {current_verdict}.")
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


def known_startup_handoff_drift_verdicts() -> list[str]:
    return [
        'first_snapshot',
        'stable',
        'changed_recently',
        'recovered_to_primary',
        'drifted_from_primary',
        'chronic_duplicate_risk',
        'chronic_missing_owner',
        'flapping_owners',
        'unavailable',
    ]

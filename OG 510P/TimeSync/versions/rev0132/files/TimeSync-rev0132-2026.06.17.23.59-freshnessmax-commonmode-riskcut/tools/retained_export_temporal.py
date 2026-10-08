#!/usr/bin/env python3
"""Retained-export temporal checks for TimeSync validation.

Retained exports are intentionally detached artifacts: their export timestamp is
not evidence freshness and must not be used to make old assessments current. This
module keeps those timestamp relationships executable and out of the monolithic
archive validator.
"""
from __future__ import annotations

from typing import Any

from temporal_coherence import check_time_not_after, parse_dt


ACTIONABLE_STATUSES = {'actionable', 'conditional'}


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _exported_at(obj: dict[str, Any]) -> Any:
    return _dict(obj.get('export_context')).get('exported_at')


def _within_window_at_export(vh: dict[str, Any], exported_at: Any) -> bool:
    try:
        exported = parse_dt(exported_at)
        not_before = parse_dt(vh['not_before']) if vh.get('not_before') else None
        not_after = parse_dt(vh['not_after']) if vh.get('not_after') else None
    except Exception:  # noqa: BLE001 - schema/format checks report parse details elsewhere
        return True
    if not_before is not None and exported < not_before:
        return False
    if not_after is not None and exported > not_after:
        return False
    return True


def check_retained_export_temporal(obj: dict[str, Any]) -> list[str]:
    """Validate timestamp relations specific to retained-export artifacts."""
    errors: list[str] = []
    export_context = _dict(obj.get('export_context'))
    exported_at = export_context.get('exported_at')
    purpose = export_context.get('purpose')
    current_policy_checked = export_context.get('current_policy_checked')

    if purpose == 'current_policy_recheck' and current_policy_checked is not True:
        errors.append('current_policy_recheck retained export requires export_context.current_policy_checked true')

    state = _dict(obj.get('local_assessed_state'))
    assessments = _list(state.get('profile_assessments'))
    for index, assessment_any in enumerate(assessments, start=1):
        assessment = _dict(assessment_any)
        prefix = f'profile_assessments[{index}]'
        if assessment.get('assessment_time') and exported_at:
            errors.extend(check_time_not_after(
                assessment.get('assessment_time'),
                exported_at,
                value_label=f'{prefix}.assessment_time',
                anchor_label='export_context.exported_at',
                error_message='retained export profile assessment_time cannot be after export_context.exported_at',
            ))

        policy_acceptance = _dict(assessment.get('policy_acceptance'))
        if policy_acceptance.get('checked_at') and exported_at:
            errors.extend(check_time_not_after(
                policy_acceptance.get('checked_at'),
                exported_at,
                value_label=f'{prefix}.policy_acceptance.checked_at',
                anchor_label='export_context.exported_at',
                error_message='retained export policy_acceptance.checked_at cannot be after export_context.exported_at',
            ))

        vh = _dict(assessment.get('validity_horizon'))
        if vh.get('evaluated_at') and exported_at:
            errors.extend(check_time_not_after(
                vh.get('evaluated_at'),
                exported_at,
                value_label=f'{prefix}.validity_horizon.evaluated_at',
                anchor_label='export_context.exported_at',
                error_message='retained export validity_horizon.evaluated_at cannot be after export_context.exported_at',
            ))
        if (
            purpose == 'current_policy_recheck'
            and vh.get('current_actionability') in ACTIONABLE_STATUSES
            and exported_at
            and not _within_window_at_export(vh, exported_at)
        ):
            errors.append('current_policy_recheck retained export cannot claim actionable/conditional assessment outside validity_horizon at export time')

        embedded_summary = assessment.get('evidence_summary')
        if isinstance(embedded_summary, dict):
            errors.extend(_check_summary_time(embedded_summary, exported_at, f'{prefix}.evidence_summary'))

    summaries = _list(obj.get('evidence_input_summaries'))
    for index, summary_any in enumerate(summaries, start=1):
        if isinstance(summary_any, dict):
            errors.extend(_check_summary_time(summary_any, exported_at, f'evidence_input_summaries[{index}]'))

    return errors


def _check_summary_time(summary: dict[str, Any], exported_at: Any, label: str) -> list[str]:
    errors: list[str] = []
    if summary.get('assessment_time') and exported_at:
        errors.extend(check_time_not_after(
            summary.get('assessment_time'),
            exported_at,
            value_label=f'{label}.assessment_time',
            anchor_label='export_context.exported_at',
            error_message='retained export evidence summary assessment_time cannot be after export_context.exported_at',
        ))
    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    base = {
        'export_context': {
            'exported_at': '2026-05-10T23:00:00Z',
            'purpose': 'current_policy_recheck',
            'current_policy_checked': True,
        },
        'local_assessed_state': {
            'profile_assessments': [
                {
                    'assessment_time': '2026-05-10T22:59:00Z',
                    'policy_acceptance': {'checked_at': '2026-05-10T22:59:00Z'},
                    'validity_horizon': {
                        'evaluated_at': '2026-05-10T22:59:00Z',
                        'current_actionability': 'actionable',
                        'not_before': '2026-05-10T22:58:00Z',
                        'not_after': '2026-05-10T23:01:00Z',
                    },
                }
            ]
        },
        'evidence_input_summaries': [{'assessment_time': '2026-05-10T22:59:00Z'}],
    }
    if check_retained_export_temporal(base):
        errors.append('retained_export_temporal self-test failed: valid current-policy export rejected')

    future = dict(base)
    future['local_assessed_state'] = {'profile_assessments': [dict(base['local_assessed_state']['profile_assessments'][0])]}
    future['local_assessed_state']['profile_assessments'][0]['assessment_time'] = '2026-05-10T23:02:00Z'
    if not any('assessment_time cannot be after' in e for e in check_retained_export_temporal(future)):
        errors.append('retained_export_temporal self-test failed: future assessment accepted')

    unchecked = {
        'export_context': {
            'exported_at': '2026-05-10T23:00:00Z',
            'purpose': 'current_policy_recheck',
            'current_policy_checked': False,
        },
        'local_assessed_state': {'profile_assessments': []},
    }
    if not any('current_policy_checked true' in e for e in check_retained_export_temporal(unchecked)):
        errors.append('retained_export_temporal self-test failed: unchecked current recheck accepted')

    expired = dict(base)
    expired['export_context'] = dict(base['export_context'])
    expired['export_context']['exported_at'] = '2026-05-10T23:10:00Z'
    if not any('outside validity_horizon at export time' in e for e in check_retained_export_temporal(expired)):
        errors.append('retained_export_temporal self-test failed: expired current recheck accepted')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync retained-export temporal self-test passed.')

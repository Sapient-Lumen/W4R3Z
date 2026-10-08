#!/usr/bin/env python3
"""Profile-assessment validity and actionability temporal checks.

This helper keeps assessment-time, policy-acceptance, and validity-horizon
ordering out of the archive validator. These checks are deliberately narrow:
they do not turn policy acceptance into provenance or freshness, but they do
prevent an assessment from being treated as actionable by status checks or
validity windows that predate the assessment they qualify.
"""
from __future__ import annotations

from typing import Any

from temporal_coherence import check_time_not_after, parse_dt


CURRENT_ACTIONABILITY_STATES = {'actionable', 'conditional'}
NON_CURRENT_PROFILE_LIFECYCLE_STATES = {'superseded', 'deprecated', 'revoked', 'unknown'}


def check_policy_acceptance(assessment: dict[str, Any]) -> list[str]:
    """Non-temporal policy-acceptance actionability guardrails."""
    errors: list[str] = []
    pa = assessment.get('policy_acceptance')
    if not isinstance(pa, dict):
        return errors
    status = pa.get('status')
    actionability = pa.get('actionability')
    if status in {'rejected', 'unknown'} and actionability == 'actionable':
        errors.append('policy_acceptance with rejected/unknown status cannot have actionable actionability')
    if status == 'accepted' and actionability == 'conditional':
        errors.append('policy_acceptance accepted cannot have conditional actionability; use accepted_with_conditions')
    if status == 'accepted_with_conditions' and not any(pa.get(k) for k in ('reason', 'policy_reference', 'actionability')):
        errors.append('accepted_with_conditions must explain reason, policy_reference, or actionability')

    conformance = assessment.get('profile_conformance')
    if conformance == 'unsatisfied' and actionability in CURRENT_ACTIONABILITY_STATES:
        errors.append('unsatisfied profile_conformance cannot support actionable or conditional current actionability')

    lifecycle_state = assessment.get('profile_lifecycle_state')
    if lifecycle_state in NON_CURRENT_PROFILE_LIFECYCLE_STATES and actionability in CURRENT_ACTIONABILITY_STATES:
        errors.append(f'profile_lifecycle_state {lifecycle_state} cannot support actionable or conditional current actionability')
    vh = assessment.get('validity_horizon') if isinstance(assessment.get('validity_horizon'), dict) else {}
    vh_action = vh.get('current_actionability')
    if conformance == 'unsatisfied' and vh_action in CURRENT_ACTIONABILITY_STATES:
        errors.append('unsatisfied profile_conformance cannot support validity_horizon actionable or conditional current actionability')
    if lifecycle_state in NON_CURRENT_PROFILE_LIFECYCLE_STATES and vh_action in CURRENT_ACTIONABILITY_STATES:
        errors.append(f'profile_lifecycle_state {lifecycle_state} cannot support validity_horizon actionable or conditional current actionability')
    return errors


def check_validity_horizon(vh: dict[str, Any], assessment: dict[str, Any] | None = None) -> list[str]:
    """Profile-assessment validity/current-actionability checks."""
    errors: list[str] = []
    try:
        evaluated_at = parse_dt(vh.get('evaluated_at', ''))
    except Exception as exc:  # noqa: BLE001
        errors.append(f'validity_horizon evaluated_at parse error: {exc}')
        return errors
    nb = na = None
    if vh.get('not_before'):
        try:
            nb = parse_dt(vh['not_before'])
        except Exception as exc:  # noqa: BLE001
            errors.append(f'validity_horizon not_before parse error: {exc}')
    if vh.get('not_after'):
        try:
            na = parse_dt(vh['not_after'])
        except Exception as exc:  # noqa: BLE001
            errors.append(f'validity_horizon not_after parse error: {exc}')
    if nb and na and nb > na:
        errors.append('validity_horizon not_before is after not_after')
    action = vh.get('current_actionability')
    if action in {'actionable', 'conditional'}:
        if na is None:
            errors.append('validity_horizon actionable/conditional decisions require not_after')
        if nb is not None and evaluated_at < nb:
            errors.append('validity_horizon current_actionability is outside the validity window')
        if na is not None and evaluated_at > na:
            errors.append('validity_horizon current_actionability is outside the validity window')
    if vh.get('export_time_role') == 'used_as_freshness_basis':
        errors.append('validity_horizon cannot use export time as a freshness or current-actionability basis')
    if vh.get('basis') == 'retention_context' and action == 'actionable':
        errors.append('validity_horizon retention_context alone cannot make an assessment actionable')
    if assessment is not None:
        pa = assessment.get('policy_acceptance') if isinstance(assessment.get('policy_acceptance'), dict) else {}
        if pa:
            pa_action = pa.get('actionability')
            if pa_action and action != pa_action:
                errors.append('validity_horizon current_actionability does not match policy_acceptance.actionability')
            checked_at = pa.get('checked_at')
            if checked_at and vh.get('evaluated_at') != checked_at:
                errors.append('validity_horizon evaluated_at must match policy_acceptance.checked_at when both are present')
        if assessment.get('profile_conformance') == 'satisfied' and action in {'record_only', 'not_actionable'} and pa.get('status') == 'accepted':
            errors.append('validity_horizon cannot mark an accepted satisfied assessment record_only/not_actionable without conditional or rejected policy')
    return errors


def check_profile_assessment_temporal(assessment: dict[str, Any]) -> list[str]:
    """Reject status or validity evidence that predates the profile assessment."""
    errors: list[str] = []
    assessment_time = assessment.get('assessment_time')
    if not isinstance(assessment_time, str):
        return errors

    pa = assessment.get('policy_acceptance') if isinstance(assessment.get('policy_acceptance'), dict) else {}
    checked_at = pa.get('checked_at')
    if isinstance(checked_at, str):
        errors.extend(check_time_not_after(
            assessment_time,
            checked_at,
            value_label='profile assessment assessment_time',
            anchor_label='policy_acceptance.checked_at',
            error_message='profile assessment assessment_time cannot be after policy_acceptance.checked_at',
        ))

    vh = assessment.get('validity_horizon') if isinstance(assessment.get('validity_horizon'), dict) else {}
    evaluated_at = vh.get('evaluated_at')
    if isinstance(evaluated_at, str):
        errors.extend(check_time_not_after(
            assessment_time,
            evaluated_at,
            value_label='profile assessment assessment_time',
            anchor_label='validity_horizon.evaluated_at',
            error_message='profile assessment assessment_time cannot be after validity_horizon.evaluated_at',
        ))

    if vh.get('assessment_time_binding') == 'profile_assessment_time':
        not_before = vh.get('not_before')
        if isinstance(not_before, str):
            errors.extend(check_time_not_after(
                not_before,
                assessment_time,
                value_label='validity_horizon.not_before',
                anchor_label='profile assessment assessment_time',
                error_message='profile assessment assessment_time cannot be before validity_horizon.not_before',
            ))
        not_after = vh.get('not_after')
        if isinstance(not_after, str):
            errors.extend(check_time_not_after(
                assessment_time,
                not_after,
                value_label='profile assessment assessment_time',
                anchor_label='validity_horizon.not_after',
                error_message='profile assessment assessment_time cannot be after validity_horizon.not_after',
            ))
    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    good = {
        'assessment_time': '2026-05-10T22:29:01Z',
        'profile_conformance': 'satisfied',
        'policy_acceptance': {
            'status': 'accepted',
            'checked_at': '2026-05-10T22:29:01Z',
            'actionability': 'actionable',
        },
        'validity_horizon': {
            'evaluated_at': '2026-05-10T22:29:01Z',
            'current_actionability': 'actionable',
            'basis': 'local_policy',
            'assessment_time_binding': 'profile_assessment_time',
            'export_time_role': 'not_used',
            'evidence_posture': 'assessed',
            'not_before': '2026-05-10T22:29:00Z',
            'not_after': '2026-05-10T22:29:02Z',
        },
    }
    if check_policy_acceptance(good) or check_validity_horizon(good['validity_horizon'], good) or check_profile_assessment_temporal(good):
        errors.append('assessment_temporal self-test rejected a coherent assessment')

    bad_policy = dict(good)
    bad_policy['policy_acceptance'] = dict(good['policy_acceptance'], checked_at='2026-05-10T22:29:00Z')
    if not any('assessment_time cannot be after policy_acceptance.checked_at' in e for e in check_profile_assessment_temporal(bad_policy)):
        errors.append('assessment_temporal self-test accepted policy check before assessment_time')

    bad_window = dict(good)
    bad_window['assessment_time'] = '2026-05-10T22:28:59Z'
    if not any('assessment_time cannot be before validity_horizon.not_before' in e for e in check_profile_assessment_temporal(bad_window)):
        errors.append('assessment_temporal self-test accepted profile_assessment_time before validity window')

    inactive_actionable = dict(good)
    inactive_actionable['profile_lifecycle_state'] = 'revoked'
    if not any('profile_lifecycle_state revoked cannot support actionable or conditional current actionability' in e for e in check_policy_acceptance(inactive_actionable)):
        errors.append('assessment_temporal self-test accepted revoked actionable profile lifecycle state')

    unsatisfied_actionable = dict(good)
    unsatisfied_actionable['profile_conformance'] = 'unsatisfied'
    if not any('unsatisfied profile_conformance cannot support actionable or conditional current actionability' in e for e in check_policy_acceptance(unsatisfied_actionable)):
        errors.append('assessment_temporal self-test accepted unsatisfied actionable assessment')

    accepted_conditional = dict(good)
    accepted_conditional['policy_acceptance'] = dict(good['policy_acceptance'], status='accepted', actionability='conditional')
    accepted_conditional['validity_horizon'] = dict(good['validity_horizon'], current_actionability='conditional')
    if not any('accepted cannot have conditional actionability' in e for e in check_policy_acceptance(accepted_conditional)):
        errors.append('assessment_temporal self-test accepted accepted+conditional policy actionability')

    inactive_record_only = dict(good)
    inactive_record_only['profile_lifecycle_state'] = 'superseded'
    inactive_record_only['policy_acceptance'] = dict(good['policy_acceptance'], status='accepted_with_conditions', actionability='record_only', reason='historical record only')
    inactive_record_only['validity_horizon'] = dict(good['validity_horizon'], current_actionability='record_only', basis='retention_context')
    if check_policy_acceptance(inactive_record_only):
        errors.append('assessment_temporal self-test rejected non-current lifecycle record-only retention posture')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync assessment temporal self-test passed.')

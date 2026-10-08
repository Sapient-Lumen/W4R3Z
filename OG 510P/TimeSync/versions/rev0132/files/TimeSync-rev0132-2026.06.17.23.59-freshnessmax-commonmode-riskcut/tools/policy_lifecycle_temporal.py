#!/usr/bin/env python3
"""Policy-lifecycle authority temporal checks for TimeSync validation.

Lifecycle-authority references and recovery attestations are compact replay-
visibility surfaces.  They are not profile evidence and they must not rely on
facts that were checked after the lifecycle status, compromise response, or
replay evaluation that consumes them.  This helper keeps those timestamp
relationships executable without growing another registry.
"""
from __future__ import annotations

from typing import Any, Iterable

from temporal_coherence import check_time_not_after, check_time_order


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _anchor_current_evaluated_at(record: dict[str, Any] | None) -> Any | None:
    if not isinstance(record, dict):
        return None
    anchor = _dict(record.get('anchor_evaluation'))
    if anchor.get('current_visibility_status') != 'current_at_evaluation':
        return None
    return anchor.get('evaluated_at')


def _lifecycle_evaluated_at(ref: dict[str, Any] | None) -> Any | None:
    if not isinstance(ref, dict):
        return None
    lifecycle = _dict(ref.get('lifecycle_status'))
    return lifecycle.get('evaluated_at')


def _recovery_attestation_events(att: dict[str, Any], prefix: str) -> Iterable[tuple[str, Any]]:
    yield f'{prefix}.issued_at', att.get('issued_at')
    yield f'{prefix}.verified_at', att.get('verified_at')
    window = _dict(att.get('incident_window'))
    yield f'{prefix}.incident_window.contained_at', window.get('contained_at')
    portability = _dict(att.get('portability'))
    yield f'{prefix}.portability.portability_checked_at', portability.get('portability_checked_at')


def check_policy_lifecycle_recovery_temporal(
    att: dict[str, Any],
    *,
    compromise: dict[str, Any] | None = None,
    lifecycle_evaluated_at: Any | None = None,
    replay_evaluated_at: Any | None = None,
    prefix: str = 'recovery attestation',
) -> list[str]:
    """Validate recovery-attestation event ordering.

    ``compromise`` is the containing compromise response when present.  A
    recovery attestation may support that response only if its issuance,
    verification, containment, and portability checks were not after the response
    check time.  When the enclosing trust-policy lifecycle or replay evaluation
    is current, the same events must also predate those consuming evaluations.
    """
    errors: list[str] = []
    if att.get('issued_at') and att.get('verified_at'):
        errors.extend(check_time_order(
            att.get('issued_at'),
            att.get('verified_at'),
            start_label=f'{prefix}.issued_at',
            end_label=f'{prefix}.verified_at',
            allow_equal=True,
            error_message='recovery attestation issued_at cannot be after verified_at',
        ))

    response_checked_at = _dict(compromise).get('checked_at')
    if response_checked_at:
        for label, value in _recovery_attestation_events(att, prefix):
            if value:
                errors.extend(check_time_not_after(
                    value,
                    response_checked_at,
                    value_label=label,
                    anchor_label='lifecycle-authority compromise response checked_at',
                    error_message=f'{label} cannot be after lifecycle-authority compromise response checked_at',
                ))

    if lifecycle_evaluated_at:
        for label, value in _recovery_attestation_events(att, prefix):
            if value:
                errors.extend(check_time_not_after(
                    value,
                    lifecycle_evaluated_at,
                    value_label=label,
                    anchor_label='trust-policy lifecycle evaluated_at',
                    error_message=f'{label} cannot be after trust-policy lifecycle evaluated_at',
                ))

    if replay_evaluated_at:
        for label, value in _recovery_attestation_events(att, prefix):
            if value:
                errors.extend(check_time_not_after(
                    value,
                    replay_evaluated_at,
                    value_label=label,
                    anchor_label='replay visibility evaluation evaluated_at',
                    error_message=f'{label} cannot be after replay visibility evaluation evaluated_at',
                ))
    return errors


def _authority_events(auth: dict[str, Any]) -> Iterable[tuple[str, Any]]:
    discovery = _dict(auth.get('discovery'))
    renewal = _dict(auth.get('renewal_hint'))
    seq = _dict(auth.get('anti_rollback_sequence'))
    freeze = _dict(seq.get('freeze_check'))
    rotation = _dict(auth.get('rotation_delegation_status'))
    compromise = _dict(rotation.get('compromise_response'))
    yield 'policy lifecycle authority discovery.discovered_at', discovery.get('discovered_at')
    yield 'policy lifecycle renewal hint.hint_checked_at', renewal.get('hint_checked_at')
    yield 'policy lifecycle authority sequence.checked_at', seq.get('checked_at')
    yield 'policy lifecycle authority sequence.freeze_check.basis_time', freeze.get('basis_time')
    yield 'policy lifecycle authority rotation.rotation_checked_at', rotation.get('rotation_checked_at')
    yield 'policy lifecycle authority delegation.delegation_checked_at', rotation.get('delegation_checked_at')
    yield 'policy lifecycle authority compromise response.checked_at', compromise.get('checked_at')

    recovery_att = compromise.get('recovery_attestation_reference')
    if isinstance(recovery_att, dict):
        yield from _recovery_attestation_events(
            recovery_att,
            'policy lifecycle authority compromise response.recovery_attestation_reference',
        )


def check_policy_lifecycle_authority_temporal(
    auth: dict[str, Any],
    *,
    ref: dict[str, Any] | None = None,
    record: dict[str, Any] | None = None,
) -> list[str]:
    """Validate temporal ordering for lifecycle-authority references."""
    errors: list[str] = []
    seq = _dict(auth.get('anti_rollback_sequence'))
    freeze = _dict(seq.get('freeze_check'))
    if seq.get('checked_at') and freeze.get('basis_time'):
        errors.extend(check_time_not_after(
            freeze.get('basis_time'),
            seq.get('checked_at'),
            value_label='policy lifecycle authority sequence.freeze_check.basis_time',
            anchor_label='policy lifecycle authority sequence.checked_at',
        ))

    lifecycle_eval = _lifecycle_evaluated_at(ref)
    if lifecycle_eval:
        for label, value in _authority_events(auth):
            if value:
                errors.extend(check_time_not_after(
                    value,
                    lifecycle_eval,
                    value_label=label,
                    anchor_label='trust-policy lifecycle evaluated_at',
                    error_message=f'{label} cannot be after trust-policy lifecycle evaluated_at',
                ))

    replay_eval = _anchor_current_evaluated_at(record)
    if replay_eval:
        for label, value in _authority_events(auth):
            if value:
                errors.extend(check_time_not_after(
                    value,
                    replay_eval,
                    value_label=label,
                    anchor_label='replay visibility evaluation evaluated_at',
                    error_message=f'{label} cannot be evaluated after replay visibility evaluation',
                ))

    rotation = _dict(auth.get('rotation_delegation_status'))
    compromise = _dict(rotation.get('compromise_response'))
    recovery_att = compromise.get('recovery_attestation_reference')
    if isinstance(recovery_att, dict):
        errors.extend(check_policy_lifecycle_recovery_temporal(
            recovery_att,
            compromise=compromise,
            lifecycle_evaluated_at=lifecycle_eval,
            replay_evaluated_at=replay_eval,
            prefix='policy lifecycle authority compromise response.recovery_attestation_reference',
        ))
    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    valid_att = {
        'issued_at': '2026-05-21T10:00:00Z',
        'verified_at': '2026-05-21T10:00:30Z',
        'incident_window': {'contained_at': '2026-05-21T09:59:00Z'},
        'portability': {'portability_checked_at': '2026-05-21T10:00:30Z'},
    }
    compromise = {'checked_at': '2026-05-21T10:00:30Z'}
    if check_policy_lifecycle_recovery_temporal(
        valid_att,
        compromise=compromise,
        lifecycle_evaluated_at='2026-05-21T10:00:40Z',
        replay_evaluated_at='2026-05-21T10:00:50Z',
    ):
        errors.append('policy_lifecycle_temporal self-test failed: valid recovery attestation rejected')

    future_verified = dict(valid_att)
    future_verified['verified_at'] = '2026-05-21T10:01:00Z'
    if not any('cannot be after lifecycle-authority compromise response checked_at' in e for e in check_policy_lifecycle_recovery_temporal(future_verified, compromise=compromise)):
        errors.append('policy_lifecycle_temporal self-test failed: future recovery verification accepted')

    auth = {
        'discovery': {'discovered_at': '2026-05-21T10:00:00Z'},
        'renewal_hint': {'hint_checked_at': '2026-05-21T10:00:00Z'},
        'anti_rollback_sequence': {
            'checked_at': '2026-05-21T10:00:00Z',
            'freeze_check': {'basis_time': '2026-05-21T10:00:01Z'},
        },
        'rotation_delegation_status': {'compromise_response': {}},
    }
    if not any('freeze_check.basis_time cannot be after policy lifecycle authority sequence.checked_at' in e for e in check_policy_lifecycle_authority_temporal(auth)):
        errors.append('policy_lifecycle_temporal self-test failed: future freeze basis accepted')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync policy-lifecycle temporal self-test passed.')

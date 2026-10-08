#!/usr/bin/env python3
"""Transparency-policy equivalence timing checks for compatibility statements.

Policy-equivalence sections inside profile compatibility statements can support
cross-operator replay visibility, so the equivalence evidence must exist before
the statement signature that binds it.  This helper keeps that temporal contract
executable without importing policy language or treating the compatibility
statement as profile evidence.
"""
from __future__ import annotations

from typing import Any

from temporal_coherence import check_active_window_status, check_time_not_after, check_time_order
from discovery_binding_semantics import digest_binds


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def check_policy_lifecycle_equivalence_temporal(
    tpe: dict[str, Any],
    *,
    statement_signed_at: str | None = None,
    statement_expires_at: str | None = None,
) -> list[str]:
    """Validate policy-lifecycle equivalence times inside a compatibility statement."""
    errors: list[str] = []
    ple = _dict(tpe.get('policy_lifecycle_equivalence'))
    if not ple:
        return ['transparency_policy_equivalence requires policy_lifecycle_equivalence']

    evaluated_at = ple.get('evaluated_at')
    not_before = ple.get('equivalence_not_before')
    not_after = ple.get('equivalence_not_after')
    state = ple.get('current_equivalence_state')

    if not_before and not_after:
        errors.extend(check_time_order(
            not_before,
            not_after,
            start_label='policy lifecycle equivalence not_before',
            end_label='policy lifecycle equivalence not_after',
            error_message='policy lifecycle equivalence not_before must be before not_after',
        ))

    errors.extend(check_active_window_status(
        state=state,
        active_state='current',
        evaluated_at=evaluated_at,
        not_before=not_before,
        not_after=not_after,
        label='policy lifecycle equivalence',
        active_outside_message='current policy lifecycle equivalence must evaluate inside equivalence window',
        expired_state='expired',
        expired_not_after_message='expired policy lifecycle equivalence must evaluate after equivalence_not_after',
    ))

    rev = _dict(ple.get('revocation_check'))
    drift = _dict(ple.get('drift_check'))
    if evaluated_at and rev.get('checked_at'):
        errors.extend(check_time_not_after(
            rev.get('checked_at'),
            evaluated_at,
            value_label='policy lifecycle equivalence revocation_check.checked_at',
            anchor_label='policy lifecycle equivalence evaluated_at',
        ))
    if isinstance(rev.get('digest'), dict) and not digest_binds(rev.get('digest'), 'transparency_trust_policy_revocation_status'):
        errors.append('policy lifecycle equivalence revocation_check.digest must bind transparency_trust_policy_revocation_status')
    if evaluated_at and drift.get('checked_at'):
        errors.extend(check_time_not_after(
            drift.get('checked_at'),
            evaluated_at,
            value_label='policy lifecycle equivalence drift_check.checked_at',
            anchor_label='policy lifecycle equivalence evaluated_at',
        ))

    if evaluated_at and statement_signed_at:
        errors.extend(check_time_not_after(
            evaluated_at,
            statement_signed_at,
            value_label='policy lifecycle equivalence evaluated_at',
            anchor_label='compatibility statement binding.signed_at',
            error_message='policy lifecycle equivalence evaluated_at cannot be after compatibility statement binding.signed_at',
        ))
    if evaluated_at and statement_expires_at:
        errors.extend(check_time_not_after(
            evaluated_at,
            statement_expires_at,
            value_label='policy lifecycle equivalence evaluated_at',
            anchor_label='compatibility statement expires_at',
            error_message='policy lifecycle equivalence evaluated_at cannot be after compatibility statement expires_at',
        ))
    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    valid = {
        'policy_lifecycle_equivalence': {
            'evaluated_at': '2026-05-22T19:45:10Z',
            'current_equivalence_state': 'current',
            'equivalence_not_before': '2026-05-01T00:00:00Z',
            'equivalence_not_after': '2026-06-22T00:00:00Z',
            'revocation_check': {'checked_at': '2026-05-22T19:45:10Z'},
            'drift_check': {'checked_at': '2026-05-22T19:45:09Z'},
        }
    }
    if check_policy_lifecycle_equivalence_temporal(
        valid,
        statement_signed_at='2026-05-22T19:45:15Z',
        statement_expires_at='2027-05-22T19:45:00Z',
    ):
        errors.append('policy equivalence temporal self-test unexpectedly rejected valid timing')

    rev_after_eval = {
        'policy_lifecycle_equivalence': {
            **valid['policy_lifecycle_equivalence'],
            'revocation_check': {'checked_at': '2026-05-22T19:45:11Z'},
        }
    }
    if not any('revocation_check.checked_at cannot be after policy lifecycle equivalence evaluated_at' in e for e in check_policy_lifecycle_equivalence_temporal(rev_after_eval, statement_signed_at='2026-05-22T19:45:15Z')):
        errors.append('policy equivalence temporal self-test failed to reject revocation check after evaluation')

    drift_after_eval = {
        'policy_lifecycle_equivalence': {
            **valid['policy_lifecycle_equivalence'],
            'drift_check': {'checked_at': '2026-05-22T19:45:11Z'},
        }
    }
    if not any('drift_check.checked_at cannot be after policy lifecycle equivalence evaluated_at' in e for e in check_policy_lifecycle_equivalence_temporal(drift_after_eval, statement_signed_at='2026-05-22T19:45:15Z')):
        errors.append('policy equivalence temporal self-test failed to reject drift check after evaluation')

    wrong_revocation_digest = {
        'policy_lifecycle_equivalence': {
            **valid['policy_lifecycle_equivalence'],
            'revocation_check': {
                'checked_at': '2026-05-22T19:45:10Z',
                'digest': {'algorithm': 'sha256', 'value': 'a' * 64, 'binds': 'transparency_trust_policy_rules'},
            },
        }
    }
    if not any('revocation_check.digest must bind transparency_trust_policy_revocation_status' in e for e in check_policy_lifecycle_equivalence_temporal(wrong_revocation_digest, statement_signed_at='2026-05-22T19:45:15Z')):
        errors.append('policy equivalence temporal self-test failed to reject wrong revocation digest binding')

    eval_after_signature = valid
    if not any('evaluated_at cannot be after compatibility statement binding.signed_at' in e for e in check_policy_lifecycle_equivalence_temporal(eval_after_signature, statement_signed_at='2026-05-22T19:45:05Z')):
        errors.append('policy equivalence temporal self-test failed to reject evaluation after signature')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync policy-equivalence temporal self-test passed.')

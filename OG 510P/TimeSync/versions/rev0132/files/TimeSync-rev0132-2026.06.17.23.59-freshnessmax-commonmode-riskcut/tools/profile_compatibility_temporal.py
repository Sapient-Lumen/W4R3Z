#!/usr/bin/env python3
"""Profile compatibility statement artifact-time checks.

Compatibility statements can authorize cross-profile portability and downgrade
review, so their own artifact times must be coherent.  This helper keeps the
portable-statement timing contract executable without turning a compatibility
statement into profile evidence, TimeState freshness, or a registry lease.
"""
from __future__ import annotations

from typing import Any

from temporal_coherence import check_time_not_after, check_time_order


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def check_profile_compatibility_statement_temporal(stmt: dict[str, Any]) -> list[str]:
    """Validate timing for a profile compatibility statement."""
    errors: list[str] = []
    issued_at = stmt.get('issued_at')
    expires_at = stmt.get('expires_at')
    signed_at = _dict(stmt.get('binding')).get('signed_at')

    if issued_at and expires_at:
        errors.extend(check_time_order(
            issued_at,
            expires_at,
            start_label='profile compatibility statement issued_at',
            end_label='profile compatibility statement expires_at',
            error_message='profile compatibility statement expires_at must be after issued_at',
        ))

    if issued_at and signed_at:
        errors.extend(check_time_not_after(
            issued_at,
            signed_at,
            value_label='profile compatibility statement issued_at',
            anchor_label='binding.signed_at',
            error_message='profile compatibility statement issued_at cannot be after binding.signed_at',
        ))
    if signed_at and expires_at:
        errors.extend(check_time_not_after(
            signed_at,
            expires_at,
            value_label='profile compatibility statement binding.signed_at',
            anchor_label='expires_at',
            error_message='profile compatibility statement binding.signed_at cannot be after expires_at',
        ))

    drift = _dict(stmt.get('compatibility_drift'))
    drift_eval = drift.get('evaluated_at')
    if drift_eval and signed_at:
        errors.extend(check_time_not_after(
            drift_eval,
            signed_at,
            value_label='profile compatibility drift evaluated_at',
            anchor_label='compatibility statement binding.signed_at',
            error_message='profile compatibility drift evaluated_at cannot be after compatibility statement binding.signed_at',
        ))
    if drift_eval and expires_at:
        errors.extend(check_time_not_after(
            drift_eval,
            expires_at,
            value_label='profile compatibility drift evaluated_at',
            anchor_label='compatibility statement expires_at',
            error_message='profile compatibility drift evaluated_at cannot be after compatibility statement expires_at',
        ))
    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    valid = {
        'issued_at': '2026-05-21T05:50:00Z',
        'expires_at': '2027-05-21T05:50:00Z',
        'binding': {'signed_at': '2026-05-21T05:50:05Z'},
        'compatibility_drift': {'evaluated_at': '2026-05-21T05:50:02Z'},
    }
    if check_profile_compatibility_statement_temporal(valid):
        errors.append('profile compatibility temporal self-test unexpectedly rejected valid timing')
    expired_before_signature = {
        **valid,
        'expires_at': '2026-05-21T05:50:04Z',
    }
    if not any('binding.signed_at cannot be after expires_at' in e for e in check_profile_compatibility_statement_temporal(expired_before_signature)):
        errors.append('profile compatibility temporal self-test failed to reject signature after expiry')
    drift_after_signature = {
        **valid,
        'compatibility_drift': {'evaluated_at': '2026-05-21T05:50:06Z'},
    }
    if not any('drift evaluated_at cannot be after compatibility statement binding.signed_at' in e for e in check_profile_compatibility_statement_temporal(drift_after_signature)):
        errors.append('profile compatibility temporal self-test failed to reject drift evaluated after signature')
    issued_after_signature = {
        **valid,
        'issued_at': '2026-05-21T05:50:06Z',
    }
    if not any('issued_at cannot be after binding.signed_at' in e for e in check_profile_compatibility_statement_temporal(issued_after_signature)):
        errors.append('profile compatibility temporal self-test failed to reject issue time after signature time')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync profile compatibility temporal self-test passed.')

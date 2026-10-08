#!/usr/bin/env python3
"""Aggregate correction-authority digest binding semantics for TimeSync."""
from __future__ import annotations

import re
from typing import Any


def _digest_binds(digest: Any, expected: str) -> bool:
    return (
        isinstance(digest, dict)
        and digest.get('algorithm') == 'sha256'
        and isinstance(digest.get('value'), str)
        and bool(re.fullmatch(r'[A-Fa-f0-9]{64}', digest.get('value', '')))
        and digest.get('binds') == expected
    )


def _digest_binds_any(digest: Any, expected: set[str]) -> bool:
    return any(_digest_binds(digest, item) for item in expected)


def _require(digest: Any, expected: str, message: str) -> list[str]:
    if not _digest_binds(digest, expected):
        return [message]
    return []


def check_aggregate_correction_authority_digest_bindings(ref: dict[str, Any]) -> list[str]:
    """Require correction-authority digest fields to bind the named artifact class."""
    errors: list[str] = []
    auth = ref.get('authority_binding', {}) if isinstance(ref.get('authority_binding'), dict) else {}
    notification = ref.get('notification_cadence', {}) if isinstance(ref.get('notification_cadence'), dict) else {}
    lifecycle = ref.get('authority_lifecycle', {}) if isinstance(ref.get('authority_lifecycle'), dict) else {}

    if not _digest_binds_any(auth.get('authority_digest'), {'aggregate_correction_authority_rules', 'aggregate_correction_authority_identity'}):
        errors.append('aggregate correction authority_digest must bind aggregate_correction_authority_rules or aggregate_correction_authority_identity')
    if auth.get('authorization_basis') == 'profile_compatibility_statement':
        errors.extend(_require(
            auth.get('authorization_policy_digest'),
            'profile_compatibility_statement',
            'aggregate correction authorization_policy_digest must bind profile_compatibility_statement when authorization_basis is profile_compatibility_statement',
        ))
    else:
        errors.extend(_require(
            auth.get('authorization_policy_digest'),
            'aggregate_correction_authority_policy',
            'aggregate correction authorization_policy_digest must bind aggregate_correction_authority_policy',
        ))

    if isinstance(notification.get('notification_digest'), dict) or notification.get('notification_state') in {'notified_within_policy', 'deferred_but_within_policy'}:
        errors.extend(_require(
            notification.get('notification_digest'),
            'aggregate_correction_notification_batch',
            'aggregate correction notification_digest must bind aggregate_correction_notification_batch',
        ))

    if lifecycle:
        errors.extend(_require(
            lifecycle.get('lifecycle_policy_digest'),
            'aggregate_correction_authority_lifecycle_rules',
            'aggregate correction lifecycle_policy_digest must bind aggregate_correction_authority_lifecycle_rules',
        ))
        if isinstance(lifecycle.get('decision_table_digest'), dict):
            errors.extend(_require(
                lifecycle.get('decision_table_digest'),
                'aggregate_lifecycle_decision_table',
                'aggregate correction decision_table_digest must bind aggregate_lifecycle_decision_table',
            ))
        emergency = lifecycle.get('emergency_withdrawal', {}) if isinstance(lifecycle.get('emergency_withdrawal'), dict) else {}
        if isinstance(emergency.get('withdrawal_digest'), dict):
            errors.extend(_require(
                emergency.get('withdrawal_digest'),
                'aggregate_emergency_withdrawal_record',
                'aggregate correction emergency withdrawal_digest must bind aggregate_emergency_withdrawal_record',
            ))
        if isinstance(emergency.get('resynchronization_digest'), dict):
            errors.extend(_require(
                emergency.get('resynchronization_digest'),
                'aggregate_emergency_resynchronization_policy',
                'aggregate correction emergency resynchronization_digest must bind aggregate_emergency_resynchronization_policy',
            ))
        contestation = lifecycle.get('contestation', {}) if isinstance(lifecycle.get('contestation'), dict) else {}
        if isinstance(contestation.get('contestation_digest'), dict):
            errors.extend(_require(
                contestation.get('contestation_digest'),
                'aggregate_correction_authority_contestation_record',
                'aggregate correction contestation_digest must bind aggregate_correction_authority_contestation_record',
            ))

    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    good = {
        'authority_binding': {
            'authorization_basis': 'local_policy_digest',
            'authority_digest': {'algorithm': 'sha256', 'value': 'a' * 64, 'binds': 'aggregate_correction_authority_rules'},
            'authorization_policy_digest': {'algorithm': 'sha256', 'value': 'b' * 64, 'binds': 'aggregate_correction_authority_policy'},
        },
        'notification_cadence': {
            'notification_state': 'notified_within_policy',
            'notification_digest': {'algorithm': 'sha256', 'value': 'c' * 64, 'binds': 'aggregate_correction_notification_batch'},
        },
        'authority_lifecycle': {
            'lifecycle_policy_digest': {'algorithm': 'sha256', 'value': 'd' * 64, 'binds': 'aggregate_correction_authority_lifecycle_rules'},
        },
    }
    if check_aggregate_correction_authority_digest_bindings(good):
        errors.append('accepted aggregate correction reference produced digest-binding errors')
    bad = {
        'authority_binding': {
            'authorization_basis': 'local_policy_digest',
            'authority_digest': {'algorithm': 'sha256', 'value': 'a' * 64, 'binds': 'retained_operator_record'},
            'authorization_policy_digest': {'algorithm': 'sha256', 'value': 'b' * 64, 'binds': 'aggregate_correction_authority_policy'},
        },
        'notification_cadence': {},
        'authority_lifecycle': {'lifecycle_policy_digest': {'algorithm': 'sha256', 'value': 'd' * 64, 'binds': 'aggregate_correction_authority_lifecycle_rules'}},
    }
    if not check_aggregate_correction_authority_digest_bindings(bad):
        errors.append('aggregate authority wrong-bind survivor was not rejected')
    return errors

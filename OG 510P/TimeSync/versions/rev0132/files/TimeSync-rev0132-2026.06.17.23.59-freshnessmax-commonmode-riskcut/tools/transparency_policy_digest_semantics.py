#!/usr/bin/env python3
"""Transparency trust-policy digest binding semantics for TimeSync."""
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


def _require(digest: Any, expected: str, message: str) -> list[str]:
    if not _digest_binds(digest, expected):
        return [message]
    return []


def check_transparency_policy_digest_bindings(ref: dict[str, Any]) -> list[str]:
    """Require trust-policy lifecycle/drift digests to bind their named classes."""
    errors: list[str] = []
    errors.extend(_require(
        ref.get('policy_digest'),
        'transparency_trust_policy_rules',
        'transparency trust policy policy_digest must bind transparency_trust_policy_rules',
    ))

    lifecycle = ref.get('lifecycle_status', {}) if isinstance(ref.get('lifecycle_status'), dict) else {}
    if lifecycle:
        errors.extend(_require(
            lifecycle.get('status_record_digest'),
            'transparency_trust_policy_lifecycle_status',
            'transparency trust policy lifecycle status_record_digest must bind transparency_trust_policy_lifecycle_status',
        ))
        revocation = lifecycle.get('revocation_check', {}) if isinstance(lifecycle.get('revocation_check'), dict) else {}
        if isinstance(revocation.get('digest'), dict):
            errors.extend(_require(
                revocation.get('digest'),
                'transparency_trust_policy_revocation_status',
                'transparency trust policy revocation_check.digest must bind transparency_trust_policy_revocation_status',
            ))
        if isinstance(lifecycle.get('successor_policy_digest'), dict):
            errors.extend(_require(
                lifecycle.get('successor_policy_digest'),
                'transparency_trust_policy_rules',
                'transparency trust policy successor_policy_digest must bind transparency_trust_policy_rules',
            ))
        drift = lifecycle.get('drift_status', {}) if isinstance(lifecycle.get('drift_status'), dict) else {}
        for field in ('previous_policy_digest', 'current_policy_digest', 'successor_policy_digest'):
            if isinstance(drift.get(field), dict):
                errors.extend(_require(
                    drift.get(field),
                    'transparency_trust_policy_rules',
                    f'transparency trust policy drift {field} must bind transparency_trust_policy_rules',
                ))
        if isinstance(drift.get('compatibility_statement_digest'), dict):
            errors.extend(_require(
                drift.get('compatibility_statement_digest'),
                'profile_compatibility_statement',
                'transparency trust policy drift compatibility_statement_digest must bind profile_compatibility_statement',
            ))

    xop = ref.get('cross_operator_equivalence', {}) if isinstance(ref.get('cross_operator_equivalence'), dict) else {}
    if isinstance(xop.get('compatibility_statement_digest'), dict):
        errors.extend(_require(
            xop.get('compatibility_statement_digest'),
            'profile_compatibility_statement',
            'transparency trust policy cross_operator compatibility_statement_digest must bind profile_compatibility_statement',
        ))
    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    good = {
        'policy_digest': {'algorithm': 'sha256', 'value': 'a' * 64, 'binds': 'transparency_trust_policy_rules'},
        'lifecycle_status': {
            'status_record_digest': {'algorithm': 'sha256', 'value': 'b' * 64, 'binds': 'transparency_trust_policy_lifecycle_status'},
            'revocation_check': {'digest': {'algorithm': 'sha256', 'value': 'c' * 64, 'binds': 'transparency_trust_policy_revocation_status'}},
            'drift_status': {'current_policy_digest': {'algorithm': 'sha256', 'value': 'd' * 64, 'binds': 'transparency_trust_policy_rules'}},
        },
    }
    if check_transparency_policy_digest_bindings(good):
        errors.append('accepted transparency policy reference produced digest-binding errors')
    bad = {
        'policy_digest': {'algorithm': 'sha256', 'value': 'a' * 64, 'binds': 'transparency_trust_policy_rules'},
        'lifecycle_status': {
            'status_record_digest': {'algorithm': 'sha256', 'value': 'b' * 64, 'binds': 'profile_compatibility_statement'},
        },
    }
    if not check_transparency_policy_digest_bindings(bad):
        errors.append('transparency policy lifecycle wrong-bind survivor was not rejected')
    return errors

#!/usr/bin/env python3
"""Policy lifecycle-authority digest binding semantics for TimeSync.

These checks keep compact lifecycle-authority references digest-bound to the
artifact classes they claim to summarize.  They deliberately do not verify an
external authority repository, rotation protocol, or recovery workflow.
"""
from __future__ import annotations

from typing import Any

from discovery_binding_semantics import digest_binds


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _has_digest(value: Any) -> bool:
    return isinstance(value, dict) and isinstance(value.get('value'), str)


def check_policy_lifecycle_authority_digest_bindings(auth: dict[str, Any]) -> list[str]:
    """Validate artifact-class bindings in a compact policy lifecycle-authority reference."""
    errors: list[str] = []
    discovery = _dict(auth.get('discovery'))
    renewal = _dict(auth.get('renewal_hint'))
    seq = _dict(auth.get('anti_rollback_sequence'))
    rotation = _dict(auth.get('rotation_delegation_status'))
    compromise = _dict(rotation.get('compromise_response'))

    if not digest_binds(auth.get('authority_digest'), 'transparency_trust_policy_lifecycle_authority'):
        errors.append('policy lifecycle authority reference requires authority_digest binding transparency_trust_policy_lifecycle_authority')
    if not digest_binds(auth.get('policy_digest'), 'transparency_trust_policy_rules'):
        errors.append('policy lifecycle authority reference requires policy_digest binding transparency_trust_policy_rules')

    if _has_digest(discovery.get('authority_binding_digest')) and not digest_binds(discovery.get('authority_binding_digest'), 'transparency_trust_policy_lifecycle_status'):
        errors.append('policy lifecycle authority discovery authority_binding_digest must bind transparency_trust_policy_lifecycle_status')
    if discovery.get('discovery_state') == 'compatibility_statement_bound':
        if not digest_binds(discovery.get('compatibility_statement_digest'), 'profile_compatibility_statement'):
            errors.append('compatibility-bound policy lifecycle authority discovery requires compatibility_statement_digest binding profile_compatibility_statement')
    elif _has_digest(discovery.get('compatibility_statement_digest')) and not digest_binds(discovery.get('compatibility_statement_digest'), 'profile_compatibility_statement'):
        errors.append('policy lifecycle authority discovery compatibility_statement_digest must bind profile_compatibility_statement')

    if not digest_binds(seq.get('status_record_digest'), 'transparency_trust_policy_lifecycle_status'):
        errors.append('policy lifecycle authority sequence status_record_digest must bind transparency_trust_policy_lifecycle_status')

    if renewal.get('hint_state') in {'successor_digest_available', 'renewal_available'}:
        if not digest_binds(renewal.get('successor_policy_digest'), 'transparency_trust_policy_rules'):
            errors.append('policy lifecycle renewal hint successor_policy_digest must bind transparency_trust_policy_rules')
    elif _has_digest(renewal.get('successor_policy_digest')) and not digest_binds(renewal.get('successor_policy_digest'), 'transparency_trust_policy_rules'):
        errors.append('policy lifecycle renewal hint successor_policy_digest must bind transparency_trust_policy_rules')
    if _has_digest(renewal.get('hint_digest')) and not digest_binds(renewal.get('hint_digest'), 'transparency_trust_policy_lifecycle_status'):
        errors.append('policy lifecycle renewal hint_digest must bind transparency_trust_policy_lifecycle_status')

    rotation_state = rotation.get('rotation_state')
    if rotation_state in {'planned_rotation_to_successor', 'successor_authority_active'}:
        if not digest_binds(rotation.get('successor_authority_digest'), 'transparency_trust_policy_lifecycle_authority'):
            errors.append('lifecycle-authority rotation successor_authority_digest must bind transparency_trust_policy_lifecycle_authority')
        if not digest_binds(rotation.get('rotation_statement_digest'), 'transparency_trust_policy_lifecycle_authority_rotation'):
            errors.append('lifecycle-authority rotation_statement_digest must bind transparency_trust_policy_lifecycle_authority_rotation')
    else:
        if _has_digest(rotation.get('successor_authority_digest')) and not digest_binds(rotation.get('successor_authority_digest'), 'transparency_trust_policy_lifecycle_authority'):
            errors.append('lifecycle-authority rotation successor_authority_digest must bind transparency_trust_policy_lifecycle_authority')
        if _has_digest(rotation.get('rotation_statement_digest')) and not digest_binds(rotation.get('rotation_statement_digest'), 'transparency_trust_policy_lifecycle_authority_rotation'):
            errors.append('lifecycle-authority rotation_statement_digest must bind transparency_trust_policy_lifecycle_authority_rotation')

    if rotation.get('delegation_state') != 'not_delegated':
        if not digest_binds(rotation.get('delegation_digest'), 'transparency_trust_policy_lifecycle_authority_delegation'):
            errors.append('delegated lifecycle authority requires delegation_digest binding transparency_trust_policy_lifecycle_authority_delegation')
    elif _has_digest(rotation.get('delegation_digest')) and not digest_binds(rotation.get('delegation_digest'), 'transparency_trust_policy_lifecycle_authority_delegation'):
        errors.append('lifecycle-authority delegation_digest must bind transparency_trust_policy_lifecycle_authority_delegation')

    if _has_digest(compromise.get('affected_authority_digest')) and not digest_binds(compromise.get('affected_authority_digest'), 'transparency_trust_policy_lifecycle_authority'):
        errors.append('lifecycle-authority compromise affected_authority_digest must bind transparency_trust_policy_lifecycle_authority')
    if compromise.get('state') == 'confirmed_contained':
        if not digest_binds(compromise.get('successor_or_recovery_authority_digest'), 'transparency_trust_policy_lifecycle_authority'):
            errors.append('contained lifecycle-authority compromise successor_or_recovery_authority_digest must bind transparency_trust_policy_lifecycle_authority')
        if not digest_binds(compromise.get('response_digest'), 'transparency_trust_policy_lifecycle_authority_compromise_response'):
            errors.append('contained lifecycle-authority compromise response_digest must bind transparency_trust_policy_lifecycle_authority_compromise_response')
    else:
        if _has_digest(compromise.get('successor_or_recovery_authority_digest')) and not digest_binds(compromise.get('successor_or_recovery_authority_digest'), 'transparency_trust_policy_lifecycle_authority'):
            errors.append('lifecycle-authority compromise successor_or_recovery_authority_digest must bind transparency_trust_policy_lifecycle_authority')
        if _has_digest(compromise.get('response_digest')) and not digest_binds(compromise.get('response_digest'), 'transparency_trust_policy_lifecycle_authority_compromise_response'):
            errors.append('lifecycle-authority compromise response_digest must bind transparency_trust_policy_lifecycle_authority_compromise_response')
    return errors


def check_policy_lifecycle_recovery_attestation_digest_bindings(att: dict[str, Any]) -> list[str]:
    """Validate digest classes in a policy lifecycle-authority recovery attestation reference."""
    errors: list[str] = []
    scope = _dict(att.get('scope'))
    portability = _dict(att.get('portability'))
    if not digest_binds(scope.get('policy_digest'), 'transparency_trust_policy_rules'):
        errors.append('policy lifecycle authority recovery attestation scope.policy_digest must bind transparency_trust_policy_rules')
    if not digest_binds(att.get('affected_authority_digest'), 'transparency_trust_policy_lifecycle_authority'):
        errors.append('policy lifecycle authority recovery attestation affected_authority_digest must bind transparency_trust_policy_lifecycle_authority')
    if not digest_binds(att.get('recovery_or_successor_authority_digest'), 'transparency_trust_policy_lifecycle_authority'):
        errors.append('policy lifecycle authority recovery attestation recovery_or_successor_authority_digest must bind transparency_trust_policy_lifecycle_authority')
    if not digest_binds(att.get('response_digest'), 'transparency_trust_policy_lifecycle_authority_compromise_response'):
        errors.append('policy lifecycle authority recovery attestation response_digest must bind transparency_trust_policy_lifecycle_authority_compromise_response')
    if not digest_binds(att.get('attestation_digest'), 'transparency_trust_policy_lifecycle_authority_recovery_attestation'):
        errors.append('policy lifecycle authority recovery attestation attestation_digest must bind transparency_trust_policy_lifecycle_authority_recovery_attestation')
    if portability.get('operator_scope') == 'compatible_operator_bound':
        if not digest_binds(portability.get('compatibility_statement_digest'), 'profile_compatibility_statement'):
            errors.append('cross-operator recovery attestation portability requires compatibility_statement_digest binding profile_compatibility_statement')
    elif _has_digest(portability.get('compatibility_statement_digest')) and not digest_binds(portability.get('compatibility_statement_digest'), 'profile_compatibility_statement'):
        errors.append('policy lifecycle authority recovery attestation compatibility_statement_digest must bind profile_compatibility_statement')
    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    auth = {
        'authority_digest': {'algorithm': 'sha256', 'value': 'a' * 64, 'binds': 'transparency_trust_policy_lifecycle_authority'},
        'policy_digest': {'algorithm': 'sha256', 'value': 'b' * 64, 'binds': 'transparency_trust_policy_rules'},
        'discovery': {
            'discovery_state': 'configured_authority',
            'authority_binding_digest': {'algorithm': 'sha256', 'value': 'c' * 64, 'binds': 'transparency_trust_policy_lifecycle_status'},
        },
        'renewal_hint': {'hint_state': 'none'},
        'anti_rollback_sequence': {
            'status_record_digest': {'algorithm': 'sha256', 'value': 'c' * 64, 'binds': 'transparency_trust_policy_lifecycle_status'},
        },
        'rotation_delegation_status': {
            'rotation_state': 'planned_rotation_to_successor',
            'successor_authority_digest': {'algorithm': 'sha256', 'value': 'd' * 64, 'binds': 'transparency_trust_policy_lifecycle_authority'},
            'rotation_statement_digest': {'algorithm': 'sha256', 'value': 'e' * 64, 'binds': 'transparency_trust_policy_lifecycle_authority_rotation'},
            'delegation_state': 'not_delegated',
            'compromise_response': {
                'state': 'none_known',
                'affected_authority_digest': {'algorithm': 'sha256', 'value': 'a' * 64, 'binds': 'transparency_trust_policy_lifecycle_authority'},
            },
        },
    }
    if check_policy_lifecycle_authority_digest_bindings(auth):
        errors.append('policy authority digest self-test rejected valid authority reference')
    bad = dict(auth)
    bad['rotation_delegation_status'] = dict(auth['rotation_delegation_status'])
    bad['rotation_delegation_status']['rotation_statement_digest'] = {'algorithm': 'sha256', 'value': 'e' * 64, 'binds': 'transparency_trust_policy_lifecycle_status'}
    if not any('rotation_statement_digest must bind transparency_trust_policy_lifecycle_authority_rotation' in e for e in check_policy_lifecycle_authority_digest_bindings(bad)):
        errors.append('policy authority digest self-test failed to reject wrong rotation statement digest binding')
    bad2 = dict(auth)
    bad2['anti_rollback_sequence'] = {'status_record_digest': {'algorithm': 'sha256', 'value': 'c' * 64, 'binds': 'profile_compatibility_statement'}}
    if not any('sequence status_record_digest must bind transparency_trust_policy_lifecycle_status' in e for e in check_policy_lifecycle_authority_digest_bindings(bad2)):
        errors.append('policy authority digest self-test failed to reject wrong status digest binding')
    bad_hint = dict(auth)
    bad_hint['renewal_hint'] = {
        'hint_state': 'successor_digest_available',
        'successor_policy_digest': {'algorithm': 'sha256', 'value': 'b' * 64, 'binds': 'transparency_trust_policy_rules'},
        'hint_digest': {'algorithm': 'sha256', 'value': 'c' * 64, 'binds': 'transparency_trust_policy_lifecycle_authority'},
    }
    if not any('renewal hint_digest must bind transparency_trust_policy_lifecycle_status' in e for e in check_policy_lifecycle_authority_digest_bindings(bad_hint)):
        errors.append('policy authority digest self-test failed to reject wrong renewal hint digest binding')

    att = {
        'scope': {'policy_digest': {'algorithm': 'sha256', 'value': 'b' * 64, 'binds': 'transparency_trust_policy_rules'}},
        'affected_authority_digest': {'algorithm': 'sha256', 'value': 'a' * 64, 'binds': 'transparency_trust_policy_lifecycle_authority'},
        'recovery_or_successor_authority_digest': {'algorithm': 'sha256', 'value': 'd' * 64, 'binds': 'transparency_trust_policy_lifecycle_authority'},
        'response_digest': {'algorithm': 'sha256', 'value': 'f' * 64, 'binds': 'transparency_trust_policy_lifecycle_authority_compromise_response'},
        'attestation_digest': {'algorithm': 'sha256', 'value': '1' * 64, 'binds': 'transparency_trust_policy_lifecycle_authority_recovery_attestation'},
        'portability': {'operator_scope': 'same_operator_only'},
    }
    if check_policy_lifecycle_recovery_attestation_digest_bindings(att):
        errors.append('policy authority digest self-test rejected valid recovery attestation')
    bad3 = dict(att)
    bad3['response_digest'] = {'algorithm': 'sha256', 'value': 'f' * 64, 'binds': 'transparency_trust_policy_lifecycle_status'}
    if not any('response_digest must bind transparency_trust_policy_lifecycle_authority_compromise_response' in e for e in check_policy_lifecycle_recovery_attestation_digest_bindings(bad3)):
        errors.append('policy authority digest self-test failed to reject wrong recovery response digest binding')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync policy authority digest semantic self-test passed.')

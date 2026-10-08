"""Authorized-verifier challenge/result semantic guardrails.

Temporal ordering lives in :mod:`authorized_verifier_temporal`; this module keeps
record-kind, disclosure-result, receipt, and portability-boundary consistency in
one small, replay-focused place.  The checks are intentionally about preventing a
schema-shaped record from being relabelled into a stronger or contradictory
current-use posture.  They do not make challenge disclosure material TimeSync
provenance or profile evidence.
"""
from __future__ import annotations

from typing import Any


def _disclosure_states(result: dict[str, Any]) -> list[str]:
    states: list[str] = []
    for disclosure in result.get('verified_disclosures', []) if isinstance(result.get('verified_disclosures'), list) else []:
        if isinstance(disclosure, dict) and isinstance(disclosure.get('verification_result'), str):
            states.append(disclosure['verification_result'])
    return states


def _check_record_kind(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    kind = record.get('record_kind')
    if kind == 'authorized_verifier_challenge':
        if isinstance(record.get('challenge_result'), dict):
            errors.append('authorized_verifier_challenge record cannot carry challenge_result')
        if isinstance(record.get('replay_context'), dict):
            errors.append('authorized_verifier_challenge record cannot carry replay_context')
    if isinstance(record.get('replay_context'), dict) and kind != 'authorized_verifier_challenge_result':
        errors.append('challenge result replay_context requires record_kind authorized_verifier_challenge_result')
    return errors


def _check_authorization_binding(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    authorization = record.get('verifier_authorization') if isinstance(record.get('verifier_authorization'), dict) else {}
    binding = authorization.get('authorization_binding') if isinstance(authorization.get('authorization_binding'), dict) else {}
    digest = binding.get('digest') if isinstance(binding.get('digest'), dict) else {}
    binding_type = binding.get('binding_type')
    binds = digest.get('binds')
    expected_by_type = {
        'local_authorization_record': 'authorization_record',
        'signed_verifier_authorization': 'authorization_record',
        'external_authority_record': 'external_authority_record',
        'test_fixture': 'authorization_record',
    }
    expected = expected_by_type.get(binding_type)
    if isinstance(binds, str) and expected is not None and binds != expected:
        errors.append(f'authorization_binding digest for {binding_type} must bind {expected}')
    return errors


def _check_scope_and_receipt(record: dict[str, Any], result: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    authorization = record.get('verifier_authorization') if isinstance(record.get('verifier_authorization'), dict) else {}
    scope = authorization.get('authorization_scope')
    requested_materials = {
        req.get('requested_material')
        for req in record.get('requested_disclosures', [])
        if isinstance(req, dict)
    }
    basis = result.get('result_basis')
    receipt = result.get('receipt') if isinstance(result.get('receipt'), dict) else {}
    receipt_kind = receipt.get('receipt_kind')
    receipt_digest = receipt.get('digest') if isinstance(receipt.get('digest'), dict) else {}
    receipt_binds = receipt_digest.get('binds')

    if 'salt_and_preimage' in requested_materials and scope != 'salt_preimage_verification':
        errors.append('salt/preimage requested material requires authorization_scope salt_preimage_verification')
    if scope == 'salt_preimage_verification':
        if requested_materials and requested_materials != {'salt_and_preimage'}:
            errors.append('salt_preimage_verification authorization requires only salt_and_preimage requested material')
        if basis != 'authorized_external_preimage_review':
            errors.append('salt_preimage_verification challenge result requires result_basis authorized_external_preimage_review')
        if receipt_kind != 'external_preimage_review_receipt':
            errors.append('salt_preimage_verification challenge result requires external_preimage_review_receipt')
    if receipt_kind == 'external_preimage_review_receipt' and receipt_binds != 'authorized_verifier_challenge_receipt':
        errors.append('external_preimage_review_receipt digest must bind authorized_verifier_challenge_receipt')
    return errors


def _check_result_consistency(result: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    status = result.get('result')
    states = _disclosure_states(result)
    if status == 'matched':
        if not states:
            errors.append('matched challenge result requires at least one matched verified disclosure')
        elif any(state != 'matched' for state in states):
            errors.append('matched challenge result requires every verified disclosure to be matched')
    elif status == 'mismatch':
        if 'mismatch' not in states:
            errors.append('mismatch challenge result requires at least one mismatching verified disclosure')
    elif status == 'external_system_verified':
        if 'external_system_verified' not in states:
            errors.append('external_system_verified challenge result requires an external_system_verified disclosure')
        if result.get('result_basis') != 'external_system_verification':
            errors.append('external_system_verified challenge result requires result_basis external_system_verification')
    elif status == 'not_disclosed':
        if states and any(state != 'not_verified' for state in states):
            errors.append('not_disclosed challenge result cannot carry matched or mismatching disclosures')
        if result.get('result_basis') != 'not_disclosed':
            errors.append('not_disclosed challenge result requires result_basis not_disclosed')

    receipt = result.get('receipt') if isinstance(result.get('receipt'), dict) else {}
    receipt_digest = receipt.get('digest') if isinstance(receipt.get('digest'), dict) else {}
    receipt_value = str(receipt_digest.get('value', '')).lower()
    for disclosure in result.get('verified_disclosures', []) if isinstance(result.get('verified_disclosures'), list) else []:
        if not isinstance(disclosure, dict):
            continue
        digest_value = disclosure.get('receipt_digest_value')
        if isinstance(digest_value, str) and receipt_value and digest_value.lower() != receipt_value:
            errors.append('verified disclosure receipt_digest_value must match challenge_result.receipt.digest.value')
    return errors


def _check_portability_boundary(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    portability = record.get('portability_boundary') if isinstance(record.get('portability_boundary'), dict) else {}
    result_may_be_replayed_for = set(portability.get('result_may_be_replayed_for', [])) if isinstance(portability.get('result_may_be_replayed_for'), list) else set()
    if portability.get('portable_result_scope') == 'not_portable' and result_may_be_replayed_for:
        errors.append('not_portable challenge result cannot advertise replay uses')
    if portability.get('replay_policy') == 'not_replayable' and result_may_be_replayed_for:
        errors.append('not_replayable challenge result cannot advertise replay uses')
    return errors


def check_authorized_verifier_result_semantics(record: dict[str, Any]) -> list[str]:
    """Validate non-temporal authorized-verifier challenge/result semantics."""
    errors: list[str] = []
    errors.extend(_check_record_kind(record))
    errors.extend(_check_authorization_binding(record))
    errors.extend(_check_portability_boundary(record))

    result = record.get('challenge_result') if isinstance(record.get('challenge_result'), dict) else None
    if result is not None:
        errors.extend(_check_scope_and_receipt(record, result))
        errors.extend(_check_result_consistency(result))
    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    base = {
        'record_kind': 'authorized_verifier_challenge_result',
        'verifier_authorization': {
            'authorization_scope': 'salt_preimage_verification',
            'authorization_binding': {
                'binding_type': 'signed_verifier_authorization',
                'digest': {'binds': 'authorization_record'},
            },
        },
        'requested_disclosures': [{'requested_material': 'salt_and_preimage'}],
        'portability_boundary': {
            'portable_result_scope': 'local_retained_record_only',
            'replay_policy': 'same_summary_same_assessment_only',
            'result_may_be_replayed_for': ['commitment_verification_only'],
        },
        'challenge_result': {
            'result': 'matched',
            'result_basis': 'authorized_external_preimage_review',
            'verified_disclosures': [{'verification_result': 'matched', 'receipt_digest_value': 'a' * 64}],
            'receipt': {
                'receipt_kind': 'external_preimage_review_receipt',
                'digest': {'value': 'a' * 64, 'binds': 'authorized_verifier_challenge_receipt'},
            },
        },
    }
    if check_authorized_verifier_result_semantics(base):
        errors.append('authorized verifier result semantic self-test rejected valid base')
    bad_kind = {**base, 'record_kind': 'authorized_verifier_challenge'}
    if not any('cannot carry challenge_result' in e for e in check_authorized_verifier_result_semantics(bad_kind)):
        errors.append('authorized verifier result semantic self-test failed: result carried by challenge kind')
    bad_result = {
        **base,
        'challenge_result': {
            **base['challenge_result'],
            'verified_disclosures': [{'verification_result': 'not_verified', 'receipt_digest_value': 'a' * 64}],
        },
    }
    if not any('every verified disclosure' in e for e in check_authorized_verifier_result_semantics(bad_result)):
        errors.append('authorized verifier result semantic self-test failed: matched result accepted not_verified disclosure')
    bad_receipt = {
        **base,
        'challenge_result': {
            **base['challenge_result'],
            'receipt': {
                **base['challenge_result']['receipt'],
                'digest': {'value': 'a' * 64, 'binds': 'selective_disclosure_proof'},
            },
        },
    }
    if not any('external_preimage_review_receipt digest must bind' in e for e in check_authorized_verifier_result_semantics(bad_receipt)):
        errors.append('authorized verifier result semantic self-test failed: wrong receipt bind accepted')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync authorized-verifier result semantic self-test passed.')

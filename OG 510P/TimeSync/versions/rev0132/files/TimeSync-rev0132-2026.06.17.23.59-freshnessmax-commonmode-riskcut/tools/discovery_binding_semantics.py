#!/usr/bin/env python3
"""Discovery-result version/digest binding semantics for TimeSync."""
from __future__ import annotations

from typing import Any
import re


def digest_binds(digest: Any, expected: str) -> bool:
    return (
        isinstance(digest, dict)
        and digest.get('algorithm') == 'sha256'
        and isinstance(digest.get('value'), str)
        and bool(re.fullmatch(r'[A-Fa-f0-9]{64}', digest.get('value', '')))
        and digest.get('binds') == expected
    )



DISCOVERY_RESULT_DIGEST_BINDINGS: dict[str, str] = {
    # These expectations are intentionally for the discovery result wrapper's
    # digest_binding.digest, not for every digest carried inside the returned
    # value.  Some returned values are self-describing artifacts; others are
    # generic discovery-returned objects whose nested value is validated by its
    # own schema when a dedicated nested checker exists.
    'aggregate_lifecycle_decision_table': 'aggregate_lifecycle_decision_table',
    'digest_binding_policy': 'digest_binding_policy',
    'external_transparency_receipt_reference': 'external_transparency_receipt',
    'profile_compatibility_drift_decision': 'discovery_returned_object',
    'scope_composition_guard': 'scope_composition_guard',
    'semantic_version_negotiation': 'discovery_returned_object',
}

def parse_semver(value: Any) -> tuple[int, int, int] | None:
    if not isinstance(value, str):
        return None
    m = re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', value)
    if not m:
        return None
    return tuple(int(part) for part in m.groups())  # type: ignore[return-value]


def check_downgrade_proof_metadata(
    item: str,
    negotiation: dict[str, Any],
    request_negotiation: dict[str, Any] | None = None,
    current_use: bool | None = None,
) -> list[str]:
    """Discovery downgrade proof checks shared by result metadata and drift decisions."""
    errors: list[str] = []
    current = negotiation.get('current_use_allowed') is True if current_use is None else bool(current_use)
    decision = negotiation.get('decision')
    downgraded = decision == 'downgraded_to_supported' or negotiation.get('downgrade_basis') not in {None, 'not_applicable'}
    basis = negotiation.get('downgrade_basis')
    if current and basis == 'weaker_or_unknown':
        errors.append(f'{item}: current downgraded result cannot use weaker_or_unknown downgrade basis')
    if current and downgraded:
        if not negotiation.get('source_semantic_version') or not negotiation.get('selected_semantic_version'):
            errors.append(f'{item}: current downgraded result requires source_semantic_version and selected_semantic_version')
        if not digest_binds(negotiation.get('downgrade_proof_digest'), 'profile_downgrade_proof'):
            errors.append(f'{item}: current downgraded result requires downgrade_proof_digest binding profile_downgrade_proof')
        if negotiation.get('stronger_or_equal_semantics') is not True:
            errors.append(f'{item}: current downgraded result requires stronger_or_equal_semantics true')
    if request_negotiation:
        supported = list(request_negotiation.get('supported_result_semantic_versions', {}).get(item, []))
        selected = negotiation.get('selected_semantic_version')
        if selected and supported and selected not in supported:
            errors.append(f'{item}: selected downgraded semantic version must be explicitly supported by request')
        if request_negotiation.get('downgrade_proof_required_for_current_use') is True and current and downgraded and not digest_binds(negotiation.get('downgrade_proof_digest'), 'profile_downgrade_proof'):
            errors.append(f'{item}: current downgraded result requires downgrade proof under request policy')
    return errors


def check_result_version_negotiation(
    item: str,
    result: dict[str, Any],
    request_negotiation: dict[str, Any] | None = None,
) -> list[str]:
    """Discovery-result semantic-version and downgrade-proof safety checks."""
    errors: list[str] = []
    version = result.get('semantic_version')
    negotiation = result.get('version_negotiation') if isinstance(result.get('version_negotiation'), dict) else {}
    if not version and not negotiation:
        return errors
    if version and parse_semver(version) is None:
        errors.append(f'{item}: semantic_version must be MAJOR.MINOR.PATCH')
    decision = negotiation.get('decision')
    current_use = negotiation.get('current_use_allowed') is True
    if decision == 'accepted_unknown_newer' and current_use:
        errors.append(f'{item}: unknown newer discovery result cannot be accepted as current')
    if negotiation.get('updates_profile_assessment') is True:
        errors.append(f'{item}: version negotiation cannot update profile assessment')
    if negotiation.get('updates_actionability') is True:
        errors.append(f'{item}: version negotiation cannot update actionability')
    supported: list[str] = []
    if request_negotiation:
        supported = list(request_negotiation.get('supported_result_semantic_versions', {}).get(item, []))
        policy = request_negotiation.get('unknown_newer_version_policy')
        if policy == 'fail_closed' and result.get('status') == 'returned' and supported and version not in supported:
            errors.append(f'{item}: fail-closed negotiation cannot return unsupported semantic_version as value')
        if request_negotiation.get('accept_legacy_canonicalization_for_current') is not False:
            errors.append(f'{item}: request negotiation must not accept legacy canonicalization for current use')
    if supported and version and version not in supported:
        parsed = parse_semver(version)
        supported_versions = [v for v in (parse_semver(x) for x in supported) if v is not None]
        newer = bool(parsed and supported_versions and parsed > max(supported_versions))
        if newer and current_use:
            errors.append(f'{item}: unknown newer discovery result cannot be accepted as current')
        if decision == 'accepted_exact':
            errors.append(f'{item}: accepted_exact requires semantic_version to be explicitly supported by request')
        if decision not in {'returned_metadata_only', 'omitted_unknown_newer', 'rejected_unknown_newer', 'downgraded_to_supported'}:
            errors.append(f'{item}: unsupported semantic_version requires metadata-only, omitted, rejected, or downgraded handling')
    errors.extend(check_downgrade_proof_metadata(item, negotiation, request_negotiation, current_use))
    return errors


def check_digest_binding_metadata(item: str, binding: Any) -> list[str]:
    """Digest binding and byte-envelope checks for discovery results."""
    errors: list[str] = []
    if not isinstance(binding, dict):
        return errors
    mode = binding.get('binding_mode')
    current = binding.get('current_use_allowed') is True
    if mode == 'canonical_json_rfc8785':
        if binding.get('canonicalization') != 'json_canonicalization_scheme_rfc8785':
            errors.append(f'{item}: canonical JSON binding requires json_canonicalization_scheme_rfc8785')
    if mode == 'legacy_python_sort_keys_historical_only' and current:
        errors.append(f'{item}: legacy canonicalization cannot bind current-use objects')
    if binding.get('canonicalization') == 'timesync_python_json_sort_keys_legacy' and current:
        errors.append(f'{item}: legacy canonicalization cannot bind current-use objects')
    if mode in {'external_byte_envelope', 'external_receipt_bytes'}:
        if binding.get('payload_type_authenticated') is not True:
            errors.append(f'{item}: byte-envelope binding requires authenticated payload type')
        if binding.get('verified_before_payload_parse') is not True:
            errors.append(f'{item}: byte-envelope binding requires bytes verified before payload parse')
        if binding.get('canonicalization_dependency') != 'not_required_for_signature_validation':
            errors.append(f'{item}: byte-envelope binding cannot depend on JSON canonicalization for signature validation')
        if binding.get('raw_payload_bytes_exported') is not False:
            errors.append(f'{item}: byte-envelope binding must not export raw payload bytes by default')
    if current and not digest_binds(binding.get('digest'), binding.get('digest', {}).get('binds', '') if isinstance(binding.get('digest'), dict) else ''):
        errors.append(f'{item}: current digest binding requires sha256 digest with binds value')
    expected_binds = DISCOVERY_RESULT_DIGEST_BINDINGS.get(item)
    if current and expected_binds and not digest_binds(binding.get('digest'), expected_binds):
        errors.append(f'{item}: current digest binding digest must bind {expected_binds}')
    if current and mode in {'canonical_json_rfc8785', 'external_byte_envelope', 'external_receipt_bytes'}:
        digest = binding.get('digest') if isinstance(binding.get('digest'), dict) else {}
        if digest.get('binds') not in {'digest_binding_policy', 'semantic_version_negotiation'} and not digest_binds(binding.get('digest_binding_policy_digest'), 'digest_binding_policy'):
            errors.append(f'{item}: current digest binding requires digest_binding_policy_digest')
    return errors


def check_current_result_binding(
    item: str,
    result: dict[str, Any],
    request_negotiation: dict[str, Any] | None = None,
) -> list[str]:
    """Make current-use discovery binding fail closed.

    Version negotiation says whether a returned object may be interpreted now.
    Digest binding says which bytes/semantic object are being interpreted.  A
    current-use result must have both in agreement; otherwise current-use
    freshness can accidentally bless an unsigned or unbound object.
    """
    errors: list[str] = []
    negotiation = result.get('version_negotiation') if isinstance(result.get('version_negotiation'), dict) else {}
    digest_binding = result.get('digest_binding') if isinstance(result.get('digest_binding'), dict) else None
    version_current = negotiation.get('current_use_allowed') is True
    digest_current = isinstance(digest_binding, dict) and digest_binding.get('current_use_allowed') is True
    current = version_current or digest_current
    if not current:
        return errors
    if digest_binding is None:
        errors.append(f'{item}: current discovery result requires digest_binding metadata')
        return errors
    if version_current and not digest_current:
        errors.append(f'{item}: version-negotiated current discovery result requires digest_binding.current_use_allowed true')
    if digest_current and not version_current:
        errors.append(f'{item}: digest-bound current discovery result requires version_negotiation.current_use_allowed true')
    if request_negotiation and request_negotiation.get('require_digest_binding_policy') is True and item != 'digest_binding_policy':
        if not digest_binds(digest_binding.get('digest_binding_policy_digest'), 'digest_binding_policy'):
            errors.append(f'{item}: request requires digest_binding_policy_digest for current discovery result')
    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    good_digest = {
        'algorithm': 'sha256',
        'value': 'a' * 64,
        'binds': 'discovery_returned_object',
    }
    good_policy_digest = {
        'algorithm': 'sha256',
        'value': 'b' * 64,
        'binds': 'digest_binding_policy',
    }
    base = {
        'status': 'returned',
        'semantic_version': '1.0.0',
        'version_negotiation': {'decision': 'accepted_exact', 'current_use_allowed': True},
        'digest_binding': {
            'binding_mode': 'canonical_json_rfc8785',
            'canonicalization': 'json_canonicalization_scheme_rfc8785',
            'current_use_allowed': True,
            'digest': good_digest,
            'digest_binding_policy_digest': good_policy_digest,
        },
    }
    request = {'require_digest_binding_policy': True, 'accept_legacy_canonicalization_for_current': False}
    if check_current_result_binding('item', base, request):
        errors.append('check_current_result_binding self-test failed: valid current result rejected')
    missing = dict(base)
    missing.pop('digest_binding')
    if not check_current_result_binding('item', missing, request):
        errors.append('check_current_result_binding self-test failed: missing digest binding accepted')
    mismatch = {**base, 'digest_binding': {**base['digest_binding'], 'current_use_allowed': False}}
    if not check_current_result_binding('item', mismatch, request):
        errors.append('check_current_result_binding self-test failed: current flag mismatch accepted')
    no_policy = {**base, 'digest_binding': {k: v for k, v in base['digest_binding'].items() if k != 'digest_binding_policy_digest'}}
    if not check_current_result_binding('item', no_policy, request):
        errors.append('check_current_result_binding self-test failed: missing policy digest accepted')
    wrong_wrapper = {
        **base,
        'digest_binding': {
            **base['digest_binding'],
            'digest': {'algorithm': 'sha256', 'value': 'a' * 64, 'binds': 'normative_profile_rules'},
        },
    }
    if not any('current digest binding digest must bind discovery_returned_object' in e for e in check_digest_binding_metadata('semantic_version_negotiation', wrong_wrapper['digest_binding'])):
        errors.append('check_digest_binding_metadata self-test failed: wrong discovery result digest binding accepted')
    return errors

if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync discovery binding semantic self-test passed.')

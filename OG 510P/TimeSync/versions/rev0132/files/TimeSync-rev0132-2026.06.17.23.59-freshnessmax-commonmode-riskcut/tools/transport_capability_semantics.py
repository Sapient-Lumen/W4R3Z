#!/usr/bin/env python3
"""Semantic validation for transport capability advertisements.

Capability advertisements are descriptive, but they can still mislead consumers
when they claim profiles or request items that the advertised adapter/profile set
cannot actually carry.  These checks keep transport capability metadata aligned
with the adapter catalog and profile catalog without turning capabilities into a
transport protocol or registry credential.
"""
from __future__ import annotations

from typing import Any

CAPABILITY_REQUEST_ITEMS = {
    'timestate',
    'assessment_time',
    'assessed_profile',
    'profile_conformance',
    'policy_acceptance',
    'validity_horizon',
    'traceability_posture',
    'sync_dimension',
    'holdover_class',
    'validity_scope',
    'time_error_bound',
    'rate_error_bound',
    'timescale_realization',
    'clock_continuity_posture',
    'source_diversity_posture',
    'pnt_risk_posture',
    'boundary_context',
}

NEGATIVE_RESULT_STATUSES = {'unavailable', 'unknown', 'omitted'}
MESSAGE_TYPES = {'wire_claim', 'local_assessed_state', 'discovery_request', 'discovery_result', 'capability_advertisement', 'retained_assessment_export'}


def _profile_key(ref: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    return (ref.get('authority'), ref.get('id'), ref.get('version') or ref.get('revision'))


def _resolve_profile(
    ref: dict[str, Any],
    catalog_index: dict[tuple[str | None, str, str | None], dict[str, Any]],
) -> dict[str, Any] | None:
    authority, pid, version = _profile_key(ref)
    if not pid:
        return None
    return catalog_index.get((authority, pid, version)) or catalog_index.get((None, pid, version))


def _profile_obligation_items(profile: dict[str, Any]) -> set[str]:
    obligations = profile.get('obligations', {}) if isinstance(profile.get('obligations'), dict) else {}
    items: set[str] = set()
    for bucket in ('required_items', 'profile_default_items', 'requestable_items'):
        values = obligations.get(bucket, [])
        if isinstance(values, list):
            items.update(str(item) for item in values if isinstance(item, str))
    return items


def check_transport_capability_semantics(
    cap: dict[str, Any],
    adapter_index: dict[str, dict[str, Any]],
    catalog_index: dict[tuple[str | None, str, str | None], dict[str, Any]],
) -> list[str]:
    """Validate capability advertisement claims against adapter/profile catalogs."""
    errors: list[str] = []
    aid = cap.get('adapter_id')
    adapter = adapter_index.get(aid)
    if adapter is None:
        errors.append(f'capability adapter_id {aid!r} not in catalog')
        return errors

    allowed = set(adapter.get('payload_types', []))
    claimed = set(cap.get('supported_message_types', [])) if isinstance(cap.get('supported_message_types'), list) else set()
    extra = claimed - allowed
    if extra:
        errors.append(f'capability for {aid} claims message types not allowed by adapter: {sorted(extra)}')
    unknown_message_types = claimed - MESSAGE_TYPES
    if unknown_message_types:
        errors.append(f'capability for {aid} claims unknown message types: {sorted(unknown_message_types)}')

    if set(cap.get('negative_result_statuses', [])) != NEGATIVE_RESULT_STATUSES:
        errors.append('capability negative_result_statuses must include unavailable, unknown, and omitted')

    supported_profiles = cap.get('supported_profiles', []) if isinstance(cap.get('supported_profiles'), list) else []
    if adapter.get('profile_reference_policy', {}).get('may_carry_profile_reference') is False and supported_profiles:
        errors.append(f'capability for {aid} cannot advertise supported_profiles because adapter forbids profile references')

    seen_profiles: set[tuple[str | None, str | None, str | None]] = set()
    resolved_profiles: list[dict[str, Any]] = []
    for ref in supported_profiles:
        if not isinstance(ref, dict):
            continue
        key = _profile_key(ref)
        if key in seen_profiles:
            errors.append(f'capability for {aid} has duplicate supported_profile reference {key}')
        seen_profiles.add(key)
        profile = _resolve_profile(ref, catalog_index)
        if profile is None:
            errors.append(f'capability for {aid} supported profile {key} is not in profile catalog')
        else:
            resolved_profiles.append(profile)

    advertised_items = set(cap.get('requestable_items', [])) if isinstance(cap.get('requestable_items'), list) else set()
    unknown_items = advertised_items - CAPABILITY_REQUEST_ITEMS
    for item in sorted(unknown_items):
        errors.append(f'capability requestable_items contains unknown item {item!r}')

    if resolved_profiles:
        supported_items: set[str] = set()
        for profile in resolved_profiles:
            supported_items.update(_profile_obligation_items(profile))
        unsupported = advertised_items - supported_items
        for item in sorted(unsupported):
            errors.append(f'capability requestable item {item!r} is not supported by advertised profiles')
    elif advertised_items:
        errors.append('capability requestable_items require at least one resolved supported_profile')

    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    adapter_index = {
        'timesync.adapter.good': {
            'payload_types': ['capability_advertisement'],
            'profile_reference_policy': {'may_carry_profile_reference': True},
        },
        'timesync.adapter.no-profile': {
            'payload_types': ['wire_claim'],
            'profile_reference_policy': {'may_carry_profile_reference': False},
        },
    }
    catalog_index = {
        ('auth', 'P1', '1.0.0'): {
            'obligations': {
                'required_items': ['timestate'],
                'profile_default_items': ['sync_dimension'],
                'requestable_items': ['traceability_posture'],
            }
        }
    }
    valid = {
        'adapter_id': 'timesync.adapter.good',
        'supported_message_types': ['capability_advertisement'],
        'supported_profiles': [{'authority': 'auth', 'id': 'P1', 'version': '1.0.0'}],
        'requestable_items': ['traceability_posture', 'sync_dimension'],
        'negative_result_statuses': ['unavailable', 'unknown', 'omitted'],
    }
    if check_transport_capability_semantics(valid, adapter_index, catalog_index):
        errors.append('transport capability self-test rejected valid capability')
    missing_profile = dict(valid, supported_profiles=[{'authority': 'auth', 'id': 'P9', 'version': '1.0.0'}])
    if not any('is not in profile catalog' in e for e in check_transport_capability_semantics(missing_profile, adapter_index, catalog_index)):
        errors.append('transport capability self-test accepted unknown supported_profile')
    unknown_item = dict(valid, requestable_items=['source_roster'])
    if not any('unknown item' in e for e in check_transport_capability_semantics(unknown_item, adapter_index, catalog_index)):
        errors.append('transport capability self-test accepted unknown requestable item')
    forbidden_profile = dict(valid, adapter_id='timesync.adapter.no-profile', supported_message_types=['wire_claim'])
    if not any('forbids profile references' in e for e in check_transport_capability_semantics(forbidden_profile, adapter_index, catalog_index)):
        errors.append('transport capability self-test accepted supported_profiles for profile-forbidden adapter')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync transport capability semantic self-test passed.')

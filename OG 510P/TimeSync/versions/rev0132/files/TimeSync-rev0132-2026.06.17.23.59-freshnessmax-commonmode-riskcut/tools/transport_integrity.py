#!/usr/bin/env python3
"""Transport-envelope integrity/binding-strength semantic checks.

The transport envelope can authenticate or sign carriage, but that protection must
not be confused with TimeState provenance or with profile-reference digest binding.
This helper keeps the executable envelope-integrity rules small and separate from
payload validation.
"""
from __future__ import annotations

from typing import Any


SEMANTIC_PAYLOAD_COVERS = {'semantic_payload', 'semantic_payload_digest'}


def check_transport_integrity(envelope: dict[str, Any]) -> list[str]:
    """Return semantic integrity/binding-strength errors for one envelope."""
    errors: list[str] = []
    adapter = envelope.get('adapter') if isinstance(envelope.get('adapter'), dict) else {}
    binding_strength = adapter.get('binding_strength')
    integrity = envelope.get('integrity') if isinstance(envelope.get('integrity'), dict) else None
    protection = integrity.get('protection') if integrity else None
    covers = set(integrity.get('covers', []) if integrity and isinstance(integrity.get('covers'), list) else [])

    if binding_strength == 'semantic_only':
        if integrity is not None and protection != 'none':
            errors.append('semantic_only transport binding must not claim transport authentication or payload signature')
        if integrity is not None and covers:
            errors.append('semantic_only transport binding must not claim integrity coverage')

    if binding_strength == 'authenticated_transport':
        if integrity is None:
            errors.append('authenticated_transport binding requires an integrity block')
        elif protection != 'transport_authenticated':
            errors.append('authenticated_transport binding requires integrity.protection transport_authenticated')
        if integrity is not None and 'semantic_payload' not in covers:
            errors.append('authenticated_transport binding must cover semantic_payload')

    if binding_strength == 'signed_payload':
        if integrity is None:
            errors.append('signed_payload binding requires an integrity block')
        elif protection not in {'signed_payload', 'detached_signature'}:
            errors.append('signed_payload binding requires signed_payload or detached_signature protection')
        if integrity is not None and not (covers & SEMANTIC_PAYLOAD_COVERS):
            errors.append('signed_payload binding must cover semantic_payload or semantic_payload_digest')
        if integrity is not None and not integrity.get('algorithm'):
            errors.append('signed_payload binding requires integrity.algorithm')
        if integrity is not None and not integrity.get('value'):
            errors.append('signed_payload binding requires integrity.value')

    if 'profile_reference' in covers and not (covers & SEMANTIC_PAYLOAD_COVERS):
        errors.append('profile_reference integrity cover cannot stand alone; profile digest obligations remain in the semantic payload')

    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    valid_signed = {
        'adapter': {'binding_strength': 'signed_payload'},
        'integrity': {'protection': 'signed_payload', 'covers': ['semantic_payload'], 'algorithm': 'ed25519', 'value': 'sig'},
    }
    if check_transport_integrity(valid_signed):
        errors.append('transport integrity self-test rejected valid signed_payload envelope')

    weak_signed = {
        'adapter': {'binding_strength': 'signed_payload'},
        'integrity': {'protection': 'none', 'covers': []},
    }
    if not any('signed_payload binding requires signed_payload or detached_signature protection' in e for e in check_transport_integrity(weak_signed)):
        errors.append('transport integrity self-test failed to reject unsigned signed_payload binding')

    weak_auth = {
        'adapter': {'binding_strength': 'authenticated_transport'},
        'integrity': {'protection': 'transport_authenticated', 'covers': ['envelope_metadata']},
    }
    if not any('authenticated_transport binding must cover semantic_payload' in e for e in check_transport_integrity(weak_auth)):
        errors.append('transport integrity self-test failed to reject authenticated transport without semantic payload cover')

    profile_only = {
        'adapter': {'binding_strength': 'signed_payload'},
        'integrity': {'protection': 'signed_payload', 'covers': ['profile_reference'], 'algorithm': 'ed25519', 'value': 'sig'},
    }
    if not any('profile_reference integrity cover cannot stand alone' in e for e in check_transport_integrity(profile_only)):
        errors.append('transport integrity self-test failed to reject profile_reference-only integrity cover')

    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync transport integrity self-test passed.')

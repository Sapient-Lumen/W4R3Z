#!/usr/bin/env python3
"""Profile-reference binding integrity and artifact-time checks.

A signed profile binding attached to a profile reference is supporting metadata
about which profile revision/digest is being named. It must not be treated as a
substitute for payload-carried digest obligations, and it must not be issued
after the artifact or assessment that relies on it.
"""
from __future__ import annotations

from typing import Any

from temporal_coherence import check_time_not_after


def _covers(binding: dict[str, Any]) -> set[str]:
    covers = binding.get('covers')
    if not isinstance(covers, list):
        return set()
    return {item for item in covers if isinstance(item, str)}


def check_profile_reference_binding(
    ref: dict[str, Any],
    *,
    used_at: Any | None = None,
    used_at_label: str = 'profile reference use time',
    prefix: str = 'profile reference',
) -> list[str]:
    """Validate a profile-reference signed binding without verifying crypto.

    The helper enforces only structural and temporal semantics that JSON Schema
    cannot express:
    - a binding has an explicit covers list;
    - the covers list actually binds the profile identity fields present on the
      reference;
    - a digest-bearing reference has the digest covered by the binding; and
    - binding.signed_at is not later than the artifact/assessment using it.
    """
    errors: list[str] = []
    binding = ref.get('binding')
    if not isinstance(binding, dict):
        return errors

    if binding.get('type') != 'signed_profile_binding':
        return errors

    covered = _covers(binding)
    if not covered:
        errors.append(f'{prefix} signed_profile_binding requires covers list')
        return errors

    for field in ('authority', 'id'):
        if ref.get(field) is not None and field not in covered:
            errors.append(f'{prefix} signed_profile_binding must cover {field}')
    if ref.get('version') is not None and 'version' not in covered:
        errors.append(f'{prefix} signed_profile_binding must cover version')
    if ref.get('revision') is not None and 'revision' not in covered:
        errors.append(f'{prefix} signed_profile_binding must cover revision')
    if isinstance(ref.get('digest'), dict) and 'digest' not in covered:
        errors.append(f'{prefix} signed_profile_binding must cover digest when digest is present')

    signed_at = binding.get('signed_at')
    if used_at is not None and signed_at is not None:
        errors.extend(check_time_not_after(
            signed_at,
            used_at,
            value_label=f'{prefix} binding.signed_at',
            anchor_label=used_at_label,
            error_message=f'{prefix} binding.signed_at cannot be after {used_at_label}',
        ))
    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    good = {
        'authority': 'example-authority',
        'id': 'P3-traceable-finance',
        'version': '1.0.0',
        'digest': {'algorithm': 'sha256', 'value': 'a' * 64, 'binds': 'normative_profile_rules'},
        'binding': {
            'type': 'signed_profile_binding',
            'issuer': 'example-authority',
            'signed_at': '2026-05-10T22:29:00Z',
            'signature': 'placeholder',
            'covers': ['authority', 'id', 'version', 'digest'],
        },
    }
    if check_profile_reference_binding(good, used_at='2026-05-10T22:29:01Z', used_at_label='assessment_time'):
        errors.append('profile_reference_binding self-test rejected coherent bound reference')

    future = dict(good)
    future['binding'] = dict(good['binding'], signed_at='2026-05-10T22:29:02Z')
    if not any('binding.signed_at cannot be after assessment_time' in e for e in check_profile_reference_binding(future, used_at='2026-05-10T22:29:01Z', used_at_label='assessment_time')):
        errors.append('profile_reference_binding self-test accepted future signed binding')

    missing_digest = dict(good)
    missing_digest['binding'] = dict(good['binding'], covers=['authority', 'id', 'version'])
    if not any('must cover digest' in e for e in check_profile_reference_binding(missing_digest, used_at='2026-05-10T22:29:01Z', used_at_label='assessment_time')):
        errors.append('profile_reference_binding self-test accepted digest outside signed binding covers')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync profile-reference binding self-test passed.')

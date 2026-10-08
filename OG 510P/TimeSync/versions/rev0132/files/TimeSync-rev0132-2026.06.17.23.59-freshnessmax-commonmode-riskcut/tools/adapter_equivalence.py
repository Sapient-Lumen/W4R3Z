#!/usr/bin/env python3
"""Cross-adapter equivalence checks for NTP-family replay evidence.

This is deliberately not a generic observation schema.  It is an executable
regression harness: two implementation-specific parsers are fed equivalent NTP
operational state and must agree on the six-field TimeState boundary, the P1
profile decision, and the exact conservative interval arithmetic.
"""
from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path
import sys
from typing import Any

sys.dont_write_bytecode = True

import chrony_adapter
import ntpq_adapter
from ntp_bound import self_test as ntp_bound_self_test

ROOT = Path(__file__).resolve().parents[1]


COMPARE_KEYS = (
    'profile_conformance',
    'applicability',
    'source_posture',
    'regime',
    'actionability',
    'policy_status',
    'fallback_mapping',
)


def _assessment(bundle: dict[str, Any]) -> dict[str, Any]:
    assessments = bundle['local_assessed_state'].get('profile_assessments', [])
    if not assessments:
        raise ValueError('local assessed state has no profile assessment')
    return assessments[0]


def _summary(bundle: dict[str, Any]) -> dict[str, Any]:
    state = bundle['local_assessed_state']
    ts = state['timestate']
    assessment = _assessment(bundle)
    acceptance = assessment.get('policy_acceptance', {})
    evaluation_summary = assessment.get('evaluation_summary', {})
    explanation = bundle['explanation']
    return {
        'interval_earliest': ts['interval']['earliest'],
        'interval_latest': ts['interval']['latest'],
        'timescale': ts['timescale'],
        'regime': ts['regime'],
        'source_posture': ts['source_posture'],
        'applicability': ts['applicability'],
        'profile_conformance': assessment.get('profile_conformance'),
        'actionability': acceptance.get('actionability'),
        'policy_status': acceptance.get('status'),
        'fallback_mapping': evaluation_summary.get('fallback_mapping'),
        'collection_age_seconds': explanation.get('collection_age_seconds'),
        'total_interval_bound_seconds': explanation.get('total_interval_bound_seconds'),
        'total_interval_bound_ms': explanation.get('total_interval_bound_ms'),
    }


def _build_chrony(case: dict[str, Any], root: Path) -> dict[str, Any]:
    spec = case['chrony']
    obs = chrony_adapter.build_observation(
        tracking_text=(root / spec['tracking']).read_text(encoding='utf-8'),
        sources_text=(root / spec.get('sources', '')).read_text(encoding='utf-8') if spec.get('sources') else '',
        sourcestats_text=(root / spec.get('sourcestats', '')).read_text(encoding='utf-8') if spec.get('sourcestats') else '',
        authdata_text=(root / spec.get('authdata', '')).read_text(encoding='utf-8') if spec.get('authdata') else '',
        ntpdata_text=(root / spec.get('ntpdata', '')).read_text(encoding='utf-8') if spec.get('ntpdata') else '',
        collected_at=case['collected_at'],
    )
    return chrony_adapter.evaluate(obs, profile_id=case.get('profile_id', chrony_adapter.SUPPORTED_PROFILE), evaluated_at=case['evaluated_at'])


def _build_ntpq(case: dict[str, Any], root: Path) -> dict[str, Any]:
    spec = case['ntpq']
    obs = ntpq_adapter.build_observation(
        readvar_text=(root / spec['readvar']).read_text(encoding='utf-8'),
        peers_text=(root / spec.get('peers', '')).read_text(encoding='utf-8') if spec.get('peers') else '',
        collected_at=case['collected_at'],
    )
    return ntpq_adapter.evaluate(obs, profile_id=case.get('profile_id', ntpq_adapter.SUPPORTED_PROFILE), evaluated_at=case['evaluated_at'])


def run_case(case: dict[str, Any], *, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    cid = case.get('id', '<no-id>')
    try:
        chrony_bundle = _build_chrony(case, root)
        ntpq_bundle = _build_ntpq(case, root)
    except Exception as exc:  # noqa: BLE001
        return [f'{cid}: unexpected adapter-equivalence setup/evaluation error: {exc}']
    chrony = _summary(chrony_bundle)
    ntpq = _summary(ntpq_bundle)
    decimal_keys = {'total_interval_bound_seconds', 'total_interval_bound_ms', 'collection_age_seconds'}
    for key in sorted(chrony):
        if key in decimal_keys:
            if Decimal(str(chrony[key])) != Decimal(str(ntpq[key])):
                errors.append(f'{cid}: chrony/ntpq mismatch for {key}: {chrony[key]!r} != {ntpq[key]!r}')
            continue
        if chrony[key] != ntpq[key]:
            errors.append(f'{cid}: chrony/ntpq mismatch for {key}: {chrony[key]!r} != {ntpq[key]!r}')
    for key, expected in case.get('expect', {}).items():
        actual = chrony.get(key)
        if key in {'total_interval_bound_seconds', 'total_interval_bound_ms', 'collection_age_seconds'}:
            if Decimal(str(actual)) != Decimal(str(expected)):
                errors.append(f'{cid}: expected {key}={expected!r}, got {actual!r}')
        elif actual != expected:
            errors.append(f'{cid}: expected {key}={expected!r}, got {actual!r}')
    return errors


def self_test(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    errors.extend(f'ntp_bound: {e}' for e in ntp_bound_self_test())
    try:
        import yaml  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return [f'PyYAML unavailable for adapter equivalence tests: {exc}']
    try:
        cases = yaml.safe_load((root / 'tests/adapter-equivalence.yaml').read_text(encoding='utf-8'))
    except Exception as exc:  # noqa: BLE001
        return [f'cannot load adapter equivalence tests: {exc}']
    if not isinstance(cases, list) or not cases:
        return ['tests/adapter-equivalence.yaml must be a non-empty list']
    for case in cases:
        if not isinstance(case, dict):
            errors.append('adapter equivalence case is not an object')
            continue
        errors.extend(run_case(case, root=root))
    return errors


def generate_example(root: Path = ROOT) -> dict[str, Any]:
    """Return the local-assessed-state for the first equivalence case."""
    import yaml  # type: ignore
    cases = yaml.safe_load((root / 'tests/adapter-equivalence.yaml').read_text(encoding='utf-8'))
    if not isinstance(cases, list) or not cases or not isinstance(cases[0], dict):
        raise ValueError('adapter equivalence cases unavailable')
    return _build_chrony(cases[0], root)['local_assessed_state']


def main() -> int:
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        return 1
    print('TimeSync adapter equivalence self-test passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

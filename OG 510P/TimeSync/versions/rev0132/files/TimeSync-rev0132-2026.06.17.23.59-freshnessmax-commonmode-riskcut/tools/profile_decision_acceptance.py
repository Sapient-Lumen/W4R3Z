#!/usr/bin/env python3
"""Executable profile-decision acceptance tests for the chrony P1 risk cut.

The older acceptance-test list is useful as a narrative checklist, but it does
not execute decisions.  This runner exercises boundary cases at the profile lane
thresholds through the real adapter and independently replays the typed
observation evaluator.  It is deliberately focused on the chrony/P1 vertical
slice opened by FT-0121.
"""
from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path
import sys
from typing import Any

sys.dont_write_bytecode = True

from chrony_adapter import build_observation, evaluate as primary_evaluate
from chrony_observation_eval import evaluate_observation as independent_evaluate

ROOT = Path(__file__).resolve().parents[1]
TESTS_REL = 'tests/profile-decision-acceptance.yaml'


def _load_yaml(root: Path) -> list[dict[str, Any]]:
    try:
        import yaml  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f'PyYAML unavailable for profile-decision acceptance tests: {exc}') from exc
    data = yaml.safe_load((root / TESTS_REL).read_text(encoding='utf-8'))
    if not isinstance(data, list) or not data:
        raise RuntimeError(f'{TESTS_REL} must be a non-empty list')
    cases: list[dict[str, Any]] = []
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise RuntimeError(f'{TESTS_REL} case #{index} must be an object')
        cases.append(item)
    return cases


def _case_bundle(case: dict[str, Any], root: Path) -> dict[str, Any]:
    tracking_text = (root / case['tracking']).read_text(encoding='utf-8')
    sources_text = (root / case['sources']).read_text(encoding='utf-8') if case.get('sources') else ''
    observation = build_observation(
        tracking_text=tracking_text,
        sources_text=sources_text,
        collected_at=case['collected_at'],
    )
    return primary_evaluate(
        observation,
        profile_id=case.get('profile_id', 'P1-general-computing'),
        evaluated_at=case['evaluated_at'],
    )


def _actuals(bundle: dict[str, Any]) -> dict[str, Any]:
    state = bundle['local_assessed_state']
    ts = state['timestate']
    assessment = state['profile_assessments'][0]
    pa = assessment.get('policy_acceptance', {})
    summary = assessment.get('evaluation_summary', {})
    explanation = bundle['explanation']
    return {
        'profile_conformance': assessment.get('profile_conformance'),
        'applicability': assessment.get('applicability'),
        'policy_status': pa.get('status'),
        'actionability': pa.get('actionability'),
        'regime': ts.get('regime'),
        'source_posture': ts.get('source_posture'),
        'fallback_mapping': summary.get('fallback_mapping'),
        'collection_age_seconds': explanation.get('collection_age_seconds'),
        'total_interval_bound_ms': explanation.get('total_interval_bound_ms'),
    }


def _compare_expectations(case: dict[str, Any], actual: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    cid = case.get('id', '<no-id>')
    expected = case.get('expect')
    if not isinstance(expected, dict):
        return [f'{cid}: expect must be an object']
    for key, value in expected.items():
        got = actual.get(key)
        if key == 'max_bound_ms_lte':
            if Decimal(str(actual.get('total_interval_bound_ms'))) > Decimal(str(value)):
                errors.append(f'{cid}: expected total_interval_bound_ms <= {value}, got {actual.get("total_interval_bound_ms")}')
        elif got != value:
            errors.append(f'{cid}: expected {key}={value!r}, got {got!r}')
    return errors


def _required_boundary_coverage(cases: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    by_id = {case.get('id') for case in cases}
    required = {
        'PDA-125-001',
        'PDA-125-002',
        'PDA-125-003',
        'PDA-125-004',
        'PDA-125-005',
        'PDA-125-006',
        'PDA-125-007',
    }
    missing = sorted(required - by_id)
    if missing:
        errors.append(f'{TESTS_REL} missing required rev0125 boundary cases: {missing}')
    return errors


def self_test(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        cases = _load_yaml(root)
    except Exception as exc:  # noqa: BLE001
        return [str(exc)]
    seen: set[str] = set()
    for case in cases:
        cid = case.get('id')
        if not isinstance(cid, str) or not cid:
            errors.append('profile-decision acceptance case missing id')
        elif cid in seen:
            errors.append(f'duplicate profile-decision acceptance id: {cid}')
        seen.add(cid)
    errors.extend(_required_boundary_coverage(cases))
    for case in cases:
        cid = case.get('id', '<no-id>')
        try:
            primary = _case_bundle(case, root)
            secondary = independent_evaluate(
                primary['chrony_observation'],
                profile_id=case.get('profile_id', 'P1-general-computing'),
                evaluated_at=case['evaluated_at'],
                root=root,
            )
        except Exception as exc:  # noqa: BLE001
            errors.append(f'{cid}: decision acceptance execution failed: {exc}')
            continue
        if secondary.get('local_assessed_state') != primary.get('local_assessed_state'):
            errors.append(f'{cid}: independent evaluator state mismatch')
        errors.extend(_compare_expectations(case, _actuals(primary)))
    return errors


def main() -> int:
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        return 1
    print('TimeSync profile-decision acceptance tests passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

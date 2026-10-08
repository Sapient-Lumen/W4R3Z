#!/usr/bin/env python3
"""Machine-readable P1 chrony policy loader and decision helper.

This module is intentionally small: it turns evaluator/p1-chrony-policy.json into
Decimal thresholds and applies the lane table.  It does not parse chrony text,
compute clock-error bounds, or mutate TimeState.  The goal is to remove hidden
threshold literals from the adapter while keeping the real observation and
interval arithmetic in the adapter/evaluator layers.
"""
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import sys
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
POLICY_REL = 'evaluator/p1-chrony-policy.json'
SUPPORTED_PROFILE = 'P1-general-computing'


class ChronyPolicyError(ValueError):
    """Raised when the machine-readable chrony policy is malformed."""


def _decimal(value: Any, *, label: str) -> Decimal:
    if isinstance(value, bool):
        raise ChronyPolicyError(f'{label} must be decimal-like, not boolean')
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ChronyPolicyError(f'{label} must be decimal-like: {value!r}') from exc
    if parsed < 0:
        raise ChronyPolicyError(f'{label} must be non-negative')
    return parsed


def _int(value: Any, *, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ChronyPolicyError(f'{label} must be an integer')
    return value


def validate_policy_document(policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(policy, dict):
        return ['chrony policy must be an object']
    if policy.get('policy_document_type') != 'timesync_chrony_p1_policy_v1':
        errors.append('policy_document_type must be timesync_chrony_p1_policy_v1')
    adapter_ids = policy.get('adapter_policy_ids')
    if adapter_ids is not None:
        if not isinstance(adapter_ids, dict):
            errors.append('adapter_policy_ids must be an object when present')
        else:
            for adapter in ('chrony', 'ntpq'):
                value = adapter_ids.get(adapter)
                if not isinstance(value, str) or not value.startswith(f'timesync-reference-evaluator:P1-{adapter}'):
                    errors.append(f'adapter_policy_ids.{adapter} must be a P1 {adapter} policy id')
    if policy.get('profile_id') != SUPPORTED_PROFILE:
        errors.append(f'profile_id must be {SUPPORTED_PROFILE}')
    if policy.get('target_applicability') != 'security_sensitive_time':
        errors.append('target_applicability must be security_sensitive_time')
    fail_closed = policy.get('fail_closed_when')
    if not isinstance(fail_closed, dict):
        errors.append('fail_closed_when must be an object')
    else:
        try:
            stratum_min = _int(fail_closed.get('stratum_min'), label='fail_closed_when.stratum_min')
            stratum_max = _int(fail_closed.get('stratum_max'), label='fail_closed_when.stratum_max')
            if not (1 <= stratum_min <= stratum_max <= 15):
                errors.append('fail_closed_when stratum range must be within 1..15 and ordered')
        except ChronyPolicyError as exc:
            errors.append(str(exc))
        if fail_closed.get('leap_status_must_equal') != 'Normal':
            errors.append('fail_closed_when.leap_status_must_equal must be Normal')
        if not isinstance(fail_closed.get('reason'), str) or not fail_closed.get('reason'):
            errors.append('fail_closed_when.reason must be a non-empty string')

    lanes = policy.get('lanes')
    expected_names = ['security_sensitive_time', 'coarse_logging', 'display_time']
    if not isinstance(lanes, list) or len(lanes) != 3:
        errors.append('lanes must contain exactly the security, logging, and display entries')
        lanes = []
    seen_names: list[str] = []
    prior_error = Decimal('-1')
    prior_age = Decimal('-1')
    for index, lane in enumerate(lanes):
        if not isinstance(lane, dict):
            errors.append(f'lane #{index + 1} must be an object')
            continue
        name = lane.get('name')
        seen_names.append(name if isinstance(name, str) else '<invalid>')
        if index < len(expected_names) and name != expected_names[index]:
            errors.append(f'lane #{index + 1} must be {expected_names[index]}')
        conformance = lane.get('profile_conformance')
        if index == 0 and conformance != 'satisfied':
            errors.append('security lane must be satisfied conformance')
        if index > 0 and conformance != 'fallback':
            errors.append(f'{name}: fallback lane must use fallback conformance')
        status = lane.get('policy_status')
        actionability = lane.get('actionability')
        if conformance == 'satisfied' and (status, actionability) != ('accepted', 'actionable'):
            errors.append(f'{name}: satisfied lane must be accepted/actionable')
        if conformance == 'fallback' and (status, actionability) != ('accepted_with_conditions', 'conditional'):
            errors.append(f'{name}: fallback lane must be accepted_with_conditions/conditional')
        if lane.get('applicability') != name:
            errors.append(f'{name}: lane applicability must match lane name')
        try:
            max_error = _decimal(lane.get('max_error_ms'), label=f'{name}.max_error_ms')
            max_age = _decimal(lane.get('max_age_seconds'), label=f'{name}.max_age_seconds')
            if max_error <= prior_error:
                errors.append(f'{name}: max_error_ms must strictly increase by weaker lane')
            if max_age <= prior_age:
                errors.append(f'{name}: max_age_seconds must strictly increase by weaker lane')
            prior_error = max_error
            prior_age = max_age
        except ChronyPolicyError as exc:
            errors.append(str(exc))
        if not isinstance(lane.get('reason'), str) or not lane.get('reason'):
            errors.append(f'{name}: reason must be a non-empty string')
    if seen_names and seen_names != expected_names:
        errors.append(f'lane order must be {expected_names}, got {seen_names}')

    unsatisfied = policy.get('unsatisfied')
    if not isinstance(unsatisfied, dict):
        errors.append('unsatisfied must be an object')
    else:
        if unsatisfied.get('profile_conformance') != 'unsatisfied':
            errors.append('unsatisfied.profile_conformance must be unsatisfied')
        if unsatisfied.get('applicability') != 'diagnostic_local_only':
            errors.append('unsatisfied.applicability must be diagnostic_local_only')
        if unsatisfied.get('policy_status') != 'rejected':
            errors.append('unsatisfied.policy_status must be rejected')
        if unsatisfied.get('actionability') != 'not_actionable':
            errors.append('unsatisfied.actionability must be not_actionable')
        for key in ('regime_when_leap_or_stratum_failed', 'regime_when_thresholds_failed', 'reason', 'missing_item'):
            if not isinstance(unsatisfied.get(key), str) or not unsatisfied.get(key):
                errors.append(f'unsatisfied.{key} must be a non-empty string')
    return errors


def load_p1_policy(root: Path = ROOT) -> dict[str, Any]:
    path = root / POLICY_REL
    try:
        policy = json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:  # noqa: BLE001
        raise ChronyPolicyError(f'cannot load {POLICY_REL}: {exc}') from exc
    errors = validate_policy_document(policy)
    if errors:
        raise ChronyPolicyError('; '.join(errors))
    parsed = deepcopy(policy)
    for lane in parsed['lanes']:
        lane['max_error_ms'] = _decimal(lane['max_error_ms'], label=f'{lane["name"]}.max_error_ms')
        lane['max_age_seconds'] = _decimal(lane['max_age_seconds'], label=f'{lane["name"]}.max_age_seconds')
    return parsed


def decide_p1_lane(
    policy: dict[str, Any],
    *,
    bound_ms: Decimal,
    age_seconds: Decimal,
    source_posture: str,
    leap_normal: bool,
    stratum_usable: bool,
) -> dict[str, Any]:
    """Return the P1 decision row for a chrony-derived observation.

    Caller supplies already-computed bound and observation posture; this function
    only applies the machine-readable lane table. Boundaries are inclusive: a
    capture at exactly the lane's maximum age or error remains in that lane.
    """
    if not leap_normal or not stratum_usable:
        unsatisfied = policy['unsatisfied']
        return {
            'profile_conformance': unsatisfied['profile_conformance'],
            'applicability': unsatisfied['applicability'],
            'policy_status': unsatisfied['policy_status'],
            'actionability': unsatisfied['actionability'],
            'fallback_mapping': None,
            'regime': unsatisfied['regime_when_leap_or_stratum_failed'],
            'reason': policy['fail_closed_when']['reason'],
            'max_staleness_ms': Decimal('0'),
            'missing_item': unsatisfied['missing_item'],
        }

    previous_max_age: Decimal | None = None
    if source_posture != 'unknown':
        for lane in policy['lanes']:
            if bound_ms <= lane['max_error_ms'] and age_seconds <= lane['max_age_seconds']:
                if lane['profile_conformance'] == 'satisfied':
                    regime = lane['regime_when_selected']
                else:
                    regime = 'holdover' if previous_max_age is not None and age_seconds > previous_max_age else 'degraded'
                return {
                    'profile_conformance': lane['profile_conformance'],
                    'applicability': lane['applicability'],
                    'policy_status': lane['policy_status'],
                    'actionability': lane['actionability'],
                    'fallback_mapping': lane.get('fallback_mapping'),
                    'regime': regime,
                    'reason': lane['reason'],
                    'max_staleness_ms': lane['max_age_seconds'] * Decimal('1000'),
                    'missing_item': None,
                }
            previous_max_age = lane['max_age_seconds']

    unsatisfied = policy['unsatisfied']
    final_age = policy['lanes'][-1]['max_age_seconds']
    return {
        'profile_conformance': unsatisfied['profile_conformance'],
        'applicability': unsatisfied['applicability'],
        'policy_status': unsatisfied['policy_status'],
        'actionability': unsatisfied['actionability'],
        'fallback_mapping': None,
        'regime': unsatisfied['regime_when_thresholds_failed'],
        'reason': unsatisfied['reason'],
        'max_staleness_ms': final_age * Decimal('1000'),
        'missing_item': unsatisfied['missing_item'],
    }


def policy_reference(policy: dict[str, Any], revision: str, *, adapter_family: str = 'chrony') -> str:
    adapter_ids = policy.get('adapter_policy_ids')
    if isinstance(adapter_ids, dict) and isinstance(adapter_ids.get(adapter_family), str):
        return f'{adapter_ids[adapter_family]}-{revision}'
    if adapter_family == 'chrony':
        return f'{policy["policy_id"]}-{revision}'
    return f'{policy["policy_id"]}-{adapter_family}-{revision}'


def self_test(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        policy = load_p1_policy(root)
    except Exception as exc:  # noqa: BLE001
        return [f'chrony policy could not be loaded: {exc}']
    if decide_p1_lane(policy, bound_ms=Decimal('50'), age_seconds=Decimal('300'), source_posture='single_source', leap_normal=True, stratum_usable=True)['profile_conformance'] != 'satisfied':
        errors.append('chrony policy rejected exact satisfied age boundary')
    if decide_p1_lane(policy, bound_ms=Decimal('50'), age_seconds=Decimal('300.000000001'), source_posture='single_source', leap_normal=True, stratum_usable=True)['applicability'] != 'coarse_logging':
        errors.append('chrony policy failed to drop to coarse_logging one nanosecond after security age boundary')
    if decide_p1_lane(policy, bound_ms=Decimal('50'), age_seconds=Decimal('3600.000000001'), source_posture='single_source', leap_normal=True, stratum_usable=True)['applicability'] != 'display_time':
        errors.append('chrony policy failed to drop to display_time one nanosecond after logging age boundary')
    if decide_p1_lane(policy, bound_ms=Decimal('50'), age_seconds=Decimal('86400.000000001'), source_posture='single_source', leap_normal=True, stratum_usable=True)['profile_conformance'] != 'unsatisfied':
        errors.append('chrony policy accepted one nanosecond after display age boundary')
    if decide_p1_lane(policy, bound_ms=Decimal('50'), age_seconds=Decimal('1'), source_posture='unknown', leap_normal=True, stratum_usable=True)['profile_conformance'] != 'unsatisfied':
        errors.append('chrony policy accepted unknown source posture')
    bad = deepcopy(policy)
    bad['lanes'][1]['max_age_seconds'] = '10'
    if not any('max_age_seconds' in error for error in validate_policy_document(bad)):
        errors.append('chrony policy validation accepted a fallback lane with lower max_age_seconds')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync chrony P1 policy self-test passed.')

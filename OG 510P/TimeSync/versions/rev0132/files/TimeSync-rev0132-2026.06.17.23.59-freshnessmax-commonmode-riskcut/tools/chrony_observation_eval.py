#!/usr/bin/env python3
"""Independent evaluator for chrony_observation JSON.

This module intentionally does not parse chronyc text and intentionally does not
import tools/chrony_adapter.py.  Its job is narrower: consume the typed
`chrony_observation` JSON boundary emitted by the adapter, independently
recompute interval/source-posture facts, and apply the shared machine-readable
P1 policy artifact.  The self-test compares the second implementation against
the adapter outputs for the replay golden suite.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from fractions import Fraction
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

sys.dont_write_bytecode = True

from temporal_coherence import parse_dt
from chrony_policy import decide_p1_lane, load_p1_policy, policy_reference
from ntp_bound import (
    conservative_ntp_error_bound,
    interval_for_bound as common_interval_for_bound,
    milliseconds as common_milliseconds,
)

ROOT = Path(__file__).resolve().parents[1]
NS_PER_SECOND = 1_000_000_000
SUPPORTED_PROFILE = 'P1-general-computing'

class IndependentEvaluationError(ValueError):
    """Raised when an observation cannot be independently evaluated."""


def _current_revision(root: Path = ROOT) -> str:
    try:
        receipt = json.loads((root / 'REVISION-RECEIPT.json').read_text(encoding='utf-8'))
        revision = receipt.get('revision')
    except Exception:  # noqa: BLE001
        revision = None
    return revision if isinstance(revision, str) else 'rev0000'


def _parse_instant_seconds(value: str, *, label: str) -> Fraction:
    try:
        parsed = parse_dt(value)
    except Exception as exc:  # noqa: BLE001
        raise IndependentEvaluationError(f'{label} must be RFC 3339 with explicit offset: {exc}') from exc
    return Fraction(parsed.epoch_second, 1) + parsed.fractional_second


def _ceil_fraction_to_ns(value: Fraction) -> int:
    return -((-value.numerator * NS_PER_SECOND) // value.denominator)


def _floor_fraction_to_ns(value: Fraction) -> int:
    return (value.numerator * NS_PER_SECOND) // value.denominator


def _format_epoch_ns(epoch_ns: int) -> str:
    seconds, nanos = divmod(epoch_ns, NS_PER_SECOND)
    dt = datetime.fromtimestamp(seconds, tz=timezone.utc)
    frac = '' if nanos == 0 else f'.{nanos:09d}'.rstrip('0')
    return dt.strftime('%Y-%m-%dT%H:%M:%S') + frac + 'Z'


def _fraction_to_decimal(value: Fraction) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def _decimal_seconds_to_fraction(value: Decimal) -> Fraction:
    return Fraction(value)


def _milliseconds(value: Decimal) -> Decimal:
    return common_milliseconds(value)


def _decimal(value: Any, *, label: str) -> Decimal:
    if isinstance(value, bool):
        raise IndependentEvaluationError(f'{label} must be decimal-like, not boolean')
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise IndependentEvaluationError(f'{label} must be decimal-like: {value!r}') from exc


def _int(value: Any, *, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise IndependentEvaluationError(f'{label} must be an integer')
    return value


def _str(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise IndependentEvaluationError(f'{label} must be a non-empty string')
    return value


def _tracking(observation: dict[str, Any]) -> dict[str, Any]:
    tracking = observation.get('tracking')
    if not isinstance(tracking, dict):
        raise IndependentEvaluationError('chrony_observation.tracking must be an object')
    required = {
        'reference_id',
        'stratum',
        'ref_time_utc',
        'system_time_offset_seconds',
        'skew_ppm',
        'root_delay_seconds',
        'root_dispersion_seconds',
        'leap_status',
    }
    missing = sorted(required - set(tracking))
    if missing:
        raise IndependentEvaluationError(f'chrony_observation.tracking missing required field(s): {", ".join(missing)}')
    return tracking


def _sources_summary(observation: dict[str, Any]) -> dict[str, Any]:
    summary = observation.get('sources_summary')
    if summary is None:
        return {}
    if not isinstance(summary, dict):
        raise IndependentEvaluationError('chrony_observation.sources_summary must be an object when present')
    return summary


def _authentication_summary(observation: dict[str, Any]) -> dict[str, Any]:
    summary = observation.get('authentication_summary')
    if summary is None:
        return {
            'reported_packet_authentication': 'not_observed',
            'verification_status': 'not_cryptographically_verified_by_timesync',
            'used_for_decision': False,
            'profile_strengthening': 'none',
        }
    if not isinstance(summary, dict):
        raise IndependentEvaluationError('chrony_observation.authentication_summary must be an object when present')
    if summary.get('used_for_decision') is not False:
        raise IndependentEvaluationError('chrony_observation.authentication_summary.used_for_decision must be false for this evaluator')
    if summary.get('verification_status') != 'not_cryptographically_verified_by_timesync':
        raise IndependentEvaluationError('chrony authentication diagnostics cannot claim TimeSync cryptographic verification')
    return summary


def load_profile_catalog(root: Path = ROOT) -> dict[str, Any]:
    return json.loads((root / 'profiles/profile-catalog.json').read_text(encoding='utf-8'))


def find_profile(catalog: dict[str, Any], profile_id: str) -> dict[str, Any]:
    for profile in catalog.get('profiles', []):
        if profile.get('id') == profile_id:
            return profile
    raise IndependentEvaluationError(f'profile not found in catalog: {profile_id}')


def profile_ref(profile: dict[str, Any]) -> dict[str, Any]:
    ref = {
        'authority': profile.get('authority'),
        'id': profile['id'],
        'version': profile.get('version', '1.0.0'),
    }
    digest = profile.get('normative_rules_digest')
    if isinstance(digest, dict):
        ref['digest'] = digest
    return ref


def source_posture(observation: dict[str, Any]) -> str:
    tracking = _tracking(observation)
    leap_status = _str(tracking.get('leap_status'), label='tracking.leap_status')
    stratum = _int(tracking.get('stratum'), label='tracking.stratum')
    if leap_status != 'Normal' or stratum <= 0:
        return 'unknown'
    summary = _sources_summary(observation)
    selected = _int(summary.get('selected_sources', 0), label='sources_summary.selected_sources') if 'selected_sources' in summary else 0
    combined = _int(summary.get('combined_sources', 0), label='sources_summary.combined_sources') if 'combined_sources' in summary else 0
    reference_id = _str(tracking.get('reference_id'), label='tracking.reference_id')
    if selected + combined >= 2:
        return 'multi_source_agreement'
    if selected >= 1 or reference_id not in {'00000000 ()', '00000000'}:
        return 'single_source'
    return 'unknown'


def chrony_bound_seconds(observation: dict[str, Any], *, evaluated_at: str) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    tracking = _tracking(observation)
    bound = conservative_ntp_error_bound(
        system_time_offset_seconds=_decimal(tracking.get('system_time_offset_seconds'), label='tracking.system_time_offset_seconds'),
        root_delay_seconds=_decimal(tracking.get('root_delay_seconds'), label='tracking.root_delay_seconds'),
        root_dispersion_seconds=_decimal(tracking.get('root_dispersion_seconds'), label='tracking.root_dispersion_seconds'),
        rate_error_ppm=_decimal(tracking.get('skew_ppm'), label='tracking.skew_ppm'),
        collected_at=_str(observation.get('collected_at'), label='chrony_observation.collected_at'),
        evaluated_at=evaluated_at,
        error_cls=IndependentEvaluationError,
    )
    return bound.base_bound_seconds, bound.age_seconds, bound.holdover_growth_seconds, bound.total_bound_seconds


def interval_for_bound(effective_at: str, total_bound_seconds: Decimal) -> dict[str, str]:
    return common_interval_for_bound(effective_at, total_bound_seconds, error_cls=IndependentEvaluationError)

def _source_diversity_hook(source_posture_value: str) -> dict[str, str]:
    if source_posture_value == 'multi_source_agreement':
        return {
            'dependency_class': 'multiple_sources_same_root',
            'common_mode_risk': 'possible_common_mode',
            'assessment_basis': 'local_measurement_summary',
            'evidence_posture': 'assessed',
            'export_detail': 'summary_only',
            'note': 'chronyc sources shows multiple usable rows, but independence of upstream roots is not proven',
        }
    if source_posture_value == 'single_source':
        return {
            'dependency_class': 'single_source',
            'common_mode_risk': 'not_assessed',
            'assessment_basis': 'local_measurement_summary',
            'evidence_posture': 'assessed',
            'export_detail': 'summary_only',
            'note': 'single selected source or only tracking reference observed',
        }
    return {
        'dependency_class': 'unknown',
        'common_mode_risk': 'unknown',
        'assessment_basis': 'unknown',
        'evidence_posture': 'unknown',
        'export_detail': 'summary_only',
        'note': 'source selection was unusable or unavailable',
    }


def _authentication_hook(summary: dict[str, Any]) -> dict[str, Any]:
    reported = summary.get('reported_packet_authentication', 'not_observed') if isinstance(summary, dict) else 'not_observed'
    if reported == 'chrony_reported_authentication_present':
        evidence_posture = 'reported_not_verified'
        note = 'chrony reports authenticated NTP evidence, but TimeSync did not verify NTS-KE, certificates, AEAD tags, cookies, symmetric keys, or packet transcripts; no TimeState or profile decision is strengthened.'
    elif reported == 'chrony_reported_authentication_absent':
        evidence_posture = 'reported_not_verified'
        note = 'chrony reports no authenticated NTP measurements for the retained ntpdata/authdata evidence; profile decisions remain based on conservative timing bounds only.'
    else:
        evidence_posture = 'not_observed'
        note = 'no chrony authdata/ntpdata diagnostics were supplied; authentication remains unsupported by this evaluator.'
    return {
        'packet_authentication': reported,
        'evidence_posture': evidence_posture,
        'verified_by_timesync': False,
        'used_for_decision': False,
        'profile_strengthening': 'none',
        'note': note,
    }


def _safe_id_time(value: str) -> str:
    return re.sub(r'[^0-9A-Za-z]', '', value.replace('Z', 'UTC'))


def evaluate_observation(
    observation: dict[str, Any],
    *,
    profile_id: str = SUPPORTED_PROFILE,
    evaluated_at: str,
    catalog: dict[str, Any] | None = None,
    root: Path = ROOT,
) -> dict[str, Any]:
    if profile_id != SUPPORTED_PROFILE:
        raise IndependentEvaluationError(f'independent chrony evaluator currently supports only {SUPPORTED_PROFILE}')
    if not isinstance(observation, dict):
        raise IndependentEvaluationError('chrony_observation must be an object')
    tracking = _tracking(observation)
    catalog = catalog or load_profile_catalog(root)
    profile = find_profile(catalog, profile_id)
    base_bound, age, growth, total_bound = chrony_bound_seconds(observation, evaluated_at=evaluated_at)
    bound_ms = _milliseconds(total_bound)
    sp = source_posture(observation)
    auth_summary = _authentication_summary(observation)
    auth_hook = _authentication_hook(auth_summary)
    leap_status = _str(tracking.get('leap_status'), label='tracking.leap_status')
    stratum = _int(tracking.get('stratum'), label='tracking.stratum')
    leap_normal = leap_status == 'Normal'
    stratum_usable = 1 <= stratum <= 15

    policy = load_p1_policy(root)
    decision = decide_p1_lane(
        policy,
        bound_ms=bound_ms,
        age_seconds=age,
        source_posture=sp,
        leap_normal=leap_normal,
        stratum_usable=stratum_usable,
    )
    conformance = decision['profile_conformance']
    applicability = decision['applicability']
    actionability = decision['actionability']
    policy_status = decision['policy_status']
    fallback_mapping = decision['fallback_mapping']
    regime = decision['regime']
    reason = decision['reason']
    max_staleness_ms = decision['max_staleness_ms']

    rev = _current_revision(root)
    interval = interval_for_bound(evaluated_at, total_bound)
    assessment_id = f'assess-{profile_id}-chrony-{_safe_id_time(evaluated_at)}'
    evaluation_summary: dict[str, Any] = {'matched_profile_catalog': True}
    if fallback_mapping is not None:
        evaluation_summary['fallback_mapping'] = fallback_mapping
    if conformance == 'unsatisfied':
        evaluation_summary['missing_items'] = [decision['missing_item']]

    ref_time_utc = _str(tracking.get('ref_time_utc'), label='tracking.ref_time_utc')
    skew_ppm = _decimal(tracking.get('skew_ppm'), label='tracking.skew_ppm')
    local_assessed_state = {
        'timestate': {
            'interval': interval,
            'timescale': 'UTC',
            'freshness': {
                'last_discipline': ref_time_utc,
                'max_staleness_ms': float(max_staleness_ms),
                'profile_expression': f'{rev} P1 chrony replay/capture policy',
            },
            'regime': regime,
            'source_posture': sp,
            'applicability': applicability,
        },
        'extension_hooks': {
            'traceability_posture': {
                'reference_anchor': 'utc_unqualified',
                'evidence_posture': 'claimed',
            },
            'sync_dimension': 'time',
            'time_error_bound': {
                'bound_ms': float(bound_ms),
                'confidence': 'conservative_chrony_tracking_bound_plus_skew_growth',
                'basis': 'abs(system_time_offset)+root_dispersion+0.5*max(root_delay,0) + skew_ppm*age',
            },
            'rate_error_bound': {
                'bound_ppb': float(skew_ppm * Decimal('1000')),
                'confidence': 'chrony_reported_skew',
                'basis': 'chronyc tracking Skew field',
            },
            'timescale_realization': {
                'scale': 'UTC',
                'realization': 'chrony-reported-UTC-unqualified',
                'leap_handling': 'standard_utc' if leap_normal else 'unknown',
                'tai_utc_offset_state': 'unknown',
                'evidence_posture': 'claimed',
                'note': 'chronyc tracking reports UTC but this adapter does not verify a named UTC realization or leap-smear policy',
            },
            'clock_continuity_posture': {
                'backward_step_policy': 'unknown',
                'smear_policy': 'none' if leap_normal else 'unknown',
                'monotonic_local_time': 'not_claimed',
                'evidence_posture': 'unknown',
                'note': 'chronyc tracking does not prove monotonic application-time behavior',
            },
            'source_diversity_posture': _source_diversity_hook(sp),
            'authentication_posture': auth_hook,
        },
        'profile_assessments': [
            {
                'assessment_time': evaluated_at,
                'assessed_profile': profile_ref(profile),
                'profile_conformance': conformance,
                'applicability': applicability,
                'profile_lifecycle_state': profile.get('lifecycle_state', 'unknown'),
                'policy_acceptance': {
                    'status': policy_status,
                    'checked_at': evaluated_at,
                    'policy_reference': policy_reference(policy, rev),
                    'reason': reason,
                    'actionability': actionability,
                },
                'evaluation_summary': evaluation_summary,
                'assessment_id': assessment_id,
                'note': 'Generated by tools/chrony_adapter.py from chronyc tracking/sources replay input.',
            }
        ],
    }

    explanation = {
        'explanation_type': 'timesync_chrony_reference_evaluation_v1',
        'profile_id': profile_id,
        'evaluated_at': evaluated_at,
        'collection_age_seconds': str(age),
        'chrony_clock_error_formula': 'abs(system_time_offset_seconds) + root_dispersion_seconds + 0.5 * max(root_delay_seconds, 0)',
        'base_bound_seconds': str(base_bound),
        'holdover_growth_seconds': str(growth),
        'total_interval_bound_seconds': str(total_bound),
        'total_interval_bound_ms': str(bound_ms),
        'system_time_offset_sign_used_to_shift_interval': False,
        'source_posture_rule_result': sp,
        'authentication_rule_result': auth_hook,
        'decision': {
            'profile_conformance': conformance,
            'applicability': applicability,
            'actionability': actionability,
            'reason': reason,
        },
        'unsupported_or_not_verified': [
            'named UTC realization traceability',
            'negative root delay interpreted conservatively as zero delay contribution',
            'chrony-reported NTS or symmetric-key authentication was not independently verified by TimeSync',
            'leap-smear detection',
            'application monotonic clock guarantee',
            'PTP or non-chrony NTP implementations',
        ],
        'input_observation': observation,
    }
    return {
        'chrony_observation': observation,
        'local_assessed_state': local_assessed_state,
        'explanation': explanation,
    }


def _adapter_bundle_for_case(case: dict[str, Any], *, root: Path) -> dict[str, Any]:
    args = [
        sys.executable,
        str(root / 'tools/chrony_adapter.py'),
    ]
    if case.get('capture'):
        args.extend(['--capture', str(root / case['capture'])])
        if case.get('collected_at'):
            args.extend(['--collected-at', case['collected_at']])
    else:
        args.extend([
            '--tracking',
            str(root / case['tracking']),
            '--collected-at',
            case['collected_at'],
        ])
        if case.get('sources'):
            args.extend(['--sources', str(root / case['sources'])])
        if case.get('sourcestats'):
            args.extend(['--sourcestats', str(root / case['sourcestats'])])
    args.extend([
        '--evaluated-at',
        case['evaluated_at'],
        '--profile-id',
        case.get('profile_id', SUPPORTED_PROFILE),
        '--output',
        'bundle',
    ])
    completed = subprocess.run(args, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if completed.returncode != 0:
        raise IndependentEvaluationError(f'adapter command failed for {case.get("id")}: {completed.stderr.strip() or completed.stdout.strip()}')
    return json.loads(completed.stdout)


def _compare_case(case: dict[str, Any], *, root: Path) -> list[str]:
    cid = case.get('id', '<no-id>')
    if case.get('expect_error_contains'):
        return []
    errors: list[str] = []
    try:
        primary = _adapter_bundle_for_case(case, root=root)
        secondary = evaluate_observation(
            primary['chrony_observation'],
            profile_id=case.get('profile_id', SUPPORTED_PROFILE),
            evaluated_at=case['evaluated_at'],
            root=root,
        )
    except Exception as exc:  # noqa: BLE001
        return [f'{cid}: independent evaluation crashed: {exc}']
    if secondary.get('local_assessed_state') != primary.get('local_assessed_state'):
        errors.append(f'{cid}: independent local_assessed_state does not match adapter output')
    for key in (
        'collection_age_seconds',
        'chrony_clock_error_formula',
        'base_bound_seconds',
        'holdover_growth_seconds',
        'total_interval_bound_seconds',
        'total_interval_bound_ms',
        'system_time_offset_sign_used_to_shift_interval',
        'source_posture_rule_result',
        'decision',
    ):
        if secondary.get('explanation', {}).get(key) != primary.get('explanation', {}).get(key):
            errors.append(f'{cid}: explanation.{key} mismatch')
    return errors


def _no_code_imports_adapter() -> list[str]:
    errors: list[str] = []
    for lineno, line in enumerate(Path(__file__).read_text(encoding='utf-8').splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith('import chrony_adapter') or stripped.startswith('from chrony_adapter import'):
            errors.append(f'chrony_observation_eval.py must not code-import chrony_adapter (line {lineno})')
    return errors


def self_test(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    errors.extend(_no_code_imports_adapter())
    try:
        import yaml  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return [f'PyYAML unavailable for independent chrony evaluator tests: {exc}']
    try:
        cases = yaml.safe_load((root / 'tests/chrony-adapter-golden.yaml').read_text(encoding='utf-8'))
    except Exception as exc:  # noqa: BLE001
        return [f'cannot load chrony golden tests: {exc}']
    if not isinstance(cases, list) or not cases:
        return ['chrony golden tests must be a non-empty list']
    for case in cases:
        if isinstance(case, dict):
            errors.extend(_compare_case(case, root=root))
        else:
            errors.append('chrony golden test case is not an object')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description='Independently evaluate chrony_observation JSON into a TimeSync P1 state.')
    parser.add_argument('--observation', type=Path, help='Path to chrony_observation JSON. If omitted, read stdin.')
    parser.add_argument('--evaluated-at', required=False, help='RFC3339 evaluation time. Defaults to observation.collected_at.')
    parser.add_argument('--profile-id', default=SUPPORTED_PROFILE)
    parser.add_argument('--output', choices=['bundle', 'state', 'explanation'], default='bundle')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()

    if args.self_test:
        failures = self_test()
        if failures:
            for failure in failures:
                print(f'ERROR: {failure}')
            return 1
        print('TimeSync independent chrony observation evaluator self-test passed.')
        return 0

    try:
        text = args.observation.read_text(encoding='utf-8') if args.observation is not None else sys.stdin.read()
        observation = json.loads(text)
        evaluated_at = args.evaluated_at or observation.get('collected_at')
        if not isinstance(evaluated_at, str):
            raise IndependentEvaluationError('--evaluated-at is required when observation.collected_at is absent')
        bundle = evaluate_observation(observation, profile_id=args.profile_id, evaluated_at=evaluated_at)
    except Exception as exc:  # noqa: BLE001
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1

    if args.output == 'state':
        obj = bundle['local_assessed_state']
    elif args.output == 'explanation':
        obj = bundle['explanation']
    else:
        obj = bundle
    print(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

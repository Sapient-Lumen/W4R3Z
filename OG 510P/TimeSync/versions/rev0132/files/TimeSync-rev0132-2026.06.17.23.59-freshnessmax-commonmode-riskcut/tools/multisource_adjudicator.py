#!/usr/bin/env python3
"""Adjudicate multiple already-assessed TimeSync states for one current use.

This module is intentionally not an NTP clock-selection algorithm and not a new
core schema. It consumes local-assessed-state outputs from existing evaluators,
intersects their correctness intervals when they agree, fails closed when they do
not, and carries the weakest profile lane forward. Its purpose is to prevent a
consumer from cherry-picking the most favorable adapter result when multiple
pieces of assessed evidence are available.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from decimal import Decimal
from fractions import Fraction
import json
from pathlib import Path
import re
import sys
from typing import Any

sys.dont_write_bytecode = True

import chrony_adapter
import ntpq_adapter
from ntp_bound import (
    ceil_fraction_to_ns,
    floor_fraction_to_ns,
    format_epoch_ns,
    fraction_to_decimal,
    parse_instant_seconds,
)

ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_PROFILE = 'P1-general-computing'

APP_RANK = {
    'diagnostic_local_only': 0,
    'display_time': 10,
    'coarse_logging': 20,
    'security_sensitive_time': 30,
}
CONFORMANCE_RANK = {'unsatisfied': 0, 'fallback': 1, 'satisfied': 2}
ACTIONABILITY_RANK = {'not_actionable': 0, 'record_only': 0, 'unknown': 0, 'conditional': 1, 'actionable': 2}
STATUS_RANK = {'rejected': 0, 'unknown': 0, 'accepted_with_conditions': 1, 'accepted': 2}
REGIME_RANK = {'unknown': 0, 'partition_local': 1, 'recovery': 1, 'holdover': 1, 'degraded': 2, 'normal': 3}
SOURCE_POSTURE_RANK = {'unknown': 0, 'local_holdover_only': 0, 'single_source': 1, 'authenticated_only': 1, 'mixed_authenticated': 1, 'multi_source_agreement': 2}


class MultiSourceAdjudicationError(ValueError):
    """Raised when a multi-source fixture or state is malformed."""


def _current_revision(root: Path = ROOT) -> str:
    try:
        receipt = json.loads((root / 'REVISION-RECEIPT.json').read_text(encoding='utf-8'))
        revision = receipt.get('revision')
    except Exception:  # noqa: BLE001
        revision = None
    return revision if isinstance(revision, str) else 'rev0000'


def _safe_id_time(value: str) -> str:
    return re.sub(r'[^0-9A-Za-z]', '', value.replace('Z', 'UTC'))


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise MultiSourceAdjudicationError(f'{path} must contain a JSON object')
    return value


def _instant(value: str, label: str) -> Fraction:
    return parse_instant_seconds(value, label=label, error_cls=MultiSourceAdjudicationError)


def _format_lower(value: Fraction) -> str:
    return format_epoch_ns(floor_fraction_to_ns(value))


def _format_upper(value: Fraction) -> str:
    return format_epoch_ns(ceil_fraction_to_ns(value))


def _duration_seconds(start: Fraction, end: Fraction) -> Decimal:
    return fraction_to_decimal(end - start)


def _first_assessment(state: dict[str, Any]) -> dict[str, Any]:
    assessments = state.get('profile_assessments')
    if not isinstance(assessments, list) or not assessments or not isinstance(assessments[0], dict):
        raise MultiSourceAdjudicationError('local assessed state has no profile assessment')
    return assessments[0]


def _interval_fracs(state: dict[str, Any], label: str) -> tuple[Fraction, Fraction]:
    interval = state.get('timestate', {}).get('interval')
    if not isinstance(interval, dict):
        raise MultiSourceAdjudicationError(f'{label} has no timestate.interval object')
    earliest = _instant(interval.get('earliest'), f'{label}.interval.earliest')
    latest = _instant(interval.get('latest'), f'{label}.interval.latest')
    if earliest > latest:
        raise MultiSourceAdjudicationError(f'{label} interval earliest is after latest')
    return earliest, latest


def _ranked_min(values: list[str], ranks: dict[str, int], default: str) -> str:
    if not values:
        return default
    return min(values, key=lambda value: ranks.get(value, -1))


def _fallback_for(applicability: str | None) -> str | None:
    if applicability == 'coarse_logging':
        return 'security_to_logging'
    if applicability == 'display_time':
        return 'logging_to_display'
    if applicability == 'diagnostic_local_only':
        return None
    return None


def _profile_ref_equal(a: dict[str, Any], b: dict[str, Any]) -> bool:
    return (
        a.get('authority') == b.get('authority')
        and a.get('id') == b.get('id')
        and (a.get('version') or a.get('revision')) == (b.get('version') or b.get('revision'))
        and a.get('digest') == b.get('digest')
    )


def _source_diversity_hook(
    *,
    source_posture: str,
    overlap: bool,
    input_count: int,
    input_hooks: list[dict[str, Any]] | None = None,
) -> dict[str, str]:
    """Summarize diversity without upgrading common-mode posture.

    Interval overlap across assessed states can support a narrower current
    interval, but it cannot prove upstream independence. If any input already
    reports same-root/common-mode dependency, carry that conservative summary
    forward instead of manufacturing a stronger multiple-roots claim.
    """
    if not overlap:
        return {
            'dependency_class': 'unknown',
            'common_mode_risk': 'confirmed_common_mode',
            'assessment_basis': 'local_policy_rule',
            'evidence_posture': 'assessed',
            'export_detail': 'summary_only',
            'note': 'input assessed intervals did not overlap; no diversity or agreement may be claimed',
        }

    hooks = input_hooks or []
    dependency_classes = {hook.get('dependency_class') for hook in hooks if isinstance(hook, dict)}
    common_mode_risks = {hook.get('common_mode_risk') for hook in hooks if isinstance(hook, dict)}

    if 'confirmed_common_mode' in common_mode_risks or 'multiple_sources_same_root' in dependency_classes:
        return {
            'dependency_class': 'multiple_sources_same_root',
            'common_mode_risk': 'possible_common_mode',
            'assessment_basis': 'local_measurement_summary',
            'evidence_posture': 'assessed',
            'export_detail': 'summary_only',
            'note': 'overlapping assessed intervals agree, but at least one input reported same-root/common-mode source posture; do not treat overlap as independent diversity',
        }

    if source_posture == 'multi_source_agreement' and input_count >= 2:
        return {
            'dependency_class': 'multiple_roots_common_distribution',
            'common_mode_risk': 'possible_common_mode',
            'assessment_basis': 'local_policy_rule',
            'evidence_posture': 'assessed',
            'export_detail': 'summary_only',
            'note': 'multiple assessed inputs overlap, but cross-adapter agreement is not proof of independent roots or absence of common-mode failure',
        }
    if source_posture == 'single_source':
        return {
            'dependency_class': 'single_source',
            'common_mode_risk': 'not_assessed',
            'assessment_basis': 'local_policy_rule',
            'evidence_posture': 'assessed',
            'export_detail': 'summary_only',
            'note': 'overlap exists, but the weakest retained input is still single-source',
        }
    return {
        'dependency_class': 'unknown',
        'common_mode_risk': 'unknown',
        'assessment_basis': 'local_policy_rule',
        'evidence_posture': 'unknown',
        'export_detail': 'summary_only',
        'note': 'source posture could not be safely promoted across assessed inputs',
    }


def _auth_hook() -> dict[str, Any]:
    return {
        'packet_authentication': 'not_observed',
        'evidence_posture': 'not_observed',
        'verified_by_timesync': False,
        'used_for_decision': False,
        'profile_strengthening': 'none',
        'note': 'multi-source adjudication consumes already-assessed local states; it does not verify NTS, symmetric keys, or packet transcripts and does not strengthen profile conformance from authentication reports.',
    }


def _profile_catalog_ref(profile_id: str, root: Path) -> dict[str, Any]:
    catalog = json.loads((root / 'profiles/profile-catalog.json').read_text(encoding='utf-8'))
    for profile in catalog.get('profiles', []):
        if profile.get('id') == profile_id:
            ref = {
                'authority': profile.get('authority'),
                'id': profile['id'],
                'version': profile.get('version', '1.0.0'),
            }
            if isinstance(profile.get('normative_rules_digest'), dict):
                ref['digest'] = profile['normative_rules_digest']
            return ref
    raise MultiSourceAdjudicationError(f'profile not found in catalog: {profile_id}')


def adjudicate(states: list[dict[str, Any]], *, adjudicated_at: str, profile_id: str = SUPPORTED_PROFILE, root: Path = ROOT) -> dict[str, Any]:
    """Return a local-assessed-state plus explanation for multiple local states."""
    if len(states) < 2:
        raise MultiSourceAdjudicationError('multi-source adjudication requires at least two input states')
    _instant(adjudicated_at, 'adjudicated_at')

    input_summaries: list[dict[str, Any]] = []
    intervals: list[tuple[Fraction, Fraction]] = []
    assessment_refs: list[dict[str, Any]] = []
    timescales: list[str] = []
    conformance_values: list[str] = []
    applicability_values: list[str] = []
    actionability_values: list[str] = []
    status_values: list[str] = []
    regime_values: list[str] = []
    source_postures: list[str] = []
    last_discipline_values: list[Fraction] = []
    last_discipline_texts: list[str] = []
    max_staleness_values: list[Decimal] = []
    source_diversity_hooks: list[dict[str, Any]] = []

    for index, state in enumerate(states, start=1):
        label = f'input[{index}]'
        assessment = _first_assessment(state)
        assessment_refs.append(deepcopy(assessment.get('assessed_profile', {})))
        earliest, latest = _interval_fracs(state, label)
        intervals.append((earliest, latest))
        ts = state.get('timestate', {}) if isinstance(state.get('timestate'), dict) else {}
        timescale = ts.get('timescale')
        if isinstance(timescale, str):
            timescales.append(timescale)
        conformance = assessment.get('profile_conformance')
        applicability = assessment.get('applicability')
        acceptance = assessment.get('policy_acceptance', {}) if isinstance(assessment.get('policy_acceptance'), dict) else {}
        status = acceptance.get('status')
        actionability = acceptance.get('actionability')
        regime = ts.get('regime')
        source_posture_value = ts.get('source_posture')
        if isinstance(conformance, str):
            conformance_values.append(conformance)
        if isinstance(applicability, str):
            applicability_values.append(applicability)
        if isinstance(status, str):
            status_values.append(status)
        if isinstance(actionability, str):
            actionability_values.append(actionability)
        if isinstance(regime, str):
            regime_values.append(regime)
        if isinstance(source_posture_value, str):
            source_postures.append(source_posture_value)
        freshness = ts.get('freshness', {}) if isinstance(ts.get('freshness'), dict) else {}
        last_discipline = freshness.get('last_discipline')
        if isinstance(last_discipline, str):
            last_discipline_values.append(_instant(last_discipline, f'{label}.freshness.last_discipline'))
            last_discipline_texts.append(last_discipline)
        max_staleness = freshness.get('max_staleness_ms')
        if isinstance(max_staleness, (int, float, str)):
            max_staleness_values.append(Decimal(str(max_staleness)))
        hooks = state.get('extension_hooks', {}) if isinstance(state.get('extension_hooks'), dict) else {}
        diversity_hook = hooks.get('source_diversity_posture') if isinstance(hooks, dict) else None
        if isinstance(diversity_hook, dict):
            source_diversity_hooks.append(deepcopy(diversity_hook))
        input_summaries.append({
            'index': index,
            'assessment_id': assessment.get('assessment_id'),
            'profile_conformance': conformance,
            'applicability': applicability,
            'policy_status': status,
            'actionability': actionability,
            'timescale': timescale,
            'regime': regime,
            'source_posture': source_posture_value,
            'interval_earliest': state.get('timestate', {}).get('interval', {}).get('earliest'),
            'interval_latest': state.get('timestate', {}).get('interval', {}).get('latest'),
            'source_diversity_dependency_class': diversity_hook.get('dependency_class') if isinstance(diversity_hook, dict) else None,
            'source_diversity_common_mode_risk': diversity_hook.get('common_mode_risk') if isinstance(diversity_hook, dict) else None,
        })

    first_ref = assessment_refs[0]
    profile_mismatch = any(not _profile_ref_equal(first_ref, ref) for ref in assessment_refs[1:])
    timescale_mismatch = len(set(timescales)) != 1 or not timescales
    inter_earliest = max(start for start, _end in intervals)
    inter_latest = min(end for _start, end in intervals)
    union_earliest = min(start for start, _end in intervals)
    union_latest = max(end for _start, end in intervals)
    overlap = inter_earliest <= inter_latest
    hard_fail = (not overlap) or profile_mismatch or timescale_mismatch or any(v == 'unsatisfied' for v in conformance_values) or any(v == 'unknown' for v in source_postures)

    if hard_fail:
        out_earliest, out_latest = union_earliest, union_latest
        conformance = 'unsatisfied'
        applicability = 'diagnostic_local_only'
        policy_status = 'rejected'
        actionability = 'not_actionable'
        regime = 'unknown'
        source_posture_value = 'unknown'
        fallback_mapping = None
        missing_items = ['overlapping_current_intervals_from_compatible_assessments']
        if profile_mismatch:
            missing_items.append('same_assessed_profile')
        if timescale_mismatch:
            missing_items.append('same_timescale')
        if any(v == 'unsatisfied' for v in conformance_values):
            missing_items.append('all_inputs_at_least_fallback')
        reason = 'multi-source adjudication failed closed because input intervals, profiles, timescales, or source postures could not all be safely combined'
    else:
        out_earliest, out_latest = inter_earliest, inter_latest
        conformance = _ranked_min(conformance_values, CONFORMANCE_RANK, 'unsatisfied')
        applicability = _ranked_min(applicability_values, APP_RANK, 'diagnostic_local_only')
        policy_status = _ranked_min(status_values, STATUS_RANK, 'rejected')
        actionability = _ranked_min(actionability_values, ACTIONABILITY_RANK, 'not_actionable')
        regime = _ranked_min(regime_values, REGIME_RANK, 'unknown')
        source_posture_value = _ranked_min(source_postures, SOURCE_POSTURE_RANK, 'unknown')
        fallback_mapping = _fallback_for(applicability) if conformance == 'fallback' else None
        missing_items = []
        reason = 'all input assessed intervals overlap; output interval is the intersection and profile lane is the weakest input lane'

    if conformance == 'satisfied':
        policy_status = 'accepted'
        actionability = 'actionable'
    elif conformance == 'fallback':
        policy_status = 'accepted_with_conditions'
        if actionability == 'actionable':
            actionability = 'conditional'
    else:
        policy_status = 'rejected'
        actionability = 'not_actionable'
        applicability = 'diagnostic_local_only'
        regime = 'unknown'
        source_posture_value = 'unknown'

    interval = {
        'earliest': _format_lower(out_earliest),
        'latest': _format_upper(out_latest),
    }
    width_seconds = _duration_seconds(out_earliest, out_latest)
    bound_ms = (width_seconds / Decimal('2')) * Decimal('1000')
    rev = _current_revision(root)
    profile_ref = _profile_catalog_ref(profile_id, root)
    evaluation_summary: dict[str, Any] = {'matched_profile_catalog': True}
    if fallback_mapping is not None:
        evaluation_summary['fallback_mapping'] = fallback_mapping
    if missing_items:
        evaluation_summary['missing_items'] = missing_items

    if last_discipline_values:
        oldest_index = min(range(len(last_discipline_values)), key=lambda i: last_discipline_values[i])
        last_discipline = last_discipline_texts[oldest_index]
    else:
        last_discipline = adjudicated_at
    max_staleness_ms = max(max_staleness_values) if max_staleness_values else Decimal('0')

    state = {
        'timestate': {
            'interval': interval,
            'timescale': timescales[0] if not timescale_mismatch else 'UTC',
            'freshness': {
                'last_discipline': last_discipline,
                'max_staleness_ms': float(max_staleness_ms),
                'profile_expression': f'{rev} P1 multi-source adjudication policy',
            },
            'regime': regime,
            'source_posture': source_posture_value,
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
                'confidence': 'interval_intersection_when_overlap_else_union_fail_closed',
                'basis': 'intersection of overlapping local-assessed-state intervals; union when fail-closed',
            },
            'rate_error_bound': {
                'bound_ppb': 0.0,
                'confidence': 'not_recomputed_by_multisource_adjudicator',
                'basis': 'input evaluators retain adapter-local rate bounds; adjudicator does not narrow rate error',
            },
            'timescale_realization': {
                'scale': timescales[0] if not timescale_mismatch else 'unknown',
                'realization': 'multi-source-adjudicated-unqualified-UTC' if not timescale_mismatch else 'unknown',
                'leap_handling': 'standard_utc' if not hard_fail else 'unknown',
                'tai_utc_offset_state': 'unknown',
                'evidence_posture': 'claimed' if not timescale_mismatch else 'unknown',
                'note': 'adjudication preserves input UTC claims but does not prove a named UTC realization or leap-smear policy',
            },
            'clock_continuity_posture': {
                'backward_step_policy': 'unknown',
                'smear_policy': 'none' if not hard_fail else 'unknown',
                'monotonic_local_time': 'not_claimed',
                'evidence_posture': 'unknown',
                'note': 'multi-source adjudication does not prove application monotonic-clock behavior',
            },
            'source_diversity_posture': _source_diversity_hook(
                source_posture=source_posture_value,
                overlap=overlap and not hard_fail,
                input_count=len(states),
                input_hooks=source_diversity_hooks,
            ),
            'authentication_posture': _auth_hook(),
        },
        'profile_assessments': [
            {
                'assessment_time': adjudicated_at,
                'assessed_profile': profile_ref,
                'profile_conformance': conformance,
                'applicability': applicability,
                'profile_lifecycle_state': 'active',
                'policy_acceptance': {
                    'status': policy_status,
                    'checked_at': adjudicated_at,
                    'policy_reference': f'timesync-reference-evaluator:P1-multisource-adjudicator-{rev}',
                    'reason': reason,
                    'actionability': actionability,
                },
                'evaluation_summary': evaluation_summary,
                'assessment_id': f'assess-{profile_id}-multisource-{_safe_id_time(adjudicated_at)}',
                'note': 'Generated by tools/multisource_adjudicator.py from already-assessed local states; weakest lane and interval relation are carried forward.',
            }
        ],
    }
    explanation = {
        'explanation_type': 'timesync_multisource_adjudication_v1',
        'profile_id': profile_id,
        'adjudicated_at': adjudicated_at,
        'input_count': len(states),
        'input_summaries': input_summaries,
        'interval_relation': {
            'overlap': overlap,
            'profile_mismatch': profile_mismatch,
            'timescale_mismatch': timescale_mismatch,
            'intersection_earliest': _format_lower(inter_earliest),
            'intersection_latest': _format_upper(inter_latest) if overlap else None,
            'union_earliest': _format_lower(union_earliest),
            'union_latest': _format_upper(union_latest),
            'output_rule': 'intersection' if not hard_fail else 'union_fail_closed',
        },
        'decision': {
            'profile_conformance': conformance,
            'applicability': applicability,
            'actionability': actionability,
            'reason': reason,
        },
        'unsupported_or_not_verified': [
            'not a replacement for NTP truechimer selection or clustering',
            'does not prove independent reference roots or absence of common-mode failures',
            'same-root or common-mode input diversity summaries are carried forward and must not be upgraded by interval overlap',
            'does not verify NTS, symmetric keys, packet MACs, or packet transcripts',
            'does not prove named UTC realization traceability or leap-smear policy',
            'does not recompute adapter-local raw observations beyond existing local-assessed-state outputs',
        ],
    }
    return {'local_assessed_state': state, 'explanation': explanation}


def _state_from_spec(spec: dict[str, Any], *, root: Path) -> dict[str, Any]:
    adapter = spec.get('adapter')
    collected_at = spec.get('collected_at')
    evaluated_at = spec.get('evaluated_at')
    if not isinstance(collected_at, str) or not isinstance(evaluated_at, str):
        raise MultiSourceAdjudicationError('adapter input requires collected_at and evaluated_at')
    if adapter == 'chrony':
        observation = chrony_adapter.build_observation(
            tracking_text=(root / spec['tracking']).read_text(encoding='utf-8'),
            sources_text=(root / spec.get('sources', '')).read_text(encoding='utf-8') if spec.get('sources') else '',
            sourcestats_text=(root / spec.get('sourcestats', '')).read_text(encoding='utf-8') if spec.get('sourcestats') else '',
            authdata_text=(root / spec.get('authdata', '')).read_text(encoding='utf-8') if spec.get('authdata') else '',
            ntpdata_text=(root / spec.get('ntpdata', '')).read_text(encoding='utf-8') if spec.get('ntpdata') else '',
            collected_at=collected_at,
        )
        return chrony_adapter.evaluate(observation, profile_id=spec.get('profile_id', SUPPORTED_PROFILE), evaluated_at=evaluated_at)['local_assessed_state']
    if adapter == 'ntpq':
        observation = ntpq_adapter.build_observation(
            readvar_text=(root / spec['readvar']).read_text(encoding='utf-8'),
            peers_text=(root / spec.get('peers', '')).read_text(encoding='utf-8') if spec.get('peers') else '',
            collected_at=collected_at,
        )
        return ntpq_adapter.evaluate(observation, profile_id=spec.get('profile_id', SUPPORTED_PROFILE), evaluated_at=evaluated_at)['local_assessed_state']
    if adapter == 'state_file':
        return _load_json(root / spec['path'])
    raise MultiSourceAdjudicationError(f'unknown input adapter {adapter!r}')


def run_case(case: dict[str, Any], *, root: Path = ROOT) -> list[str]:
    cid = case.get('id', '<no-id>')
    errors: list[str] = []
    try:
        inputs = case.get('inputs')
        if not isinstance(inputs, list) or len(inputs) < 2:
            raise MultiSourceAdjudicationError('case requires at least two inputs')
        states = [_state_from_spec(spec, root=root) for spec in inputs]
        bundle = adjudicate(states, adjudicated_at=case['adjudicated_at'], profile_id=case.get('profile_id', SUPPORTED_PROFILE), root=root)
    except Exception as exc:  # noqa: BLE001
        expected_error = case.get('expect_error_contains')
        if expected_error and expected_error.lower() in str(exc).lower():
            return []
        return [f'{cid}: unexpected multi-source adjudication error: {exc}']
    if case.get('expect_error_contains'):
        return [f'{cid}: expected error containing {case["expect_error_contains"]!r} but adjudication succeeded']

    state = bundle['local_assessed_state']
    assessment = _first_assessment(state)
    acceptance = assessment.get('policy_acceptance', {}) if isinstance(assessment.get('policy_acceptance'), dict) else {}
    evaluation_summary = assessment.get('evaluation_summary', {}) if isinstance(assessment.get('evaluation_summary'), dict) else {}
    ts = state['timestate']
    explanation = bundle['explanation']
    checks = {
        'profile_conformance': assessment.get('profile_conformance'),
        'applicability': assessment.get('applicability'),
        'policy_status': acceptance.get('status'),
        'actionability': acceptance.get('actionability'),
        'fallback_mapping': evaluation_summary.get('fallback_mapping'),
        'source_posture': ts.get('source_posture'),
        'regime': ts.get('regime'),
        'interval_earliest': ts.get('interval', {}).get('earliest'),
        'interval_latest': ts.get('interval', {}).get('latest'),
        'interval_overlap': explanation.get('interval_relation', {}).get('overlap'),
        'output_rule': explanation.get('interval_relation', {}).get('output_rule'),
        'missing_items': evaluation_summary.get('missing_items'),
        'freshness_max_staleness_ms': ts.get('freshness', {}).get('max_staleness_ms'),
        'dependency_class': state.get('extension_hooks', {}).get('source_diversity_posture', {}).get('dependency_class'),
        'common_mode_risk': state.get('extension_hooks', {}).get('source_diversity_posture', {}).get('common_mode_risk'),
    }
    for key, expected in case.get('expect', {}).items():
        actual = checks.get(key)
        if actual != expected:
            errors.append(f'{cid}: expected {key}={expected!r}, got {actual!r}')
    return errors


def self_test(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        import yaml  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return [f'PyYAML unavailable for multi-source adjudication tests: {exc}']
    path = root / 'tests/multisource-adjudication.yaml'
    try:
        cases = yaml.safe_load(path.read_text(encoding='utf-8'))
    except Exception as exc:  # noqa: BLE001
        return [f'cannot load multi-source adjudication tests: {exc}']
    if not isinstance(cases, list) or not cases:
        return ['tests/multisource-adjudication.yaml must be a non-empty list']
    for case in cases:
        if not isinstance(case, dict):
            errors.append('multi-source adjudication case is not an object')
            continue
        errors.extend(run_case(case, root=root))
    return errors


def generate_example(root: Path = ROOT) -> dict[str, Any]:
    import yaml  # type: ignore
    cases = yaml.safe_load((root / 'tests/multisource-adjudication.yaml').read_text(encoding='utf-8'))
    if not isinstance(cases, list) or not cases or not isinstance(cases[0], dict):
        raise MultiSourceAdjudicationError('multi-source adjudication cases unavailable')
    states = [_state_from_spec(spec, root=root) for spec in cases[0]['inputs']]
    return adjudicate(states, adjudicated_at=cases[0]['adjudicated_at'], profile_id=cases[0].get('profile_id', SUPPORTED_PROFILE), root=root)['local_assessed_state']


def main() -> int:
    parser = argparse.ArgumentParser(description='Adjudicate multiple TimeSync local-assessed-state JSON files.')
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--adjudicated-at')
    parser.add_argument('--profile-id', default=SUPPORTED_PROFILE)
    parser.add_argument('--state', action='append', type=Path, help='Local-assessed-state JSON path. Repeat at least twice.')
    parser.add_argument('--output', choices=['bundle', 'state', 'explanation'], default='bundle')
    args = parser.parse_args()
    if args.self_test:
        failures = self_test()
        if failures:
            for failure in failures:
                print(f'ERROR: {failure}')
            return 1
        print('TimeSync multi-source adjudication self-test passed.')
        return 0
    try:
        if not args.adjudicated_at or not args.state or len(args.state) < 2:
            raise MultiSourceAdjudicationError('--adjudicated-at and at least two --state files are required')
        states = [_load_json(path) for path in args.state]
        bundle = adjudicate(states, adjudicated_at=args.adjudicated_at, profile_id=args.profile_id)
    except Exception as exc:  # noqa: BLE001
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    if args.output == 'state':
        obj = bundle['local_assessed_state']
    elif args.output == 'explanation':
        obj = bundle['explanation']
    else:
        obj = bundle
    print(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

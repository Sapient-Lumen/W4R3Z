"""Scope-composition semantic checks for TimeSync validation.

Scope-composition guards stitch together otherwise separate surfaces such as
profile drift, discovery downgrade proof, digest binding, aggregate lifecycle,
and transparency-policy lifecycle metadata. The guard is allowed to coordinate
current-use interpretation, but it must not let one surface's freshness metadata
qualify a different digest-bound surface.

This module owns the mixed-layer decision-matrix and guard checks so the main
archive validator does not keep accreting another cross-surface policy branch.
"""
from __future__ import annotations

from typing import Any

from discovery_binding_semantics import digest_binds
from temporal_coherence import check_scope_temporal_coherence

SCOPE_COMPOSITION_REQUIRED_ROWS = {
    'safe-separated-mixed-layer-current-guarded',
    'downgrade-cannot-bypass-lifecycle-suppression',
    'lifecycle-rollup-cannot-bypass-profile-drift',
    'transparency-policy-equivalence-cannot-reopen-profile-assessment',
    'aggregate-rollup-cannot-update-actionability',
    'unknown-newer-version-metadata-only',
    'digest-binding-cannot-become-profile-evidence',
    'stale-composed-input-cannot-remain-current',
}
SCOPE_COMPOSITION_MIXED_REQUIRED_SURFACES = {
    'profile_compatibility_drift',
    'discovery_version_negotiation',
    'discovery_digest_binding',
    'aggregate_correction_authority_lifecycle',
    'aggregate_lifecycle_rollup',
    'transparency_trust_policy_lifecycle',
}
SCOPE_SURFACE_BOUNDARY_FALSE = (
    'surface_is_profile_evidence',
    'surface_updates_timestate',
    'surface_updates_profile_assessment',
    'surface_updates_actionability',
    'surface_reopens_assessment',
    'surface_interpreted_as_timesync_provenance',
    'surface_overrides_lifecycle_suppression',
    'surface_bypasses_downgrade_proof',
    'surface_bypasses_profile_drift',
    'raw_surface_material_exported',
)
SCOPE_GUARD_BOUNDARY_FALSE = (
    'guard_is_profile_evidence',
    'guard_updates_timestate',
    'guard_updates_profile_assessment',
    'guard_updates_actionability',
    'guard_reopens_assessment',
    'guard_interpreted_as_timesync_provenance',
    'guard_overrides_lifecycle_suppression',
    'guard_bypasses_downgrade_proof',
    'guard_bypasses_profile_drift',
    'raw_composed_surface_material_exported',
)

EXPECTED_SOURCE_DIGEST_BINDINGS: dict[str, str] = {
    'profile_compatibility_drift': 'profile_compatibility_drift_matrix',
    'discovery_version_negotiation': 'profile_downgrade_proof',
    'discovery_digest_binding': 'digest_binding_policy',
    'aggregate_correction_authority_lifecycle': 'aggregate_correction_authority_lifecycle_summary',
    'aggregate_lifecycle_rollup': 'aggregate_correction_authority_lifecycle_summary',
    'transparency_trust_policy_lifecycle': 'transparency_trust_policy_reference',
}


def _digest_identity(digest: Any) -> tuple[Any, Any, Any] | None:
    if not isinstance(digest, dict):
        return None
    return digest.get('algorithm'), digest.get('value'), digest.get('binds')


def _same_digest(left: Any, right: Any) -> bool:
    return _digest_identity(left) is not None and _digest_identity(left) == _digest_identity(right)


def check_scope_composition_decision_matrix(matrix: dict[str, Any]) -> list[str]:
    """Completeness checks for mixed-layer composition attack rows."""
    errors: list[str] = []
    if not digest_binds(matrix.get('matrix_digest'), 'scope_composition_decision_matrix'):
        errors.append('scope composition matrix requires matrix_digest binding scope_composition_decision_matrix')
    rows = matrix.get('rows', []) if isinstance(matrix.get('rows'), list) else []
    ids = {r.get('row_id') for r in rows if isinstance(r, dict)}
    missing = SCOPE_COMPOSITION_REQUIRED_ROWS - ids
    if missing:
        errors.append(f'scope composition matrix missing required rows {sorted(missing)}')
    for row in rows:
        if not isinstance(row, dict):
            continue
        rid = row.get('row_id', '<unknown-row>')
        if row.get('unsafe_upgrade_blocked') is not True:
            errors.append(f'scope composition matrix row {rid} must block unsafe upgrade')
        if row.get('safe_guard_effect') == 'current_use_guarded' and row.get('failure_mode') != 'none':
            errors.append(f'scope composition matrix row {rid} current-use guarded row must have failure_mode none')
        if row.get('attack_pattern') != 'safe_separated_surfaces' and row.get('safe_guard_effect') == 'current_use_guarded':
            errors.append(f'scope composition matrix row {rid} attack row cannot have current_use_guarded safe effect')
    return errors


def check_scope_composition_guard(guard: dict[str, Any], record: dict[str, Any] | None = None) -> list[str]:
    """Fail-closed guardrails for composing profile drift, downgrade, lifecycle, and transparency surfaces."""
    errors: list[str] = []
    if guard.get('guard_version') != 'rev0090':
        errors.append('scope composition guard_version must be rev0090')
    if not digest_binds(guard.get('guard_digest'), 'scope_composition_guard'):
        errors.append('scope composition guard requires guard_digest binding scope_composition_guard')
    boundary = guard.get('non_upgrade_boundary', {}) if isinstance(guard.get('non_upgrade_boundary'), dict) else {}
    for key in SCOPE_GUARD_BOUNDARY_FALSE:
        if boundary.get(key) is not False:
            errors.append(f'scope composition guard boundary.{key} must be false')

    decision = guard.get('composition_decision', {}) if isinstance(guard.get('composition_decision'), dict) else {}
    if decision.get('profile_assessment_effect') != 'no_effect':
        errors.append('scope composition guard cannot update profile assessment')
    if decision.get('current_actionability_effect') != 'no_effect':
        errors.append('scope composition guard cannot update current actionability')

    surfaces = [s for s in guard.get('surface_decisions', []) if isinstance(s, dict)]
    surface_names = [s.get('surface') for s in surfaces]
    if len(surface_names) != len(set(surface_names)):
        errors.append('scope composition guard surface decisions must be unique by surface')
    surface_set = {s for s in surface_names if isinstance(s, str)}
    if guard.get('composition_scope') == 'mixed_layer_portability_review':
        missing = SCOPE_COMPOSITION_MIXED_REQUIRED_SURFACES - surface_set
        if missing:
            errors.append(f'mixed-layer scope composition guard missing required surfaces {sorted(missing)}')
        if not digest_binds(guard.get('matrix_digest'), 'scope_composition_decision_matrix'):
            errors.append('mixed-layer scope composition guard requires matrix_digest binding scope_composition_decision_matrix')

    suppressed = []
    non_current = []
    by_surface = {s.get('surface'): s for s in surfaces if isinstance(s.get('surface'), str)}
    for surface in surfaces:
        name = surface.get('surface', '<unknown-surface>')
        nb = surface.get('non_upgrade_boundary', {}) if isinstance(surface.get('non_upgrade_boundary'), dict) else {}
        for key in SCOPE_SURFACE_BOUNDARY_FALSE:
            if nb.get(key) is not False:
                errors.append(f'scope composition surface {name} boundary.{key} must be false')
        if surface.get('suppression_effect') != 'no_suppression':
            suppressed.append(name)
        if surface.get('current_use_allowed') is not True:
            non_current.append(name)
        if surface.get('current_use_allowed') is True and surface.get('suppression_effect') != 'no_suppression':
            errors.append(f'scope composition surface {name} cannot be current-use allowed while suppressed or historical')
        expected_binding = EXPECTED_SOURCE_DIGEST_BINDINGS.get(str(name))
        if surface.get('current_use_allowed') is True and expected_binding and not digest_binds(surface.get('source_digest'), expected_binding):
            errors.append(f'current scope composition surface {name} requires source_digest binding {expected_binding}')
        if name == 'profile_compatibility_drift' and surface.get('current_use_allowed') is True and surface.get('interpretation_scope') != 'compatibility_interpretation_only':
            errors.append('profile compatibility drift can only affect compatibility interpretation')
        if name in {'aggregate_correction_authority_lifecycle', 'aggregate_lifecycle_rollup'} and surface.get('interpretation_scope') not in {'aggregate_interpretation_only', 'historical_only', 'metadata_only'}:
            errors.append(f'{name} can only affect aggregate interpretation, historical, or metadata scope')

    current_guard = decision.get('guard_effect') in {'current_use_allowed', 'current_use_guarded'}
    current_surfaces = {s.get('surface') for s in surfaces if s.get('current_use_allowed') is True and isinstance(s.get('surface'), str)}
    errors.extend(check_scope_temporal_coherence(
        guard,
        current_guard=current_guard,
        current_surfaces=current_surfaces,
        composition_scope=guard.get('composition_scope') if isinstance(guard.get('composition_scope'), str) else None,
    ))

    if current_guard:
        temporal = guard.get('temporal_coherence') if isinstance(guard.get('temporal_coherence'), dict) else {}
        observations = temporal.get('input_observations', []) if isinstance(temporal.get('input_observations'), list) else []
        for obs in observations:
            if not isinstance(obs, dict):
                continue
            name = obs.get('surface')
            time_digest = obs.get('source_time_digest')
            if name == 'scope_composition_decision_matrix':
                if not _same_digest(guard.get('matrix_digest'), time_digest):
                    errors.append('scope composition decision matrix temporal observation must match matrix_digest')
                continue
            if not isinstance(name, str) or name not in current_surfaces:
                continue
            surface_digest = by_surface.get(name, {}).get('source_digest') if isinstance(by_surface.get(name), dict) else None
            if surface_digest is None:
                continue
            if not _same_digest(surface_digest, time_digest):
                errors.append(f'current scope composition temporal observation for {name} must match surface source_digest')

    if current_guard and non_current:
        errors.append('scope composition guard cannot allow current use when a composed surface is not current-use allowed')
    if current_guard and suppressed:
        errors.append('scope composition guard cannot bypass composed suppression')
    if decision.get('replay_visibility_effect') == 'current_replay_visibility_supported' and (non_current or suppressed):
        errors.append('scope composition guard cannot derive current replay visibility from non-current or suppressed surfaces')
    if decision.get('aggregate_interpretation_effect') == 'current_supported' and any(s in surface_set for s in {'aggregate_correction_authority_lifecycle', 'aggregate_lifecycle_rollup'}) and suppressed:
        errors.append('scope composition guard cannot derive current aggregate interpretation from suppressed lifecycle surfaces')
    if decision.get('portability_effect') == 'portable_current_guarded' and (non_current or suppressed):
        errors.append('scope composition guard cannot allow current portability from non-current or suppressed surfaces')
    reasons = set(decision.get('suppression_reasons', [])) if isinstance(decision.get('suppression_reasons'), list) else set()
    if decision.get('guard_effect') in {'suppressed', 'fail_closed', 'historical_only', 'metadata_only'} and not reasons:
        errors.append('non-current scope composition guard effect requires suppression_reasons')
    if decision.get('guard_effect') in {'current_use_allowed', 'current_use_guarded'} and reasons - {'none'}:
        errors.append('current scope composition guard cannot carry non-none suppression reasons')

    if record is not None and isinstance(record.get('aggregate_summary'), dict):
        rollup = record.get('aggregate_summary', {}).get('aggregate_correction_authority_lifecycle_rollup')
        if isinstance(rollup, dict):
            rdecision = rollup.get('current_interpretation_decision')
            if rdecision not in {None, 'current_supported', 'current_supported_guarded'} and decision.get('aggregate_interpretation_effect') == 'current_supported':
                errors.append('scope composition guard conflicts with aggregate lifecycle rollup suppression')
    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    guard = {
        'guard_version': 'rev0090',
        'evaluated_at': '2026-05-26T07:00:00Z',
        'composition_scope': 'mixed_layer_portability_review',
        'guard_digest': {'algorithm': 'sha256', 'value': 'a' * 64, 'binds': 'scope_composition_guard'},
        'matrix_digest': {'algorithm': 'sha256', 'value': 'b' * 64, 'binds': 'scope_composition_decision_matrix'},
        'non_upgrade_boundary': {key: False for key in SCOPE_GUARD_BOUNDARY_FALSE},
        'surface_decisions': [],
        'composition_decision': {
            'guard_effect': 'current_use_guarded',
            'profile_assessment_effect': 'no_effect',
            'current_actionability_effect': 'no_effect',
            'suppression_reasons': ['none'],
        },
        'temporal_coherence': {
            'evaluation_window': {
                'not_before': '2026-05-26T06:59:00Z',
                'not_after': '2026-05-26T07:00:00Z',
                'max_span_seconds': 120,
            },
            'coherence_decision': {
                'decision': 'coherent_current_guard',
                'all_current_inputs_within_window': True,
                'guard_evaluated_within_window': True,
                'stale_input_blocks_current_use': True,
            },
            'input_observations': [],
            'non_provenance_boundary': {
                'temporal_metadata_updates_timestate': False,
                'temporal_metadata_updates_profile_assessment': False,
                'temporal_metadata_updates_actionability': False,
                'temporal_metadata_interpreted_as_time_source_provenance': False,
                'stale_input_reuse_allowed_for_current': False,
            },
        },
    }
    surface_template = {
        'interpretation_scope': 'compatibility_interpretation_only',
        'current_use_allowed': True,
        'suppression_effect': 'no_suppression',
        'source_semantic_version': '1.0.0',
        'non_upgrade_boundary': {key: False for key in SCOPE_SURFACE_BOUNDARY_FALSE},
    }
    digest = {'algorithm': 'sha256', 'value': 'c' * 64, 'binds': 'profile_compatibility_drift_matrix'}
    guard['surface_decisions'] = [
        {**surface_template, 'surface': 'profile_compatibility_drift', 'source_digest': digest},
        {**surface_template, 'surface': 'discovery_version_negotiation', 'interpretation_scope': 'discovery_interpretation_only', 'source_digest': {'algorithm': 'sha256', 'value': 'd' * 64, 'binds': 'profile_downgrade_proof'}},
        {**surface_template, 'surface': 'discovery_digest_binding', 'interpretation_scope': 'discovery_interpretation_only', 'source_digest': {'algorithm': 'sha256', 'value': 'e' * 64, 'binds': 'digest_binding_policy'}},
        {**surface_template, 'surface': 'aggregate_correction_authority_lifecycle', 'interpretation_scope': 'aggregate_interpretation_only', 'source_digest': {'algorithm': 'sha256', 'value': 'f' * 64, 'binds': 'aggregate_correction_authority_lifecycle_summary'}},
        {**surface_template, 'surface': 'aggregate_lifecycle_rollup', 'interpretation_scope': 'aggregate_interpretation_only', 'source_digest': {'algorithm': 'sha256', 'value': '1' * 64, 'binds': 'aggregate_correction_authority_lifecycle_summary'}},
        {**surface_template, 'surface': 'transparency_trust_policy_lifecycle', 'interpretation_scope': 'replay_visibility_only', 'source_digest': {'algorithm': 'sha256', 'value': '2' * 64, 'binds': 'transparency_trust_policy_reference'}},
    ]
    roles = {
        'profile_compatibility_drift': 'profile_drift_evaluated_at',
        'discovery_version_negotiation': 'discovery_negotiated_at',
        'discovery_digest_binding': 'digest_policy_checked_at',
        'aggregate_correction_authority_lifecycle': 'lifecycle_checked_at',
        'aggregate_lifecycle_rollup': 'lifecycle_rollup_checked_at',
        'transparency_trust_policy_lifecycle': 'transparency_policy_checked_at',
    }
    guard['temporal_coherence']['input_observations'] = [
        {
            'surface': surface['surface'],
            'time_role': roles[surface['surface']],
            'observed_at': '2026-05-26T06:59:30Z',
            'freshness_status': 'fresh_at_guard_evaluation',
            'current_use_effect': 'no_effect',
            'max_age_seconds': 120,
            'source_time_digest': surface['source_digest'],
        }
        for surface in guard['surface_decisions']
    ] + [
        {
            'surface': 'aggregate_correction_authority_lifecycle',
            'time_role': 'revocation_checked_at',
            'observed_at': '2026-05-26T06:59:31Z',
            'freshness_status': 'fresh_at_guard_evaluation',
            'current_use_effect': 'no_effect',
            'max_age_seconds': 120,
            'source_time_digest': guard['surface_decisions'][3]['source_digest'],
        },
        {
            'surface': 'scope_composition_decision_matrix',
            'time_role': 'decision_matrix_observed_at',
            'observed_at': '2026-05-26T06:59:55Z',
            'freshness_status': 'fresh_at_guard_evaluation',
            'current_use_effect': 'no_effect',
            'max_age_seconds': 120,
            'source_time_digest': {'algorithm': 'sha256', 'value': 'b' * 64, 'binds': 'scope_composition_decision_matrix'},
        },
    ]
    mismatch = {**guard, 'temporal_coherence': {**guard['temporal_coherence']}}
    mismatch_obs = [dict(item) for item in guard['temporal_coherence']['input_observations']]
    mismatch_obs[0] = {**mismatch_obs[0], 'source_time_digest': {'algorithm': 'sha256', 'value': '0' * 64, 'binds': 'profile_compatibility_drift_matrix'}}
    mismatch['temporal_coherence']['input_observations'] = mismatch_obs
    if not any('must match surface source_digest' in err for err in check_scope_composition_guard(mismatch)):
        errors.append('scope composition self-test failed: temporal source mismatch accepted')
    wrong_bind = {**guard, 'surface_decisions': [dict(item) for item in guard['surface_decisions']]}
    wrong_bind['surface_decisions'][0] = {**wrong_bind['surface_decisions'][0], 'source_digest': {'algorithm': 'sha256', 'value': 'c' * 64, 'binds': 'digest_binding_policy'}}
    if not any('requires source_digest binding profile_compatibility_drift_matrix' in err for err in check_scope_composition_guard(wrong_bind)):
        errors.append('scope composition self-test failed: wrong source binding accepted')
    wrong_matrix_obs = {**guard, 'temporal_coherence': {**guard['temporal_coherence']}}
    matrix_obs = [dict(item) for item in guard['temporal_coherence']['input_observations']]
    matrix_obs[-1] = {
        **matrix_obs[-1],
        'source_time_digest': {'algorithm': 'sha256', 'value': 'b' * 64, 'binds': 'aggregate_lifecycle_decision_table'},
    }
    wrong_matrix_obs['temporal_coherence']['input_observations'] = matrix_obs
    if not any('decision matrix temporal observation must match matrix_digest' in err for err in check_scope_composition_guard(wrong_matrix_obs)):
        errors.append('scope composition self-test failed: wrong matrix temporal digest accepted')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync scope composition semantic self-test passed.')

#!/usr/bin/env python3
"""Aggregate privacy-control semantic checks.

These checks keep aggregate privacy metadata fail-closed without turning TimeSync
into a privacy-budget ledger, operator registry, or profile-equivalence service.
"""
from __future__ import annotations

from typing import Any

from discovery_binding_semantics import digest_binds


def _boundary_false_errors(boundary: dict[str, Any], keys: tuple[str, ...], prefix: str) -> list[str]:
    return [f'{prefix} boundary {key} must be false' for key in keys if boundary.get(key) is not False]


def _non_negative_int(value: Any) -> int:
    return value if isinstance(value, int) and value >= 0 else 0


def check_aggregate_privacy_controls(aggregate: dict[str, Any]) -> list[str]:
    """Publication-cadence, threshold-equivalence, and statistical-noise checks."""
    errors: list[str] = []
    controls = aggregate.get('aggregate_privacy_controls') if isinstance(aggregate.get('aggregate_privacy_controls'), dict) else None
    if controls is None:
        return ['aggregate verifier audit summary requires aggregate_privacy_controls']

    privacy_boundary = controls.get('privacy_boundary', {}) if isinstance(controls.get('privacy_boundary'), dict) else {}
    errors.extend(_boundary_false_errors(privacy_boundary, (
        'privacy_controls_are_profile_evidence',
        'privacy_controls_update_actionability',
        'privacy_controls_reopen_assessment',
        'privacy_controls_identify_verifiers_or_results',
        'privacy_controls_interpreted_as_timesync_provenance',
    ), 'aggregate_privacy_controls'))

    publication = controls.get('publication_cadence', {}) if isinstance(controls.get('publication_cadence'), dict) else {}
    pub_boundary = publication.get('publication_boundary', {}) if isinstance(publication.get('publication_boundary'), dict) else {}
    errors.extend(_boundary_false_errors(pub_boundary, (
        'exact_adjacent_windows_exported',
        'cross_publication_reconstruction_material_exported',
        'publication_sequence_updates_profile_assessment',
    ), 'aggregate_privacy_controls.publication_cadence'))
    if pub_boundary.get('publication_cadence_updates_replay_visibility_only') is not True:
        errors.append('publication cadence may update only aggregate replay-visibility posture')
    if publication.get('window_relation_to_previous') == 'adjacent_exact_windows':
        errors.append('aggregate publication cadence must not export exact adjacent reporting windows')
    if publication.get('differencing_risk') in {'unbounded', 'unknown'}:
        errors.append('aggregate publication differencing risk must be bounded by suppression or policy-bound noise')
    seq = publication.get('publication_sequence')
    if isinstance(seq, int) and seq > 1 and not isinstance(publication.get('previous_publication_digest'), dict):
        errors.append('aggregate publication sequence after first publication requires previous_publication_digest')
    if publication.get('window_relation_to_previous') in {'non_overlapping', 'overlapping_suppression_safe'} and isinstance(seq, int) and seq > 1:
        prev = publication.get('previous_publication_digest', {}) if isinstance(publication.get('previous_publication_digest'), dict) else {}
        if prev.get('binds') != 'aggregate_verifier_audit_summary':
            errors.append('previous publication digest must bind aggregate_verifier_audit_summary')

    threshold = controls.get('suppression_threshold_equivalence', {}) if isinstance(controls.get('suppression_threshold_equivalence'), dict) else {}
    base_privacy = aggregate.get('privacy_boundary', {}) if isinstance(aggregate.get('privacy_boundary'), dict) else {}
    base_min = base_privacy.get('minimum_group_size')
    ctrl_min = threshold.get('minimum_group_size')
    if isinstance(base_min, int) and isinstance(ctrl_min, int) and ctrl_min < base_min:
        errors.append('aggregate privacy-controls minimum_group_size cannot be weaker than privacy_boundary minimum_group_size')
    if threshold.get('thresholds_weakened') is not False or threshold.get('compatible_operator_equivalence') == 'weaker_or_unknown':
        errors.append('aggregate suppression-threshold equivalence cannot be weaker_or_unknown or weaken thresholds')
    if threshold.get('threshold_basis') == 'unknown':
        errors.append('aggregate suppression-threshold basis cannot be unknown for published aggregate controls')
    scope = aggregate.get('aggregation_scope', {}) if isinstance(aggregate.get('aggregation_scope'), dict) else {}
    cross_operator = scope.get('operator_scope') == 'compatible_operator_cohort'
    needs_compat_digest = (
        cross_operator
        or threshold.get('compatible_operator_equivalence') == 'digest_bound_equivalent_or_stricter'
        or threshold.get('threshold_basis') == 'profile_compatibility_statement'
    )
    if needs_compat_digest and not digest_binds(threshold.get('compatibility_statement_digest'), 'profile_compatibility_statement'):
        errors.append('aggregate suppression-threshold compatibility_statement_digest must bind profile_compatibility_statement')
    elif not needs_compat_digest and isinstance(threshold.get('compatibility_statement_digest'), dict) and not digest_binds(threshold.get('compatibility_statement_digest'), 'profile_compatibility_statement'):
        errors.append('aggregate suppression-threshold compatibility_statement_digest must bind profile_compatibility_statement when present')

    noise = controls.get('statistical_noise', {}) if isinstance(controls.get('statistical_noise'), dict) else {}
    errors.extend(_boundary_false_errors(noise, (
        'budget_material_exported',
        'noise_parameters_exported',
        'noise_used_to_desuppress_small_groups',
    ), 'aggregate_privacy_controls.statistical_noise'))
    if noise.get('count_semantics') == 'noisy_count':
        if noise.get('noise_status') != 'applied_policy_bound' or not isinstance(noise.get('privacy_policy_digest'), dict):
            errors.append('noisy aggregate counts require applied_policy_bound status and privacy_policy_digest')
        elif not digest_binds(noise.get('privacy_policy_digest'), 'aggregate_privacy_policy_rules'):
            errors.append('noisy aggregate counts privacy_policy_digest must bind aggregate_privacy_policy_rules')
    if noise.get('noise_status') == 'applied_policy_bound' and noise.get('count_semantics') != 'noisy_count':
        errors.append('applied policy-bound noise must declare noisy_count count_semantics')
    if noise.get('count_semantics') == 'suppressed_count' and noise.get('noise_status') == 'applied_policy_bound':
        errors.append('suppressed aggregate counts must not be represented as policy-bound noisy counts')

    counts = aggregate.get('counts', {}) if isinstance(aggregate.get('counts'), dict) else {}
    total = _non_negative_int(counts.get('total_replay_events'))
    minimum = base_privacy.get('minimum_group_size')
    if isinstance(minimum, int) and total < minimum and counts.get('small_group_suppressed') is not True:
        # Keep legacy wording from the aggregate-count check while also detecting noise-based de-suppression.
        if noise.get('noise_status') == 'applied_policy_bound' or noise.get('count_semantics') == 'noisy_count':
            errors.append('statistical noise cannot be used to desuppress aggregate counts below minimum group size')
    return errors


def check_compromise_era_suppression(aggregate: dict[str, Any]) -> list[str]:
    """Privacy-preserving compromise-era suppression checks for aggregate audit summaries."""
    errors: list[str] = []
    ces = aggregate.get('compromise_era_suppression') if isinstance(aggregate.get('compromise_era_suppression'), dict) else None
    if ces is None:
        return errors
    boundary = ces.get('suppression_boundary', {}) if isinstance(ces.get('suppression_boundary'), dict) else {}
    errors.extend(_boundary_false_errors(boundary, (
        'incident_id_exported',
        'incident_forensics_exported',
        'affected_authority_identity_exported',
        'affected_result_ids_exported',
        'verifier_identity_exported',
        'legal_authority_details_exported',
        'exact_incident_window_exported',
        'external_incident_record_interpreted_as_timesync_provenance',
        'suppression_updates_profile_assessment',
    ), 'compromise_era_suppression'))
    if boundary.get('suppression_updates_replay_visibility_only') is not True:
        errors.append('compromise-era suppression may update only aggregate replay-visibility posture')
    if ces.get('window_granularity') == 'exact_incident_window' or boundary.get('exact_incident_window_exported') is True:
        errors.append('compromise-era suppression must not export exact incident-window timing')
    if ces.get('replay_visibility_effect') == 'current_replay_visibility':
        errors.append('aggregate compromise-era suppression cannot be promoted to current replay visibility')
    minimum = ces.get('minimum_group_size')
    affected_events = ces.get('affected_replay_event_count', 0)
    affected_results = ces.get('affected_challenge_result_count', 0)
    if not isinstance(affected_events, int):
        affected_events = 0
    if not isinstance(affected_results, int):
        affected_results = 0
    affected = max(affected_events, affected_results)
    if isinstance(minimum, int) and affected > 0 and affected < minimum and ces.get('small_group_suppressed') is not True:
        errors.append('compromise-era aggregate counts below minimum group size must be suppressed')
    if ces.get('status') in {'compromise_era_reported_aggregate', 'recovery_window_reported_aggregate'}:
        if isinstance(minimum, int) and affected < minimum:
            errors.append('reported compromise-era aggregate must meet minimum group size')
        if ces.get('small_group_suppressed') is not False:
            errors.append('reported compromise-era aggregate must not be marked small_group_suppressed')
    if ces.get('status') == 'compromise_era_suppressed' and ces.get('small_group_suppressed') is not True:
        errors.append('suppressed compromise-era aggregate must mark small_group_suppressed true')
    return errors


def check_recovery_audit_rollup(aggregate: dict[str, Any]) -> list[str]:
    """Privacy-preserving lifecycle-authority recovery audit rollup checks."""
    errors: list[str] = []
    roll = aggregate.get('recovery_audit_rollup') if isinstance(aggregate.get('recovery_audit_rollup'), dict) else None
    if roll is None:
        return errors
    boundary = roll.get('rollup_boundary', {}) if isinstance(roll.get('rollup_boundary'), dict) else {}
    errors.extend(_boundary_false_errors(boundary, (
        'attestation_ids_exported',
        'incident_ids_exported',
        'authority_identity_exported',
        'verifier_identity_exported',
        'incident_forensics_exported',
        'legal_authority_details_exported',
        'compatibility_statement_material_exported',
        'external_recovery_record_interpreted_as_timesync_provenance',
        'rollup_is_profile_evidence',
        'rollup_updates_actionability',
        'rollup_reopens_assessment',
    ), 'recovery_audit_rollup'))
    if boundary.get('rollup_updates_replay_visibility_only') is not True:
        errors.append('recovery audit rollup may update only aggregate replay-visibility posture')
    if roll.get('replay_visibility_effect') == 'current_replay_visibility':
        errors.append('aggregate recovery audit rollup cannot be promoted to current replay visibility')
    minimum = roll.get('minimum_group_size')
    counts = []
    for key in ('current_recovered_count', 'historical_only_count', 'contested_count', 'unknown_or_suppressed_count', 'expired_attestation_count'):
        val = roll.get(key, 0)
        counts.append(val if isinstance(val, int) else 0)
    total = sum(counts)
    if isinstance(minimum, int) and total > 0 and total < minimum and roll.get('small_group_suppressed') is not True:
        errors.append('recovery audit rollup counts below minimum group size must be suppressed')
    if roll.get('status') == 'reported_aggregate':
        if isinstance(minimum, int) and total < minimum:
            errors.append('reported recovery audit rollup must meet minimum group size')
        if roll.get('small_group_suppressed') is not False:
            errors.append('reported recovery audit rollup must not be marked small_group_suppressed')
    if roll.get('status') in {'reported_suppressed', 'insufficient_group_suppressed'} and roll.get('small_group_suppressed') is not True:
        errors.append('suppressed recovery audit rollup must mark small_group_suppressed true')
    if roll.get('compatible_operator_rollup_state') == 'portable_without_compatibility':
        errors.append('cross-operator recovery audit rollup portability requires compatibility digest')
    if roll.get('compatible_operator_rollup_state') == 'compatible_operator_digest_bound' and not digest_binds(roll.get('compatibility_statement_digest'), 'profile_compatibility_statement'):
        errors.append('cross-operator recovery audit rollup compatibility_statement_digest must bind profile_compatibility_statement')
    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    base_aggregate = {
        'aggregation_scope': {'operator_scope': 'compatible_operator_cohort'},
        'privacy_boundary': {'minimum_group_size': 5},
        'counts': {'total_replay_events': 8, 'small_group_suppressed': False},
        'aggregate_privacy_controls': {
            'publication_cadence': {
                'publication_sequence': 2,
                'window_relation_to_previous': 'non_overlapping',
                'differencing_risk': 'bounded_by_suppression',
                'previous_publication_digest': {'algorithm': 'sha256', 'value': 'a' * 64, 'binds': 'aggregate_verifier_audit_summary'},
                'publication_boundary': {
                    'exact_adjacent_windows_exported': False,
                    'cross_publication_reconstruction_material_exported': False,
                    'publication_sequence_updates_profile_assessment': False,
                    'publication_cadence_updates_replay_visibility_only': True,
                },
            },
            'suppression_threshold_equivalence': {
                'threshold_basis': 'profile_compatibility_statement',
                'minimum_group_size': 5,
                'compatible_operator_equivalence': 'digest_bound_equivalent_or_stricter',
                'thresholds_weakened': False,
                'compatibility_statement_digest': {'algorithm': 'sha256', 'value': 'b' * 64, 'binds': 'profile_compatibility_statement'},
            },
            'statistical_noise': {
                'noise_status': 'not_applied',
                'count_semantics': 'exact_count',
                'budget_material_exported': False,
                'noise_parameters_exported': False,
                'noise_used_to_desuppress_small_groups': False,
            },
            'privacy_boundary': {
                'privacy_controls_are_profile_evidence': False,
                'privacy_controls_update_actionability': False,
                'privacy_controls_reopen_assessment': False,
                'privacy_controls_identify_verifiers_or_results': False,
                'privacy_controls_interpreted_as_timesync_provenance': False,
            },
        },
    }
    if check_aggregate_privacy_controls(base_aggregate):
        errors.append('valid aggregate privacy controls failed self-test')

    wrong_threshold_bind = {**base_aggregate, 'aggregate_privacy_controls': dict(base_aggregate['aggregate_privacy_controls'])}
    wrong_threshold_bind['aggregate_privacy_controls']['suppression_threshold_equivalence'] = dict(base_aggregate['aggregate_privacy_controls']['suppression_threshold_equivalence'])
    wrong_threshold_bind['aggregate_privacy_controls']['suppression_threshold_equivalence']['compatibility_statement_digest'] = {'algorithm': 'sha256', 'value': 'b' * 64, 'binds': 'aggregate_privacy_policy_rules'}
    if not any('compatibility_statement_digest must bind profile_compatibility_statement' in e for e in check_aggregate_privacy_controls(wrong_threshold_bind)):
        errors.append('wrong suppression-threshold compatibility digest bind was not rejected')

    missing_threshold_digest = {**base_aggregate, 'aggregation_scope': {'operator_scope': 'single_operator'}, 'aggregate_privacy_controls': dict(base_aggregate['aggregate_privacy_controls'])}
    missing_threshold_digest['aggregate_privacy_controls']['suppression_threshold_equivalence'] = dict(base_aggregate['aggregate_privacy_controls']['suppression_threshold_equivalence'])
    missing_threshold_digest['aggregate_privacy_controls']['suppression_threshold_equivalence']['compatible_operator_equivalence'] = 'not_applicable'
    missing_threshold_digest['aggregate_privacy_controls']['suppression_threshold_equivalence'].pop('compatibility_statement_digest')
    if not any('compatibility_statement_digest must bind profile_compatibility_statement' in e for e in check_aggregate_privacy_controls(missing_threshold_digest)):
        errors.append('profile_compatibility_statement threshold basis without digest was not rejected')

    noisy_wrong_bind = {**base_aggregate, 'aggregate_privacy_controls': dict(base_aggregate['aggregate_privacy_controls'])}
    noisy_wrong_bind['aggregate_privacy_controls']['suppression_threshold_equivalence'] = {
        'threshold_basis': 'local_policy',
        'minimum_group_size': 5,
        'compatible_operator_equivalence': 'not_applicable',
        'thresholds_weakened': False,
    }
    noisy_wrong_bind['aggregate_privacy_controls']['statistical_noise'] = {
        'noise_status': 'applied_policy_bound',
        'count_semantics': 'noisy_count',
        'budget_material_exported': False,
        'noise_parameters_exported': False,
        'noise_used_to_desuppress_small_groups': False,
        'privacy_policy_digest': {'algorithm': 'sha256', 'value': 'c' * 64, 'binds': 'profile_compatibility_statement'},
    }
    if not any('privacy_policy_digest must bind aggregate_privacy_policy_rules' in e for e in check_aggregate_privacy_controls(noisy_wrong_bind)):
        errors.append('noisy-count privacy policy digest wrong bind was not rejected')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync aggregate privacy semantic self-test passed.')

#!/usr/bin/env python3
"""Aggregate revision-lineage semantic checks.

Aggregate publication cadence and aggregate revision lineage both describe the
same publication artifact. Keep those compact surfaces aligned without turning
TimeSync into a publication repository or correction workflow engine.
"""
from __future__ import annotations

from typing import Any

from discovery_binding_semantics import digest_binds

CONCRETE_LINEAGE_STATUSES = {'corrected', 'withdrawn', 'superseded', 'reconciled'}


def _boundary_false_errors(boundary: dict[str, Any], keys: tuple[str, ...], label: str) -> list[str]:
    errors: list[str] = []
    for key in keys:
        if boundary.get(key) is not False:
            errors.append(f'{label} boundary.{key} must be false')
    return errors


def _digest_identity(digest: Any) -> tuple[Any, Any, Any] | None:
    if not isinstance(digest, dict):
        return None
    return (digest.get('algorithm'), digest.get('value'), digest.get('binds'))


def check_aggregate_revision_lineage_semantics(aggregate: dict[str, Any]) -> list[str]:
    """Check aggregate revision-lineage semantics and publication-cadence alignment."""
    errors: list[str] = []
    lineage = aggregate.get('aggregate_revision_lineage') if isinstance(aggregate.get('aggregate_revision_lineage'), dict) else None
    if lineage is None:
        return ['aggregate verifier audit summary requires aggregate_revision_lineage']

    boundary = lineage.get('lineage_boundary', {}) if isinstance(lineage.get('lineage_boundary'), dict) else {}
    errors.extend(_boundary_false_errors(boundary, (
        'prior_publication_rewritten',
        'suppressed_delta_exported',
        'individual_result_identifiers_exported',
        'verifier_identity_exported',
        'correction_updates_profile_assessment',
        'external_correction_record_interpreted_as_timesync_provenance',
    ), 'aggregate_revision_lineage'))
    if boundary.get('correction_updates_replay_visibility_only') is not True:
        errors.append('aggregate revision lineage may update only aggregate replay-visibility posture')

    status = lineage.get('status')
    seq = lineage.get('publication_sequence')
    prev_seq = lineage.get('previous_publication_sequence')
    requires_prior = status in CONCRETE_LINEAGE_STATUSES

    controls = aggregate.get('aggregate_privacy_controls', {}) if isinstance(aggregate.get('aggregate_privacy_controls'), dict) else {}
    publication = controls.get('publication_cadence', {}) if isinstance(controls.get('publication_cadence'), dict) else {}
    pub_seq = publication.get('publication_sequence')
    if isinstance(seq, int) and isinstance(pub_seq, int) and seq != pub_seq:
        errors.append('aggregate revision lineage publication_sequence must match aggregate_privacy_controls.publication_cadence.publication_sequence')

    if status == 'original':
        if lineage.get('prior_aggregate_digest') is not None or lineage.get('previous_publication_sequence') is not None:
            errors.append('original aggregate publication must not claim a prior aggregate digest or previous publication sequence')
        if lineage.get('correction_reason') not in {None, 'not_applicable'}:
            errors.append('original aggregate publication must not declare a correction reason')
    if requires_prior:
        if not digest_binds(lineage.get('prior_aggregate_digest'), 'aggregate_verifier_audit_summary'):
            errors.append(f'{status} aggregate publication requires prior_aggregate_digest binding aggregate_verifier_audit_summary')
        if not isinstance(seq, int) or seq <= 1:
            errors.append(f'{status} aggregate publication must have publication_sequence greater than 1')
        if not isinstance(prev_seq, int):
            errors.append(f'{status} aggregate publication requires previous_publication_sequence')
        elif isinstance(seq, int) and prev_seq >= seq:
            errors.append('aggregate publication lineage sequence must be monotonic across corrections')
        if lineage.get('correction_reason') in {None, 'not_applicable'}:
            errors.append(f'{status} aggregate publication requires a non_not_applicable correction_reason')
        if lineage.get('correction_effect') in {'current_replay_visibility', 'profile_assessment_update'}:
            errors.append('aggregate correction lineage cannot be promoted to current replay visibility or profile assessment update')
        if lineage.get('correction_effect') == 'unknown':
            errors.append('aggregate correction lineage with a concrete revision status cannot use unknown correction_effect')

    revision_chain_digest = lineage.get('revision_chain_digest')
    if revision_chain_digest is not None and not digest_binds(revision_chain_digest, 'aggregate_publication_revision_chain'):
        errors.append('aggregate revision_chain_digest must bind aggregate_publication_revision_chain')

    if requires_prior and isinstance(seq, int) and isinstance(prev_seq, int) and isinstance(pub_seq, int) and prev_seq == pub_seq - 1:
        prior_identity = _digest_identity(lineage.get('prior_aggregate_digest'))
        previous_identity = _digest_identity(publication.get('previous_publication_digest'))
        if prior_identity is not None and previous_identity is not None and prior_identity != previous_identity:
            errors.append('aggregate lineage prior_aggregate_digest must match publication_cadence.previous_publication_digest for immediate predecessor corrections')

    if status == 'withdrawn' and lineage.get('withdrawal_disposition') in {None, 'not_applicable'}:
        errors.append('withdrawn aggregate publication requires historical, contested, or unknown withdrawal_disposition')
    if status == 'superseded' and not digest_binds(lineage.get('supersedes_aggregate_digest'), 'aggregate_verifier_audit_summary'):
        errors.append('superseded aggregate publication requires supersedes_aggregate_digest binding aggregate_verifier_audit_summary')

    reconciliation = lineage.get('reconciliation') if isinstance(lineage.get('reconciliation'), dict) else None
    if status == 'reconciled' and reconciliation is None:
        errors.append('reconciled aggregate publication requires reconciliation object')
    if reconciliation is not None:
        rb = reconciliation.get('reconciliation_boundary', {}) if isinstance(reconciliation.get('reconciliation_boundary'), dict) else {}
        errors.extend(_boundary_false_errors(rb, (
            'suppressed_deltas_exported',
            'individual_result_identifiers_exported',
            'adjacent_exact_windows_exported',
            'reconciliation_updates_profile_assessment',
            'external_reconciliation_record_interpreted_as_timesync_provenance',
        ), 'aggregate_revision_lineage.reconciliation'))
        if rb.get('reconciliation_updates_replay_visibility_only') is not True:
            errors.append('aggregate longitudinal reconciliation may update only aggregate replay-visibility posture')
        if reconciliation.get('status') == 'unbounded_or_unknown':
            errors.append('aggregate longitudinal reconciliation cannot be unbounded_or_unknown')
        if reconciliation.get('window_relation') in {'adjacent_exact_windows', 'unknown'}:
            errors.append('aggregate longitudinal reconciliation must not expose adjacent exact windows or unknown window relation')
        if reconciliation.get('cumulative_count_semantics') == 'reported_aggregate' and reconciliation.get('status') == 'reconciled_with_suppression':
            errors.append('suppression-aware reconciliation must not report raw aggregate cumulative counts')
        if status == 'reconciled':
            if not digest_binds(reconciliation.get('previous_chain_digest'), 'aggregate_publication_revision_chain'):
                errors.append('reconciled aggregate publication requires previous_chain_digest binding aggregate_publication_revision_chain')
            if not digest_binds(reconciliation.get('chain_head_digest'), 'aggregate_publication_revision_chain'):
                errors.append('reconciled aggregate publication requires chain_head_digest binding aggregate_publication_revision_chain')
    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    base_digest = {'algorithm': 'sha256', 'value': 'a' * 64, 'binds': 'aggregate_verifier_audit_summary'}
    chain_digest = {'algorithm': 'sha256', 'value': 'b' * 64, 'binds': 'aggregate_publication_revision_chain'}
    aggregate = {
        'aggregate_privacy_controls': {
            'publication_cadence': {
                'publication_sequence': 2,
                'previous_publication_digest': base_digest,
            }
        },
        'aggregate_revision_lineage': {
            'status': 'corrected',
            'publication_sequence': 2,
            'previous_publication_sequence': 1,
            'prior_aggregate_digest': base_digest,
            'revision_chain_digest': chain_digest,
            'correction_reason': 'count_correction',
            'correction_effect': 'aggregate_posture_only',
            'withdrawal_disposition': 'not_applicable',
            'lineage_boundary': {
                'prior_publication_rewritten': False,
                'suppressed_delta_exported': False,
                'individual_result_identifiers_exported': False,
                'verifier_identity_exported': False,
                'correction_updates_profile_assessment': False,
                'correction_updates_replay_visibility_only': True,
                'external_correction_record_interpreted_as_timesync_provenance': False,
            },
        },
    }
    if check_aggregate_revision_lineage_semantics(aggregate):
        errors.append('aggregate_lineage_semantics self-test valid fixture failed')
    bad = {
        **aggregate,
        'aggregate_revision_lineage': {
            **aggregate['aggregate_revision_lineage'],
            'publication_sequence': 3,
        },
    }
    if not any('publication_sequence must match' in e for e in check_aggregate_revision_lineage_semantics(bad)):
        errors.append('aggregate_lineage_semantics self-test failed to catch sequence mismatch')
    bad_digest = {
        **aggregate,
        'aggregate_revision_lineage': {
            **aggregate['aggregate_revision_lineage'],
            'prior_aggregate_digest': {'algorithm': 'sha256', 'value': 'c' * 64, 'binds': 'aggregate_verifier_audit_summary'},
        },
    }
    if not any('prior_aggregate_digest must match' in e for e in check_aggregate_revision_lineage_semantics(bad_digest)):
        errors.append('aggregate_lineage_semantics self-test failed to catch immediate predecessor digest mismatch')
    bad_chain = {
        **aggregate,
        'aggregate_revision_lineage': {
            **aggregate['aggregate_revision_lineage'],
            'revision_chain_digest': {'algorithm': 'sha256', 'value': 'd' * 64, 'binds': 'aggregate_verifier_audit_summary'},
        },
    }
    if not any('revision_chain_digest must bind' in e for e in check_aggregate_revision_lineage_semantics(bad_chain)):
        errors.append('aggregate_lineage_semantics self-test failed to catch revision chain digest binding')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync aggregate lineage semantic self-test passed.')

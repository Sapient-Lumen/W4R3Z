#!/usr/bin/env python3
"""Evaluator evidence-summary semantic checks for TimeSync archives.

This module owns evidence-summary obligation usability, redacted external
reference guardrails, profile-map binding checks, and evidence-class catalog
consistency.  The archive validator supplies JSON Schema validation for the
embedded redacted-external-evidence-reference schema so this module can remain
focused on semantic invariants rather than schema loading.
"""
from __future__ import annotations

from typing import Any, Callable

from profile_reference_binding import check_profile_reference_binding

SchemaValidateExternalReference = Callable[[dict[str, Any]], list[str]]

EVIDENCE_CLASSES = {
    'local_measurement_summary',
    'authenticated_source_claim',
    'unauthenticated_source_claim',
    'source_diversity_summary',
    'operator_configuration',
    'validity_horizon_summary',
    'profile_catalog_rule',
    'local_policy_rule',
    'external_evidence_reference',
    'authorized_verifier_disclosure',
    'replay_transparency_receipt',
    'witness_cohort_summary',
    'transparency_trust_policy_reference',
    'lifecycle_authority_rotation_summary',
    'lifecycle_authority_recovery_attestation',
    'recovery_audit_rollup_summary',
    'aggregate_privacy_control_summary',
    'aggregate_revision_lineage_summary',
    'aggregate_correction_authority_summary',
    'aggregate_correction_authority_lifecycle_summary',
    'portable_digest_binding_policy_summary',
    'scope_composition_guard_summary',
    'retained_prior_assessment',
    'transport_metadata_only',
    'not_observed',
}

FORBIDDEN_OBLIGATION_EVIDENCE = {
    'unauthenticated_source_claim',
    'transport_metadata_only',
    'not_observed',
    'retained_prior_assessment',
    'authorized_verifier_disclosure',
    'replay_transparency_receipt',
    'witness_cohort_summary',
    'transparency_trust_policy_reference',
    'lifecycle_authority_rotation_summary',
    'lifecycle_authority_recovery_attestation',
    'recovery_audit_rollup_summary',
    'aggregate_privacy_control_summary',
    'aggregate_revision_lineage_summary',
    'aggregate_correction_authority_summary',
    'aggregate_correction_authority_lifecycle_summary',
    'portable_digest_binding_policy_summary',
    'scope_composition_guard_summary',
}

UNUSABLE_VALUE_STATES_FOR_MET_OBLIGATION = {'ignored', 'conflicting', 'withdrawn'}


def resolve_profile(
    ref: dict[str, Any],
    catalog_index: dict[tuple[str | None, str, str | None], dict[str, Any]],
) -> dict[str, Any] | None:
    pid = ref.get('id')
    version = ref.get('version') or ref.get('revision')
    authority = ref.get('authority')
    if not pid:
        return None
    return catalog_index.get((authority, pid, version)) or catalog_index.get((None, pid, version))


def same_profile_ref(a: dict[str, Any], b: dict[str, Any]) -> bool:
    return (
        a.get('authority'),
        a.get('id'),
        a.get('version') or a.get('revision'),
    ) == (
        b.get('authority'),
        b.get('id'),
        b.get('version') or b.get('revision'),
    )


def forbidden_obligation_classes(catalog: dict[str, Any] | None = None) -> set[str]:
    """Evidence classes marked false in the evaluator catalog cannot satisfy obligations."""
    if catalog is None:
        return set(FORBIDDEN_OBLIGATION_EVIDENCE)
    return {
        c.get('name')
        for c in catalog.get('classes', [])
        if c.get('may_satisfy_profile_obligation') is False and c.get('name')
    }


def check_evidence_class_catalog(catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    names = [c.get('name') for c in catalog.get('classes', [])]
    if set(names) != EVIDENCE_CLASSES:
        errors.append(f'evidence class catalog mismatch: {sorted(set(names))}')
    if len(names) != len(set(names)):
        errors.append('evidence class catalog has duplicate classes')
    lookup = {c.get('name'): c for c in catalog.get('classes', [])}
    for name in forbidden_obligation_classes(catalog):
        if lookup.get(name, {}).get('may_satisfy_profile_obligation') is not False:
            errors.append(f'{name} must not satisfy profile obligations')
    lanes = {x.get('name') for x in catalog.get('visibility_lanes', [])}
    if lanes != {'local_only', 'requestable', 'profile_default', 'retention_only'}:
        errors.append(f'evidence visibility lanes mismatch: {sorted(lanes)}')
    return errors


NOT_TIME_BOUND_MINIMUM_ITEMS = {
    'profile.required_items',
    'profile.profile_default_items',
    'profile.fallback_mappings',
    'extension_hooks.sync_dimension',
}

ASSESSMENT_MINIMUM_FACTS = {
    'assessment.assessment_id',
    'assessment.assessment_time',
    'assessment.assessed_profile',
    'assessment.profile_conformance',
    'assessment.applicability',
}


def _minimum_item_requires_current_freshness(name: str) -> bool:
    return name not in NOT_TIME_BOUND_MINIMUM_ITEMS and name not in ASSESSMENT_MINIMUM_FACTS


def evidence_summary_minimum_item_errors(
    summary: dict[str, Any],
    name: str,
    *,
    forbidden: set[str],
    require_usable: bool,
) -> list[str]:
    """Return semantic errors for one profile ``minimum_summary_items`` entry.

    Earlier validation treated an input item name as sufficient for every
    profile-conformance outcome.  That is still acceptable for failed or
    unsatisfied summaries, where a minimum item can be present precisely to show
    absence or conflict.  For a ``satisfied`` summary, however, an input item that
    makes a minimum current-state claim must pass the same basic usability guards
    as evidence named by a met obligation.
    """
    errors: list[str] = []
    input_items = [item for item in summary.get('input_items', []) if isinstance(item, dict)]
    matches = [item for item in input_items if item.get('name') == name]
    if matches:
        if not require_usable:
            return []
        usable = False
        detail_errors: list[str] = []
        for item in matches:
            item_errors = _check_met_obligation_item_usability({'item': name}, item, forbidden=forbidden)
            if _minimum_item_requires_current_freshness(name) and item.get('freshness_relation') != 'current_at_assessment':
                item_errors.append(
                    f'evidence summary minimum_summary_item {name} requires freshness_relation current_at_assessment'
                )
            if item_errors:
                detail_errors.extend(item_errors)
            else:
                usable = True
        if not usable:
            errors.append(f'evidence summary minimum_summary_item {name} is present but not usable')
            errors.extend(detail_errors)
        return errors

    conclusion = summary.get('conclusion_binding', {})
    decision = summary.get('decision_outputs', {})
    if name == 'assessment.assessment_id':
        return [] if conclusion.get('assessment_id') else [f'evidence summary missing minimum_summary_item {name}']
    if name == 'assessment.assessment_time':
        return [] if summary.get('assessment_time') else [f'evidence summary missing minimum_summary_item {name}']
    if name == 'assessment.assessed_profile':
        return [] if isinstance(summary.get('assessed_profile'), dict) else [f'evidence summary missing minimum_summary_item {name}']
    if name == 'assessment.profile_conformance':
        return [] if bool(conclusion.get('profile_conformance')) and bool(decision.get('profile_conformance')) else [f'evidence summary missing minimum_summary_item {name}']
    if name == 'assessment.applicability':
        return [] if bool(conclusion.get('applicability')) and bool(decision.get('applicability')) else [f'evidence summary missing minimum_summary_item {name}']
    return [f'evidence summary missing minimum_summary_item {name}']


def evidence_summary_satisfies_minimum_item(summary: dict[str, Any], name: str) -> bool:
    """Compatibility wrapper for older tests; prefer minimum-item errors."""
    return not evidence_summary_minimum_item_errors(
        summary,
        name,
        forbidden=forbidden_obligation_classes(),
        require_usable=summary.get('decision_outputs', {}).get('profile_conformance') == 'satisfied',
    )


def check_external_evidence_reference(
    ref: dict[str, Any],
    item: dict[str, Any],
    *,
    schema_validate_external_reference: SchemaValidateExternalReference | None = None,
) -> list[str]:
    """Semantic guardrails for redacted external evidence references."""
    errors: list[str] = []
    if schema_validate_external_reference is not None:
        errors.extend(schema_validate_external_reference(ref))
    if ref.get('external_provenance_not_interpreted') is not True:
        errors.append('external_evidence_reference external provenance must not be interpreted as TimeSync provenance')
    handle = str(ref.get('handle', ''))
    if ref.get('handle_disclosure') == 'opaque' and '://' in handle:
        errors.append('opaque external_evidence_reference handle must not be a direct URI')
    commitment = ref.get('commitment')
    if item.get('value_state') == 'redacted':
        if not isinstance(commitment, dict):
            errors.append('redacted evidence item with external_evidence_reference requires salted commitment')
        elif commitment.get('low_cardinality_protection') is not True:
            errors.append('redacted evidence item commitment must assert low_cardinality_protection')
    if isinstance(commitment, dict):
        salt = commitment.get('salt', {})
        if commitment.get('scheme', '').startswith('salted_') and not isinstance(salt, dict):
            errors.append('salted commitment requires salt metadata')
        elif isinstance(salt, dict) and salt.get('length_bytes', 0) < 16:
            errors.append('salted commitment salt length must be at least 16 bytes')
    return errors


def _redacted_item_has_commitment(item: dict[str, Any]) -> bool:
    ext_ref = item.get('external_evidence_reference')
    return isinstance(ext_ref, dict) and isinstance(ext_ref.get('commitment'), dict)


def _check_met_obligation_item_usability(
    obligation: dict[str, Any],
    item: dict[str, Any],
    *,
    forbidden: set[str],
) -> list[str]:
    errors: list[str] = []
    item_name = item.get('name')
    obligation_name = obligation.get('item')
    if item.get('presence') != 'present':
        errors.append(f'obligation {obligation_name} is met using non-present evidence item {item_name}')
    if item.get('value_state') in UNUSABLE_VALUE_STATES_FOR_MET_OBLIGATION:
        errors.append(f'obligation {obligation_name} is met using unusable evidence value_state {item.get("value_state")} for {item_name}')
    if item.get('used_for') == 'not_used':
        errors.append(f'obligation {obligation_name} is met using evidence item marked not_used: {item_name}')
    if item.get('value_state') == 'redacted' and not _redacted_item_has_commitment(item):
        errors.append(f'obligation {obligation_name} is met using redacted evidence item without salted commitment: {item_name}')
    if item.get('evidence_class') in forbidden:
        errors.append(f'obligation {obligation_name} is met using forbidden evidence class {item.get("evidence_class")}')
    return errors


def check_evidence_summary(
    summary: dict[str, Any],
    catalog_index: dict[tuple[str | None, str, str | None], dict[str, Any]],
    assessment: dict[str, Any] | None = None,
    *,
    schema_validate_external_reference: SchemaValidateExternalReference | None = None,
) -> list[str]:
    errors: list[str] = []
    forbidden = forbidden_obligation_classes()
    ref = summary.get('assessed_profile', {})
    profile = resolve_profile(ref, catalog_index) if isinstance(ref, dict) else None
    if isinstance(ref, dict):
        errors.extend(check_profile_reference_binding(
            ref,
            used_at=summary.get('assessment_time'),
            used_at_label='evidence summary assessment_time',
            prefix='evidence summary assessed_profile',
        ))
    if profile is not None and ref.get('digest'):
        expected_digest = profile.get('normative_rules_digest', {}).get('value')
        if ref.get('digest', {}).get('value') != expected_digest:
            errors.append(f'evidence summary assessed_profile digest does not match catalog for {profile.get("id")}')

    if profile is not None:
        app = summary.get('decision_outputs', {}).get('applicability')
        labels = {x['name'] for x in profile.get('applicability_labels', [])}
        if app and app not in labels:
            errors.append(f'evidence summary applicability {app!r} not in profile applicability map for {profile.get("id")}')
        minimum_errors: list[str] = []
        require_minimum_usability = summary.get('decision_outputs', {}).get('profile_conformance') == 'satisfied'
        for name in profile.get('evidence_policy', {}).get('minimum_summary_items', []):
            minimum_errors.extend(evidence_summary_minimum_item_errors(
                summary,
                name,
                forbidden=forbidden,
                require_usable=require_minimum_usability,
            ))
        if minimum_errors:
            errors.append(f'evidence summary minimum_summary_items unusable for {profile.get("id")}')
            errors.extend(minimum_errors)

    item_by_name: dict[str, dict[str, Any]] = {}
    for item in summary.get('input_items', []):
        if not isinstance(item, dict):
            continue
        name = item.get('name')
        if name in item_by_name:
            errors.append(f'duplicate evidence input item {name}')
        if isinstance(name, str):
            item_by_name[name] = item
        if item.get('evidence_class') == 'transport_metadata_only' and item.get('used_for') != 'not_used':
            errors.append('transport_metadata_only cannot be used for profile obligations or evaluator conclusions')
        if item.get('evidence_class') == 'not_observed' and item.get('presence') == 'present':
            errors.append('not_observed evidence class cannot have present presence')
        if item.get('evidence_class') in forbidden and item.get('used_for') == 'profile_obligation':
            errors.append(f"{item.get('evidence_class')} cannot be used_for profile_obligation")
        ext_ref = item.get('external_evidence_reference')
        if isinstance(ext_ref, dict):
            errors.extend(check_external_evidence_reference(
                ext_ref,
                item,
                schema_validate_external_reference=schema_validate_external_reference,
            ))
        if item.get('evidence_class') in {'external_evidence_reference', 'authorized_verifier_disclosure'} and item.get('used_for') != 'not_used':
            errors.append(f"{item.get('evidence_class')} evidence class cannot be used for evaluator conclusions or profile obligations")
        if item.get('value_state') == 'redacted' and item.get('digest', {}).get('binds') == 'redacted_input_group':
            commitment = ext_ref.get('commitment') if isinstance(ext_ref, dict) else None
            if not isinstance(commitment, dict):
                errors.append('redacted low-cardinality evidence values require a salted commitment; unsalted digest is not sufficient')

    if 'obligation_results' not in summary:
        errors.append('evidence summary missing obligation_results')
    for obligation in summary.get('obligation_results', []):
        if not isinstance(obligation, dict):
            continue
        ev_names = obligation.get('evidence_items', []) or []
        for ev_name in ev_names:
            if ev_name not in item_by_name:
                errors.append(f'obligation {obligation.get("item")} references unknown evidence item {ev_name}')
        if obligation.get('result') == 'met' and ev_names:
            for ev_name in ev_names:
                item = item_by_name.get(ev_name)
                if isinstance(item, dict):
                    errors.extend(_check_met_obligation_item_usability(obligation, item, forbidden=forbidden))

    decision = summary.get('decision_outputs', {})
    conclusion = summary.get('conclusion_binding', {})
    for field in ('profile_conformance', 'applicability'):
        if decision.get(field) != conclusion.get(field):
            errors.append(f'evidence summary decision_outputs.{field} does not match conclusion_binding.{field}')

    if decision.get('profile_conformance') == 'satisfied':
        bad = [
            o.get('item')
            for o in summary.get('obligation_results', [])
            if o.get('requirement_class') in {'required', 'profile_default'} and o.get('result') in {'missing', 'failed', 'unknown'}
        ]
        if bad:
            errors.append(f'satisfied evidence summary has unmet obligations: {bad}')

    guards = summary.get('non_provenance_guards', {})
    for key in (
        'source_roster_exported',
        'path_history_exported',
        'clock_algorithm_exported',
        'raw_observations_exported',
        'transport_authentication_promoted_to_traceability',
        'external_evidence_interpreted_as_provenance',
    ):
        if guards.get(key) is not False:
            errors.append(f'non_provenance_guards.{key} must be false')

    if assessment is not None:
        if conclusion.get('assessment_id') != assessment.get('assessment_id'):
            errors.append('evidence summary conclusion assessment_id does not match profile assessment')
        if summary.get('assessment_time') != assessment.get('assessment_time'):
            errors.append('evidence summary assessment_time does not match profile assessment')
        if not same_profile_ref(summary.get('assessed_profile', {}), assessment.get('assessed_profile', {})):
            errors.append('evidence summary assessed_profile does not match profile assessment')
        if conclusion.get('profile_conformance') != assessment.get('profile_conformance'):
            errors.append('evidence summary conclusion profile_conformance does not match profile assessment')
        if conclusion.get('applicability') != assessment.get('applicability'):
            errors.append('evidence summary conclusion applicability does not match profile assessment')
    return errors


def self_test() -> list[str]:
    base_item = {
        'name': 'traceability',
        'presence': 'present',
        'evidence_class': 'authenticated_source_claim',
        'used_for': 'profile_obligation',
        'value_state': 'accepted',
    }
    obligation = {'item': 'traceability_posture', 'result': 'met'}
    errors: list[str] = []
    if _check_met_obligation_item_usability(obligation, base_item, forbidden=forbidden_obligation_classes()):
        errors.append('evidence-summary self-test rejected usable accepted evidence')
    absent = dict(base_item, presence='absent')
    if not any('non-present evidence item' in e for e in _check_met_obligation_item_usability(obligation, absent, forbidden=forbidden_obligation_classes())):
        errors.append('evidence-summary self-test accepted absent evidence for met obligation')
    ignored = dict(base_item, value_state='ignored')
    if not any('unusable evidence value_state' in e for e in _check_met_obligation_item_usability(obligation, ignored, forbidden=forbidden_obligation_classes())):
        errors.append('evidence-summary self-test accepted ignored evidence for met obligation')
    redacted = dict(base_item, value_state='redacted')
    if not any('redacted evidence item without salted commitment' in e for e in _check_met_obligation_item_usability(obligation, redacted, forbidden=forbidden_obligation_classes())):
        errors.append('evidence-summary self-test accepted uncommitted redacted obligation evidence')
    forbidden_item = dict(base_item, evidence_class='transport_metadata_only', used_for='not_used')
    if not any('forbidden evidence class' in e for e in _check_met_obligation_item_usability(obligation, forbidden_item, forbidden=forbidden_obligation_classes())):
        errors.append('evidence-summary self-test accepted forbidden evidence class for met obligation')

    if not _minimum_item_requires_current_freshness('assessment.validity_horizon'):
        errors.append('evidence-summary self-test failed to require freshness for assessment.validity_horizon')
    if _minimum_item_requires_current_freshness('assessment.profile_conformance'):
        errors.append('evidence-summary self-test wrongly required freshness for assessment.profile_conformance fact')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync evidence-summary semantic self-test passed.')

#!/usr/bin/env python3
"""Validation helper for the current TimeSync release.

Checks:
- JSON syntax for schemas, examples, profile catalog, transport catalog, evaluator catalog, manifest, and receipt.
- JSON Schema validation for fixtures.
- Acceptance-test YAML structure.
- Semantic invariants that JSON Schema does not express cleanly:
  * interval ordering
  * profile catalog digest consistency and exact resolved profile-reference digest values
  * profile-local applicability label membership
  * fallback target validity and non-stronger rank
  * required/default item presence for profile fixtures
  * current-policy actionability consistency
  * transport adapter catalog consistency
  * nested transport-envelope payload semantics
  * retained export retained-state, profile-reference-strength, and evidence-summary rules
  * evaluator evidence summary binding and non-provenance guardrails
  * manifest file hashes
  * JSON Schema date-time format assertions
  * duplicate semantic vector identifiers
  * RFC 8785/JCS-subset digest canonicalization self-tests
  * reusable temporal-coherence helper self-tests
  * discovery current-use freshness and version/digest binding alignment checks
  * authorized-verifier issue/response/revocation/replay-window checks
  * replay-transparency event/anchor/freshness/evaluation temporal checks
  * retained-export artifact-time and current-recheck temporal checks
  * transport-envelope semantic event timestamps do not occur after sent_at
  * transport-envelope binding_strength/protection/covers alignment
  * profile-assessment assessment_time does not postdate policy/validity checks
  * signed profile-reference bindings cover referenced identity/digest fields and do not postdate use
  * evidence-summary met obligations cannot rely on absent, ignored, withdrawn, or uncommitted redacted items
  * current-use discovery results require aligned version negotiation and digest binding metadata
  * transport capability advertisements cannot claim unknown profiles, impossible request items, or profile references for profile-forbidden adapters
  * aggregate revision-lineage sequence/digest metadata aligns with publication cadence
  * aggregate privacy controls bind cross-operator threshold/noise policy digests to the right artifact classes
  * external transparency receipt references bind statement/checkpoint/receipt digests to the right artifact classes
  * aggregate verifier audit publication periods do not extend beyond publication/check artifact time
  * profile compatibility statements have coherent issue/signature/expiry/drift timing
  * profile compatibility drift decisions require digest-bound equivalence for current digest-distinct reuse
  * scope-composition current surfaces require correct source_digest binding and temporal source-digest alignment
  * policy lifecycle-authority digest fields bind the artifact classes they claim to summarize
  * replay, aggregate correction-authority, and transparency trust-policy digest fields bind the artifact classes their local fields claim
  * transparency-policy equivalence evidence is not after equivalence evaluation or statement signature
  * aggregate lifecycle decision-table row posture checks
  * patch-derived negative fixture drift checks
  * semantic test-vector execution via reusable runner
  * I-JSON duplicate-member and string sanity checks
- Positive and negative fixture expectations from tests/semantic-test-vectors.yaml.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
import sys
from typing import Any

sys.dont_write_bytecode = True

from release_integrity import (
    check_release_integrity,
    current_revision,
    self_test as release_integrity_self_test,
)
from temporal_coherence import (
    check_active_window_status,
    check_discovery_result_freshness,
    check_scope_temporal_coherence,
    check_time_not_after,
    check_time_order,
    parse_dt,
    self_test as temporal_self_test,
)
from assessment_temporal import (
    check_policy_acceptance,
    check_profile_assessment_temporal,
    check_validity_horizon,
    self_test as assessment_temporal_self_test,
)
from jcs import JcsCanonicalizationError, load_json_ijson, self_test as jcs_self_test, sha256_hexdigest as jcs_sha256
from evidence_summary_semantics import (
    EVIDENCE_CLASSES,
    check_evidence_class_catalog,
    check_evidence_summary as check_evidence_summary_semantics,
    forbidden_obligation_classes,
    resolve_profile,
    same_profile_ref,
    self_test as evidence_summary_semantics_self_test,
)
from retained_export_temporal import check_retained_export_temporal, self_test as retained_export_temporal_self_test
from fixture_derivations import self_test as fixture_derivation_self_test, validate_derivations
from semantic_vectors import (
    check_example_vector_coverage,
    check_vector_ids as check_semantic_vector_ids,
    run_vectors as run_semantic_vectors,
    self_test as semantic_vectors_self_test,
)
from mutation_survivor_audit import (
    run_probes as run_mutation_survivor_probes,
    self_test as mutation_survivor_audit_self_test,
)
from chrony_adapter import self_test as chrony_adapter_self_test
from chrony_observation_eval import self_test as chrony_observation_eval_self_test
from ntpq_adapter import self_test as ntpq_adapter_self_test
from adapter_equivalence import self_test as adapter_equivalence_self_test
from multisource_adjudicator import self_test as multisource_adjudicator_self_test
from chrony_policy import self_test as chrony_policy_self_test
from profile_decision_acceptance import self_test as profile_decision_acceptance_self_test
from rfc9249_crosswalk import self_test as rfc9249_crosswalk_self_test
from transport_envelope_temporal import check_transport_envelope_temporal, self_test as transport_envelope_temporal_self_test
from transport_integrity import check_transport_integrity, self_test as transport_integrity_self_test
from transport_capability_semantics import (
    check_transport_capability_semantics,
    self_test as transport_capability_semantics_self_test,
)
from aggregate_temporal import check_aggregate_publication_temporal, self_test as aggregate_temporal_self_test
from aggregate_lifecycle_decision_semantics import (
    check_lifecycle_decision_table,
    expected_lifecycle_decision,
    self_test as aggregate_lifecycle_decision_semantics_self_test,
)
from aggregate_lineage_semantics import (
    check_aggregate_revision_lineage_semantics,
    self_test as aggregate_lineage_semantics_self_test,
)
from aggregate_privacy_semantics import (
    check_aggregate_privacy_controls,
    check_compromise_era_suppression,
    check_recovery_audit_rollup,
    self_test as aggregate_privacy_semantics_self_test,
)
from profile_compatibility_temporal import (
    check_profile_compatibility_statement_temporal,
    self_test as profile_compatibility_temporal_self_test,
)
from profile_drift_semantics import (
    check_profile_compatibility_drift_decision,
    check_profile_compatibility_drift_matrix,
    self_test as profile_drift_semantics_self_test,
)
from scope_composition_semantics import (
    check_scope_composition_decision_matrix,
    check_scope_composition_guard,
    self_test as scope_composition_semantics_self_test,
)
from policy_equivalence_temporal import (
    check_policy_lifecycle_equivalence_temporal,
    self_test as policy_equivalence_temporal_self_test,
)
from authorized_verifier_temporal import (
    check_authorized_verifier_temporal,
    self_test as authorized_verifier_temporal_self_test,
)
from authorized_verifier_result_semantics import (
    check_authorized_verifier_result_semantics,
    self_test as authorized_verifier_result_semantics_self_test,
)
from replay_transparency_temporal import (
    check_replay_transparency_temporal,
    self_test as replay_transparency_temporal_self_test,
)
from profile_reference_binding import (
    check_profile_reference_binding,
    self_test as profile_reference_binding_self_test,
)
from policy_lifecycle_temporal import (
    check_policy_lifecycle_authority_temporal,
    check_policy_lifecycle_recovery_temporal,
    self_test as policy_lifecycle_temporal_self_test,
)

from policy_authority_digest_semantics import (
    check_policy_lifecycle_authority_digest_bindings,
    check_policy_lifecycle_recovery_attestation_digest_bindings,
    self_test as policy_authority_digest_semantics_self_test,
)

from replay_digest_semantics import (
    check_replay_core_digest_bindings,
    self_test as replay_digest_semantics_self_test,
)
from aggregate_correction_digest_semantics import (
    check_aggregate_correction_authority_digest_bindings,
    self_test as aggregate_correction_digest_semantics_self_test,
)
from transparency_policy_digest_semantics import (
    check_transparency_policy_digest_bindings,
    self_test as transparency_policy_digest_semantics_self_test,
)

from external_receipt_semantics import (
    check_external_transparency_receipt_reference,
    self_test as external_receipt_semantics_self_test,
)

from discovery_binding_semantics import (
    check_current_result_binding,
    check_digest_binding_metadata,
    check_result_version_negotiation,
    digest_binds,
    parse_semver,
    self_test as discovery_binding_semantics_self_test,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ID_PREFIX = 'https://example.invalid/timesync/schema/'

SCHEMA_FILES = {
    'wire-claim': 'schema/wire-claim.schema.json',
    'local-assessed-state': 'schema/local-assessed-state.schema.json',
    'discovery-request': 'schema/discovery-request.schema.json',
    'profile-catalog': 'schema/profile-catalog.schema.json',
    'profile-compatibility-statement': 'schema/profile-compatibility-statement.schema.json',
    'profile-applicability-map': 'schema/profile-applicability-map.schema.json',
    'transport-envelope': 'schema/transport-envelope.schema.json',
    'transport-adapter': 'schema/transport-adapter.schema.json',
    'transport-adapter-catalog': 'schema/transport-adapter-catalog.schema.json',
    'transport-capability': 'schema/transport-capability.schema.json',
    'retained-export': 'schema/retained-export.schema.json',
    'evaluator-evidence-summary': 'schema/evaluator-evidence-summary.schema.json',
    'evidence-class-catalog': 'schema/evidence-class-catalog.schema.json',
    'validity-horizon': 'schema/validity-horizon.schema.json',
    'redacted-external-evidence-reference': 'schema/redacted-external-evidence-reference.schema.json',
    'authorized-verifier-challenge': 'schema/authorized-verifier-challenge.schema.json',
    'replay-transparency-audit': 'schema/replay-transparency-audit.schema.json',
    'transparency-trust-policy-reference': 'schema/transparency-trust-policy-reference.schema.json',
    'policy-lifecycle-authority-reference': 'schema/policy-lifecycle-authority-reference.schema.json',
    'policy-lifecycle-authority-recovery-attestation': 'schema/policy-lifecycle-authority-recovery-attestation.schema.json',
    'aggregate-correction-authority-reference': 'schema/aggregate-correction-authority-reference.schema.json',
    'aggregate-correction-authority-lifecycle': 'schema/aggregate-correction-authority-lifecycle.schema.json',
    'aggregate-lifecycle-decision-table': 'schema/aggregate-lifecycle-decision-table.schema.json',
    'digest-binding-policy': 'schema/digest-binding-policy.schema.json',
    'semantic-version-negotiation': 'schema/semantic-version-negotiation.schema.json',
    'profile-compatibility-drift-matrix': 'schema/profile-compatibility-drift-matrix.schema.json',
    'profile-compatibility-drift-decision': 'schema/profile-compatibility-drift-decision.schema.json',
    'scope-composition-guard': 'schema/scope-composition-guard.schema.json',
    'scope-composition-decision-matrix': 'schema/scope-composition-decision-matrix.schema.json',
}

CORE_JSON = [
    'MANIFEST.json',
    'REVISION-RECEIPT.json',
    'frontier-ticket.json',
    'profiles/profile-catalog.json',
    'transport/adapter-catalog.json',
    'evaluator/evidence-class-catalog.json',
    'evaluator/p1-chrony-policy.json',
    'schema/timestate.schema.json',
    'schema/wire-claim.schema.json',
    'schema/local-assessed-state.schema.json',
    'schema/profile.schema.json',
    'schema/profile-reference.schema.json',
    'schema/profile-assessment.schema.json',
    'schema/profile-catalog.schema.json',
    'schema/profile-compatibility-statement.schema.json',
    'schema/profile-applicability-map.schema.json',
    'schema/extension-hooks.schema.json',
    'schema/discovery-request.schema.json',
    'schema/boundary-context.schema.json',
    'schema/transport-envelope.schema.json',
    'schema/transport-adapter.schema.json',
    'schema/transport-adapter-catalog.schema.json',
    'schema/transport-capability.schema.json',
    'schema/retained-export.schema.json',
    'schema/evaluator-evidence-summary.schema.json',
    'schema/evidence-class-catalog.schema.json',
    'schema/validity-horizon.schema.json',
    'schema/redacted-external-evidence-reference.schema.json',
    'schema/authorized-verifier-challenge.schema.json',
    'schema/replay-transparency-audit.schema.json',
    'schema/transparency-trust-policy-reference.schema.json',
    'schema/policy-lifecycle-authority-reference.schema.json',
    'schema/policy-lifecycle-authority-recovery-attestation.schema.json',
    'schema/aggregate-correction-authority-reference.schema.json',
    'schema/aggregate-correction-authority-lifecycle.schema.json',
    'schema/aggregate-lifecycle-decision-table.schema.json',
    'schema/digest-binding-policy.schema.json',
    'schema/semantic-version-negotiation.schema.json',
    'schema/profile-compatibility-drift-matrix.schema.json',
    'schema/profile-compatibility-drift-decision.schema.json',
    'schema/scope-composition-guard.schema.json',
    'schema/scope-composition-decision-matrix.schema.json',
]

HOOK_PATHS = {
    'traceability_posture': ('extension_hooks', 'traceability_posture'),
    'sync_dimension': ('extension_hooks', 'sync_dimension'),
    'holdover_class': ('extension_hooks', 'holdover_class'),
    'validity_scope': ('extension_hooks', 'validity_scope'),
    'time_error_bound': ('extension_hooks', 'time_error_bound'),
    'rate_error_bound': ('extension_hooks', 'rate_error_bound'),
    'timescale_realization': ('extension_hooks', 'timescale_realization'),
    'clock_continuity_posture': ('extension_hooks', 'clock_continuity_posture'),
    'source_diversity_posture': ('extension_hooks', 'source_diversity_posture'),
    'pnt_risk_posture': ('extension_hooks', 'pnt_risk_posture'),
    'boundary_context': ('boundary_context',),
}
ASSESSMENT_ITEMS = {'assessment_time', 'assessed_profile', 'profile_conformance', 'policy_acceptance', 'validity_horizon'}
VALID_OBLIGATION_ITEMS = {'timestate'} | ASSESSMENT_ITEMS | set(HOOK_PATHS)
VALID_MINIMUM_SUMMARY_ITEMS = {
    'timestate.interval',
    'timestate.timescale',
    'timestate.freshness',
    'timestate.regime',
    'timestate.source_posture',
    'timestate.applicability',
    'assessment.assessment_id',
    'assessment.assessment_time',
    'assessment.assessed_profile',
    'assessment.profile_conformance',
    'assessment.applicability',
    'assessment.validity_horizon',
    'profile.required_items',
    'profile.profile_default_items',
    'profile.fallback_mappings',
    'policy_acceptance',
    'boundary_context',
    'validity_scope',
    'holdover_class',
    'extension_hooks.traceability_posture',
    'extension_hooks.sync_dimension',
    'extension_hooks.holdover_class',
    'extension_hooks.validity_scope',
    'extension_hooks.time_error_bound',
    'extension_hooks.rate_error_bound',
    'extension_hooks.timescale_realization',
    'extension_hooks.clock_continuity_posture',
    'extension_hooks.source_diversity_posture',
    'extension_hooks.pnt_risk_posture',
}
MESSAGE_TYPES = {'wire_claim', 'local_assessed_state', 'discovery_request', 'discovery_result', 'capability_advertisement', 'retained_assessment_export'}
def load_json(rel: str) -> Any:
    with (ROOT / rel).open('r', encoding='utf-8') as f:
        return load_json_ijson(f.read())


def load_yaml(rel: str) -> Any:
    import yaml  # type: ignore
    with (ROOT / rel).open('r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def canonical_sha(obj: Any) -> str:
    return jcs_sha256(obj)



def get_path(obj: dict[str, Any], path: tuple[str, ...]) -> Any:
    cur: Any = obj
    for part in path:
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def profile_key(ref: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    return (ref.get('authority'), ref.get('id'), ref.get('version') or ref.get('revision'))


def build_catalog_index(catalog: dict[str, Any]) -> dict[tuple[str | None, str, str | None], dict[str, Any]]:
    idx: dict[tuple[str | None, str, str | None], dict[str, Any]] = {}
    for rec in catalog.get('profiles', []):
        idx[(rec.get('authority'), rec['id'], rec.get('version'))] = rec
        idx[(None, rec['id'], rec.get('version'))] = rec
    return idx



def check_profile_catalog(catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[tuple[str, str, str]] = set()
    for rec in catalog.get('profiles', []):
        key = (rec.get('authority', ''), rec.get('id', ''), rec.get('version', ''))
        if key in seen_ids:
            errors.append(f'duplicate profile map {key}')
        seen_ids.add(key)

        labels = rec.get('applicability_labels', [])
        label_names = [x.get('name') for x in labels]
        ranks = {x.get('name'): x.get('rank') for x in labels}
        if len(label_names) != len(set(label_names)):
            errors.append(f"{rec['id']} has duplicate applicability labels")

        for m in rec.get('fallback_mappings', []):
            if m.get('from') not in ranks:
                errors.append(f"{rec['id']} fallback {m.get('name')} has unknown source label {m.get('from')}")
            if m.get('to') not in ranks:
                errors.append(f"{rec['id']} fallback {m.get('name')} has unknown target label {m.get('to')}")
            if m.get('from') in ranks and m.get('to') in ranks and ranks[m['to']] > ranks[m['from']]:
                errors.append(f"{rec['id']} fallback {m.get('name')} upgrades {m['from']} -> {m['to']}")

        ep = rec.get('evidence_policy', {})
        if ep:
            forbidden = set(ep.get('classes_that_cannot_satisfy_profile_obligations', []))
            false_classes = forbidden_obligation_classes()
            missing_false = false_classes - forbidden
            if missing_false:
                errors.append(f"{rec['id']} evidence_policy must forbid all non-satisfying evidence classes {sorted(missing_false)}")
            unknown_classes = forbidden - EVIDENCE_CLASSES
            if unknown_classes:
                errors.append(f"{rec['id']} evidence_policy references unknown evidence classes {sorted(unknown_classes)}")
            if ep.get('default_visibility') == 'retention_required':
                errors.append(f"{rec['id']} evidence_policy.default_visibility must be a visibility lane, not retention_required")
            if ep.get('default_visibility') == 'retention_only' and ep.get('retention_required') is not True:
                errors.append(f"{rec['id']} retention_only evidence policy must state retention_required true or use a requestable/profile_default lane")

        for bucket in ('required_items', 'profile_default_items', 'requestable_items'):
            for item in rec.get('obligations', {}).get(bucket, []):
                if item not in VALID_OBLIGATION_ITEMS:
                    errors.append(f"{rec['id']} obligations.{bucket} contains unknown item {item!r}")
        for item in rec.get('evidence_policy', {}).get('minimum_summary_items', []):
            if item not in VALID_MINIMUM_SUMMARY_ITEMS:
                errors.append(f"{rec['id']} evidence_policy.minimum_summary_items contains unknown item {item!r}")

        declared = rec.get('normative_rules_digest', {}).get('value')
        rule_obj = {k: v for k, v in rec.items() if k != 'normative_rules_digest'}
        try:
            computed = canonical_sha(rule_obj)
        except JcsCanonicalizationError as exc:
            errors.append(f"{rec['id']} normative_rules_digest canonicalization error: {exc}")
        else:
            if declared != computed:
                errors.append(f"{rec['id']} normative_rules_digest mismatch: declared {declared}, computed {computed}")
    return errors


def schema_validate(schema_name: str, obj: Any) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return [f'jsonschema dependency unavailable: {exc}']
    schema = load_json(SCHEMA_FILES[schema_name])
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    return [f"schema error at {'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in sorted(validator.iter_errors(obj), key=str)]


def check_interval_order(obj: dict[str, Any], prefix: str) -> list[str]:
    errors: list[str] = []
    if prefix == 'wire':
        interval = obj.get('interval_claim')
    else:
        interval = obj.get('timestate', {}).get('interval')
    if isinstance(interval, dict) and 'earliest' in interval and 'latest' in interval:
        try:
            if parse_dt(interval['earliest']) > parse_dt(interval['latest']):
                errors.append('interval earliest is after latest')
        except Exception as exc:  # noqa: BLE001
            errors.append(f'interval parse error: {exc}')
    return errors


def check_required_default_items(state: dict[str, Any], assessment: dict[str, Any], profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if assessment.get('profile_conformance') != 'satisfied':
        return errors
    items = list(profile.get('obligations', {}).get('required_items', [])) + list(profile.get('obligations', {}).get('profile_default_items', []))
    for item in items:
        if item == 'timestate':
            if 'timestate' not in state:
                errors.append('missing required item timestate')
        elif item in ASSESSMENT_ITEMS:
            if item not in assessment:
                errors.append(f'missing required item {item}')
        elif item in HOOK_PATHS:
            if get_path(state, HOOK_PATHS[item]) is None:
                errors.append(f'missing profile-default item {item}')
        else:
            pass
    return errors




def check_evidence_summary(summary: dict[str, Any], catalog_index: dict[tuple[str | None, str, str | None], dict[str, Any]], assessment: dict[str, Any] | None = None) -> list[str]:
    return check_evidence_summary_semantics(
        summary,
        catalog_index,
        assessment,
        schema_validate_external_reference=lambda ref: schema_validate('redacted-external-evidence-reference', ref),
    )


def check_extension_hook_values(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    hooks = state.get('extension_hooks', {}) if isinstance(state.get('extension_hooks', {}), dict) else {}
    timescale = state.get('timestate', {}).get('timescale')
    tr = hooks.get('timescale_realization')
    cc = hooks.get('clock_continuity_posture')
    tp = hooks.get('traceability_posture')
    sd = hooks.get('source_diversity_posture')

    if isinstance(tr, dict):
        scale = tr.get('scale')
        if timescale == 'UTC' and scale not in {'UTC', 'unknown'}:
            errors.append(f'timescale_realization.scale {scale!r} is inconsistent with timestate.timescale UTC')
        if timescale == 'local_private' and scale not in {'local_private', 'unknown'}:
            errors.append(f'timescale_realization.scale {scale!r} is inconsistent with timestate.timescale local_private')
        if tr.get('leap_handling') == 'smeared' and isinstance(cc, dict) and cc.get('smear_policy') in {'none', 'not_applicable'}:
            errors.append('clock_continuity_posture.smear_policy conflicts with smeared timescale_realization')
        if tr.get('leap_handling') in {'standard_utc', 'not_applicable'} and isinstance(cc, dict) and cc.get('smear_policy') == 'leap_smear':
            errors.append('clock_continuity_posture.smear_policy says leap_smear but timescale_realization is not smeared')

    if isinstance(tp, dict) and tp.get('reference_anchor') == 'utc_named_realization':
        if not isinstance(tr, dict):
            errors.append('traceability_posture utc_named_realization requires extension_hooks.timescale_realization')
        else:
            if tr.get('scale') != 'UTC':
                errors.append('traceability_posture utc_named_realization requires timescale_realization.scale UTC')
            if str(tr.get('realization', '')).strip().lower() in {'', 'utc', 'unqualified', 'unknown', 'utc_unqualified'}:
                errors.append('traceability_posture utc_named_realization requires a named timescale realization')
            if tp.get('evidence_posture') == 'traceable' and tr.get('evidence_posture') in {'claimed', 'unknown'}:
                errors.append('traceable utc_named_realization cannot be backed only by claimed/unknown timescale realization evidence')

    if isinstance(sd, dict):
        dep = sd.get('dependency_class')
        cmr = sd.get('common_mode_risk')
        if timescale is None:
            pass
        source_posture = state.get('timestate', {}).get('source_posture')
        if source_posture == 'single_source' and dep in {'multiple_sources_same_root', 'multiple_roots_common_distribution', 'multiple_independent_roots'}:
            errors.append('source_diversity_posture cannot claim multiple dependency roots when timestate.source_posture is single_source')
        if source_posture == 'multi_source_agreement' and dep == 'single_source':
            errors.append('multi_source_agreement cannot be paired with source_diversity_posture dependency_class single_source')
        if source_posture == 'authenticated_only' and dep in {'multiple_sources_same_root', 'multiple_roots_common_distribution', 'multiple_independent_roots'}:
            errors.append('authenticated_only source_posture cannot by itself support multiple-source source_diversity_posture')
        if source_posture == 'local_holdover_only' and dep not in {'holdover_from_prior_source', 'unknown'}:
            errors.append('local_holdover_only requires source_diversity_posture dependency_class holdover_from_prior_source or unknown')
        if cmr == 'mitigated_by_diversity' and dep != 'multiple_independent_roots':
            errors.append('source_diversity_posture common_mode_risk mitigated_by_diversity requires multiple_independent_roots')
        if dep == 'multiple_sources_same_root' and cmr == 'mitigated_by_diversity':
            errors.append('source_diversity_posture multiple_sources_same_root cannot claim common-mode risk mitigated_by_diversity')
        if sd.get('export_detail') != 'summary_only':
            errors.append('source_diversity_posture export_detail must remain summary_only')
    return errors


def schema_validate_extension_item(item: str, value: Any) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return [f'jsonschema dependency unavailable: {exc}']
    schema = load_json('schema/extension-hooks.schema.json')
    subschema = schema.get('properties', {}).get(item)
    if subschema is None:
        return []
    validator = jsonschema.Draft202012Validator(subschema)
    return [f"{item} schema error at {'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in sorted(validator.iter_errors(value), key=str)]


def check_local_assessed_state(state: dict[str, Any], catalog_index: dict[tuple[str | None, str, str | None], dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    errors.extend(check_interval_order(state, 'local'))
    errors.extend(check_extension_hook_values(state))
    retained = bool(state.get('retention_context', {}).get('retained'))
    has_boundary_context = 'boundary_context' in state

    for i, assessment in enumerate(state.get('profile_assessments', []), start=1):
        prefix = f'profile_assessments[{i}]'
        ref = assessment.get('assessed_profile', {})
        profile = resolve_profile(ref, catalog_index)
        errors.extend(f'{prefix}: {e}' for e in check_profile_reference_binding(
            ref,
            used_at=assessment.get('assessment_time'),
            used_at_label='assessment_time',
            prefix='profile reference',
        ))
        if profile is None:
            if assessment.get('policy_acceptance', {}).get('status') in {'accepted', 'accepted_with_conditions'} and not ref.get('digest'):
                errors.append(f'{prefix}: unresolved accepted profile reference lacks digest')
            errors.extend(f'{prefix}: {e}' for e in check_policy_acceptance(assessment))
            errors.extend(f'{prefix}: {e}' for e in check_profile_assessment_temporal(assessment))
            vh = assessment.get('validity_horizon')
            if isinstance(vh, dict):
                errors.extend(f'{prefix}: {e}' for e in check_validity_horizon(vh, assessment))
            ev = assessment.get('evidence_summary')
            if isinstance(ev, dict):
                errors.extend(f'{prefix}.evidence_summary: {e}' for e in check_evidence_summary(ev, catalog_index, assessment))
            continue

        if ref.get('digest'):
            expected = profile.get('normative_rules_digest', {}).get('value')
            if ref.get('digest', {}).get('value') != expected:
                errors.append(f'{prefix}: profile reference digest does not match catalog for {profile.get("id")}')

        pid = profile.get('id')
        label_names = {x['name'] for x in profile['applicability_labels']}
        ranks = {x['name']: x['rank'] for x in profile['applicability_labels']}
        fallback_by_target: dict[str, list[dict[str, Any]]] = {}
        for m in profile.get('fallback_mappings', []):
            fallback_by_target.setdefault(m['to'], []).append(m)

        app = assessment.get('applicability')
        if app not in label_names:
            errors.append(f'{prefix}: applicability {app!r} not in profile applicability map for {pid}')

        eval_summary = assessment.get('evaluation_summary') if isinstance(assessment.get('evaluation_summary'), dict) else {}
        fallback_name = eval_summary.get('fallback_mapping')
        if assessment.get('profile_conformance') == 'fallback':
            mappings = fallback_by_target.get(app, [])
            if not mappings:
                errors.append(f'{prefix}: fallback applicability {app!r} is not a fallback target in profile map for {pid}')
            else:
                if all(m.get('boundary_context_required') for m in mappings) and not has_boundary_context:
                    errors.append(f'{prefix}: fallback applicability {app!r} requires boundary_context')
                for m in mappings:
                    if ranks.get(m['to'], 10**9) > ranks.get(m['from'], -1):
                        errors.append(f"{prefix}: fallback mapping {m['name']} upgrades {m['from']} -> {m['to']}")
                if fallback_name and not any(m.get('name') == fallback_name for m in mappings):
                    errors.append(f'{prefix}: evaluation_summary.fallback_mapping {fallback_name!r} is not valid for fallback applicability {app!r}')
        elif fallback_name:
            errors.append(f'{prefix}: non-fallback profile_conformance cannot carry evaluation_summary.fallback_mapping')

        errors.extend(f'{prefix}: {e}' for e in check_required_default_items(state, assessment, profile))
        errors.extend(f'{prefix}: {e}' for e in check_policy_acceptance(assessment))
        errors.extend(f'{prefix}: {e}' for e in check_profile_assessment_temporal(assessment))
        vh = assessment.get('validity_horizon')
        if isinstance(vh, dict):
            errors.extend(f'{prefix}: {e}' for e in check_validity_horizon(vh, assessment))

        ev = assessment.get('evidence_summary')
        if isinstance(ev, dict):
            errors.extend(f'{prefix}.evidence_summary: {e}' for e in check_evidence_summary(ev, catalog_index, assessment))

        min_tier = profile.get('reference_policy', {}).get('minimum_export_tier')
        high_strength_boundary = retained or min_tier == 3
        if high_strength_boundary and min_tier == 3 and assessment.get('profile_conformance') in {'satisfied', 'fallback'}:
            if not ref.get('digest'):
                errors.append(f'{prefix}: profile reference for {pid} expects digest at this boundary')
            elif ref.get('digest', {}).get('binds') != 'normative_profile_rules':
                errors.append(f'{prefix}: profile reference digest must bind normative_profile_rules')
    return errors


def check_discovery_result(obj: dict[str, Any], catalog_index: dict[tuple[str | None, str, str | None], dict[str, Any]] | None = None) -> list[str]:
    errors: list[str] = []
    request_negotiation = None
    if isinstance(obj.get('request'), dict) and isinstance(obj.get('request', {}).get('negotiation'), dict):
        request_negotiation = obj.get('request', {}).get('negotiation')
    for item, result in obj.get('results', {}).items():
        errors.extend(check_current_result_binding(item, result, request_negotiation))
        errors.extend(check_result_version_negotiation(item, result, request_negotiation))
        errors.extend(check_digest_binding_metadata(item, result.get('digest_binding')))
        errors.extend(check_discovery_result_freshness(item, result))
        if result.get('status') == 'returned' and 'value' not in result:
            errors.append(f'{item}: returned result missing value')
        if result.get('status') in {'unavailable', 'unknown', 'omitted'} and 'value' in result:
            errors.append(f'{item}: negative result should not carry value')
        if result.get('status') == 'returned' and item in HOOK_PATHS and item != 'boundary_context' and 'value' in result:
            errors.extend(f'{item}: {e}' for e in schema_validate_extension_item(item, result.get('value')))
        if item == 'validity_horizon' and result.get('status') == 'returned' and 'value' in result:
            value = result.get('value')
            if not isinstance(value, dict):
                errors.append('validity_horizon: returned value must be object')
            else:
                nested = schema_validate('validity-horizon', value) + check_validity_horizon(value, None)
                errors.extend(f'validity_horizon: {e}' for e in nested)
        if item == 'evaluator_evidence_summary' and result.get('status') == 'returned' and 'value' in result and catalog_index is not None:
            value = result.get('value')
            if not isinstance(value, dict):
                errors.append('evaluator_evidence_summary: returned value must be object')
            else:
                nested = schema_validate('evaluator-evidence-summary', value) + check_evidence_summary(value, catalog_index, None)
                errors.extend(f'evaluator_evidence_summary: {e}' for e in nested)
        if item == 'authorized_verifier_challenge_result' and result.get('status') == 'returned' and 'value' in result and catalog_index is not None:
            value = result.get('value')
            if not isinstance(value, dict):
                errors.append('authorized_verifier_challenge_result: returned value must be object')
            else:
                nested = schema_validate('authorized-verifier-challenge', value) + check_authorized_verifier_challenge(value, catalog_index)
                errors.extend(f'authorized_verifier_challenge_result: {e}' for e in nested)
        if item == 'transparency_trust_policy_reference' and result.get('status') == 'returned' and 'value' in result:
            value = result.get('value')
            if not isinstance(value, dict):
                errors.append('transparency_trust_policy_reference: returned value must be object')
            else:
                nested = schema_validate('transparency-trust-policy-reference', value) + check_transparency_trust_policy_reference(value, None)
                errors.extend(f'transparency_trust_policy_reference: {e}' for e in nested)
        if item == 'policy_lifecycle_authority_recovery_attestation' and result.get('status') == 'returned' and 'value' in result:
            value = result.get('value')
            if not isinstance(value, dict):
                errors.append('policy_lifecycle_authority_recovery_attestation: returned value must be object')
            else:
                nested = schema_validate('policy-lifecycle-authority-recovery-attestation', value) + check_policy_lifecycle_authority_recovery_attestation(value, None, None, None)
                errors.extend(f'policy_lifecycle_authority_recovery_attestation: {e}' for e in nested)
        if item == 'external_transparency_receipt_reference' and result.get('status') == 'returned' and 'value' in result:
            value = result.get('value')
            if not isinstance(value, dict):
                errors.append('external_transparency_receipt_reference: returned value must be object')
            else:
                errors.extend(f'external_transparency_receipt_reference: {e}' for e in check_external_transparency_receipt_reference(value))
        if item in {'replay_transparency_receipt', 'aggregate_verifier_audit_summary'} and result.get('status') == 'returned' and 'value' in result and catalog_index is not None:
            value = result.get('value')
            if not isinstance(value, dict):
                errors.append(f'{item}: returned value must be object')
            else:
                nested = schema_validate('replay-transparency-audit', value) + check_replay_transparency_audit(value, catalog_index)
                errors.extend(f'{item}: {e}' for e in nested)
        if item == 'aggregate_correction_authority_reference' and result.get('status') == 'returned' and 'value' in result:
            value = result.get('value')
            if not isinstance(value, dict):
                errors.append('aggregate_correction_authority_reference: returned value must be object')
            else:
                nested = schema_validate('aggregate-correction-authority-reference', value) + check_aggregate_correction_authority_reference(value, None, None)
                errors.extend(f'aggregate_correction_authority_reference: {e}' for e in nested)
        if item == 'aggregate_lifecycle_decision_table' and result.get('status') == 'returned' and 'value' in result:
            value = result.get('value')
            if not isinstance(value, dict):
                errors.append('aggregate_lifecycle_decision_table: returned value must be object')
            else:
                nested = schema_validate('aggregate-lifecycle-decision-table', value) + check_lifecycle_decision_table(value)
                errors.extend(f'aggregate_lifecycle_decision_table: {e}' for e in nested)
        if item == 'digest_binding_policy' and result.get('status') == 'returned' and 'value' in result:
            value = result.get('value')
            if not isinstance(value, dict):
                errors.append('digest_binding_policy: returned value must be object')
            else:
                nested = schema_validate('digest-binding-policy', value) + check_digest_binding_policy(value)
                errors.extend(f'digest_binding_policy: {e}' for e in nested)
        if item == 'semantic_version_negotiation' and result.get('status') == 'returned' and 'value' in result:
            value = result.get('value')
            if not isinstance(value, dict):
                errors.append('semantic_version_negotiation: returned value must be object')
            else:
                nested = schema_validate('semantic-version-negotiation', value) + check_semantic_version_negotiation_policy(value)
                errors.extend(f'semantic_version_negotiation: {e}' for e in nested)
        if item == 'profile_compatibility_drift_decision' and result.get('status') == 'returned' and 'value' in result:
            value = result.get('value')
            if not isinstance(value, dict):
                errors.append('profile_compatibility_drift_decision: returned value must be object')
            else:
                nested = schema_validate('profile-compatibility-drift-decision', value) + check_profile_compatibility_drift_decision(value)
                errors.extend(f'profile_compatibility_drift_decision: {e}' for e in nested)
        if item == 'scope_composition_guard' and result.get('status') == 'returned' and 'value' in result:
            value = result.get('value')
            if not isinstance(value, dict):
                errors.append('scope_composition_guard: returned value must be object')
            else:
                nested = schema_validate('scope-composition-guard', value) + check_scope_composition_guard(value)
                errors.extend(f'scope_composition_guard: {e}' for e in nested)
    return errors


def build_adapter_index(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {a['id']: a for a in catalog.get('adapters', [])}


def check_transport_adapter_catalog(catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for adapter in catalog.get('adapters', []):
        aid = adapter.get('id')
        if aid in seen:
            errors.append(f'duplicate adapter id {aid}')
        seen.add(aid)
        if adapter.get('does_not_define_protocol') is not True:
            errors.append(f'{aid}: does_not_define_protocol must be true')
        if adapter.get('timestate_core_mutation') != 'forbidden':
            errors.append(f'{aid}: timestate_core_mutation must be forbidden')
        prp = adapter.get('profile_reference_policy', {})
        if prp.get('envelope_signature_substitutes_for_profile_binding') is not False:
            errors.append(f'{aid}: envelope signature cannot substitute for profile binding')
        if prp.get('digest_obligations_remain_in_payload') is not True:
            errors.append(f'{aid}: digest obligations must remain in payload')
        if set(adapter.get('result_policy', {}).get('negative_optional_item_results', [])) != {'unavailable', 'unknown', 'omitted'}:
            errors.append(f'{aid}: negative optional item result set is incomplete')
        for pt in adapter.get('payload_types', []):
            if pt not in MESSAGE_TYPES:
                errors.append(f'{aid}: unknown payload type {pt}')
    return errors


def check_transport_capability(cap: dict[str, Any], adapter_index: dict[str, dict[str, Any]], catalog_index: dict[tuple[str | None, str, str | None], dict[str, Any]]) -> list[str]:
    return check_transport_capability_semantics(cap, adapter_index, catalog_index)


def evidence_matches_assessment(summary: dict[str, Any], assessment: dict[str, Any]) -> bool:
    sid = summary.get('conclusion_binding', {}).get('assessment_id')
    aid = assessment.get('assessment_id')
    if sid or aid:
        return sid == aid and summary.get('assessment_time') == assessment.get('assessment_time') and same_profile_ref(summary.get('assessed_profile', {}), assessment.get('assessed_profile', {}))
    return (
        summary.get('assessment_time') == assessment.get('assessment_time')
        and same_profile_ref(summary.get('assessed_profile', {}), assessment.get('assessed_profile', {}))
        and summary.get('conclusion_binding', {}).get('profile_conformance') == assessment.get('profile_conformance')
        and summary.get('conclusion_binding', {}).get('applicability') == assessment.get('applicability')
    )


def check_retained_export(obj: dict[str, Any], catalog_index: dict[tuple[str | None, str, str | None], dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    state = obj.get('local_assessed_state')
    if not isinstance(state, dict):
        errors.append('retained export local_assessed_state must be object')
        return errors
    if state.get('retention_context', {}).get('retained') is not True:
        errors.append('retained export requires retention_context.retained true')
    errors.extend(check_local_assessed_state(state, catalog_index))
    errors.extend(check_retained_export_temporal(obj))

    export_summaries = obj.get('evidence_input_summaries', [])
    if export_summaries is None:
        export_summaries = []
    if not isinstance(export_summaries, list):
        export_summaries = []
    embedded_summaries = [a.get('evidence_summary') for a in state.get('profile_assessments', []) if isinstance(a.get('evidence_summary'), dict)]
    all_summaries = [s for s in list(export_summaries) + embedded_summaries if isinstance(s, dict)]

    for j, summary in enumerate(export_summaries, start=1):
        if not isinstance(summary, dict):
            continue
        matching = [a for a in state.get('profile_assessments', []) if evidence_matches_assessment(summary, a)]
        if not matching:
            errors.append(f'evidence_input_summaries[{j}]: conclusion does not match any profile assessment')
            errors.extend(f'evidence_input_summaries[{j}]: {e}' for e in check_evidence_summary(summary, catalog_index, None))
        else:
            errors.extend(f'evidence_input_summaries[{j}]: {e}' for e in check_evidence_summary(summary, catalog_index, matching[0]))

    tier = obj.get('export_context', {}).get('profile_reference_tier')
    purpose = obj.get('export_context', {}).get('purpose')
    for i, assessment in enumerate(state.get('profile_assessments', []), start=1):
        if assessment.get('profile_conformance') not in {'satisfied', 'fallback'}:
            continue
        ref = assessment.get('assessed_profile', {})
        profile = resolve_profile(ref, catalog_index)
        pid = ref.get('id')
        min_tier = profile.get('reference_policy', {}).get('minimum_export_tier') if profile else None
        if (isinstance(tier, int) and tier >= 3) or min_tier == 3:
            if not ref.get('digest'):
                errors.append(f'profile_assessments[{i}]: retained export expects digest for {pid}')
            elif ref.get('digest', {}).get('binds') != 'normative_profile_rules':
                errors.append(f'profile_assessments[{i}]: retained export digest must bind normative_profile_rules')
        if profile:
            ep = profile.get('evidence_policy', {})
            requires_evidence = ep.get('retention_required') is True and purpose != 'test_fixture'
            if requires_evidence and not any(evidence_matches_assessment(s, assessment) for s in all_summaries):
                errors.append(f'profile_assessments[{i}]: missing required evidence_input_summary for {pid}')
    return errors


def check_transport_envelope(obj: dict[str, Any], catalog_index: dict[tuple[str | None, str, str | None], dict[str, Any]], adapter_index: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    adapter_stub = obj.get('adapter', {})
    aid = adapter_stub.get('id')
    adapter = adapter_index.get(aid)
    if adapter is None:
        errors.append(f'adapter id not in catalog: {aid}')
    else:
        msg_type = obj.get('message_type')
        if msg_type not in adapter.get('payload_types', []):
            errors.append(f'adapter {aid} does not allow message_type {msg_type}')
        for field in ('carrier', 'mode'):
            if adapter_stub.get(field) != adapter.get(field):
                errors.append(f'adapter {aid} {field} mismatch: envelope {adapter_stub.get(field)!r}, catalog {adapter.get(field)!r}')

    errors.extend(check_transport_envelope_temporal(obj))
    errors.extend(check_transport_integrity(obj))

    payload = obj.get('semantic_payload')
    if not isinstance(payload, dict):
        errors.append('semantic_payload must be object')
        return errors
    msg_type = obj.get('message_type')
    if msg_type == 'wire_claim':
        nested = schema_validate('wire-claim', payload) + check_interval_order(payload, 'wire')
        errors.extend(f'payload for message_type wire_claim: {e}' for e in nested)
    elif msg_type == 'local_assessed_state':
        nested = schema_validate('local-assessed-state', payload) + check_local_assessed_state(payload, catalog_index)
        errors.extend(f'payload for message_type local_assessed_state: {e}' for e in nested)
    elif msg_type in {'discovery_request', 'discovery_result'}:
        nested = schema_validate('discovery-request', payload) + check_discovery_result(payload, catalog_index)
        errors.extend(f'payload for message_type {msg_type}: {e}' for e in nested)
    elif msg_type == 'capability_advertisement':
        nested = schema_validate('transport-capability', payload) + check_transport_capability(payload, adapter_index, catalog_index)
        errors.extend(f'payload for message_type capability_advertisement: {e}' for e in nested)
    elif msg_type == 'retained_assessment_export':
        nested = schema_validate('retained-export', payload) + check_retained_export(payload, catalog_index)
        errors.extend(f'payload for message_type retained_assessment_export: {e}' for e in nested)
    return errors


def semantic_validate(schema_name: str, obj: Any, catalog_index: dict[tuple[str | None, str, str | None], dict[str, Any]], adapter_index: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    if schema_name == 'local-assessed-state' and isinstance(obj, dict):
        errors.extend(check_local_assessed_state(obj, catalog_index))
    elif schema_name == 'wire-claim' and isinstance(obj, dict):
        errors.extend(check_interval_order(obj, 'wire'))
    elif schema_name == 'discovery-request' and isinstance(obj, dict):
        errors.extend(check_discovery_result(obj, catalog_index))
    elif schema_name == 'profile-catalog' and isinstance(obj, dict):
        errors.extend(check_profile_catalog(obj))
    elif schema_name == 'transport-adapter-catalog' and isinstance(obj, dict):
        errors.extend(check_transport_adapter_catalog(obj))
    elif schema_name == 'transport-capability' and isinstance(obj, dict):
        errors.extend(check_transport_capability(obj, adapter_index, catalog_index))
    elif schema_name == 'retained-export' and isinstance(obj, dict):
        errors.extend(check_retained_export(obj, catalog_index))
    elif schema_name == 'transport-envelope' and isinstance(obj, dict):
        errors.extend(check_transport_envelope(obj, catalog_index, adapter_index))
    elif schema_name == 'evaluator-evidence-summary' and isinstance(obj, dict):
        errors.extend(check_evidence_summary(obj, catalog_index, None))
    elif schema_name == 'profile-compatibility-statement' and isinstance(obj, dict):
        errors.extend(check_profile_compatibility_statement(obj, catalog_index))
    elif schema_name == 'authorized-verifier-challenge' and isinstance(obj, dict):
        errors.extend(check_authorized_verifier_challenge(obj, catalog_index))
    elif schema_name == 'replay-transparency-audit' and isinstance(obj, dict):
        errors.extend(check_replay_transparency_audit(obj, catalog_index))
    elif schema_name == 'policy-lifecycle-authority-reference' and isinstance(obj, dict):
        errors.extend(check_policy_lifecycle_authority_reference(obj, None, None))
    elif schema_name == 'policy-lifecycle-authority-recovery-attestation' and isinstance(obj, dict):
        errors.extend(check_policy_lifecycle_authority_recovery_attestation(obj, None, None, None))
    elif schema_name == 'aggregate-correction-authority-reference' and isinstance(obj, dict):
        errors.extend(check_aggregate_correction_authority_reference(obj, None, None))
    elif schema_name == 'aggregate-lifecycle-decision-table' and isinstance(obj, dict):
        errors.extend(check_lifecycle_decision_table(obj))
    elif schema_name == 'digest-binding-policy' and isinstance(obj, dict):
        errors.extend(check_digest_binding_policy(obj))
    elif schema_name == 'semantic-version-negotiation' and isinstance(obj, dict):
        errors.extend(check_semantic_version_negotiation_policy(obj))
    elif schema_name == 'profile-compatibility-drift-matrix' and isinstance(obj, dict):
        errors.extend(check_profile_compatibility_drift_matrix(obj))
    elif schema_name == 'profile-compatibility-drift-decision' and isinstance(obj, dict):
        errors.extend(check_profile_compatibility_drift_decision(obj))
    elif schema_name == 'scope-composition-guard' and isinstance(obj, dict):
        errors.extend(check_scope_composition_guard(obj))
    elif schema_name == 'scope-composition-decision-matrix' and isinstance(obj, dict):
        errors.extend(check_scope_composition_decision_matrix(obj))
    elif schema_name == 'evidence-class-catalog' and isinstance(obj, dict):
        errors.extend(check_evidence_class_catalog(obj))
    return errors



def check_authorized_verifier_challenge(record: dict[str, Any], catalog_index: dict[tuple[str | None, str, str | None], dict[str, Any]]) -> list[str]:
    """Semantic checks for detached authorized-verifier challenge result records."""
    errors: list[str] = []
    errors.extend(check_authorized_verifier_temporal(record))
    errors.extend(check_authorized_verifier_result_semantics(record))

    target = record.get('target_binding', {}) if isinstance(record.get('target_binding'), dict) else {}
    commitments = target.get('commitments', []) if isinstance(target.get('commitments'), list) else []
    commitment_by_pair = {(c.get('item_name'), str(c.get('commitment_value', '')).lower()): c for c in commitments if isinstance(c, dict)}
    commitment_values = {str(c.get('commitment_value', '')).lower() for c in commitments if isinstance(c, dict)}

    ref = target.get('assessed_profile', {}) if isinstance(target.get('assessed_profile'), dict) else {}
    profile = resolve_profile(ref, catalog_index) if isinstance(ref, dict) else None
    if isinstance(ref, dict):
        errors.extend(check_profile_reference_binding(
            ref,
            used_at=record.get('issued_at'),
            used_at_label='authorized verifier challenge issued_at',
            prefix='authorized verifier challenge assessed_profile',
        ))
    if profile is not None and ref.get('digest'):
        expected_digest = profile.get('normative_rules_digest', {}).get('value')
        if ref.get('digest', {}).get('value') != expected_digest:
            errors.append(f'authorized verifier challenge assessed_profile digest does not match catalog for {profile.get("id")}')

    for req in record.get('requested_disclosures', []) if isinstance(record.get('requested_disclosures'), list) else []:
        if not isinstance(req, dict):
            continue
        if (req.get('item_name'), str(req.get('commitment_value', '')).lower()) not in commitment_by_pair:
            errors.append(f"requested disclosure for {req.get('item_name')} does not match a target commitment")
        if req.get('ordinary_timesync_export_allowed') is not False:
            errors.append('requested disclosure cannot allow ordinary TimeSync export of salt/preimage material')

    boundary = record.get('disclosure_boundary', {}) if isinstance(record.get('disclosure_boundary'), dict) else {}
    if boundary.get('salt_preimage_material_location') != 'external_authorized_channel_only':
        errors.append('authorized verifier challenge must keep salt/preimage material in an external authorized channel')
    for key in ('ordinary_exchange_allowed', 'ordinary_retained_summary_allowed', 'challenge_result_is_profile_evidence', 'challenge_result_reopens_assessment', 'external_provenance_interpreted_by_timesync'):
        if boundary.get(key) is not False:
            errors.append(f'disclosure_boundary.{key} must be false')

    portability = record.get('portability_boundary', {}) if isinstance(record.get('portability_boundary'), dict) else {}
    if portability.get('portable_result_is_profile_evidence') is not False:
        errors.append('portability_boundary.portable_result_is_profile_evidence must be false')
    if portability.get('portability_does_not_expand_disclosure_scope') is not True:
        errors.append('portability_boundary.portability_does_not_expand_disclosure_scope must be true')
    for key in ('portable_across_profile_revisions', 'portable_across_profile_digest_change', 'portable_across_operators_without_profile_compatibility'):
        if portability.get(key) is not False:
            errors.append(f'portability_boundary.{key} must be false')
    if 'commitment_verification_only' not in set(portability.get('result_may_be_replayed_for', [])):
        errors.append('challenge result portability is limited to commitment_verification_only')
    if portability.get('portable_result_scope') == 'cross_operator_with_profile_compatibility' and not portability.get('profile_compatibility_statement'):
        errors.append('cross-operator challenge-result portability requires a profile compatibility statement digest')

    summary = record.get('referenced_evidence_summary')
    if isinstance(summary, dict):
        nested = schema_validate('evaluator-evidence-summary', summary) + check_evidence_summary(summary, catalog_index, None)
        errors.extend(f'referenced_evidence_summary: {e}' for e in nested)
        if summary.get('summary_id') != target.get('summary_id'):
            errors.append('authorized verifier challenge target summary_id does not match referenced evidence summary')
        if summary.get('conclusion_binding', {}).get('assessment_id') != target.get('assessment_id'):
            errors.append('authorized verifier challenge target assessment_id does not match referenced evidence summary')
        found_values: set[str] = set()
        for item in summary.get('input_items', []):
            if not isinstance(item, dict):
                continue
            ext = item.get('external_evidence_reference')
            if isinstance(ext, dict):
                commitment = ext.get('commitment')
                if isinstance(commitment, dict):
                    found_values.add(str(commitment.get('value', '')).lower())
        missing = commitment_values - found_values
        if missing:
            errors.append(f'authorized verifier challenge target commitment does not appear in referenced evidence summary: {sorted(missing)}')

    result = record.get('challenge_result')
    if isinstance(result, dict):
        if result.get('challenge_id') != record.get('challenge_id'):
            errors.append('challenge_result.challenge_id does not match challenge_id')
        receipt = result.get('receipt', {}) if isinstance(result.get('receipt'), dict) else {}
        if receipt.get('disclosure_material_exported_in_timesync') is not False:
            errors.append('challenge receipt must not export salt/preimage material in TimeSync')
        rb = result.get('response_boundary', {}) if isinstance(result.get('response_boundary'), dict) else {}
        for key in ('disclosure_does_not_update_timestate', 'disclosure_does_not_reassess_profile', 'disclosure_cannot_satisfy_profile_obligation', 'disclosure_not_timesync_provenance', 'ordinary_retained_summary_must_not_include_preimage'):
            if rb.get(key) is not True:
                errors.append(f'challenge_result.response_boundary.{key} must be true')
        for key in ('source_roster_exported', 'path_history_exported', 'clock_algorithm_exported', 'raw_observations_exported'):
            if rb.get(key) is not False:
                errors.append(f'challenge_result.response_boundary.{key} must be false')
        state = result.get('portable_result_state', {}) if isinstance(result.get('portable_result_state'), dict) else {}
        rev = state.get('revocation_check', {}) if isinstance(state.get('revocation_check'), dict) else {}
        if state.get('current_status') == 'revoked' or rev.get('status') == 'revoked':
            errors.append('authorized verifier challenge result is revoked and cannot be reused')
        if state.get('current_status') == 'usable_for_commitment_verification_only' and rev.get('status') != 'checked_not_revoked':
            errors.append('usable portable challenge result requires revocation status checked_not_revoked')
        if state.get('current_status_does_not_update_profile_assessment') is not True:
            errors.append('portable result status must not update the profile assessment')
        for vd in result.get('verified_disclosures', []) if isinstance(result.get('verified_disclosures'), list) else []:
            if not isinstance(vd, dict):
                continue
            if (vd.get('item_name'), str(vd.get('commitment_value', '')).lower()) not in commitment_by_pair:
                errors.append(f"verified disclosure for {vd.get('item_name')} does not match a target commitment")
        if result.get('result') in {'matched', 'mismatch', 'external_system_verified'} and not result.get('verified_disclosures'):
            errors.append('authorized verifier challenge result requires verified_disclosures for matched/mismatch/external_system_verified results')
    elif record.get('record_kind') == 'authorized_verifier_challenge_result':
        errors.append('authorized_verifier_challenge_result record requires challenge_result')

    replay = record.get('replay_context') if isinstance(record.get('replay_context'), dict) else None
    if replay is not None:
        if replay.get('replay_use') != 'commitment_verification_review':
            errors.append('challenge result replay use cannot upgrade to profile evidence, current actionability, transport authentication, or reassessment')
        if replay.get('replay_material_exported_in_timesync') is not False:
            errors.append('challenge result replay must not export disclosure material in TimeSync')
        rt = replay.get('replay_target', {}) if isinstance(replay.get('replay_target'), dict) else {}
        if rt.get('summary_id') != target.get('summary_id') or rt.get('assessment_id') != target.get('assessment_id'):
            errors.append('challenge result replay target must match the original summary_id and assessment_id')
        replay_digest = rt.get('assessed_profile_digest', {}) if isinstance(rt.get('assessed_profile_digest'), dict) else {}
        target_digest = ref.get('digest', {}) if isinstance(ref.get('digest'), dict) else {}
        if replay_digest.get('value') != target_digest.get('value'):
            errors.append('challenge result replay target profile digest must match the original assessed profile digest')
        using_operator = replay.get('using_operator')
        local_authorities = {target.get('assessed_profile', {}).get('authority'), record.get('verifier_authorization', {}).get('verifier_authority')}
        if using_operator not in local_authorities:
            if portability.get('portable_result_scope') != 'cross_operator_with_profile_compatibility' or not (portability.get('profile_compatibility_statement') or replay.get('profile_compatibility_statement')):
                errors.append('cross-operator challenge-result replay requires a profile compatibility statement digest')

    return errors



def check_anchor_evaluation(record: dict[str, Any]) -> list[str]:
    """Compact transparency-anchor freshness, checkpoint consistency, and split-view checks."""
    errors: list[str] = []
    evaluation = record.get('anchor_evaluation')
    if record.get('record_kind') == 'challenge_replay_transparency_receipt' and not isinstance(evaluation, dict):
        errors.append('replay transparency receipt requires anchor_evaluation')
        return errors
    if not isinstance(evaluation, dict):
        return errors

    evaluated_at_raw = evaluation.get('evaluated_at')
    try:
        parse_dt(evaluated_at_raw or '')
    except Exception as exc:  # noqa: BLE001
        errors.append(f'anchor_evaluation evaluated_at parse error: {exc}')
        return errors

    current_status = evaluation.get('current_visibility_status')
    anchor = record.get('transparency_anchor', {}) if isinstance(record.get('transparency_anchor'), dict) else {}
    freshness = evaluation.get('anchor_freshness', {}) if isinstance(evaluation.get('anchor_freshness'), dict) else {}
    consistency = evaluation.get('checkpoint_consistency', {}) if isinstance(evaluation.get('checkpoint_consistency'), dict) else {}
    split_view = evaluation.get('split_view_boundary', {}) if isinstance(evaluation.get('split_view_boundary'), dict) else {}

    if freshness.get('freshness_does_not_update_profile_assessment') is not True:
        errors.append('anchor freshness must not update profile assessment')
    if consistency.get('proof_material_exported') is not False:
        errors.append('checkpoint consistency proof material must not be exported in TimeSync')
    if consistency.get('external_log_interpreted_as_timesync_provenance') is not False:
        errors.append('checkpoint consistency must not interpret external log state as TimeSync provenance')
    if split_view.get('conflict_details_exported') is not False:
        errors.append('split-view conflict details must not be exported in TimeSync')
    if split_view.get('allegation_updates_profile_assessment') is not False:
        errors.append('split-view allegation must not update profile assessment')
    if split_view.get('allegation_interpreted_as_timesync_provenance') is not False:
        errors.append('split-view allegation must not be interpreted as TimeSync provenance')

    fstatus = freshness.get('status')

    if current_status == 'current_at_evaluation':
        if anchor.get('inclusion_status') != 'included':
            errors.append('current replay visibility requires included transparency anchor')
        if fstatus != 'fresh_at_evaluation':
            errors.append('stale or unchecked transparency anchor cannot be current replay visibility')
        if consistency.get('status') != 'checked_consistent':
            errors.append('current replay visibility requires checked_consistent checkpoint consistency')
        if split_view.get('status') != 'no_conflicting_view_observed':
            errors.append('current replay visibility requires no conflicting transparency view observed')

    if consistency.get('status') == 'checked_consistent':
        if not consistency.get('checked_at'):
            errors.append('checked_consistent checkpoint consistency requires checked_at')
    if consistency.get('status') in {'failed', 'not_checked'} and current_status == 'current_at_evaluation':
        errors.append('failed or unchecked checkpoint consistency cannot be current replay visibility')
    if consistency.get('status') == 'failed' and current_status not in {'contested', 'historical_only', 'unknown'}:
        errors.append('failed checkpoint consistency must be represented as contested, historical_only, or unknown')
    if split_view.get('status') == 'conflicting_view_reported' and current_status == 'current_at_evaluation':
        errors.append('conflicting transparency view cannot be current replay visibility')

    current_digest = consistency.get('current_checkpoint_digest', {}) if isinstance(consistency.get('current_checkpoint_digest'), dict) else {}
    anchor_digest = anchor.get('digest', {}) if isinstance(anchor.get('digest'), dict) else {}
    if current_digest and anchor_digest and current_digest.get('value') != anchor_digest.get('value'):
        errors.append('anchor_evaluation current_checkpoint_digest must match transparency_anchor.digest')
    return errors



def check_witness_cohort_evaluation(record: dict[str, Any]) -> list[str]:
    """Summary-only witnessed-checkpoint and monitor-cohort posture checks."""
    errors: list[str] = []
    wc = record.get('witness_cohort_evaluation')
    if wc is None:
        return errors
    if not isinstance(wc, dict):
        return ['witness_cohort_evaluation must be object']

    status = wc.get('status')
    basis = wc.get('basis')
    anchor_eval = record.get('anchor_evaluation', {}) if isinstance(record.get('anchor_evaluation'), dict) else {}
    current_status = anchor_eval.get('current_visibility_status')
    consistency = anchor_eval.get('checkpoint_consistency', {}) if isinstance(anchor_eval.get('checkpoint_consistency'), dict) else {}
    split_signal = wc.get('split_view_signal', {}) if isinstance(wc.get('split_view_signal'), dict) else {}
    independence = wc.get('cohort_independence', {}) if isinstance(wc.get('cohort_independence'), dict) else {}
    proof = wc.get('proof_boundary', {}) if isinstance(wc.get('proof_boundary'), dict) else {}

    for key in ('witness_signature_material_exported', 'monitor_logs_exported', 'gossip_transcript_exported', 'external_witness_or_monitor_state_interpreted_as_timesync_provenance', 'witness_cohort_updates_profile_assessment'):
        if proof.get(key) is not False:
            errors.append(f'witness_cohort_evaluation.proof_boundary.{key} must be false')
    if proof.get('witness_cohort_updates_replay_visibility_only') is not True:
        errors.append('witness_cohort_evaluation may update only replay-visibility posture')

    for key in ('roster_exported', 'identity_exported', 'dependency_details_exported'):
        if independence.get(key) is not False:
            errors.append(f'witness_cohort_evaluation.cohort_independence.{key} must be false')
    for key in ('details_exported', 'signal_updates_profile_assessment', 'signal_interpreted_as_timesync_provenance'):
        if split_signal.get(key) is not False:
            errors.append(f'witness_cohort_evaluation.split_view_signal.{key} must be false')

    if status in {'witnessed_consistent', 'monitor_cohort_observed', 'combined_witness_and_monitor_consistent'}:
        if not wc.get('observed_at'):
            errors.append('witness or monitor consistent posture requires observed_at')
        if consistency.get('status') != 'checked_consistent':
            errors.append('witness or monitor consistent posture requires checked_consistent checkpoint consistency')
        if split_signal.get('status') != 'none_observed':
            errors.append('witness or monitor consistent posture requires split_view_signal none_observed')
        if independence.get('status') != 'independent_threshold_met':
            errors.append('witness or monitor consistent posture requires independent_threshold_met')
        threshold = independence.get('threshold')
        witness_count = independence.get('reported_witness_count', 0)
        monitor_count = independence.get('reported_monitor_count', 0)
        if not isinstance(threshold, int) or threshold <= 0:
            errors.append('witness or monitor consistent posture requires positive threshold')
        elif status == 'witnessed_consistent' and (not isinstance(witness_count, int) or witness_count < threshold):
            errors.append('witnessed checkpoint threshold not met')
        elif status == 'monitor_cohort_observed' and (not isinstance(monitor_count, int) or monitor_count < threshold):
            errors.append('monitor cohort threshold not met')
        elif status == 'combined_witness_and_monitor_consistent':
            if not isinstance(witness_count, int) or not isinstance(monitor_count, int) or witness_count <= 0 or monitor_count <= 0 or witness_count + monitor_count < threshold:
                errors.append('combined witness and monitor threshold not met')

    if status == 'witnessed_consistent' and basis not in {'witnessed_checkpoint', 'combined_witness_and_monitor'}:
        errors.append('witnessed_consistent requires witnessed checkpoint basis')
    if status == 'monitor_cohort_observed' and basis not in {'monitor_cohort_observation', 'combined_witness_and_monitor'}:
        errors.append('monitor_cohort_observed requires monitor cohort basis')
    if status == 'combined_witness_and_monitor_consistent' and basis != 'combined_witness_and_monitor':
        errors.append('combined witness and monitor status requires combined basis')

    positive_basis = {'witnessed_checkpoint', 'monitor_cohort_observation', 'combined_witness_and_monitor'}
    if status in {'not_checked', 'unknown', 'not_used'} and basis in positive_basis:
        errors.append('witness cohort positive basis cannot have not_checked, unknown, or not_used status')
    if status in {'not_checked', 'unknown', 'not_used'} and independence.get('status') == 'independent_threshold_met':
        errors.append('witness cohort independent_threshold_met requires a checked witness or monitor status')

    if status == 'witness_or_monitor_disagreement_observed' or split_signal.get('status') == 'disagreement_observed':
        if current_status == 'current_at_evaluation':
            errors.append('witness or monitor disagreement cannot be current replay visibility')
        if split_signal.get('signal_interpreted_as_timesync_provenance') is not False:
            errors.append('witness or monitor disagreement must not be interpreted as TimeSync provenance')
    return errors


def check_monitor_cohort_coverage(aggregate: dict[str, Any]) -> list[str]:
    """Aggregate monitor/witness coverage privacy and threshold checks."""
    errors: list[str] = []
    coverage = aggregate.get('monitor_cohort_coverage') if isinstance(aggregate.get('monitor_cohort_coverage'), dict) else None
    if coverage is None:
        return errors
    for key in ('monitor_roster_exported', 'monitor_identity_exported', 'cohort_details_exported', 'gossip_transcripts_exported'):
        if coverage.get(key) is not False:
            errors.append(f'aggregate monitor cohort coverage {key} must be false')
    minimum = coverage.get('minimum_group_size')
    monitor_count = coverage.get('monitor_observation_count', 0)
    witness_count = coverage.get('witness_observation_count', 0)
    total = (monitor_count if isinstance(monitor_count, int) else 0) + (witness_count if isinstance(witness_count, int) else 0)
    if isinstance(minimum, int) and total < minimum and coverage.get('small_group_suppressed') is not True:
        errors.append('aggregate monitor cohort coverage must suppress small groups below the minimum group size')
    if coverage.get('coverage_status') == 'reported_aggregate' and isinstance(minimum, int):
        if total < minimum:
            errors.append('aggregate monitor cohort coverage cannot report aggregate coverage below the minimum group size')
        if coverage.get('small_group_suppressed') is not False:
            errors.append('reported aggregate monitor cohort coverage must not be marked suppressed')
    if coverage.get('coverage_status') == 'insufficient_group_suppressed' and coverage.get('small_group_suppressed') is not True:
        errors.append('insufficient monitor cohort coverage must be marked suppressed')
    return errors




def boundary_false_errors(boundary: dict[str, Any], keys: tuple[str, ...], prefix: str) -> list[str]:
    """Refactored helper for repeated non-leakage/non-upgrade boolean boundary checks."""
    return [f'{prefix} boundary {key} must be false' for key in keys if boundary.get(key) is not False]


def non_negative_int(value: Any) -> int:
    return value if isinstance(value, int) and value >= 0 else 0



def check_digest_binding_policy(policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    canonical = policy.get('canonical_json_profile', {}) if isinstance(policy.get('canonical_json_profile'), dict) else {}
    if canonical.get('canonicalization') != 'json_canonicalization_scheme_rfc8785':
        errors.append('digest binding policy canonical_json_profile must use json_canonicalization_scheme_rfc8785')
    if canonical.get('digest_algorithm') != 'sha256':
        errors.append('digest binding policy canonical_json_profile must use sha256')
    if canonical.get('object_member_order') != 'lexicographic_utf16_code_unit_order':
        errors.append('digest binding policy canonical_json_profile must sort object members by UTF-16 code units')
    if canonical.get('number_policy') != 'integers_only_for_digest_bound_timesync_objects':
        errors.append('digest binding policy canonical_json_profile must use the TimeSync safe-integer JCS subset for current digest surfaces')
    if canonical.get('ijson_constraints_enforced') is not True:
        errors.append('digest binding policy canonical_json_profile must enforce I-JSON constraints before digesting')
    if canonical.get('duplicate_member_names_rejected') is not True:
        errors.append('digest binding policy canonical_json_profile must reject duplicate JSON member names')
    if canonical.get('unsafe_numbers_rejected_for_timesync_digest_surfaces') is not True:
        errors.append('digest binding policy canonical_json_profile must reject unsafe numbers for TimeSync-owned digest surfaces')
    if canonical.get('legacy_python_sort_keys_permitted_for_current_binding') is not False:
        errors.append('legacy canonicalization cannot bind current-use objects')
    byte = policy.get('byte_envelope_profile', {}) if isinstance(policy.get('byte_envelope_profile'), dict) else {}
    if byte.get('payload_type_authenticated') is not True:
        errors.append('digest binding policy byte-envelope profile requires authenticated payload type')
    if byte.get('verifier_must_verify_bytes_before_parse') is not True:
        errors.append('digest binding policy byte-envelope profile requires bytes verified before payload parse')
    if byte.get('canonical_json_required_for_signature_validation') is not False:
        errors.append('digest binding policy byte-envelope profile cannot require canonical JSON for signature validation')
    if byte.get('raw_payload_bytes_exported_by_default') is not False:
        errors.append('digest binding policy must not export raw payload bytes by default')
    for idx, rule in enumerate(policy.get('digest_surface_rules', []) if isinstance(policy.get('digest_surface_rules'), list) else []):
        if not isinstance(rule, dict):
            continue
        if rule.get('current_use_allowed') is True and rule.get('binding_mode') == 'legacy_python_sort_keys_historical_only':
            errors.append(f'digest surface rule #{idx + 1}: legacy canonicalization cannot bind current-use objects')
        if rule.get('current_use_allowed') is True and rule.get('legacy_binding_allowed') is True:
            errors.append(f'digest surface rule #{idx + 1}: legacy binding cannot be allowed for current-use objects')
        if rule.get('binding_mode') in {'external_byte_envelope', 'external_receipt_bytes'} and not rule.get('byte_envelope_payload_type'):
            errors.append(f'digest surface rule #{idx + 1}: external byte binding requires byte_envelope_payload_type')
        if rule.get('surface') == 'retained_operator_record' and rule.get('current_use_allowed') is True:
            errors.append(f'digest surface rule #{idx + 1}: retained_operator_record cannot be current-use allowed')
    boundary = policy.get('boundary', {}) if isinstance(policy.get('boundary'), dict) else {}
    for key in ('digest_policy_updates_profile_assessment', 'digest_policy_interpreted_as_timesync_provenance', 'digest_policy_creates_credential_system', 'digest_policy_operates_transparency_log', 'digest_policy_exports_raw_payload_bytes'):
        if boundary.get(key) is not False:
            errors.append(f'digest binding policy boundary.{key} must be false')
    if boundary.get('digest_policy_updates_digest_interpretation_only') is not True:
        errors.append('digest binding policy may update digest interpretation only')
    return errors


def check_semantic_version_negotiation_policy(policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    supported = policy.get('supported_result_semantic_versions', {}) if isinstance(policy.get('supported_result_semantic_versions'), dict) else {}
    for item, versions in supported.items():
        for version in versions if isinstance(versions, list) else []:
            if parse_semver(version) is None:
                errors.append(f'{item}: supported semantic version must be MAJOR.MINOR.PATCH')
    downgrade_policy = policy.get('downgrade_proof_policy') if isinstance(policy.get('downgrade_proof_policy'), dict) else None
    if downgrade_policy is not None:
        if downgrade_policy.get('weaker_semantics_current_use_allowed') is not False:
            errors.append('semantic version negotiation cannot allow weaker downgrade semantics for current use')
        if downgrade_policy.get('current_use_downgrade_requires_proof') is True and downgrade_policy.get('downgrade_proof_digest_required') is not True:
            errors.append('semantic version negotiation downgrade proof policy must require a proof digest for current-use downgrade')
        if downgrade_policy.get('downgrade_proof_digest_required') is True and not digest_binds(downgrade_policy.get('proof_digest'), 'profile_downgrade_proof'):
            errors.append('semantic version negotiation downgrade proof policy requires proof_digest binding profile_downgrade_proof')
        dpb = downgrade_policy.get('boundary', {}) if isinstance(downgrade_policy.get('boundary'), dict) else {}
        for key in ('downgrade_proof_updates_profile_assessment', 'downgrade_proof_updates_actionability', 'downgrade_proof_interpreted_as_timesync_provenance'):
            if dpb.get(key) is not False:
                errors.append(f'semantic version negotiation downgrade_proof_policy.boundary.{key} must be false')
        if dpb.get('downgrade_proof_updates_discovery_interpretation_only') is not True:
            errors.append('semantic version negotiation downgrade proof may update discovery interpretation only')
    boundary = policy.get('boundary', {}) if isinstance(policy.get('boundary'), dict) else {}
    for key in ('negotiation_updates_profile_assessment', 'negotiation_updates_actionability', 'negotiation_interpreted_as_timesync_provenance'):
        if boundary.get(key) is not False:
            errors.append(f'semantic version negotiation boundary.{key} must be false')
    if boundary.get('negotiation_updates_discovery_interpretation_only') is not True:
        errors.append('semantic version negotiation may update discovery interpretation only')
    return errors

def check_aggregate_correction_authority_lifecycle(lifecycle: dict[str, Any], aggregate: dict[str, Any] | None = None) -> list[str]:
    """Correction-authority lifecycle, revocation, emergency withdrawal, contestation, and decision-table checks."""
    errors: list[str] = []
    errors.extend(schema_validate('aggregate-correction-authority-lifecycle', lifecycle))
    boundary = lifecycle.get('lifecycle_boundary', {}) if isinstance(lifecycle.get('lifecycle_boundary'), dict) else {}
    errors.extend(boundary_false_errors(boundary, (
        'authority_roster_exported',
        'authority_key_material_exported',
        'revocation_endpoint_exported',
        'repository_topology_exported',
        'incident_forensics_exported',
        'legal_process_details_exported',
        'emergency_response_plan_exported',
        'contestation_party_identity_exported',
        'lifecycle_updates_profile_assessment',
        'external_lifecycle_record_interpreted_as_timesync_provenance',
    ), 'aggregate_correction_authority_lifecycle'))
    if boundary.get('lifecycle_updates_replay_visibility_only') is not True:
        errors.append('aggregate correction-authority lifecycle may update only aggregate replay-visibility posture')

    state = lifecycle.get('lifecycle_state')
    effect = lifecycle.get('lifecycle_effect')
    revocation = lifecycle.get('revocation_status')
    decision = lifecycle.get('current_interpretation_decision')
    emergency = lifecycle.get('emergency_withdrawal', {}) if isinstance(lifecycle.get('emergency_withdrawal'), dict) else {}
    contestation = lifecycle.get('contestation', {}) if isinstance(lifecycle.get('contestation'), dict) else {}

    if not digest_binds(lifecycle.get('decision_table_digest'), 'aggregate_lifecycle_decision_table'):
        errors.append('correction-authority lifecycle requires decision_table_digest binding aggregate_lifecycle_decision_table')
    if state != 'unknown_or_redacted' and not digest_binds(lifecycle.get('lifecycle_policy_digest'), 'aggregate_correction_authority_lifecycle_rules'):
        errors.append('known correction-authority lifecycle requires lifecycle_policy_digest binding aggregate_correction_authority_lifecycle_rules')

    expected = expected_lifecycle_decision(lifecycle)
    if decision != expected:
        errors.append(f'correction-authority lifecycle current_interpretation_decision must be {expected} for this posture')

    current_decision = decision in {'current_supported', 'current_supported_guarded'}
    if current_decision and effect != 'aggregate_interpretation_current':
        errors.append('current-supported lifecycle decision requires aggregate_interpretation_current lifecycle_effect')
    if effect == 'aggregate_interpretation_current' and decision not in {'current_supported', 'current_supported_guarded'}:
        errors.append('aggregate_interpretation_current lifecycle_effect requires current-supported decision')

    if state in {'active', 'pending_rotation'}:
        if revocation != 'not_revoked':
            errors.append('active or pending-rotation lifecycle requires not_revoked revocation_status')
        if not lifecycle.get('revocation_checked_at'):
            errors.append('active or pending-rotation lifecycle requires revocation_checked_at')
    if state == 'active' and decision == 'current_supported_guarded':
        errors.append('active lifecycle cannot use guarded pending-rotation current decision')
    if state == 'pending_rotation' and decision == 'current_supported':
        errors.append('pending-rotation lifecycle current interpretation must be guarded')
    if state == 'expired' and effect == 'aggregate_interpretation_current':
        errors.append('expired correction-authority lifecycle cannot support current aggregate interpretation')
    if state == 'expired' and decision != 'historical_only':
        errors.append('expired correction-authority lifecycle must resolve to historical_only decision')
    if state == 'revoked':
        if revocation != 'revoked':
            errors.append('revoked correction-authority lifecycle requires revoked revocation_status')
        if effect == 'aggregate_interpretation_current':
            errors.append('revoked correction-authority lifecycle cannot support current aggregate interpretation')
    if revocation in {'revoked', 'not_checked', 'unknown_or_redacted'} and effect == 'aggregate_interpretation_current':
        errors.append('revoked or unchecked correction-authority revocation posture cannot support current aggregate interpretation')
    if state == 'unknown_or_redacted' and effect == 'aggregate_interpretation_current':
        errors.append('unknown correction-authority lifecycle cannot support current aggregate interpretation')

    estate = emergency.get('state')
    resync = emergency.get('resynchronization_state')
    if estate == 'not_applicable':
        if emergency.get('scope') != 'not_applicable':
            errors.append('not-applicable emergency withdrawal requires not_applicable scope')
        if emergency.get('suppresses_current_interpretation') is not False:
            errors.append('not-applicable emergency withdrawal must not suppress current interpretation')
        if resync not in {None, 'not_applicable'}:
            errors.append('not-applicable emergency withdrawal requires not_applicable resynchronization_state')
    if estate in {'active', 'completed', 'contested'}:
        if emergency.get('scope') == 'not_applicable':
            errors.append('active/completed/contested emergency withdrawal requires a concrete or redacted aggregate scope')
        if emergency.get('suppresses_current_interpretation') is not True:
            errors.append('active/completed/contested emergency withdrawal must suppress current interpretation')
        if not digest_binds(emergency.get('withdrawal_digest'), 'aggregate_emergency_withdrawal_record'):
            errors.append('active/completed/contested emergency withdrawal requires withdrawal_digest binding aggregate_emergency_withdrawal_record')
        if effect == 'aggregate_interpretation_current':
            errors.append('active/completed/contested emergency withdrawal cannot support current aggregate interpretation')
        if decision != 'suppressed_by_emergency_withdrawal':
            errors.append('active/completed/contested emergency withdrawal must resolve to suppressed_by_emergency_withdrawal')
        if resync in {None, 'not_applicable'}:
            errors.append('active/completed/contested emergency withdrawal requires a concrete resynchronization_state')
        if resync in {'resync_required', 'resync_in_progress', 'resync_completed', 'resync_failed', 'resync_contested'} and not digest_binds(emergency.get('resynchronization_digest'), 'aggregate_emergency_resynchronization_policy'):
            errors.append('emergency resynchronization requires resynchronization_digest binding aggregate_emergency_resynchronization_policy')
    if state == 'emergency_withdrawal':
        if estate not in {'active', 'completed', 'contested'}:
            errors.append('emergency correction-authority lifecycle requires active, completed, or contested emergency_withdrawal state')
        if effect == 'aggregate_interpretation_current':
            errors.append('emergency correction-authority withdrawal cannot support current aggregate interpretation')
    elif estate not in {None, 'not_applicable'}:
        errors.append('non-emergency lifecycle cannot carry active/completed/contested emergency_withdrawal state')

    cstate = contestation.get('state')
    ceffect = contestation.get('contestation_effect')
    if cstate == 'none':
        if ceffect != 'not_applicable':
            errors.append('no contestation requires contestation_effect not_applicable')
    else:
        if not digest_binds(contestation.get('contestation_digest'), 'aggregate_correction_authority_contestation_record'):
            errors.append('non-empty contestation state requires contestation_digest binding aggregate_correction_authority_contestation_record')
    if state == 'contested' and cstate in {None, 'none'}:
        errors.append('contested correction-authority lifecycle requires a non-empty contestation state')
    if state == 'contested' or cstate in {'pending_contestation', 'resolved_overturned', 'unknown_or_redacted'}:
        if effect == 'aggregate_interpretation_current' or ceffect == 'aggregate_interpretation_current':
            errors.append('contested correction-authority lifecycle cannot support current aggregate interpretation')
    if cstate == 'resolved_upheld' and ceffect not in {'aggregate_interpretation_current', 'historical_only'}:
        errors.append('resolved-upheld correction-authority contestation must declare current or historical-only effect')
    if cstate == 'resolved_upheld' and ceffect == 'aggregate_interpretation_current' and decision not in {'current_supported', 'current_supported_guarded'}:
        errors.append('resolved-upheld current contestation requires a current-supported lifecycle decision')

    portability = lifecycle.get('lifecycle_portability', {}) if isinstance(lifecycle.get('lifecycle_portability'), dict) else {}
    if portability:
        for key in ('portability_updates_profile_assessment', 'external_lifecycle_portability_interpreted_as_timesync_provenance'):
            if portability.get(key) is not False:
                errors.append(f'lifecycle_portability.{key} must be false')
        if portability.get('portability_updates_replay_visibility_only') is not True:
            errors.append('lifecycle_portability may update only aggregate replay-visibility posture')
        if portability.get('portability_state') == 'portable_to_compatible_operator':
            if portability.get('authority_equivalence') != 'digest_bound_equivalent_or_stricter':
                errors.append('portable lifecycle state requires digest-bound equivalent-or-stricter authority equivalence')
            if not digest_binds(portability.get('compatibility_statement_digest'), 'profile_compatibility_statement'):
                errors.append('portable lifecycle state requires compatibility_statement_digest binding profile_compatibility_statement')
        if portability.get('authority_equivalence') == 'weaker_or_unknown' and decision in {'current_supported', 'current_supported_guarded'}:
            errors.append('current lifecycle interpretation cannot rely on weaker-or-unknown lifecycle portability')

    if aggregate is not None:
        record_time = aggregate.get('_record_created_at') or aggregate.get('_record_issued_at')
        if record_time and lifecycle.get('lifecycle_checked_at'):
            errors.extend(check_time_not_after(
                lifecycle.get('lifecycle_checked_at'),
                record_time,
                value_label='aggregate correction-authority lifecycle_checked_at',
                anchor_label='aggregate_record_created_at',
            ))
        if record_time and lifecycle.get('revocation_checked_at'):
            errors.extend(check_time_not_after(
                lifecycle.get('revocation_checked_at'),
                record_time,
                value_label='aggregate correction-authority revocation_checked_at',
                anchor_label='aggregate_record_created_at',
            ))
    return errors

def check_aggregate_correction_authority_reference(ref: dict[str, Any], lineage: dict[str, Any] | None = None, aggregate: dict[str, Any] | None = None) -> list[str]:
    """Correction-authority, notification cadence, and portable correction-chain checks."""
    errors: list[str] = []
    errors.extend(schema_validate('aggregate-correction-authority-reference', ref))
    errors.extend(check_aggregate_correction_authority_digest_bindings(ref))
    auth = ref.get('authority_binding', {}) if isinstance(ref.get('authority_binding'), dict) else {}
    notification = ref.get('notification_cadence', {}) if isinstance(ref.get('notification_cadence'), dict) else {}
    portability = ref.get('portability_boundary', {}) if isinstance(ref.get('portability_boundary'), dict) else {}
    lifecycle = ref.get('authority_lifecycle') if isinstance(ref.get('authority_lifecycle'), dict) else None
    nb = notification.get('notification_boundary', {}) if isinstance(notification.get('notification_boundary'), dict) else {}

    if lifecycle is None:
        errors.append('aggregate correction authority reference requires authority_lifecycle')
    else:
        errors.extend(check_aggregate_correction_authority_lifecycle(lifecycle, aggregate))

    errors.extend(boundary_false_errors(nb, (
        'recipient_roster_exported',
        'recipient_identity_exported',
        'delivery_channel_details_exported',
        'notification_payload_material_exported',
        'notification_updates_profile_assessment',
        'external_notification_record_interpreted_as_timesync_provenance',
    ), 'aggregate_correction_authority_reference.notification'))
    if nb.get('notification_updates_replay_visibility_only') is not True:
        errors.append('aggregate correction notification may update only aggregate replay-visibility posture')

    errors.extend(boundary_false_errors(portability, (
        'authority_roster_exported',
        'authority_key_material_exported',
        'repository_topology_exported',
        'notification_recipient_details_exported',
        'thresholds_or_authority_equivalence_weakened',
        'portability_updates_profile_assessment',
        'external_correction_chain_interpreted_as_timesync_provenance',
    ), 'aggregate_correction_authority_reference.portability'))
    if portability.get('portability_updates_replay_visibility_only') is not True:
        errors.append('aggregate correction-chain portability may update only aggregate replay-visibility posture')

    if auth.get('authorization_status') != 'authorized':
        errors.append('aggregate correction authority reference requires authorized authorization_status')
    if auth.get('authority_role') == 'unknown_or_redacted':
        errors.append('aggregate correction authority role cannot be unknown_or_redacted')
    if auth.get('authorization_basis') == 'unknown_or_redacted':
        errors.append('aggregate correction authority authorization_basis cannot be unknown_or_redacted')
    if not isinstance(auth.get('authority_digest'), dict):
        errors.append('aggregate correction authority reference requires authority_digest')

    status = lineage.get('status') if isinstance(lineage, dict) else None
    role = auth.get('authority_role')
    if status == 'original' and role != 'original_publication_authority':
        errors.append('original aggregate publication requires original_publication_authority role')
    expected_roles = {
        'corrected': 'aggregate_publication_correction_authority',
        'withdrawn': 'aggregate_withdrawal_authority',
        'superseded': 'aggregate_supersession_authority',
        'reconciled': 'aggregate_reconciliation_authority',
    }
    if status in expected_roles and role != expected_roles[status]:
        errors.append(f'{status} aggregate publication requires {expected_roles[status]} role')

    nstate = notification.get('notification_state')
    effect = notification.get('staleness_effect')
    if status == 'original':
        if nstate not in {'not_applicable', 'notified_within_policy'}:
            errors.append('original aggregate publication notification state must be not_applicable or notified_within_policy')
    elif status in expected_roles:
        if nstate not in {'notified_within_policy', 'deferred_but_within_policy'}:
            errors.append(f'{status} aggregate publication requires correction notification within policy')
        if not isinstance(notification.get('notification_digest'), dict):
            errors.append(f'{status} aggregate publication requires notification_digest')
        if effect != 'aggregate_interpretation_current':
            errors.append(f'{status} aggregate publication with current correction lineage requires aggregate_interpretation_current notification staleness_effect')

    if nstate in {'stale_or_unchecked', 'failed_or_withdrawn', 'unknown_or_redacted'} and effect == 'aggregate_interpretation_current':
        errors.append('stale or unknown correction notification cannot support current aggregate interpretation')
    if nstate in {'notified_within_policy', 'deferred_but_within_policy'}:
        if not notification.get('issued_at') or not notification.get('last_notification_at') or not isinstance(notification.get('max_notification_delay_seconds'), int):
            errors.append('correction notification within policy requires issued_at, last_notification_at, and max_notification_delay_seconds')
        else:
            try:
                issued = parse_dt(notification.get('issued_at', ''))
                last = parse_dt(notification.get('last_notification_at', ''))
                max_delay = int(notification.get('max_notification_delay_seconds'))
                if last < issued:
                    errors.append('correction notification last_notification_at cannot be before issued_at')
                if (last - issued).total_seconds() > max_delay:
                    errors.append('correction notification exceeded max_notification_delay_seconds')
            except Exception as exc:  # noqa: BLE001
                errors.append(f'correction notification time parse error: {exc}')

    if aggregate is not None:
        record_time = aggregate.get('_record_created_at') or aggregate.get('_record_issued_at')
        if record_time and auth.get('authorization_checked_at'):
            errors.extend(check_time_not_after(
                auth.get('authorization_checked_at'),
                record_time,
                value_label='aggregate correction authority authorization_checked_at',
                anchor_label='aggregate_record_created_at',
            ))
        if record_time and notification.get('issued_at'):
            errors.extend(check_time_not_after(
                notification.get('issued_at'),
                record_time,
                value_label='aggregate correction notification issued_at',
                anchor_label='aggregate_record_created_at',
            ))
        if record_time and notification.get('last_notification_at'):
            errors.extend(check_time_not_after(
                notification.get('last_notification_at'),
                record_time,
                value_label='aggregate correction notification last_notification_at',
                anchor_label='aggregate_record_created_at',
            ))
        scope = aggregate.get('aggregation_scope', {}) if isinstance(aggregate.get('aggregation_scope'), dict) else {}
        cross_operator = scope.get('operator_scope') == 'compatible_operator_cohort'
    else:
        cross_operator = False

    portable = portability.get('chain_portability_state') == 'portable_to_compatible_operator' or portability.get('operator_scope') == 'compatible_operator_digest_bound'
    if portability.get('authority_equivalence') == 'weaker_or_unknown':
        errors.append('aggregate correction authority equivalence cannot be weaker_or_unknown')
    if portability.get('thresholds_or_authority_equivalence_weakened') is not False:
        errors.append('aggregate correction authority equivalence cannot weaken thresholds or authority')
    if cross_operator or portable:
        if portability.get('operator_scope') != 'compatible_operator_digest_bound':
            errors.append('compatible-operator correction-chain portability requires compatible_operator_digest_bound operator_scope')
        if portability.get('authority_equivalence') != 'digest_bound_equivalent_or_stricter':
            errors.append('compatible-operator correction-chain portability requires digest-bound equivalent-or-stricter authority equivalence')
        if not digest_binds(portability.get('compatibility_statement_digest'), 'profile_compatibility_statement'):
            errors.append('compatible-operator correction-chain portability requires compatibility_statement_digest')
        if not digest_binds(portability.get('portable_correction_chain_digest'), 'aggregate_publication_revision_chain'):
            errors.append('compatible-operator correction-chain portability requires portable_correction_chain_digest')
    if portability.get('operator_scope') == 'unknown_or_redacted' or portability.get('chain_portability_state') == 'unknown_or_redacted':
        errors.append('aggregate correction-chain portability cannot be unknown_or_redacted for retained aggregate interpretation')
    return errors


def check_aggregate_revision_lineage(aggregate: dict[str, Any]) -> list[str]:
    """Correction, withdrawal, supersession, and reconciliation checks for aggregate publications."""
    errors: list[str] = []
    lineage = aggregate.get('aggregate_revision_lineage') if isinstance(aggregate.get('aggregate_revision_lineage'), dict) else None
    if lineage is None:
        return ['aggregate verifier audit summary requires aggregate_revision_lineage']

    authority_ref = lineage.get('correction_authority_reference')
    if not isinstance(authority_ref, dict):
        errors.append('aggregate revision lineage requires correction_authority_reference')
    else:
        errors.extend(check_aggregate_correction_authority_reference(authority_ref, lineage, aggregate))

    errors.extend(check_aggregate_revision_lineage_semantics(aggregate))
    return errors

def check_aggregate_lifecycle_rollup(aggregate: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    rollup = aggregate.get('aggregate_correction_authority_lifecycle_rollup')
    if not isinstance(rollup, dict):
        return errors
    boundary = rollup.get('boundary', {}) if isinstance(rollup.get('boundary'), dict) else {}
    for key in ('authority_roster_exported', 'authority_identity_exported', 'incident_times_exported', 'notification_recipient_details_exported', 'lifecycle_rollup_updates_profile_assessment', 'external_lifecycle_rollup_interpreted_as_timesync_provenance'):
        if boundary.get(key) is not False:
            errors.append(f'aggregate lifecycle rollup boundary.{key} must be false')
    if boundary.get('lifecycle_rollup_updates_replay_visibility_only') is not True:
        errors.append('aggregate lifecycle rollup may update only aggregate replay-visibility posture')
    window = rollup.get('rollup_window', {}) if isinstance(rollup.get('rollup_window'), dict) else {}
    if window.get('start') and window.get('end'):
        errors.extend(check_time_order(
            window.get('start'),
            window.get('end'),
            start_label='aggregate lifecycle rollup window start',
            end_label='aggregate lifecycle rollup window end',
            error_message='aggregate lifecycle rollup window start must be before end',
        ))
        record_time = aggregate.get('_record_created_at') or aggregate.get('_record_issued_at')
        if record_time:
            errors.extend(check_time_not_after(
                window.get('end'),
                record_time,
                value_label='aggregate lifecycle rollup window end',
                anchor_label='aggregate_record_created_at',
            ))
    decisions = rollup.get('decision_population', {}) if isinstance(rollup.get('decision_population'), dict) else {}
    decision = rollup.get('current_interpretation_decision')
    if decision in {'current_supported', 'current_supported_guarded'}:
        suppress_total = sum(decisions.get(k, 0) for k in decisions if isinstance(k, str) and k.startswith('suppressed_by_'))
        if suppress_total:
            errors.append('aggregate lifecycle rollup cannot be current-supported while suppressed decisions are present in the rollup population')
    if decision and isinstance(decisions.get(decision), int) and decisions.get(decision) == 0 and decision != 'historical_only':
        errors.append('aggregate lifecycle rollup selected decision must have non-zero population unless historical_only')
    digest_bindings = [d for d in rollup.get('digest_bindings', []) if isinstance(d, dict)]
    if not any(digest_binds(d, 'aggregate_lifecycle_decision_table') for d in digest_bindings):
        errors.append('aggregate lifecycle rollup requires a digest binding to aggregate_lifecycle_decision_table')
    if not any(digest_binds(d, 'aggregate_correction_authority_lifecycle_summary') for d in digest_bindings):
        errors.append('aggregate lifecycle rollup requires a digest binding to aggregate_correction_authority_lifecycle_summary')
    resync = rollup.get('emergency_resynchronization_summary', {}) if isinstance(rollup.get('emergency_resynchronization_summary'), dict) else {}
    if resync and resync.get('resynchronization_state') not in {None, 'not_applicable'}:
        if not digest_binds(resync.get('notification_policy_digest'), 'aggregate_emergency_resynchronization_policy'):
            errors.append('emergency resynchronization rollup requires notification_policy_digest binding aggregate_emergency_resynchronization_policy')
        if decision == 'current_supported':
            errors.append('current-supported rollup cannot carry active emergency resynchronization')
    portability = rollup.get('lifecycle_portability_aggregation', {}) if isinstance(rollup.get('lifecycle_portability_aggregation'), dict) else {}
    if portability.get('portability_decision') == 'portable_digest_bound' and not digest_binds(portability.get('compatibility_statement_digest'), 'profile_compatibility_statement'):
        errors.append('portable lifecycle aggregation requires compatibility_statement_digest binding profile_compatibility_statement')
    if portability.get('portability_decision') == 'suppressed_by_portability_failure' and decision in {'current_supported', 'current_supported_guarded'}:
        errors.append('current-supported rollup cannot coexist with portability failure suppression')
    return errors


def check_policy_lifecycle_authority_recovery_attestation(att: dict[str, Any], compromise: dict[str, Any] | None = None, auth: dict[str, Any] | None = None, record: dict[str, Any] | None = None) -> list[str]:
    """Check digest-bound lifecycle-authority recovery attestation references."""
    errors: list[str] = []
    scope = att.get('scope', {}) if isinstance(att.get('scope'), dict) else {}
    portability = att.get('portability', {}) if isinstance(att.get('portability'), dict) else {}
    window = att.get('incident_window', {}) if isinstance(att.get('incident_window'), dict) else {}
    boundary = att.get('non_interpretation_boundary', {}) if isinstance(att.get('non_interpretation_boundary'), dict) else {}

    for key in (
        'recovery_attestation_is_profile_evidence',
        'recovery_attestation_updates_actionability',
        'recovery_attestation_reopens_assessment',
        'recovery_attestation_interpreted_as_timesync_provenance',
        'authority_key_material_exported',
        'authority_roster_exported',
        'delegation_chain_exported',
        'incident_forensics_exported',
        'legal_authority_details_exported',
        'external_incident_record_interpreted_by_timesync',
    ):
        if boundary.get(key) is not False:
            errors.append(f'policy lifecycle authority recovery attestation boundary {key} must be false')
    if window.get('incident_forensics_exported') is not False:
        errors.append('policy lifecycle authority recovery attestation cannot export incident forensics')
    if window.get('window_updates_replay_visibility_only') is not True:
        errors.append('policy lifecycle authority recovery attestation incident window must update replay visibility only')
    if portability.get('portability_updates_replay_visibility_only') is not True:
        errors.append('policy lifecycle authority recovery attestation portability must update replay visibility only')
    if portability.get('operator_scope') == 'compatible_operator_bound' and not isinstance(portability.get('compatibility_statement_digest'), dict):
        errors.append('cross-operator recovery attestation portability requires compatibility_statement_digest')
    if portability.get('operator_scope') == 'unknown_or_redacted':
        errors.append('current recovery attestation portability cannot be unknown_or_redacted')

    status = att.get('attestation_status')
    effect = att.get('replay_visibility_effect')
    if effect == 'recovered_current' and status != 'current':
        errors.append('current recovery attestation replay visibility requires current attestation_status')
    if effect in {'historical_only', 'contested_visibility'} and record is not None:
        anchor_eval = record.get('anchor_evaluation', {}) if isinstance(record.get('anchor_evaluation'), dict) else {}
        if anchor_eval.get('current_visibility_status') == 'current_at_evaluation':
            errors.append('recovery attestation with non-current visibility cannot support current replay visibility')
    if effect == 'unknown':
        errors.append('recovery attestation replay visibility effect cannot be unknown for current evaluation')
    if window.get('window_state') in {'open_under_review', 'unknown_or_redacted'} and effect == 'recovered_current':
        errors.append('recovered-current replay visibility requires bounded recovery incident window')
    errors.extend(check_time_order(
        window.get('not_before'),
        window.get('not_after'),
        start_label='recovery attestation incident_window.not_before',
        end_label='recovery attestation incident_window.not_after',
        allow_equal=False,
        error_message='recovery attestation incident_window.not_before must be before not_after',
    ))
    errors.extend(check_policy_lifecycle_recovery_temporal(att, compromise=compromise))
    errors.extend(check_policy_lifecycle_recovery_attestation_digest_bindings(att))

    if auth is not None:
        pol = auth.get('policy_digest', {}) if isinstance(auth.get('policy_digest'), dict) else {}
        if pol and scope.get('policy_digest', {}).get('value') != pol.get('value'):
            errors.append('recovery attestation policy_digest must match lifecycle authority reference')
    if compromise is not None:
        affected = compromise.get('affected_authority_digest', {}) if isinstance(compromise.get('affected_authority_digest'), dict) else {}
        att_affected = att.get('affected_authority_digest', {}) if isinstance(att.get('affected_authority_digest'), dict) else {}
        if affected and att_affected and affected.get('value') != att_affected.get('value'):
            errors.append('recovery attestation affected_authority_digest must match compromise response')
        succ = compromise.get('successor_or_recovery_authority_digest', {}) if isinstance(compromise.get('successor_or_recovery_authority_digest'), dict) else {}
        att_succ = att.get('recovery_or_successor_authority_digest', {}) if isinstance(att.get('recovery_or_successor_authority_digest'), dict) else {}
        if succ and att_succ and succ.get('value') != att_succ.get('value'):
            errors.append('recovery attestation recovery authority digest must match compromise response')
        response_digest = compromise.get('response_digest', {}) if isinstance(compromise.get('response_digest'), dict) else {}
        att_response = att.get('response_digest', {}) if isinstance(att.get('response_digest'), dict) else {}
        if response_digest and att_response and response_digest.get('value') != att_response.get('value'):
            errors.append('recovery attestation response_digest must match compromise response')
        if compromise.get('replay_visibility_effect') != effect:
            errors.append('recovery attestation replay_visibility_effect must match compromise response')
    return errors


def check_policy_lifecycle_authority_reference(auth: dict[str, Any], ref: dict[str, Any] | None = None, record: dict[str, Any] | None = None) -> list[str]:
    """Check compact lifecycle-authority discovery, renewal, and anti-rollback posture."""
    errors: list[str] = []
    discovery = auth.get('discovery', {}) if isinstance(auth.get('discovery'), dict) else {}
    renewal = auth.get('renewal_hint', {}) if isinstance(auth.get('renewal_hint'), dict) else {}
    seq = auth.get('anti_rollback_sequence', {}) if isinstance(auth.get('anti_rollback_sequence'), dict) else {}
    rotation = auth.get('rotation_delegation_status', {}) if isinstance(auth.get('rotation_delegation_status'), dict) else {}
    rotation_boundary = rotation.get('non_interpretation_boundary', {}) if isinstance(rotation.get('non_interpretation_boundary'), dict) else {}
    compromise = rotation.get('compromise_response', {}) if isinstance(rotation.get('compromise_response'), dict) else {}
    boundary = auth.get('non_interpretation_boundary', {}) if isinstance(auth.get('non_interpretation_boundary'), dict) else {}

    if ref is not None:
        ref_digest = ref.get('policy_digest', {}) if isinstance(ref.get('policy_digest'), dict) else {}
        auth_digest = auth.get('policy_digest', {}) if isinstance(auth.get('policy_digest'), dict) else {}
        if auth_digest.get('value') != ref_digest.get('value'):
            errors.append('policy lifecycle authority reference policy_digest must match trust-policy reference')
        lifecycle = ref.get('lifecycle_status', {}) if isinstance(ref.get('lifecycle_status'), dict) else {}
        status_digest = lifecycle.get('status_record_digest', {}) if isinstance(lifecycle.get('status_record_digest'), dict) else {}
        seq_digest = seq.get('status_record_digest', {}) if isinstance(seq.get('status_record_digest'), dict) else {}
        binding_digest = discovery.get('authority_binding_digest', {}) if isinstance(discovery.get('authority_binding_digest'), dict) else {}
        if status_digest and seq_digest and seq_digest.get('value') != status_digest.get('value'):
            errors.append('policy lifecycle authority sequence must bind the lifecycle status_record_digest')
        if status_digest and binding_digest and binding_digest.get('binds') == 'transparency_trust_policy_lifecycle_status' and binding_digest.get('value') != status_digest.get('value'):
            errors.append('policy lifecycle authority discovery must bind the lifecycle status_record_digest')

    if auth.get('status_channel') == 'unknown_or_redacted':
        errors.append('current policy lifecycle authority status channel cannot be unknown_or_redacted')
    if discovery.get('discovery_state') == 'unknown_or_redacted' or discovery.get('discovery_basis') == 'unknown_or_redacted':
        errors.append('current policy lifecycle authority discovery cannot be unknown_or_redacted')
    if discovery.get('repository_topology_exported') is not False:
        errors.append('policy lifecycle authority discovery cannot export repository topology')
    if discovery.get('status_endpoint_exported') is not False:
        errors.append('policy lifecycle authority discovery cannot export status endpoints or APIs')
    if discovery.get('trust_anchor_material_exported') is not False:
        errors.append('policy lifecycle authority discovery cannot export trust-anchor material')
    if discovery.get('authority_discovery_updates_replay_visibility_only') is not True:
        errors.append('policy lifecycle authority discovery must update replay visibility only')
    if discovery.get('discovery_state') == 'compatibility_statement_bound' and not isinstance(discovery.get('compatibility_statement_digest'), dict):
        errors.append('compatibility-bound policy lifecycle authority discovery requires compatibility_statement_digest')

    hint_state = renewal.get('hint_state')
    if hint_state in {'successor_digest_available', 'renewal_available'}:
        if not isinstance(renewal.get('successor_policy_digest'), dict):
            errors.append('policy lifecycle renewal hint requires successor_policy_digest')
        if not isinstance(renewal.get('expected_next_sequence'), int):
            errors.append('policy lifecycle renewal hint requires expected_next_sequence')
    if renewal.get('hint_does_not_export_repository_topology') is not True:
        errors.append('policy lifecycle renewal hint cannot export repository topology')
    if renewal.get('hint_does_not_update_profile_assessment') is not True:
        errors.append('policy lifecycle renewal hint must not update profile assessment')
    if renewal.get('hint_interpreted_as_timesync_provenance') is not False:
        errors.append('policy lifecycle renewal hint cannot be interpreted as TimeSync provenance')

    seq_num = seq.get('sequence_number')
    prev_num = seq.get('previous_sequence_number')
    if isinstance(seq_num, int) and isinstance(prev_num, int) and prev_num >= seq_num:
        errors.append('policy lifecycle sequence must be monotonic when previous_sequence_number is present')
    expected_next = renewal.get('expected_next_sequence')
    if isinstance(seq_num, int) and isinstance(expected_next, int) and expected_next <= seq_num:
        errors.append('policy lifecycle renewal hint expected_next_sequence must be greater than current sequence_number')
    if seq.get('monotonicity') != 'monotonic_checked':
        errors.append('current policy lifecycle authority requires monotonic sequence checked')
    if seq.get('rollback_status') != 'no_rollback_detected':
        errors.append('current policy lifecycle authority requires no rollback detected')
    freeze = seq.get('freeze_check', {}) if isinstance(seq.get('freeze_check'), dict) else {}
    if freeze.get('status') != 'fresh':
        errors.append('current policy lifecycle authority requires fresh lifecycle status, not stale or unchecked')
    if isinstance(freeze.get('observed_status_age_seconds'), int) and isinstance(freeze.get('max_status_age_seconds'), int):
        if freeze['observed_status_age_seconds'] > freeze['max_status_age_seconds']:
            errors.append('policy lifecycle authority status age exceeds max_status_age_seconds')
    if seq.get('sequence_does_not_update_profile_assessment') is not True:
        errors.append('policy lifecycle authority sequence must not update profile assessment')

    rotation_state = rotation.get('rotation_state')
    if rotation_state == 'unknown_or_redacted' or rotation_state is None:
        errors.append('current policy lifecycle authority rotation cannot be unknown_or_redacted')
    if rotation_state == 'planned_rotation_to_successor' and not isinstance(rotation.get('successor_authority_digest'), dict):
        errors.append('planned lifecycle-authority rotation requires successor_authority_digest')
    if rotation_state in {'planned_rotation_to_successor', 'successor_authority_active'} and not isinstance(rotation.get('rotation_statement_digest'), dict):
        errors.append('lifecycle-authority rotation requires rotation_statement_digest')
    auth_digest_value = auth.get('authority_digest', {}).get('value') if isinstance(auth.get('authority_digest'), dict) else None
    succ_digest = rotation.get('successor_authority_digest', {}) if isinstance(rotation.get('successor_authority_digest'), dict) else {}
    if rotation_state == 'planned_rotation_to_successor' and auth_digest_value and succ_digest.get('value') == auth_digest_value:
        errors.append('planned lifecycle-authority successor digest must differ from current authority digest')

    delegation_state = rotation.get('delegation_state')
    delegation_scope = rotation.get('delegation_scope')
    if delegation_state == 'unknown_or_redacted' or delegation_state is None:
        errors.append('current policy lifecycle authority delegation cannot be unknown_or_redacted')
    if delegation_state == 'not_delegated' and delegation_scope != 'none':
        errors.append('not_delegated lifecycle authority must use delegation_scope none')
    if delegation_state != 'not_delegated' and delegation_scope in {None, 'none', 'redacted'}:
        errors.append('delegated lifecycle authority requires a concrete delegation_scope')
    if delegation_state != 'not_delegated' and not isinstance(rotation.get('delegation_digest'), dict):
        errors.append('delegated lifecycle authority requires delegation_digest')

    compromise_state = compromise.get('state')
    if compromise_state in {'suspected_under_review', 'confirmed_unresolved', 'unknown', None}:
        errors.append('current policy lifecycle authority rotation/delegation requires no unresolved compromise')
    if compromise_state == 'none_known' and compromise.get('replay_visibility_effect') != 'no_current_effect':
        errors.append('none_known lifecycle-authority compromise requires replay_visibility_effect no_current_effect')
    if compromise_state == 'confirmed_contained':
        if compromise.get('replay_visibility_effect') not in {'recovered_current', 'historical_only', 'contested_visibility'}:
            errors.append('contained lifecycle-authority compromise requires recovered_current, historical_only, or contested replay-visibility effect')
        if not isinstance(compromise.get('successor_or_recovery_authority_digest'), dict):
            errors.append('contained lifecycle-authority compromise requires successor_or_recovery_authority_digest')
        if not isinstance(compromise.get('response_digest'), dict):
            errors.append('contained lifecycle-authority compromise requires response_digest')
        recovery_att = compromise.get('recovery_attestation_reference')
        if not isinstance(recovery_att, dict):
            errors.append('contained lifecycle-authority compromise requires recovery_attestation_reference')
        else:
            errors.extend(check_policy_lifecycle_authority_recovery_attestation(recovery_att, compromise, auth, record))
        if record is not None:
            anchor_eval = record.get('anchor_evaluation', {}) if isinstance(record.get('anchor_evaluation'), dict) else {}
            current_visibility = anchor_eval.get('current_visibility_status')
            if current_visibility == 'current_at_evaluation' and compromise.get('replay_visibility_effect') != 'recovered_current':
                errors.append('current replay visibility after contained compromise requires recovered_current recovery attestation')
            if current_visibility == 'historical_only' and compromise.get('replay_visibility_effect') == 'recovered_current':
                errors.append('historical-only replay visibility cannot use recovered_current compromise effect')
    if compromise.get('compromise_response_updates_replay_visibility_only') is not True:
        errors.append('lifecycle-authority compromise response must update replay visibility only')
    if compromise.get('compromise_response_interpreted_as_timesync_provenance') is not False:
        errors.append('lifecycle-authority compromise response cannot be interpreted as TimeSync provenance')

    for key in (
        'authority_key_material_exported',
        'delegation_chain_exported',
        'authority_roster_exported',
        'rotation_protocol_exported',
        'compromise_forensics_exported',
        'rotation_or_delegation_is_profile_evidence',
        'rotation_or_delegation_updates_actionability',
        'rotation_or_delegation_reopens_assessment',
        'rotation_or_delegation_interpreted_as_timesync_provenance',
    ):
        if rotation_boundary.get(key) is not False:
            errors.append(f'policy lifecycle authority rotation boundary {key} must be false')
    if rotation_boundary.get('rotation_or_delegation_updates_replay_visibility_only') is not True:
        errors.append('policy lifecycle authority rotation/delegation must update replay visibility only')

    for key in (
        'authority_reference_is_profile_evidence',
        'authority_reference_updates_actionability',
        'authority_reference_reopens_assessment',
        'authority_reference_interpreted_as_timesync_provenance',
        'authority_repository_metadata_exported',
        'status_endpoint_or_api_exported',
        'trust_anchor_material_exported',
    ):
        if boundary.get(key) is not False:
            errors.append(f'policy lifecycle authority boundary {key} must be false')
    if boundary.get('authority_reference_updates_replay_visibility_only') is not True:
        errors.append('policy lifecycle authority reference must update replay visibility only')

    errors.extend(check_policy_lifecycle_authority_temporal(auth, ref=ref, record=record))
    errors.extend(check_policy_lifecycle_authority_digest_bindings(auth))
    return errors

def check_transparency_policy_lifecycle_status(ref: dict[str, Any], record: dict[str, Any] | None = None) -> list[str]:
    """Evaluate policy-reference lifecycle without importing a policy repository."""
    errors: list[str] = []
    lifecycle = ref.get('lifecycle_status')
    if not isinstance(lifecycle, dict):
        return ['transparency_trust_policy_reference requires lifecycle_status']

    state = lifecycle.get('state')
    evaluated_at_raw = lifecycle.get('evaluated_at')
    errors.extend(check_active_window_status(
        state=state,
        active_state='active',
        evaluated_at=evaluated_at_raw,
        not_before=lifecycle.get('not_before'),
        not_after=lifecycle.get('not_after'),
        label='policy lifecycle',
        active_outside_message='active policy lifecycle evaluation must be inside not_before/not_after',
        expired_state='expired',
        expired_not_after_message='expired policy lifecycle must evaluate after not_after',
        pending_state='pending_activation',
        pending_not_before_message='pending policy lifecycle must evaluate before not_before',
    ))
    try:
        evaluated_at = parse_dt(evaluated_at_raw or '')
    except Exception:  # noqa: BLE001
        evaluated_at = None  # type: ignore[assignment]

    rev = lifecycle.get('revocation_check', {}) if isinstance(lifecycle.get('revocation_check'), dict) else {}
    drift = lifecycle.get('drift_status', {}) if isinstance(lifecycle.get('drift_status'), dict) else {}
    if evaluated_at_raw and rev.get('checked_at'):
        errors.extend(check_time_not_after(
            rev.get('checked_at'),
            evaluated_at_raw,
            value_label='policy lifecycle revocation_check.checked_at',
            anchor_label='policy lifecycle evaluated_at',
        ))
    if evaluated_at_raw and drift.get('checked_at'):
        errors.extend(check_time_not_after(
            drift.get('checked_at'),
            evaluated_at_raw,
            value_label='policy lifecycle drift_status.checked_at',
            anchor_label='policy lifecycle evaluated_at',
        ))
    boundary = lifecycle.get('lifecycle_boundary', {}) if isinstance(lifecycle.get('lifecycle_boundary'), dict) else {}

    if boundary.get('lifecycle_status_updates_replay_visibility_only') is not True:
        errors.append('policy lifecycle status must update replay visibility only')
    for key in (
        'lifecycle_status_is_profile_evidence',
        'lifecycle_status_updates_actionability',
        'lifecycle_status_reopens_assessment',
        'lifecycle_status_interpreted_as_timesync_provenance',
        'policy_language_or_rules_exported',
        'external_policy_repository_interpreted_by_timesync',
    ):
        if boundary.get(key) is not False:
            errors.append(f'policy lifecycle boundary {key} must be false')

    if rev.get('status') == 'revoked' or state == 'revoked':
        errors.append('revoked transparency trust policy reference cannot support current replay visibility')
    if state in {'retired', 'superseded'} and not isinstance(lifecycle.get('successor_policy_digest'), dict):
        errors.append('retired or superseded policy lifecycle requires successor_policy_digest')
    if state == 'active' and rev.get('status') != 'checked_not_revoked':
        errors.append('active policy lifecycle requires revocation status checked_not_revoked')
    if drift.get('thresholds_weakened') is True or drift.get('state') == 'thresholds_weakened':
        errors.append('policy lifecycle drift cannot weaken replay-visibility thresholds')
    if drift.get('state') == 'digest_rollover_without_equivalence':
        errors.append('policy digest rollover requires compatibility-backed lifecycle equivalence')
    if drift.get('state') in {'digest_rollover_compatible', 'thresholds_stricter_or_equal'}:
        if not (isinstance(drift.get('successor_policy_digest'), dict) or isinstance(drift.get('current_policy_digest'), dict)):
            errors.append('policy lifecycle drift compatibility requires current or successor policy digest')
        if drift.get('state') == 'digest_rollover_compatible' and not isinstance(drift.get('compatibility_statement_digest'), dict):
            errors.append('policy digest rollover compatibility requires compatibility_statement_digest')
    if drift.get('state') in {'not_checked', 'unknown'} and state == 'active':
        errors.append('active policy lifecycle requires drift status checked or known')
    if drift.get('drift_does_not_update_profile_assessment') is not True:
        errors.append('policy lifecycle drift must not update profile assessment')

    policy_digest = ref.get('policy_digest', {}) if isinstance(ref.get('policy_digest'), dict) else {}
    cur = drift.get('current_policy_digest', {}) if isinstance(drift.get('current_policy_digest'), dict) else {}
    prev = drift.get('previous_policy_digest', {}) if isinstance(drift.get('previous_policy_digest'), dict) else {}
    if cur and cur.get('value') != policy_digest.get('value') and drift.get('state') == 'no_drift_detected':
        errors.append('no_drift_detected lifecycle status requires current_policy_digest to match policy_digest')
    if prev and prev.get('binds') != 'transparency_trust_policy_rules':
        errors.append('policy lifecycle previous_policy_digest must bind transparency_trust_policy_rules')

    if record is not None:
        anchor_eval = record.get('anchor_evaluation', {}) if isinstance(record.get('anchor_evaluation'), dict) else {}
        if anchor_eval.get('current_visibility_status') == 'current_at_evaluation':
            if state != 'active':
                errors.append('current replay visibility requires active trust-policy lifecycle')
            if rev.get('status') != 'checked_not_revoked':
                errors.append('current replay visibility requires trust-policy revocation checked_not_revoked')
            if drift.get('state') not in {'no_drift_detected', 'thresholds_stricter_or_equal', 'digest_rollover_compatible'}:
                errors.append('current replay visibility requires non-weakening trust-policy drift status')
            if evaluated_at is not None:
                try:
                    ae = parse_dt(anchor_eval.get('evaluated_at', ''))
                    if evaluated_at > ae:
                        errors.append('trust-policy lifecycle cannot be evaluated after replay visibility evaluation')
                except Exception as exc:  # noqa: BLE001
                    errors.append(f'trust-policy lifecycle replay evaluation time parse error: {exc}')
    return errors


def check_policy_lifecycle_equivalence(tpe: dict[str, Any], stmt: dict[str, Any] | None = None) -> list[str]:
    """Check compatibility-statement policy lifecycle equivalence without policy-language import."""
    errors: list[str] = []
    ple = tpe.get('policy_lifecycle_equivalence')
    if not isinstance(ple, dict):
        return ['transparency_policy_equivalence requires policy_lifecycle_equivalence']
    signed_at = None
    expires_at = None
    if isinstance(stmt, dict):
        binding = stmt.get('binding', {}) if isinstance(stmt.get('binding'), dict) else {}
        signed_at = binding.get('signed_at')
        expires_at = stmt.get('expires_at')
    errors.extend(check_policy_lifecycle_equivalence_temporal(
        tpe,
        statement_signed_at=signed_at,
        statement_expires_at=expires_at,
    ))
    state = ple.get('current_equivalence_state')

    if state == 'current':
        if ple.get('subject_policy_state') != 'active' or ple.get('related_policy_state') != 'active':
            errors.append('current policy lifecycle equivalence requires both policy states active')
    if state in {'expired', 'revoked', 'drifted', 'unknown'}:
        errors.append('non-current policy lifecycle equivalence cannot authorize current replay-visibility equivalence')

    rev = ple.get('revocation_check', {}) if isinstance(ple.get('revocation_check'), dict) else {}
    drift = ple.get('drift_check', {}) if isinstance(ple.get('drift_check'), dict) else {}
    nb = ple.get('non_upgrade_boundary', {}) if isinstance(ple.get('non_upgrade_boundary'), dict) else {}
    if rev.get('status') != 'checked_not_revoked' and state == 'current':
        errors.append('current policy lifecycle equivalence requires revocation status checked_not_revoked')
    if drift.get('thresholds_weakened') is True or drift.get('state') == 'thresholds_weakened':
        errors.append('policy lifecycle equivalence cannot weaken thresholds')
    if drift.get('state') == 'digest_rollover_without_equivalence':
        errors.append('policy lifecycle equivalence cannot accept digest rollover without equivalence')
    if drift.get('state') in {'not_checked', 'unknown'} and state == 'current':
        errors.append('current policy lifecycle equivalence requires drift checked or known')
    seqeq = ple.get('sequence_equivalence', {}) if isinstance(ple.get('sequence_equivalence'), dict) else {}
    if state == 'current':
        if seqeq.get('subject_sequence_status') != 'monotonic_checked' or seqeq.get('related_sequence_status') != 'monotonic_checked':
            errors.append('current policy lifecycle equivalence requires monotonic sequence checked for both policies')
        if seqeq.get('rollback_status') != 'no_rollback_detected':
            errors.append('current policy lifecycle equivalence requires no rollback detected')
        if seqeq.get('freeze_status') != 'fresh':
            errors.append('current policy lifecycle equivalence requires fresh sequence status')
    if seqeq.get('sequence_relation') in {'weaker_or_unknown', None}:
        errors.append('policy lifecycle sequence equivalence cannot be weaker_or_unknown')
    if seqeq.get('sequence_equivalence_updates_replay_visibility_only') is not True:
        errors.append('policy lifecycle sequence equivalence must update replay visibility only')

    areq = ple.get('authority_rotation_equivalence', {}) if isinstance(ple.get('authority_rotation_equivalence'), dict) else {}
    if state == 'current':
        if areq.get('subject_rotation_state') in {'unknown_or_redacted', None} or areq.get('related_rotation_state') in {'unknown_or_redacted', None}:
            errors.append('current policy lifecycle authority rotation equivalence requires known rotation states')
        if areq.get('subject_delegation_state') in {'unknown_or_redacted', None} or areq.get('related_delegation_state') in {'unknown_or_redacted', None}:
            errors.append('current policy lifecycle authority delegation equivalence requires known delegation states')
        if areq.get('compromise_response_relation') in {'contested_or_unknown', 'weaker_or_unknown', None}:
            errors.append('current policy lifecycle authority equivalence requires no unresolved compromise')
    if areq.get('authority_rotation_relation') in {'weaker_or_unknown', None}:
        errors.append('policy lifecycle authority rotation equivalence cannot be weaker_or_unknown')
    if areq.get('delegation_relation') in {'weaker_or_unknown', None}:
        errors.append('policy lifecycle authority delegation equivalence cannot be weaker_or_unknown')
    if areq.get('compromise_response_relation') in {'weaker_or_unknown', None}:
        errors.append('policy lifecycle authority compromise-response equivalence cannot be weaker_or_unknown')
    if areq.get('authority_rotation_equivalence_updates_replay_visibility_only') is not True:
        errors.append('policy lifecycle authority rotation equivalence must update replay visibility only')
    arn = areq.get('non_upgrade_boundary', {}) if isinstance(areq.get('non_upgrade_boundary'), dict) else {}
    for key in (
        'authority_rotation_equivalence_is_profile_evidence',
        'authority_rotation_equivalence_updates_actionability',
        'authority_rotation_equivalence_reopens_assessment',
        'authority_rotation_equivalence_interpreted_as_timesync_provenance',
        'authority_roster_or_key_material_exported',
        'delegation_chain_exported',
    ):
        if arn.get(key) is not False:
            errors.append(f'policy_lifecycle_equivalence.authority_rotation_equivalence.non_upgrade_boundary.{key} must be false')

    for key in (
        'lifecycle_equivalence_is_profile_evidence',
        'lifecycle_equivalence_updates_actionability',
        'lifecycle_equivalence_reopens_assessment',
        'lifecycle_equivalence_interpreted_as_timesync_provenance',
        'policy_repository_metadata_exported',
    ):
        if nb.get(key) is not False:
            errors.append(f'policy_lifecycle_equivalence.non_upgrade_boundary.{key} must be false')
    return errors


def check_transparency_trust_policy_reference(ref: dict[str, Any], record: dict[str, Any] | None = None) -> list[str]:
    """Validate digest-bound transparency trust-policy references without importing policy language."""
    errors: list[str] = []
    boundary = ref.get('non_interpretation_boundary', {}) if isinstance(ref.get('non_interpretation_boundary'), dict) else {}
    for key in (
        'trust_policy_reference_is_profile_evidence',
        'trust_policy_reference_updates_actionability',
        'trust_policy_reference_reopens_assessment',
        'trust_policy_reference_interpreted_as_timesync_provenance',
        'trust_policy_language_or_rules_exported',
        'trust_anchor_material_exported',
        'witness_or_monitor_roster_exported',
        'witness_or_monitor_identity_exported',
        'gossip_transcript_exported',
        'external_trust_framework_interpreted_by_timesync',
    ):
        if boundary.get(key) is not False:
            if key == 'trust_policy_reference_updates_actionability':
                errors.append('trust policy reference cannot update actionability')
            elif key == 'trust_policy_reference_is_profile_evidence':
                errors.append('trust policy reference cannot be profile evidence')
            else:
                errors.append(f'transparency_trust_policy_reference.non_interpretation_boundary.{key} must be false')

    digest = ref.get('policy_digest', {}) if isinstance(ref.get('policy_digest'), dict) else {}
    if digest.get('binds') != 'transparency_trust_policy_rules':
        errors.append('transparency_trust_policy_reference policy_digest must bind transparency_trust_policy_rules')
    errors.extend(check_transparency_policy_digest_bindings(ref))

    errors.extend(check_transparency_policy_lifecycle_status(ref, record))
    auth = ref.get('lifecycle_authority_reference')
    if not isinstance(auth, dict):
        errors.append('transparency_trust_policy_reference requires lifecycle_authority_reference')
    else:
        errors.extend(schema_validate('policy-lifecycle-authority-reference', auth))
        errors.extend(check_policy_lifecycle_authority_reference(auth, ref, record))

    xop = ref.get('cross_operator_equivalence', {}) if isinstance(ref.get('cross_operator_equivalence'), dict) else {}
    if xop.get('equivalence_relation') == 'weaker_or_unknown' or xop.get('thresholds_weakened') is True:
        errors.append('trust-policy equivalence cannot be weaker_or_unknown or weaken thresholds')
    if xop.get('equivalence_state') == 'asserted_by_compatibility_statement' and not isinstance(xop.get('compatibility_statement_digest'), dict):
        errors.append('asserted trust-policy equivalence requires compatibility_statement_digest')

    if record is not None:
        replay = record.get('replay_event', {}) if isinstance(record.get('replay_event'), dict) else {}
        anchor_eval = record.get('anchor_evaluation', {}) if isinstance(record.get('anchor_evaluation'), dict) else {}
        wc = record.get('witness_cohort_evaluation', {}) if isinstance(record.get('witness_cohort_evaluation'), dict) else {}
        threshold = ref.get('threshold_summary', {}) if isinstance(ref.get('threshold_summary'), dict) else {}
        if replay.get('using_operator_scope') == 'compatible_operator' and anchor_eval.get('current_visibility_status') == 'current_at_evaluation':
            if xop.get('equivalence_state') != 'asserted_by_compatibility_statement' or not isinstance(xop.get('compatibility_statement_digest'), dict):
                errors.append('cross-operator current replay visibility requires trust-policy equivalence backed by a compatibility statement digest')
        af = anchor_eval.get('anchor_freshness', {}) if isinstance(anchor_eval.get('anchor_freshness'), dict) else {}
        pol_age = threshold.get('anchor_max_age_seconds')
        rec_age = af.get('max_age_seconds')
        if isinstance(pol_age, int) and isinstance(rec_age, int) and rec_age > pol_age:
            errors.append('anchor freshness max_age_seconds exceeds referenced trust-policy threshold')
        if threshold.get('checkpoint_consistency_required') is True:
            cc = anchor_eval.get('checkpoint_consistency', {}) if isinstance(anchor_eval.get('checkpoint_consistency'), dict) else {}
            if cc.get('status') != 'checked_consistent':
                errors.append('referenced trust policy requires checked checkpoint consistency')
        ci = wc.get('cohort_independence', {}) if isinstance(wc.get('cohort_independence'), dict) else {}
        witness_count = ci.get('reported_witness_count', 0)
        monitor_count = ci.get('reported_monitor_count', 0)
        if not isinstance(witness_count, int):
            witness_count = 0
        if not isinstance(monitor_count, int):
            monitor_count = 0
        min_witness = threshold.get('minimum_witness_count')
        min_monitor = threshold.get('minimum_monitor_observation_count')
        min_combined = threshold.get('minimum_combined_observation_count')
        if isinstance(min_witness, int) and wc.get('status') in {'witnessed_consistent', 'combined_witness_and_monitor_consistent'} and witness_count < min_witness:
            errors.append('policy minimum witness threshold not met')
        if isinstance(min_monitor, int) and wc.get('status') in {'monitor_cohort_observed', 'combined_witness_and_monitor_consistent'} and monitor_count < min_monitor:
            errors.append('policy minimum monitor observation threshold not met')
        if isinstance(min_combined, int) and wc.get('status') in {'witnessed_consistent', 'monitor_cohort_observed', 'combined_witness_and_monitor_consistent'} and witness_count + monitor_count < min_combined:
            errors.append('policy minimum combined observation threshold not met')
    return errors

def check_replay_transparency_audit(record: dict[str, Any], catalog_index: dict[tuple[str | None, str, str | None], dict[str, Any]]) -> list[str]:
    """Semantic checks for detached replay-transparency receipts and aggregate verifier summaries."""
    errors: list[str] = []
    boundary = record.get('transparency_boundary', {}) if isinstance(record.get('transparency_boundary'), dict) else {}
    for key in ('replay_transparency_is_profile_evidence', 'replay_transparency_updates_actionability', 'replay_transparency_reopens_assessment', 'verifier_roster_exported', 'verifier_identity_exported', 'legal_authority_details_exported', 'salt_or_preimage_material_exported', 'external_log_interpreted_as_timesync_provenance', 'witness_roster_exported', 'witness_identity_exported', 'monitor_roster_exported', 'monitor_identity_exported', 'gossip_transcript_exported', 'witness_or_monitor_state_interpreted_as_timesync_provenance'):
        if boundary.get(key) is not False:
            errors.append(f'transparency_boundary.{key} must be false')

    tpr = record.get('transparency_trust_policy_reference')
    if isinstance(tpr, dict):
        errors.extend(schema_validate('transparency-trust-policy-reference', tpr))
        errors.extend(check_transparency_trust_policy_reference(tpr, record))

    errors.extend(check_anchor_evaluation(record))
    errors.extend(check_replay_transparency_temporal(record))
    errors.extend(check_aggregate_publication_temporal(record))
    errors.extend(check_replay_core_digest_bindings(record))

    kind = record.get('record_kind')
    if kind == 'challenge_replay_transparency_receipt':
        replay = record.get('replay_event', {}) if isinstance(record.get('replay_event'), dict) else {}
        if replay.get('replay_use') != 'commitment_verification_review':
            errors.append('replay transparency receipt cannot upgrade replay use beyond commitment_verification_review')
        anchor = record.get('transparency_anchor', {}) if isinstance(record.get('transparency_anchor'), dict) else {}
        if anchor.get('anchor_kind') == 'not_logged':
            errors.append('replay transparency receipt must be anchored or explicitly omitted, not exported as not_logged')
        if anchor.get('inclusion_status') != 'included':
            errors.append('replay transparency receipt requires included transparency status')
        if anchor.get('consistency_status') != 'checked_consistent':
            errors.append('replay transparency receipt requires checked_consistent status')
        errors.extend(check_witness_cohort_evaluation(record))
        scope = record.get('scope_binding', {}) if isinstance(record.get('scope_binding'), dict) else {}
        ref_challenge = record.get('referenced_challenge_result')
        if isinstance(ref_challenge, dict):
            nested = schema_validate('authorized-verifier-challenge', ref_challenge) + check_authorized_verifier_challenge(ref_challenge, catalog_index)
            errors.extend(f'referenced_challenge_result: {e}' for e in nested)
            target = ref_challenge.get('target_binding', {}) if isinstance(ref_challenge.get('target_binding'), dict) else {}
            result = ref_challenge.get('challenge_result', {}) if isinstance(ref_challenge.get('challenge_result'), dict) else {}
            if scope.get('challenge_id') != ref_challenge.get('challenge_id'):
                errors.append('replay transparency scope challenge_id does not match referenced challenge result')
            if scope.get('result_id') != result.get('result_id'):
                errors.append('replay transparency scope result_id does not match referenced challenge result')
            if scope.get('summary_id') != target.get('summary_id') or scope.get('assessment_id') != target.get('assessment_id'):
                errors.append('replay transparency scope summary_id/assessment_id does not match referenced challenge result')
            scope_digest = scope.get('assessed_profile_digest', {}) if isinstance(scope.get('assessed_profile_digest'), dict) else {}
            target_digest = target.get('assessed_profile', {}).get('digest', {}) if isinstance(target.get('assessed_profile'), dict) else {}
            if scope_digest.get('value') != target_digest.get('value'):
                errors.append('replay transparency scope profile digest does not match referenced challenge result')
            target_commitments = {str(c.get('commitment_value', '')).lower() for c in target.get('commitments', []) if isinstance(c, dict)}
            scope_commitments = {str(c).lower() for c in scope.get('commitment_values', []) if isinstance(c, str)}
            if not scope_commitments.issubset(target_commitments):
                errors.append('replay transparency scope commitment values must be present in referenced challenge result')
    elif kind == 'aggregate_verifier_audit_summary':
        ag = record.get('aggregate_summary', {}) if isinstance(record.get('aggregate_summary'), dict) else {}
        counts = ag.get('counts', {}) if isinstance(ag.get('counts'), dict) else {}
        privacy = ag.get('privacy_boundary', {}) if isinstance(ag.get('privacy_boundary'), dict) else {}
        total = counts.get('total_replay_events')
        unique = counts.get('unique_challenge_results')
        reuses = counts.get('portable_result_reuses')
        if isinstance(total, int) and isinstance(unique, int) and unique > total:
            errors.append('aggregate verifier audit summary unique_challenge_results cannot exceed total_replay_events')
        if isinstance(total, int) and isinstance(reuses, int) and reuses > total:
            errors.append('aggregate verifier audit summary portable_result_reuses cannot exceed total_replay_events')
        minimum = privacy.get('minimum_group_size')
        if isinstance(total, int) and isinstance(minimum, int) and total < minimum and counts.get('small_group_suppressed') is not True:
            errors.append('aggregate verifier audit summary must suppress counts below the minimum group size')
        for key in ('verifier_roster_exported', 'verifier_identity_exported', 'legal_authority_details_exported', 'commitment_values_exported'):
            if privacy.get(key) is not False:
                errors.append(f'aggregate verifier audit privacy_boundary.{key} must be false')
        ag['_record_issued_at'] = record.get('issued_at')
        ag['_record_created_at'] = record.get('aggregate_record_created_at') or record.get('issued_at')
        if not record.get('aggregate_record_created_at'):
            errors.append('aggregate verifier audit summary requires aggregate_record_created_at to separate publication event time from artifact creation/check time')
        guard = record.get('scope_composition_guard')
        if isinstance(guard, dict):
            errors.extend(f'scope_composition_guard: {e}' for e in schema_validate('scope-composition-guard', guard))
            errors.extend(f'scope_composition_guard: {e}' for e in check_scope_composition_guard(guard, record))
        external_receipt = record.get('external_transparency_receipt_reference')
        if isinstance(external_receipt, dict):
            errors.extend(check_external_transparency_receipt_reference(external_receipt))
        errors.extend(check_monitor_cohort_coverage(ag))
        errors.extend(check_aggregate_privacy_controls(ag))
        errors.extend(check_aggregate_revision_lineage(ag))
        errors.extend(check_aggregate_lifecycle_rollup(ag))
        errors.extend(check_compromise_era_suppression(ag))
        errors.extend(check_recovery_audit_rollup(ag))
    return errors

def check_profile_compatibility_statement(stmt: dict[str, Any], catalog_index: dict[tuple[str | None, str, str | None], dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    subject = stmt.get('subject_profile', {})
    related = stmt.get('related_profile', {})
    relation = stmt.get('relation')
    for label, ref in (('subject_profile', subject), ('related_profile', related)):
        if not isinstance(ref, dict):
            errors.append(f'{label} must be object')
            continue
        if not ref.get('authority'):
            errors.append(f'{label} must include authority')
        if not ref.get('digest'):
            errors.append(f'{label} must include digest')
    subject_rec = resolve_profile(subject, catalog_index) if isinstance(subject, dict) else None
    if subject_rec is not None and subject.get('digest', {}).get('value') != subject_rec.get('normative_rules_digest', {}).get('value'):
        errors.append('subject_profile digest does not match local catalog')
    if relation == 'exact_equivalent':
        if subject.get('digest', {}).get('value') != related.get('digest', {}).get('value'):
            errors.append('exact_equivalent requires identical normative profile digest values')
    if relation == 'alias_for':
        issuer = stmt.get('binding', {}).get('issuer')
        if issuer not in {subject.get('authority'), related.get('authority')}:
            errors.append('alias_for binding issuer must be subject or related profile authority')
    workflows = set(stmt.get('compatible_workflows', [])) if isinstance(stmt.get('compatible_workflows'), list) else set()
    if 'authorized_verifier_challenge_result_portability' in workflows:
        if stmt.get('evidence_policy_relation') not in {'identical', 'stricter_or_equal'}:
            errors.append('authorized verifier challenge portability workflow requires identical or stricter_or_equal evidence policy relation')
        if relation == 'alias_for':
            errors.append('alias_for cannot by itself authorize challenge-result portability')
    if 'replay_transparency_recovery_attestation_portability' in workflows:
        if stmt.get('evidence_policy_relation') not in {'identical', 'stricter_or_equal'}:
            errors.append('replay-transparency recovery attestation portability requires identical or stricter_or_equal evidence policy relation')
        if relation == 'alias_for':
            errors.append('alias_for cannot by itself authorize recovery-attestation portability')
    if 'replay_transparency_policy_equivalence' in workflows:
        if stmt.get('evidence_policy_relation') not in {'identical', 'stricter_or_equal'}:
            errors.append('replay-transparency policy equivalence requires identical or stricter_or_equal evidence policy relation')
        if relation == 'alias_for':
            errors.append('alias_for cannot by itself authorize replay-transparency policy equivalence')
        tpe = stmt.get('transparency_policy_equivalence')
        if not isinstance(tpe, dict):
            errors.append('replay-transparency policy equivalence workflow requires transparency_policy_equivalence')
        else:
            if tpe.get('equivalence_scope') != 'replay_visibility_only':
                errors.append('transparency_policy_equivalence scope must be replay_visibility_only')
            if tpe.get('equivalence_relation') == 'weaker_or_unknown':
                errors.append('replay-transparency policy equivalence cannot be weaker_or_unknown')
            subj_pol = tpe.get('subject_policy_reference', {}) if isinstance(tpe.get('subject_policy_reference'), dict) else {}
            rel_pol = tpe.get('related_policy_reference', {}) if isinstance(tpe.get('related_policy_reference'), dict) else {}
            if tpe.get('equivalence_relation') == 'identical_policy_digest' and subj_pol.get('policy_digest', {}).get('value') != rel_pol.get('policy_digest', {}).get('value'):
                errors.append('identical replay-transparency policy equivalence requires identical policy digest values')
            th = tpe.get('threshold_equivalence', {}) if isinstance(tpe.get('threshold_equivalence'), dict) else {}
            if th.get('weaker_thresholds_allowed') is not False or any(th.get(k) in {'weaker', 'unknown'} for k in ('anchor_freshness_relation', 'checkpoint_consistency_relation', 'witness_threshold_relation', 'monitor_cohort_relation', 'split_view_handling_relation')):
                errors.append('replay-transparency policy equivalence cannot allow weaker thresholds')
            nb = tpe.get('non_upgrade_boundary', {}) if isinstance(tpe.get('non_upgrade_boundary'), dict) else {}
            for key in ('policy_equivalence_is_profile_evidence', 'policy_equivalence_updates_actionability', 'policy_equivalence_reopens_assessment', 'policy_equivalence_interpreted_as_timesync_provenance', 'trust_anchor_or_witness_roster_exported'):
                if nb.get(key) is not False:
                    errors.append(f'transparency_policy_equivalence.non_upgrade_boundary.{key} must be false')
            errors.extend(check_policy_lifecycle_equivalence(tpe, stmt))
    elif isinstance(stmt.get('transparency_policy_equivalence'), dict):
        errors.append('transparency_policy_equivalence requires replay_transparency_policy_equivalence compatible workflow')

    drift = stmt.get('compatibility_drift') if isinstance(stmt.get('compatibility_drift'), dict) else None
    drift_workflows = {'profile_compatibility_drift_review', 'aggregate_lifecycle_portability', 'discovery_downgrade_review'}
    if workflows & drift_workflows and drift is None:
        errors.append('profile compatibility drift workflow requires compatibility_drift decision')
    if drift is not None:
        errors.extend(f'compatibility_drift: {e}' for e in schema_validate('profile-compatibility-drift-decision', drift))
        errors.extend(f'compatibility_drift: {e}' for e in check_profile_compatibility_drift_decision(drift))
        if stmt.get('evidence_policy_relation') in {'weaker', 'unknown'} and drift.get('current_use_allowed') is True:
            errors.append('profile compatibility statement cannot allow current use with weaker or unknown evidence policy relation')
    errors.extend(check_profile_compatibility_statement_temporal(stmt))
    return errors


def check_profile_markdown_digests(catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    by_id = {rec.get('id'): rec for rec in catalog.get('profiles', [])}
    for path in sorted((ROOT / 'profiles').glob('P[0-9]*.md')):
        text = path.read_text(encoding='utf-8')
        pid = path.stem
        rec = by_id.get(pid)
        if rec is None:
            errors.append(f'{path.relative_to(ROOT)} has no matching profile catalog entry')
            continue
        digests = re.findall(r'sha256:([A-Fa-f0-9]{64})', text)
        if not digests:
            errors.append(f'{path.relative_to(ROOT)} does not render a normative digest')
            continue
        expected = rec.get('normative_rules_digest', {}).get('value')
        if expected not in digests:
            errors.append(f'{path.relative_to(ROOT)} rendered digest does not match profile catalog for {pid}')
        rendered_line = ''
        for line in text.splitlines():
            if line.startswith('classes_that_cannot_satisfy_profile_obligations:'):
                rendered_line = line
                break
        if rendered_line:
            for cls in rec.get('evidence_policy', {}).get('classes_that_cannot_satisfy_profile_obligations', []):
                if cls not in rendered_line:
                    errors.append(f'{path.relative_to(ROOT)} rendered forbidden evidence class list omits {cls}')
        else:
            errors.append(f'{path.relative_to(ROOT)} does not render forbidden evidence class list')
        if 'rev0062 profile map' in text or 'rev0064 evidence policy' in text:
            errors.append(f'{path.relative_to(ROOT)} contains stale revision text')
    return errors

def check_acceptance_tests() -> list[str]:
    errors: list[str] = []
    try:
        tests = load_yaml('tests/acceptance-tests.yaml')
    except Exception as exc:  # noqa: BLE001
        return [f'YAML error in tests/acceptance-tests.yaml: {exc}']
    if not isinstance(tests, list):
        return ['tests/acceptance-tests.yaml must be a list']
    required = {'id', 'name', 'given', 'when', 'then'}
    seen: set[str] = set()
    for i, test in enumerate(tests, start=1):
        if not isinstance(test, dict):
            errors.append(f'test #{i} is not an object')
            continue
        missing = required - set(test)
        if missing:
            errors.append(f'test #{i} missing fields: {sorted(missing)}')
        test_id = test.get('id')
        if test_id in seen:
            errors.append(f'duplicate test id: {test_id}')
        seen.add(test_id)
    return errors


def check_schema_documents() -> list[str]:
    errors: list[str] = []
    try:
        import jsonschema  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return [f'jsonschema dependency unavailable: {exc}']
    for path in sorted((ROOT / 'schema').glob('*.json')):
        rel = str(path.relative_to(ROOT))
        try:
            schema = load_json(rel)
        except Exception as exc:  # noqa: BLE001
            errors.append(f'{rel}: JSON error: {exc}')
            continue
        try:
            jsonschema.Draft202012Validator.check_schema(schema)
        except Exception as exc:  # noqa: BLE001
            errors.append(f'{rel}: invalid Draft 2020-12 JSON Schema: {exc}')
        if schema.get('$schema') != 'https://json-schema.org/draft/2020-12/schema':
            errors.append(f"{rel}: $schema must be 'https://json-schema.org/draft/2020-12/schema'")
        expected_id = SCHEMA_ID_PREFIX + path.name
        if schema.get('$id') != expected_id:
            errors.append(f"{rel}: $id {schema.get('$id')!r} must be {expected_id!r}")
    return errors



def check_manifest() -> list[str]:
    errors: list[str] = []
    try:
        manifest = load_json('MANIFEST.json')
    except Exception as exc:  # noqa: BLE001
        return [f'MANIFEST.json error: {exc}']
    files = manifest.get('files')
    if not isinstance(files, list):
        return ['MANIFEST.json files must be a list']
    listed: dict[str, dict[str, Any]] = {}
    ordered_paths: list[str] = []
    for index, entry in enumerate(files):
        if not isinstance(entry, dict):
            errors.append(f'MANIFEST entry #{index + 1} must be an object')
            continue
        rel = entry.get('path')
        if not isinstance(rel, str) or not rel:
            errors.append(f'MANIFEST entry #{index + 1} requires a non-empty string path')
            continue
        if rel.startswith('/') or '\\' in rel or '..' in Path(rel).parts:
            errors.append(f'MANIFEST contains unsafe path: {rel}')
            continue
        if rel in listed:
            errors.append(f'MANIFEST contains duplicate path: {rel}')
            continue
        byte_count = entry.get('bytes')
        digest = entry.get('sha256')
        if isinstance(byte_count, bool) or not isinstance(byte_count, int) or byte_count < 0:
            errors.append(f'MANIFEST bytes for {rel} must be a non-negative integer')
        if not isinstance(digest, str) or re.fullmatch(r'[0-9a-f]{64}', digest) is None:
            errors.append(f'MANIFEST sha256 for {rel} must be 64 lowercase hex digits')
        listed[rel] = entry
        ordered_paths.append(rel)
    if ordered_paths != sorted(ordered_paths):
        errors.append('MANIFEST file entries must be sorted by path')
    actual = sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and str(p.relative_to(ROOT)) != 'MANIFEST.json')
    for rel in actual:
        if rel not in listed:
            errors.append(f'MANIFEST missing file: {rel}')
            continue
        entry = listed[rel]
        data = (ROOT / rel).read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if entry.get('sha256') != digest:
            errors.append(f'MANIFEST hash mismatch for {rel}')
        if entry.get('bytes') != len(data):
            errors.append(f'MANIFEST byte count mismatch for {rel}')
    for rel in sorted(set(listed) - set(actual)):
        errors.append(f'MANIFEST lists missing file: {rel}')
    return errors


def main() -> int:
    errors: list[str] = []

    errors.extend(f'Release integrity helpers: {e}' for e in release_integrity_self_test())
    errors.extend(f'Release integrity: {e}' for e in check_release_integrity(ROOT))
    errors.extend(f'JCS canonicalization: {e}' for e in jcs_self_test())
    errors.extend(f'Temporal coherence helpers: {e}' for e in temporal_self_test())
    errors.extend(f'Discovery binding semantic helpers: {e}' for e in discovery_binding_semantics_self_test())
    errors.extend(f'Assessment temporal helpers: {e}' for e in assessment_temporal_self_test())
    errors.extend(f'Profile-reference binding helpers: {e}' for e in profile_reference_binding_self_test())
    errors.extend(f'Evidence-summary semantic helpers: {e}' for e in evidence_summary_semantics_self_test())
    errors.extend(f'Retained-export temporal helpers: {e}' for e in retained_export_temporal_self_test())
    errors.extend(f'Transport-envelope temporal helpers: {e}' for e in transport_envelope_temporal_self_test())
    errors.extend(f'Transport integrity helpers: {e}' for e in transport_integrity_self_test())
    errors.extend(f'Transport capability semantic helpers: {e}' for e in transport_capability_semantics_self_test())
    errors.extend(f'Policy-lifecycle temporal helpers: {e}' for e in policy_lifecycle_temporal_self_test())
    errors.extend(f'Policy authority digest semantic helpers: {e}' for e in policy_authority_digest_semantics_self_test())
    errors.extend(f'Replay digest semantic helpers: {e}' for e in replay_digest_semantics_self_test())
    errors.extend(f'Aggregate correction digest semantic helpers: {e}' for e in aggregate_correction_digest_semantics_self_test())
    errors.extend(f'Transparency policy digest semantic helpers: {e}' for e in transparency_policy_digest_semantics_self_test())
    errors.extend(f'Aggregate temporal helpers: {e}' for e in aggregate_temporal_self_test())
    errors.extend(f'Aggregate lifecycle decision semantic helpers: {e}' for e in aggregate_lifecycle_decision_semantics_self_test())
    errors.extend(f'Aggregate lineage semantic helpers: {e}' for e in aggregate_lineage_semantics_self_test())
    errors.extend(f'Aggregate privacy semantic helpers: {e}' for e in aggregate_privacy_semantics_self_test())
    errors.extend(f'External receipt semantic helpers: {e}' for e in external_receipt_semantics_self_test())
    errors.extend(f'Profile compatibility temporal helpers: {e}' for e in profile_compatibility_temporal_self_test())
    errors.extend(f'Profile-drift semantic helpers: {e}' for e in profile_drift_semantics_self_test())
    errors.extend(f'Scope composition semantic helpers: {e}' for e in scope_composition_semantics_self_test())
    errors.extend(f'Policy equivalence temporal helpers: {e}' for e in policy_equivalence_temporal_self_test())
    errors.extend(f'Authorized-verifier temporal helpers: {e}' for e in authorized_verifier_temporal_self_test())
    errors.extend(f'Authorized-verifier result semantic helpers: {e}' for e in authorized_verifier_result_semantics_self_test())
    errors.extend(f'Replay-transparency temporal helpers: {e}' for e in replay_transparency_temporal_self_test())
    errors.extend(f'Fixture derivation helpers: {e}' for e in fixture_derivation_self_test())
    errors.extend(f'Semantic vector helpers: {e}' for e in semantic_vectors_self_test())
    errors.extend(f'Mutation survivor audit helpers: {e}' for e in mutation_survivor_audit_self_test())
    errors.extend(f'Chrony P1 policy helpers: {e}' for e in chrony_policy_self_test(ROOT))
    errors.extend(f'Chrony adapter/evaluator helpers: {e}' for e in chrony_adapter_self_test(ROOT))
    errors.extend(f'Independent chrony observation evaluator helpers: {e}' for e in chrony_observation_eval_self_test(ROOT))
    errors.extend(f'NTPQ adapter/evaluator helpers: {e}' for e in ntpq_adapter_self_test(ROOT))
    errors.extend(f'Adapter equivalence helpers: {e}' for e in adapter_equivalence_self_test(ROOT))
    errors.extend(f'Multi-source adjudication helpers: {e}' for e in multisource_adjudicator_self_test(ROOT))
    errors.extend(f'Profile-decision acceptance helpers: {e}' for e in profile_decision_acceptance_self_test(ROOT))
    errors.extend(f'RFC 9249 chrony crosswalk helpers: {e}' for e in rfc9249_crosswalk_self_test(ROOT))
    errors.extend(f'Fixture derivations: {e}' for e in validate_derivations())

    for rel in CORE_JSON:
        try:
            load_json(rel)
        except Exception as exc:  # noqa: BLE001
            errors.append(f'JSON error in {rel}: {exc}')

    errors.extend(check_schema_documents())

    catalog = load_json('profiles/profile-catalog.json')
    catalog_index = build_catalog_index(catalog)
    adapter_catalog = load_json('transport/adapter-catalog.json')
    adapter_index = build_adapter_index(adapter_catalog)
    evidence_catalog = load_json('evaluator/evidence-class-catalog.json')

    errors.extend(f'profile catalog: {e}' for e in schema_validate('profile-catalog', catalog))
    errors.extend(f'profile catalog: {e}' for e in check_profile_catalog(catalog))
    errors.extend(check_profile_markdown_digests(catalog))
    errors.extend(f'transport adapter catalog: {e}' for e in schema_validate('transport-adapter-catalog', adapter_catalog))
    errors.extend(f'transport adapter catalog: {e}' for e in check_transport_adapter_catalog(adapter_catalog))
    errors.extend(f'evidence class catalog: {e}' for e in schema_validate('evidence-class-catalog', evidence_catalog))
    errors.extend(f'evidence class catalog: {e}' for e in check_evidence_class_catalog(evidence_catalog))
    errors.extend(f'Mutation survivor audit: {e}' for e in run_mutation_survivor_probes(
        load_json=load_json,
        schema_validate=schema_validate,
        semantic_validate=semantic_validate,
        catalog_index=catalog_index,
        adapter_index=adapter_index,
    ))

    for path in sorted((ROOT / 'profiles/applicability').glob('*.json')):
        rel = str(path.relative_to(ROOT))
        obj = load_json(rel)
        errors.extend(f'{rel}: {e}' for e in schema_validate('profile-applicability-map', obj))
        errors.extend(f'{rel}: {e}' for e in check_profile_catalog({'profiles': [obj]}))

    errors.extend(check_acceptance_tests())
    try:
        lifecycle_table = load_yaml('tests/aggregate-lifecycle-decision-table.yaml')
        if not isinstance(lifecycle_table, dict):
            errors.append('tests/aggregate-lifecycle-decision-table.yaml must be an object')
        else:
            errors.extend(f'aggregate lifecycle decision table: {e}' for e in schema_validate('aggregate-lifecycle-decision-table', lifecycle_table))
            errors.extend(f'aggregate lifecycle decision table: {e}' for e in check_lifecycle_decision_table(lifecycle_table))
    except Exception as exc:  # noqa: BLE001
        errors.append(f'YAML error in tests/aggregate-lifecycle-decision-table.yaml: {exc}')

    try:
        drift_matrix = load_yaml('tests/profile-compatibility-drift-matrix.yaml')
        if not isinstance(drift_matrix, dict):
            errors.append('tests/profile-compatibility-drift-matrix.yaml must be an object')
        else:
            errors.extend(f'profile compatibility drift matrix: {e}' for e in schema_validate('profile-compatibility-drift-matrix', drift_matrix))
            errors.extend(f'profile compatibility drift matrix: {e}' for e in check_profile_compatibility_drift_matrix(drift_matrix))
    except Exception as exc:  # noqa: BLE001
        errors.append(f'YAML error in tests/profile-compatibility-drift-matrix.yaml: {exc}')

    try:
        composition_matrix = load_yaml('tests/mixed-layer-scope-composition.yaml')
        if not isinstance(composition_matrix, dict):
            errors.append('tests/mixed-layer-scope-composition.yaml must be an object')
        else:
            errors.extend(f'scope composition decision matrix: {e}' for e in schema_validate('scope-composition-decision-matrix', composition_matrix))
            errors.extend(f'scope composition decision matrix: {e}' for e in check_scope_composition_decision_matrix(composition_matrix))
    except Exception as exc:  # noqa: BLE001
        errors.append(f'YAML error in tests/mixed-layer-scope-composition.yaml: {exc}')

    try:
        vectors = load_yaml('tests/semantic-test-vectors.yaml')
    except Exception as exc:  # noqa: BLE001
        errors.append(f'YAML error in tests/semantic-test-vectors.yaml: {exc}')
        vectors = []

    if not isinstance(vectors, list):
        errors.append('tests/semantic-test-vectors.yaml must be a list')
        vectors = []

    errors.extend(check_semantic_vector_ids(vectors))
    errors.extend(check_example_vector_coverage(vectors, ROOT))
    errors.extend(run_semantic_vectors(
        vectors,
        load_json=load_json,
        schema_validate=schema_validate,
        semantic_validate=semantic_validate,
        catalog_index=catalog_index,
        adapter_index=adapter_index,
    ))

    errors.extend(check_manifest())

    if errors:
        for err in errors:
            print(f'ERROR: {err}')
        return 1

    print(f'TimeSync {current_revision(ROOT)} validation passed.')
    print(f'Validated {len(vectors)} semantic vectors, {len(catalog.get("profiles", []))} profile maps, {len(adapter_catalog.get("adapters", []))} transport adapters, and {len(evidence_catalog.get("classes", []))} evidence classes.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

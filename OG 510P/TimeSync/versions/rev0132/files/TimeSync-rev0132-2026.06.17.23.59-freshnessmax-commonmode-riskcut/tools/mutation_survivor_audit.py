#!/usr/bin/env python3
"""Focused mutation-survivor probes for TimeSync validation.

The probes start from passing fixtures, mutate one schema-shaped value into a
semantically wrong value, and require the archive validator to reject the mutated
object.  This is intentionally smaller than exhaustive fuzzing: it locks down the
highest-risk survivors discovered during review without making normal archive
validation expensive or registry-heavy.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

LoadJson = Callable[[str], Any]
SchemaValidate = Callable[[str, Any], list[str]]
SemanticValidate = Callable[[str, Any, Any, Any], list[str]]


@dataclass(frozen=True)
class MutationProbe:
    id: str
    base: str
    schema: str
    path: str
    value: Any
    expected_error_contains: str
    rationale: str


MUTATION_PROBES: tuple[MutationProbe, ...] = (
    MutationProbe(
        id='MP-0115-001',
        base='examples/evaluator/replay-transparency-receipt-p3-policy-authority-sequenced.json',
        schema='replay-transparency-audit',
        path='/replay_event/replay_event_digest/binds',
        value='aggregate_publication_revision_chain',
        expected_error_contains='replay_event_digest must bind challenge_result_replay_event',
        rationale='Replay receipts must not bind replay_event_digest to another replay-adjacent artifact class.',
    ),
    MutationProbe(
        id='MP-0115-002',
        base='examples/evaluator/aggregate-verifier-audit-summary-p3-authority-lifecycle-active.json',
        schema='replay-transparency-audit',
        path='/aggregate_summary/integrity_binding/digest/binds',
        value='aggregate_publication_revision_chain',
        expected_error_contains='integrity_binding.digest must bind aggregate_verifier_audit_summary',
        rationale='Aggregate integrity bindings must name the aggregate summary artifact, not lineage metadata.',
    ),
    MutationProbe(
        id='MP-0115-003',
        base='examples/discovery-request-with-aggregate-correction-authority-reference.json',
        schema='discovery-request',
        path='/results/aggregate_correction_authority_reference/value/authority_binding/authority_digest/binds',
        value='retained_operator_record',
        expected_error_contains='authority_digest must bind aggregate_correction_authority_rules or aggregate_correction_authority_identity',
        rationale='Aggregate correction authority identity/rules must not be confused with retained operator material.',
    ),
    MutationProbe(
        id='MP-0115-004',
        base='examples/evaluator/replay-transparency-receipt-p3-policy-authority-sequenced.json',
        schema='replay-transparency-audit',
        path='/transparency_trust_policy_reference/lifecycle_status/status_record_digest/binds',
        value='profile_compatibility_statement',
        expected_error_contains='status_record_digest must bind transparency_trust_policy_lifecycle_status',
        rationale='Trust-policy lifecycle status must bind status material, not compatibility material.',
    ),
    MutationProbe(
        id='MP-0116-001',
        base='profiles/compatibility/p3-replay-transparency-policy-equivalence.json',
        schema='profile-compatibility-statement',
        path='/transparency_policy_equivalence/policy_lifecycle_equivalence/revocation_check/digest/binds',
        value='transparency_trust_policy_rules',
        expected_error_contains='revocation_check.digest must bind transparency_trust_policy_revocation_status',
        rationale='Current policy lifecycle equivalence must bind revocation evidence, not the policy rules themselves.',
    ),
    MutationProbe(
        id='MP-0116-002',
        base='examples/evaluator/replay-transparency-receipt-p3-policy-rollover-compatible.json',
        schema='replay-transparency-audit',
        path='/transparency_trust_policy_reference/lifecycle_authority_reference/renewal_hint/hint_digest/binds',
        value='transparency_trust_policy_lifecycle_authority',
        expected_error_contains='renewal hint_digest must bind transparency_trust_policy_lifecycle_status',
        rationale='Renewal hints summarize lifecycle status; they must not be rebound to authority identity.',
    ),
    MutationProbe(
        id='MP-0116-003',
        base='examples/evaluator/aggregate-verifier-audit-summary-p3-lifecycle-rollup-rev0086.json',
        schema='replay-transparency-audit',
        path='/aggregate_summary/aggregate_correction_authority_lifecycle_rollup/digest_bindings/1/binds',
        value='aggregate_lifecycle_decision_table',
        expected_error_contains='requires a digest binding to aggregate_correction_authority_lifecycle_summary',
        rationale='A lifecycle rollup must bind both the decision table and the lifecycle-summary population it summarizes.',
    ),
    MutationProbe(
        id='MP-0116-004',
        base='examples/discovery-request-with-version-negotiation.json',
        schema='discovery-request',
        path='/results/semantic_version_negotiation/digest_binding/digest/binds',
        value='normative_profile_rules',
        expected_error_contains='semantic_version_negotiation: current digest binding digest must bind discovery_returned_object',
        rationale='Discovery result wrappers must not accept arbitrary profile-rule digests as returned-object bindings.',
    ),
    MutationProbe(
        id='MP-0116-005',
        base='examples/discovery-request-with-downgrade-proof.json',
        schema='discovery-request',
        path='/results/profile_compatibility_drift_decision/value/subject_profile/digest/binds',
        value='transparency_trust_policy_rules',
        expected_error_contains='profile_compatibility_drift_decision: schema error',
        rationale='Nested drift-decision values returned by discovery must receive the same schema checks as detached drift decisions.',
    ),
    MutationProbe(
        id='MP-0116-006',
        base='examples/scope-composition-guard-rev0090.json',
        schema='scope-composition-guard',
        path='/temporal_coherence/input_observations/7/source_time_digest/binds',
        value='aggregate_lifecycle_decision_table',
        expected_error_contains='decision matrix temporal observation must match matrix_digest',
        rationale='A scope-composition decision-matrix freshness observation must qualify the matrix digest, not a different allowed artifact class.',
    ),
    MutationProbe(
        id='MP-0117-001',
        base='examples/local-assessed-state-p3-satisfied.json',
        schema='local-assessed-state',
        path='/profile_assessments/0/profile_lifecycle_state',
        value='revoked',
        expected_error_contains='profile_lifecycle_state revoked cannot support actionable or conditional current actionability',
        rationale='An actionable satisfied profile assessment must not remain current-actionable after its profile lifecycle is revoked.',
    ),
    MutationProbe(
        id='MP-0117-002',
        base='examples/evaluator/policy-lifecycle-authority-reference-p3-current.json',
        schema='policy-lifecycle-authority-reference',
        path='/rotation_delegation_status/compromise_response/replay_visibility_effect',
        value='contested_visibility',
        expected_error_contains='none_known lifecycle-authority compromise requires replay_visibility_effect no_current_effect',
        rationale='A no-compromise authority posture must not smuggle a contested or suppressing replay-visibility effect.',
    ),
    MutationProbe(
        id='MP-0117-003',
        base='examples/discovery-request-with-aggregate-lifecycle-decision-table.json',
        schema='discovery-request',
        path='/results/aggregate_lifecycle_decision_table/value/rows/0/lifecycle_state',
        value='revoked',
        expected_error_contains='aggregate lifecycle decision table row active-current lifecycle_state must be active',
        rationale='Canonical decision-table row ids must not silently drift to a different lifecycle posture.',
    ),
    MutationProbe(
        id='MP-0117-004',
        base='examples/digest-binding-policy-rev0086.json',
        schema='digest-binding-policy',
        path='/digest_surface_rules/4/current_use_allowed',
        value=True,
        expected_error_contains='retained_operator_record cannot be current-use allowed',
        rationale='A retention-only digest surface must not be lifted into current-use by flipping a boolean.',
    ),
    MutationProbe(
        id='MP-0118-001',
        base='examples/evaluator/evidence-input-summary-p3-satisfied.json',
        schema='evaluator-evidence-summary',
        path='/input_items/12/value_state',
        value='ignored',
        expected_error_contains='minimum_summary_item profile.profile_default_items is present but not usable',
        rationale='Satisfied evidence summaries must not satisfy profile minimum-summary coverage with ignored evidence by name alone.',
    ),
    MutationProbe(
        id='MP-0118-002',
        base='examples/evaluator/evidence-input-summary-p3-satisfied.json',
        schema='evaluator-evidence-summary',
        path='/input_items/6/freshness_relation',
        value='stale_at_assessment',
        expected_error_contains='minimum_summary_item policy_acceptance requires freshness_relation current_at_assessment',
        rationale='Satisfied current policy-acceptance coverage must remain fresh at assessment time, not stale by retained item name.',
    ),
    MutationProbe(
        id='MP-0118-003',
        base='examples/evaluator/replay-transparency-receipt-p3-witnessed.json',
        schema='replay-transparency-audit',
        path='/witness_cohort_evaluation/status',
        value='not_checked',
        expected_error_contains='witness cohort positive basis cannot have not_checked, unknown, or not_used status',
        rationale='A positive witness/monitor basis with threshold evidence must not be downgraded to an unchecked status.',
    ),
    MutationProbe(
        id='MP-0118-004',
        base='examples/evaluator/replay-transparency-receipt-p3-witnessed.json',
        schema='replay-transparency-audit',
        path='/witness_cohort_evaluation/split_view_signal/status',
        value='not_checked',
        expected_error_contains='witness or monitor consistent posture requires split_view_signal none_observed',
        rationale='A consistent witness/monitor posture must not leave the split-view signal unchecked.',
    ),
    MutationProbe(
        id='MP-0119-001',
        base='examples/evaluator/evidence-input-summary-p3-satisfied.json',
        schema='evaluator-evidence-summary',
        path='/input_items/13/freshness_relation',
        value='stale_at_assessment',
        expected_error_contains='minimum_summary_item assessment.validity_horizon requires freshness_relation current_at_assessment',
        rationale='Satisfied evidence summaries must not keep current validity-horizon coverage after the witness becomes stale.',
    ),
    MutationProbe(
        id='MP-0119-002',
        base='examples/local-assessed-state-p3-satisfied.json',
        schema='local-assessed-state',
        path='/profile_assessments/0/profile_conformance',
        value='unsatisfied',
        expected_error_contains='unsatisfied profile_conformance cannot support actionable or conditional current actionability',
        rationale='A downgrade to unsatisfied conformance must not preserve actionable policy and validity-horizon state.',
    ),
    MutationProbe(
        id='MP-0119-003',
        base='examples/p1-coarse-logging-fallback.json',
        schema='local-assessed-state',
        path='/profile_assessments/0/profile_conformance',
        value='satisfied',
        expected_error_contains='non-fallback profile_conformance cannot carry evaluation_summary.fallback_mapping',
        rationale='A fallback assessment must not be upgraded to satisfied while retaining fallback explanation metadata.',
    ),
    MutationProbe(
        id='MP-0119-004',
        base='examples/p1-coarse-logging-fallback.json',
        schema='local-assessed-state',
        path='/profile_assessments/0/policy_acceptance/status',
        value='accepted',
        expected_error_contains='policy_acceptance accepted cannot have conditional actionability',
        rationale='Conditional policy actionability must remain represented as accepted_with_conditions, not accepted.',
    ),
    MutationProbe(
        id='MP-0120-001',
        base='examples/evaluator/authorized-verifier-challenge-result-p3-redacted.json',
        schema='authorized-verifier-challenge',
        path='/record_kind',
        value='authorized_verifier_challenge',
        expected_error_contains='authorized_verifier_challenge record cannot carry challenge_result',
        rationale='A result-bearing authorized-verifier record must not be relabelled as a bare challenge.',
    ),
    MutationProbe(
        id='MP-0120-002',
        base='examples/evaluator/authorized-verifier-challenge-result-p3-redacted.json',
        schema='authorized-verifier-challenge',
        path='/challenge_result/result',
        value='mismatch',
        expected_error_contains='mismatch challenge result requires at least one mismatching verified disclosure',
        rationale='Changing the aggregate result must stay consistent with verified disclosure row outcomes.',
    ),
    MutationProbe(
        id='MP-0120-003',
        base='examples/evaluator/authorized-verifier-challenge-result-p3-redacted.json',
        schema='authorized-verifier-challenge',
        path='/challenge_result/verified_disclosures/0/verification_result',
        value='not_verified',
        expected_error_contains='matched challenge result requires every verified disclosure to be matched',
        rationale='A matched challenge result must not survive when its disclosure row is weakened to not_verified.',
    ),
    MutationProbe(
        id='MP-0120-004',
        base='examples/evaluator/authorized-verifier-challenge-result-p3-redacted.json',
        schema='authorized-verifier-challenge',
        path='/challenge_result/receipt/digest/binds',
        value='selective_disclosure_proof',
        expected_error_contains='external_preimage_review_receipt digest must bind authorized_verifier_challenge_receipt',
        rationale='External preimage review receipts must bind the challenge receipt, not a neighboring proof artifact.',
    ),
    MutationProbe(
        id='MP-0120-005',
        base='examples/evaluator/authorized-verifier-challenge-result-p3-redacted.json',
        schema='authorized-verifier-challenge',
        path='/verifier_authorization/authorization_scope',
        value='external_system_verification',
        expected_error_contains='salt/preimage requested material requires authorization_scope salt_preimage_verification',
        rationale='Salt/preimage disclosure cannot be reinterpreted as a different verifier authorization scope.',
    ),
    MutationProbe(
        id='MP-0120-006',
        base='examples/evaluator/authorized-verifier-challenge-result-p3-redacted.json',
        schema='authorized-verifier-challenge',
        path='/portability_boundary/portable_result_scope',
        value='not_portable',
        expected_error_contains='not_portable challenge result cannot advertise replay uses',
        rationale='A not-portable result must not keep a commitment-verification replay advertisement.',
    ),
    MutationProbe(
        id='MP-0120-007',
        base='examples/evaluator/authorized-verifier-challenge-result-p3-redacted.json',
        schema='authorized-verifier-challenge',
        path='/challenge_result/verified_disclosures/0/receipt_digest_value',
        value='0000000000000000000000000000000000000000000000000000000000000000',
        expected_error_contains='verified disclosure receipt_digest_value must match challenge_result.receipt.digest.value',
        rationale='Verified disclosure rows must continue to point at the receipt digest they claim to summarize.',
    ),
)


def _decode_pointer(pointer: str) -> list[str]:
    if pointer == '':
        return []
    if not pointer.startswith('/'):
        raise ValueError(f'JSON pointer must start with /: {pointer}')
    return [part.replace('~1', '/').replace('~0', '~') for part in pointer.split('/')[1:]]


def _set_pointer(obj: Any, pointer: str, value: Any) -> None:
    parts = _decode_pointer(pointer)
    if not parts:
        raise ValueError('mutation probe cannot replace document root')
    cur = obj
    for part in parts[:-1]:
        if isinstance(cur, list):
            cur = cur[int(part)]
        elif isinstance(cur, dict):
            cur = cur[part]
        else:
            raise ValueError(f'cannot descend through {type(cur).__name__} at {pointer}')
    last = parts[-1]
    if isinstance(cur, list):
        cur[int(last)] = copy.deepcopy(value)
    elif isinstance(cur, dict):
        cur[last] = copy.deepcopy(value)
    else:
        raise ValueError(f'cannot set member on {type(cur).__name__} at {pointer}')


def run_probes(
    *,
    load_json: LoadJson,
    schema_validate: SchemaValidate,
    semantic_validate: SemanticValidate,
    catalog_index: Any,
    adapter_index: Any,
    probes: tuple[MutationProbe, ...] = MUTATION_PROBES,
) -> list[str]:
    """Run focused mutation probes and return validation failures."""
    errors: list[str] = []
    seen_ids: set[str] = set()
    for probe in probes:
        if probe.id in seen_ids:
            errors.append(f'{probe.id}: duplicate mutation probe id')
            continue
        seen_ids.add(probe.id)
        try:
            obj = copy.deepcopy(load_json(probe.base))
            _set_pointer(obj, probe.path, probe.value)
        except Exception as exc:  # noqa: BLE001
            errors.append(f'{probe.id}: cannot build mutated fixture from {probe.base}: {exc}')
            continue
        schema_errors = schema_validate(probe.schema, obj)
        semantic_errors = semantic_validate(probe.schema, obj, catalog_index, adapter_index)
        all_errors = schema_errors + semantic_errors
        if not all_errors:
            errors.append(f'{probe.id}: mutation survived validation at {probe.base}{probe.path} -> {probe.value!r}')
            continue
        needle = probe.expected_error_contains.lower()
        if needle and not any(needle in err.lower() for err in all_errors):
            errors.append(f'{probe.id}: mutation rejected for the wrong reason; expected {probe.expected_error_contains!r}, got {all_errors}')
    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    sample = {'a': [{'b': {'c': 1}}], 'slash/key': True, 'tilde~key': 'x'}
    _set_pointer(sample, '/a/0/b/c', 2)
    _set_pointer(sample, '/slash~1key', False)
    _set_pointer(sample, '/tilde~0key', 'y')
    if sample != {'a': [{'b': {'c': 2}}], 'slash/key': False, 'tilde~key': 'y'}:
        errors.append(f'mutation_survivor_audit JSON pointer self-test failed: {sample!r}')
    if len({probe.id for probe in MUTATION_PROBES}) != len(MUTATION_PROBES):
        errors.append('mutation_survivor_audit contains duplicate probe ids')
    return errors


def main() -> int:
    import sys

    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'tools'))
    import validate_archive as validator  # type: ignore  # noqa: PLC0415

    catalog_index = validator.build_catalog_index(validator.load_json('profiles/profile-catalog.json'))
    adapter_index = validator.build_adapter_index(validator.load_json('transport/adapter-catalog.json'))
    errors = self_test() + run_probes(
        load_json=validator.load_json,
        schema_validate=validator.schema_validate,
        semantic_validate=validator.semantic_validate,
        catalog_index=catalog_index,
        adapter_index=adapter_index,
    )
    if errors:
        for error in errors:
            print(f'ERROR: {error}')
        return 1
    print(f'TimeSync mutation-survivor audit passed ({len(MUTATION_PROBES)} probes).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

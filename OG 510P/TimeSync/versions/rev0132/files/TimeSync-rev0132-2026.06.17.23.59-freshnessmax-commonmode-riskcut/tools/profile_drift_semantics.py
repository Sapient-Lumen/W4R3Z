#!/usr/bin/env python3
"""Profile compatibility drift matrix/decision semantics for TimeSync."""
from __future__ import annotations

from typing import Any

from discovery_binding_semantics import check_downgrade_proof_metadata, digest_binds


PROFILE_DRIFT_SUPPRESSED_CLASSES = {'weaker', 'incomparable', 'unknown', 'digest_rollover_without_equivalence'}
PROFILE_DRIFT_CURRENT_DECISIONS = {'current_use_allowed', 'current_use_guarded'}
REQUIRED_PROFILE_DRIFT_ROWS = {
    'exact-equivalent-current',
    'stricter-or-equal-current-guarded',
    'weaker-suppressed',
    'unknown-suppressed',
    'incomparable-suppressed',
    'digest-rollover-compatible-current-guarded',
    'digest-rollover-without-equivalence-suppressed',
    'downgrade-with-proof-current-guarded',
    'downgrade-without-proof-suppressed',
    'unknown-newer-metadata-only',
    'legacy-historical-only',
}


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _require_current_digest_equivalence(
    *,
    drift_class: Any,
    digest_relation: Any,
    compatibility_statement_digest: Any,
    prefix: str,
) -> list[str]:
    """Reject current-use drift decisions without a digest-bound equivalence surface."""
    errors: list[str] = []
    if digest_relation in {'different_digest_without_equivalence', 'unknown_or_redacted'}:
        errors.append(f'{prefix} current profile compatibility drift requires digest equivalence; got {digest_relation}')
    if drift_class in {'stricter_or_equal', 'digest_rollover_compatible'} and digest_relation != 'different_digest_with_equivalence':
        errors.append(f'{prefix} current {drift_class} profile drift requires different_digest_with_equivalence')
    if digest_relation == 'different_digest_with_equivalence' and not digest_binds(compatibility_statement_digest, 'profile_compatibility_statement'):
        errors.append(f'{prefix} current profile compatibility drift with different digest requires compatibility_statement_digest binding profile_compatibility_statement')
    return errors


def check_profile_compatibility_drift_matrix(matrix: dict[str, Any]) -> list[str]:
    """Executable profile-drift matrix completeness and non-upgrade checks."""
    errors: list[str] = []
    if not digest_binds(matrix.get('matrix_digest'), 'profile_compatibility_drift_matrix'):
        errors.append('profile compatibility drift matrix requires matrix_digest binding profile_compatibility_drift_matrix')
    rows = matrix.get('rows', []) if isinstance(matrix.get('rows'), list) else []
    ids = {r.get('row_id') for r in rows if isinstance(r, dict)}
    missing = REQUIRED_PROFILE_DRIFT_ROWS - ids
    if missing:
        errors.append(f'profile compatibility drift matrix missing required rows {sorted(missing)}')
    for row in rows:
        if not isinstance(row, dict):
            continue
        rid = row.get('row_id', '<unknown-row>')
        drift = row.get('drift_class')
        decision = row.get('compatibility_decision')
        digest_relation = row.get('digest_relation')
        current = row.get('current_use_allowed') is True
        failure = row.get('failure_mode')
        prefix = f'profile compatibility drift matrix row {rid}'
        if drift in PROFILE_DRIFT_SUPPRESSED_CLASSES and current:
            errors.append(f'{prefix} cannot allow current use for {drift} drift')
        if decision in PROFILE_DRIFT_CURRENT_DECISIONS and row.get('evidence_policy_relation') in {'weaker', 'unknown'}:
            errors.append(f'{prefix} cannot allow current use with weaker or unknown evidence policy relation')
        if decision in PROFILE_DRIFT_CURRENT_DECISIONS and failure != 'none':
            errors.append(f'{prefix} current decision must have failure_mode none')
        if decision not in PROFILE_DRIFT_CURRENT_DECISIONS and current:
            errors.append(f'{prefix} non-current decision cannot set current_use_allowed true')
        if drift == 'digest_rollover_without_equivalence' and decision != 'suppressed_by_digest_rollover':
            errors.append(f'{prefix} digest rollover without equivalence must suppress by digest rollover')
        if drift == 'equivalent' and digest_relation != 'identical_digest':
            errors.append(f'{prefix} equivalent drift requires identical_digest')
        if decision in PROFILE_DRIFT_CURRENT_DECISIONS:
            if digest_relation in {'different_digest_without_equivalence', 'unknown_or_redacted'}:
                errors.append(f'{prefix} current decision requires digest equivalence; got {digest_relation}')
            if drift in {'stricter_or_equal', 'digest_rollover_compatible'} and digest_relation != 'different_digest_with_equivalence':
                errors.append(f'{prefix} current {drift} row requires different_digest_with_equivalence')
            if digest_relation == 'different_digest_with_equivalence' and row.get('proof_required') is not True:
                errors.append(f'{prefix} current digest-distinct row requires proof_required true')
    boundary = matrix.get('boundary', {}) if isinstance(matrix.get('boundary'), dict) else {}
    for key in ('matrix_updates_profile_assessment', 'matrix_updates_actionability', 'matrix_reopens_assessment', 'matrix_interpreted_as_timesync_provenance', 'profile_rule_delta_exported'):
        if boundary.get(key) is not False:
            errors.append(f'profile compatibility drift matrix boundary.{key} must be false')
    if boundary.get('matrix_updates_compatibility_interpretation_only') is not True:
        errors.append('profile compatibility drift matrix may update compatibility interpretation only')
    return errors


def check_profile_compatibility_drift_decision(decision: dict[str, Any]) -> list[str]:
    """Fail-closed checks for profile compatibility drift and digest rollover decisions."""
    errors: list[str] = []
    if not digest_binds(decision.get('matrix_digest'), 'profile_compatibility_drift_matrix'):
        errors.append('profile compatibility drift decision requires matrix_digest binding profile_compatibility_drift_matrix')
    drift = decision.get('drift_class')
    compat_decision = decision.get('compatibility_decision')
    current = decision.get('current_use_allowed') is True
    epr = decision.get('evidence_policy_relation')
    digest_relation = decision.get('digest_relation')
    if drift in PROFILE_DRIFT_SUPPRESSED_CLASSES and current:
        if drift == 'weaker':
            errors.append('weaker profile compatibility drift cannot support current compatibility use')
        elif drift == 'unknown':
            errors.append('unknown profile compatibility drift cannot support current compatibility use')
        elif drift == 'incomparable':
            errors.append('incomparable profile compatibility drift cannot support current compatibility use')
        else:
            errors.append('digest rollover without equivalence cannot support current compatibility use')
    if epr in {'weaker', 'unknown'} and compat_decision in PROFILE_DRIFT_CURRENT_DECISIONS:
        errors.append('profile compatibility current use cannot rely on weaker or unknown evidence policy relation')
    if compat_decision in PROFILE_DRIFT_CURRENT_DECISIONS and not current:
        errors.append('current profile compatibility decision must set current_use_allowed true')
    if compat_decision not in PROFILE_DRIFT_CURRENT_DECISIONS and current:
        errors.append('suppressed or historical profile compatibility decision cannot set current_use_allowed true')
    if drift == 'equivalent' and digest_relation != 'identical_digest':
        errors.append('equivalent profile drift requires identical normative profile digest values')
    if current:
        errors.extend(_require_current_digest_equivalence(
            drift_class=drift,
            digest_relation=digest_relation,
            compatibility_statement_digest=decision.get('compatibility_statement_digest'),
            prefix='',
        ))
    if drift == 'digest_rollover_compatible':
        rollover = decision.get('digest_rollover', {}) if isinstance(decision.get('digest_rollover'), dict) else {}
        if rollover.get('rollover_equivalence') not in {'digest_bound_equivalent', 'stricter_or_equal_successor'}:
            errors.append('compatible digest rollover requires digest-bound equivalent or stricter-or-equal successor')
        if current:
            if not digest_binds(rollover.get('prior_profile_digest'), 'normative_profile_rules'):
                errors.append('current digest rollover compatible decision requires prior_profile_digest binding normative_profile_rules')
            if not digest_binds(rollover.get('current_profile_digest'), 'normative_profile_rules'):
                errors.append('current digest rollover compatible decision requires current_profile_digest binding normative_profile_rules')
            if not digest_binds(rollover.get('successor_compatibility_statement_digest'), 'profile_compatibility_statement'):
                errors.append('current digest rollover compatible decision requires successor_compatibility_statement_digest binding profile_compatibility_statement')
    if drift == 'digest_rollover_without_equivalence' and compat_decision != 'suppressed_by_digest_rollover':
        errors.append('digest rollover without equivalence must use suppressed_by_digest_rollover decision')
    downgrade = decision.get('downgrade_proof') if isinstance(decision.get('downgrade_proof'), dict) else None
    if downgrade is not None:
        errors.extend(check_downgrade_proof_metadata('profile_compatibility_drift_decision', downgrade, None, current))
    boundary = decision.get('non_upgrade_boundary', {}) if isinstance(decision.get('non_upgrade_boundary'), dict) else {}
    for key in ('drift_decision_is_profile_evidence', 'drift_decision_updates_actionability', 'drift_decision_reopens_assessment', 'drift_decision_interpreted_as_timesync_provenance', 'profile_rule_delta_exported', 'profile_authority_registry_exported'):
        if boundary.get(key) is not False:
            errors.append(f'profile compatibility drift decision boundary.{key} must be false')
    if boundary.get('profile_drift_updates_compatibility_interpretation_only') is not True:
        errors.append('profile compatibility drift decision may update compatibility interpretation only')
    return [e.strip() for e in errors]


def self_test() -> list[str]:
    errors: list[str] = []
    digest = {'algorithm': 'sha256', 'value': 'a' * 64, 'binds': 'profile_compatibility_drift_matrix'}
    compat = {'algorithm': 'sha256', 'value': 'b' * 64, 'binds': 'profile_compatibility_statement'}
    boundary = {
        'drift_decision_is_profile_evidence': False,
        'drift_decision_updates_actionability': False,
        'drift_decision_reopens_assessment': False,
        'drift_decision_interpreted_as_timesync_provenance': False,
        'profile_rule_delta_exported': False,
        'profile_authority_registry_exported': False,
        'profile_drift_updates_compatibility_interpretation_only': True,
    }
    valid = {
        'matrix_digest': digest,
        'drift_class': 'stricter_or_equal',
        'digest_relation': 'different_digest_with_equivalence',
        'evidence_policy_relation': 'stricter_or_equal',
        'compatibility_decision': 'current_use_guarded',
        'current_use_allowed': True,
        'compatibility_statement_digest': compat,
        'non_upgrade_boundary': boundary,
    }
    if check_profile_compatibility_drift_decision(valid):
        errors.append('profile_drift_semantics self-test failed: valid current drift rejected')
    invalid = dict(valid)
    invalid.pop('compatibility_statement_digest')
    if not any('compatibility_statement_digest' in e for e in check_profile_compatibility_drift_decision(invalid)):
        errors.append('profile_drift_semantics self-test failed: missing compatibility digest accepted')
    rollover = dict(valid)
    rollover['drift_class'] = 'digest_rollover_compatible'
    rollover['digest_rollover'] = {'rollover_equivalence': 'digest_bound_equivalent'}
    if not any('prior_profile_digest' in e for e in check_profile_compatibility_drift_decision(rollover)):
        errors.append('profile_drift_semantics self-test failed: incomplete rollover accepted')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync profile-drift semantic self-test passed.')

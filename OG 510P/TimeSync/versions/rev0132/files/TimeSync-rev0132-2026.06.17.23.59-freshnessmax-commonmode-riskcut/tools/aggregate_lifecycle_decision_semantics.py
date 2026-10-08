#!/usr/bin/env python3
"""Aggregate lifecycle decision-table semantics for TimeSync validation.

The decision table is a compact executable policy surface.  Schema validation can
prove the rows are shaped like rows, but it cannot prove that the canonical row
ids still mean the same lifecycle posture after a copy/edit or mutation.  These
checks keep the required rows pinned to their semantic posture while leaving the
external authority lifecycle protocol out of scope.
"""
from __future__ import annotations

from typing import Any

CURRENT_INTERPRETATION_DECISIONS = {
    'current_supported',
    'current_supported_guarded',
    'historical_only',
    'suppressed_by_emergency_withdrawal',
    'suppressed_by_revocation',
    'suppressed_by_contestation',
    'suppressed_by_unknown_lifecycle',
    'suppressed_by_notification_staleness',
    'suppressed_by_portability_failure',
}

REQUIRED_LIFECYCLE_DECISION_ROWS = {
    'active-current',
    'pending-rotation-current-guarded',
    'expired-historical-only',
    'revoked-suppressed',
    'emergency-withdrawal-suppressed',
    'contested-suppressed',
    'unknown-redacted-suppressed',
}

REQUIRED_ROW_SHAPES: dict[str, dict[str, Any]] = {
    'active-current': {
        'lifecycle_state': 'active',
        'allowed_lifecycle_effects': {'aggregate_interpretation_current', 'historical_only'},
        'allowed_current_interpretation_decisions': {'current_supported', 'historical_only'},
        'required_posture': {
            'revocation_status': 'not_revoked',
            'emergency_withdrawal.state': 'not_applicable',
            'contestation.state': {'none', 'resolved_upheld'},
            'revocation_checked_at': 'required',
        },
    },
    'pending-rotation-current-guarded': {
        'lifecycle_state': 'pending_rotation',
        'allowed_lifecycle_effects': {'aggregate_interpretation_current', 'historical_only'},
        'allowed_current_interpretation_decisions': {'current_supported_guarded', 'historical_only'},
        'required_posture': {
            'revocation_status': 'not_revoked',
            'emergency_withdrawal.state': 'not_applicable',
            'contestation.state': {'none', 'resolved_upheld'},
            'revocation_checked_at': 'required',
        },
    },
    'expired-historical-only': {
        'lifecycle_state': 'expired',
        'allowed_lifecycle_effects': {'historical_only'},
        'allowed_current_interpretation_decisions': {'historical_only'},
        'required_posture': {
            'emergency_withdrawal.state': 'not_applicable',
        },
    },
    'revoked-suppressed': {
        'lifecycle_state': 'revoked',
        'allowed_lifecycle_effects': {'historical_only'},
        'allowed_current_interpretation_decisions': {'suppressed_by_revocation'},
        'required_posture': {
            'revocation_status': 'revoked',
            'emergency_withdrawal.state': 'not_applicable',
        },
    },
    'emergency-withdrawal-suppressed': {
        'lifecycle_state': 'emergency_withdrawal',
        'allowed_lifecycle_effects': {'historical_only', 'emergency_withdrawal_required'},
        'allowed_current_interpretation_decisions': {'suppressed_by_emergency_withdrawal'},
        'required_posture': {
            'emergency_withdrawal.state': {'active', 'completed', 'contested'},
            'emergency_withdrawal.scope': 'concrete_or_redacted_aggregate_scope',
            'emergency_withdrawal.suppresses_current_interpretation': True,
            'emergency_withdrawal.resynchronization_state': 'concrete',
        },
    },
    'contested-suppressed': {
        'lifecycle_state': 'contested',
        'allowed_lifecycle_effects': {'contested', 'historical_only'},
        'allowed_current_interpretation_decisions': {'suppressed_by_contestation'},
        'required_posture': {
            'contestation.state': {'pending_contestation', 'resolved_overturned', 'unknown_or_redacted'},
            'contestation_effect': {'contested', 'historical_only', 'unknown'},
        },
    },
    'unknown-redacted-suppressed': {
        'lifecycle_state': 'unknown_or_redacted',
        'allowed_lifecycle_effects': {'unknown', 'historical_only'},
        'allowed_current_interpretation_decisions': {'suppressed_by_unknown_lifecycle'},
        'required_posture': {
            'revocation_status': {'not_checked', 'unknown_or_redacted'},
            'emergency_withdrawal.state': {'not_applicable', 'unknown_or_redacted'},
        },
    },
}


def _as_set(value: Any) -> set[Any] | None:
    if not isinstance(value, list):
        return None
    return set(value)


def _expected_as_set(value: Any) -> set[Any]:
    if isinstance(value, set):
        return set(value)
    if isinstance(value, list):
        return set(value)
    return {value}


def _compare_row_collection(row_id: str, row: dict[str, Any], field: str, expected: set[str]) -> list[str]:
    actual = _as_set(row.get(field))
    if actual != expected:
        return [f'aggregate lifecycle decision table row {row_id} {field} must be {sorted(expected)}']
    return []


def _compare_posture(row_id: str, posture: dict[str, Any], key: str, expected: Any) -> list[str]:
    actual = posture.get(key)
    expected_set = _expected_as_set(expected)
    if isinstance(expected, set):
        actual_set = _as_set(actual)
        if actual_set != expected_set:
            return [f'aggregate lifecycle decision table row {row_id} required_posture.{key} must be {sorted(expected_set)}']
        return []
    if actual != expected:
        return [f'aggregate lifecycle decision table row {row_id} required_posture.{key} must be {expected!r}']
    return []


def _check_required_row_shape(row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    row_id = row.get('row_id')
    if not isinstance(row_id, str) or row_id not in REQUIRED_ROW_SHAPES:
        return errors
    expected = REQUIRED_ROW_SHAPES[row_id]
    if row.get('lifecycle_state') != expected['lifecycle_state']:
        errors.append(f'aggregate lifecycle decision table row {row_id} lifecycle_state must be {expected["lifecycle_state"]}')
    errors.extend(_compare_row_collection(row_id, row, 'allowed_lifecycle_effects', expected['allowed_lifecycle_effects']))
    errors.extend(_compare_row_collection(row_id, row, 'allowed_current_interpretation_decisions', expected['allowed_current_interpretation_decisions']))
    posture = row.get('required_posture', {}) if isinstance(row.get('required_posture'), dict) else {}
    for key, value in expected.get('required_posture', {}).items():
        errors.extend(_compare_posture(row_id, posture, key, value))
    return errors


def expected_lifecycle_decision(lifecycle: dict[str, Any]) -> str:
    state = lifecycle.get('lifecycle_state')
    effect = lifecycle.get('lifecycle_effect')
    revocation = lifecycle.get('revocation_status')
    emergency = lifecycle.get('emergency_withdrawal', {}) if isinstance(lifecycle.get('emergency_withdrawal'), dict) else {}
    contestation = lifecycle.get('contestation', {}) if isinstance(lifecycle.get('contestation'), dict) else {}
    estate = emergency.get('state')
    cstate = contestation.get('state')
    if revocation == 'revoked' or state == 'revoked':
        return 'suppressed_by_revocation'
    if estate in {'active', 'completed', 'contested'} or state == 'emergency_withdrawal':
        return 'suppressed_by_emergency_withdrawal'
    if state == 'contested' or cstate in {'pending_contestation', 'resolved_overturned', 'unknown_or_redacted'}:
        return 'suppressed_by_contestation'
    if revocation in {'not_checked', 'unknown_or_redacted'} or state == 'unknown_or_redacted':
        return 'suppressed_by_unknown_lifecycle'
    if effect == 'historical_only' or state == 'expired':
        return 'historical_only'
    if state == 'pending_rotation' and effect == 'aggregate_interpretation_current':
        return 'current_supported_guarded'
    if state == 'active' and effect == 'aggregate_interpretation_current':
        return 'current_supported'
    return 'suppressed_by_unknown_lifecycle'


def check_lifecycle_decision_table(table: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if table.get('canonicalization') != 'json_canonicalization_scheme_rfc8785':
        errors.append('aggregate lifecycle decision table requires json_canonicalization_scheme_rfc8785 for current digest binding')
    decisions = set(table.get('current_interpretation_decisions', [])) if isinstance(table.get('current_interpretation_decisions'), list) else set()
    if decisions != CURRENT_INTERPRETATION_DECISIONS:
        errors.append('aggregate lifecycle decision table must enumerate the complete current_interpretation_decision vocabulary')
    rows = table.get('rows', []) if isinstance(table.get('rows'), list) else []
    row_ids = {row.get('row_id') for row in rows if isinstance(row, dict)}
    missing = REQUIRED_LIFECYCLE_DECISION_ROWS - row_ids
    if missing:
        errors.append(f'aggregate lifecycle decision table missing required rows {sorted(missing)}')
    for row in rows:
        if isinstance(row, dict):
            errors.extend(_check_required_row_shape(row))
    boundary = table.get('boundary', {}) if isinstance(table.get('boundary'), dict) else {}
    for key in ('decision_table_updates_profile_assessment', 'decision_table_exports_authority_registry', 'decision_table_interpreted_as_timesync_provenance'):
        if boundary.get(key) is not False:
            errors.append(f'aggregate lifecycle decision table boundary.{key} must be false')
    if boundary.get('decision_table_updates_replay_visibility_only') is not True:
        errors.append('aggregate lifecycle decision table may update only aggregate replay-visibility interpretation')
    return errors


def _row(row_id: str) -> dict[str, Any]:
    shape = REQUIRED_ROW_SHAPES[row_id]
    row = {
        'row_id': row_id,
        'lifecycle_state': shape['lifecycle_state'],
        'allowed_lifecycle_effects': sorted(shape['allowed_lifecycle_effects']),
        'allowed_current_interpretation_decisions': sorted(shape['allowed_current_interpretation_decisions']),
        'required_posture': {},
    }
    for key, value in shape.get('required_posture', {}).items():
        row['required_posture'][key] = sorted(value) if isinstance(value, set) else value
    return row


def _self_test_table() -> dict[str, Any]:
    return {
        'canonicalization': 'json_canonicalization_scheme_rfc8785',
        'current_interpretation_decisions': sorted(CURRENT_INTERPRETATION_DECISIONS),
        'rows': [_row(row_id) for row_id in sorted(REQUIRED_LIFECYCLE_DECISION_ROWS)],
        'boundary': {
            'decision_table_updates_profile_assessment': False,
            'decision_table_updates_replay_visibility_only': True,
            'decision_table_exports_authority_registry': False,
            'decision_table_interpreted_as_timesync_provenance': False,
        },
    }


def self_test() -> list[str]:
    errors: list[str] = []
    good = _self_test_table()
    if check_lifecycle_decision_table(good):
        errors.append('aggregate lifecycle decision self-test rejected canonical row shapes')
    bad = _self_test_table()
    for row in bad['rows']:
        if row['row_id'] == 'active-current':
            row['lifecycle_state'] = 'revoked'
            break
    if not any('row active-current lifecycle_state must be active' in e for e in check_lifecycle_decision_table(bad)):
        errors.append('aggregate lifecycle decision self-test failed to reject row lifecycle_state drift')
    probe = {
        'lifecycle_state': 'revoked',
        'lifecycle_effect': 'historical_only',
        'revocation_status': 'revoked',
        'emergency_withdrawal': {'state': 'not_applicable'},
        'contestation': {'state': 'none'},
    }
    if expected_lifecycle_decision(probe) != 'suppressed_by_revocation':
        errors.append('aggregate lifecycle decision self-test failed expected_lifecycle_decision revoked case')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync aggregate lifecycle decision semantic self-test passed.')

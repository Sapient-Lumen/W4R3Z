#!/usr/bin/env python3
"""External transparency receipt reference semantic checks.

The receipt reference is a compact, aggregate/discovery-safe hook into an
outside transparency mechanism.  These checks make the digest-binding and
boundary claims executable without turning TimeSync into a transparency-log
verifier, monitor registry, or proof-disclosure format.
"""
from __future__ import annotations

from typing import Any

from discovery_binding_semantics import digest_binds

EXTERNAL_CHECKPOINT_BINDS = {'append_only_replay_log_checkpoint', 'private_log_checkpoint'}
BOUNDARY_FALSE = (
    'log_operator_identity_exported',
    'monitor_identity_exported',
    'raw_log_entry_exported',
    'external_receipt_updates_profile_assessment',
    'external_receipt_interpreted_as_timesync_provenance',
)


def _binds_any(digest: Any, expected: set[str]) -> bool:
    return isinstance(digest, dict) and digest.get('algorithm') == 'sha256' and digest.get('binds') in expected and isinstance(digest.get('value'), str)


def check_external_transparency_receipt_reference(ref: dict[str, Any]) -> list[str]:
    """Validate digest classes and non-upgrade boundary for an external receipt reference."""
    errors: list[str] = []
    boundary = ref.get('boundary', {}) if isinstance(ref.get('boundary'), dict) else {}
    for key in BOUNDARY_FALSE:
        if boundary.get(key) is not False:
            errors.append(f'external transparency receipt boundary.{key} must be false')
    if boundary.get('external_receipt_updates_replay_visibility_only') is not True:
        errors.append('external transparency receipt may update only aggregate replay-visibility posture')

    if ref.get('receipt_validation_status') == 'validated':
        if not digest_binds(ref.get('statement_digest'), 'aggregate_verifier_audit_summary'):
            errors.append('validated external transparency receipt requires statement_digest binding aggregate_verifier_audit_summary')
        if not isinstance(ref.get('checkpoint_digest'), dict):
            errors.append('validated external transparency receipt requires checkpoint_digest')
        elif not _binds_any(ref.get('checkpoint_digest'), EXTERNAL_CHECKPOINT_BINDS):
            errors.append('validated external transparency receipt checkpoint_digest must bind append_only_replay_log_checkpoint or private_log_checkpoint')
        if not digest_binds(ref.get('receipt_digest'), 'external_transparency_receipt'):
            errors.append('validated external transparency receipt requires receipt_digest binding external_transparency_receipt')
    return errors


def self_test() -> list[str]:
    good = {
        'receipt_validation_status': 'validated',
        'statement_digest': {'algorithm': 'sha256', 'value': 'a' * 64, 'binds': 'aggregate_verifier_audit_summary'},
        'checkpoint_digest': {'algorithm': 'sha256', 'value': 'b' * 64, 'binds': 'private_log_checkpoint'},
        'receipt_digest': {'algorithm': 'sha256', 'value': 'c' * 64, 'binds': 'external_transparency_receipt'},
        'boundary': {
            'log_operator_identity_exported': False,
            'monitor_identity_exported': False,
            'raw_log_entry_exported': False,
            'external_receipt_updates_profile_assessment': False,
            'external_receipt_updates_replay_visibility_only': True,
            'external_receipt_interpreted_as_timesync_provenance': False,
        },
    }
    errors: list[str] = []
    if check_external_transparency_receipt_reference(good):
        errors.append('external receipt self-test rejected valid receipt reference')
    bad = dict(good)
    bad['statement_digest'] = {'algorithm': 'sha256', 'value': 'a' * 64, 'binds': 'scope_composition_guard'}
    if not any('statement_digest binding aggregate_verifier_audit_summary' in e for e in check_external_transparency_receipt_reference(bad)):
        errors.append('external receipt self-test failed to reject wrong statement digest binding')
    bad2 = dict(good)
    bad2['checkpoint_digest'] = {'algorithm': 'sha256', 'value': 'b' * 64, 'binds': 'aggregate_verifier_audit_batch'}
    if not any('checkpoint_digest must bind append_only_replay_log_checkpoint or private_log_checkpoint' in e for e in check_external_transparency_receipt_reference(bad2)):
        errors.append('external receipt self-test failed to reject wrong checkpoint digest binding')
    bad3 = dict(good)
    bad3['receipt_digest'] = {'algorithm': 'sha256', 'value': 'c' * 64, 'binds': 'retained_operator_record'}
    if not any('receipt_digest binding external_transparency_receipt' in e for e in check_external_transparency_receipt_reference(bad3)):
        errors.append('external receipt self-test failed to reject wrong receipt digest binding')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync external receipt semantic self-test passed.')

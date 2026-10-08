#!/usr/bin/env python3
"""Replay-transparency core digest binding semantics for TimeSync."""
from __future__ import annotations

import re
from typing import Any


def _digest_binds(digest: Any, expected: str) -> bool:
    return (
        isinstance(digest, dict)
        and digest.get('algorithm') == 'sha256'
        and isinstance(digest.get('value'), str)
        and bool(re.fullmatch(r'[A-Fa-f0-9]{64}', digest.get('value', '')))
        and digest.get('binds') == expected
    )


def _require(digest: Any, expected: str, message: str) -> list[str]:
    if not _digest_binds(digest, expected):
        return [message]
    return []


def check_replay_core_digest_bindings(record: dict[str, Any]) -> list[str]:
    """Make replay/aggregate record-local digest classes fail closed.

    JSON Schema can prove that digest objects are shaped like digests, but it
    cannot always prove that each digest is bound to the artifact class that the
    surrounding semantic field claims to reference.  These checks cover core
    replay receipt and aggregate verifier summary digests before they are used
    for current replay visibility or aggregate interpretation.
    """
    errors: list[str] = []
    kind = record.get('record_kind')

    if kind == 'challenge_replay_transparency_receipt':
        replay = record.get('replay_event', {}) if isinstance(record.get('replay_event'), dict) else {}
        errors.extend(_require(
            replay.get('replay_event_digest'),
            'challenge_result_replay_event',
            'replay transparency receipt replay_event_digest must bind challenge_result_replay_event',
        ))

        anchor = record.get('transparency_anchor', {}) if isinstance(record.get('transparency_anchor'), dict) else {}
        if anchor.get('anchor_kind') != 'not_logged':
            errors.extend(_require(
                anchor.get('digest'),
                'append_only_replay_log_checkpoint',
                'replay transparency anchor digest must bind append_only_replay_log_checkpoint',
            ))

        anchor_eval = record.get('anchor_evaluation', {}) if isinstance(record.get('anchor_evaluation'), dict) else {}
        consistency = anchor_eval.get('checkpoint_consistency', {}) if isinstance(anchor_eval.get('checkpoint_consistency'), dict) else {}
        if consistency.get('status') == 'checked_consistent' or isinstance(consistency.get('current_checkpoint_digest'), dict):
            errors.extend(_require(
                consistency.get('current_checkpoint_digest'),
                'append_only_replay_log_checkpoint',
                'replay transparency current_checkpoint_digest must bind append_only_replay_log_checkpoint',
            ))

    elif kind == 'aggregate_verifier_audit_summary':
        aggregate = record.get('aggregate_summary', {}) if isinstance(record.get('aggregate_summary'), dict) else {}
        integrity = aggregate.get('integrity_binding', {}) if isinstance(aggregate.get('integrity_binding'), dict) else {}
        errors.extend(_require(
            integrity.get('digest'),
            'aggregate_verifier_audit_summary',
            'aggregate verifier audit integrity_binding.digest must bind aggregate_verifier_audit_summary',
        ))

    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    good = {
        'record_kind': 'challenge_replay_transparency_receipt',
        'replay_event': {'replay_event_digest': {'algorithm': 'sha256', 'value': 'a' * 64, 'binds': 'challenge_result_replay_event'}},
        'transparency_anchor': {'anchor_kind': 'local_append_only_log_checkpoint', 'digest': {'algorithm': 'sha256', 'value': 'b' * 64, 'binds': 'append_only_replay_log_checkpoint'}},
        'anchor_evaluation': {'checkpoint_consistency': {'status': 'checked_consistent', 'current_checkpoint_digest': {'algorithm': 'sha256', 'value': 'c' * 64, 'binds': 'append_only_replay_log_checkpoint'}}},
    }
    if check_replay_core_digest_bindings(good):
        errors.append('accepted replay receipt produced digest-binding errors')
    bad = {
        'record_kind': 'aggregate_verifier_audit_summary',
        'aggregate_summary': {'integrity_binding': {'digest': {'algorithm': 'sha256', 'value': 'd' * 64, 'binds': 'aggregate_publication_revision_chain'}}},
    }
    if not check_replay_core_digest_bindings(bad):
        errors.append('aggregate integrity wrong-bind survivor was not rejected')
    return errors

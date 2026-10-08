#!/usr/bin/env python3
"""Aggregate verifier audit publication-time checks.

Aggregate summaries have two relevant artifact times:
- ``issued_at``: the aggregate publication event time.
- ``aggregate_record_created_at``: the later artifact/check time used by the
  compact audit record.

Prior revisions checked many nested lifecycle and notification times against the
record-created time, but did not make the top-level relationship between
``issued_at`` and ``aggregate_record_created_at`` executable. This helper keeps
that ordering and the aggregate period interval check outside the monolithic
validator without turning aggregate timing metadata into TimeState freshness or
profile evidence.
"""
from __future__ import annotations

from typing import Any

from temporal_coherence import check_time_not_after, check_time_order


def check_aggregate_publication_temporal(record: dict[str, Any]) -> list[str]:
    """Validate artifact-time ordering for aggregate verifier audit summaries."""
    errors: list[str] = []
    if record.get('record_kind') != 'aggregate_verifier_audit_summary':
        return errors

    issued_at = record.get('issued_at')
    created_at = record.get('aggregate_record_created_at')
    if issued_at and created_at:
        errors.extend(check_time_not_after(
            issued_at,
            created_at,
            value_label='aggregate verifier audit issued_at',
            anchor_label='aggregate_record_created_at',
        ))

    aggregate = record.get('aggregate_summary') if isinstance(record.get('aggregate_summary'), dict) else None
    if not isinstance(aggregate, dict):
        return errors
    period = aggregate.get('period') if isinstance(aggregate.get('period'), dict) else None
    if not isinstance(period, dict):
        return errors

    start = period.get('start')
    end = period.get('end')
    if start and end:
        errors.extend(check_time_order(
            start,
            end,
            start_label='aggregate verifier audit summary period start',
            end_label='aggregate verifier audit summary period end',
            error_message='aggregate verifier audit summary period start must be before end',
        ))
    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    valid = {
        'record_kind': 'aggregate_verifier_audit_summary',
        'issued_at': '2026-05-22T00:05:00Z',
        'aggregate_record_created_at': '2026-05-22T00:10:00Z',
        'aggregate_summary': {'period': {'start': '2026-05-21T00:00:00Z', 'end': '2026-05-22T00:00:00Z'}},
    }
    if check_aggregate_publication_temporal(valid):
        errors.append('aggregate temporal self-test unexpectedly rejected valid aggregate timing')
    inverted_period = {
        **valid,
        'aggregate_summary': {'period': {'start': '2026-05-22T00:00:00Z', 'end': '2026-05-22T00:00:00Z'}},
    }
    if not any('period start must be before end' in e for e in check_aggregate_publication_temporal(inverted_period)):
        errors.append('aggregate temporal self-test failed to reject inverted/equal aggregate period')
    future_issue = {**valid, 'issued_at': '2026-05-22T00:11:00Z'}
    if not any('issued_at cannot be after aggregate_record_created_at' in e for e in check_aggregate_publication_temporal(future_issue)):
        errors.append('aggregate temporal self-test failed to reject issued_at after record-created time')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync aggregate temporal self-test passed.')

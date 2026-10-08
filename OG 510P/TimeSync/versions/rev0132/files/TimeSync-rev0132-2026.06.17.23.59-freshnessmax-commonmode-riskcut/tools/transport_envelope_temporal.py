#!/usr/bin/env python3
"""Transport-envelope temporal boundary checks for TimeSync validation.

Transport metadata is deliberately not TimeState freshness.  Even so, an
optional envelope ``sent_at`` must not predate semantic facts that the envelope
already carries.  This module keeps that artifact-time sanity check separate
from transport binding strength and from semantic payload validation.
"""
from __future__ import annotations

from typing import Any, Iterable

from temporal_coherence import check_time_not_after

# Deliberately narrow: these are event/observation/publication timestamps that
# assert something already happened.  Window bounds such as not_after,
# current_use_not_after, expires_at, and validity horizons are intentionally not
# checked against sent_at because they may point into the future.
SEMANTIC_EVENT_TIME_KEYS = {
    'assessment_time',
    'basis_time',
    'checked_at',
    'created_at',
    'evaluated_at',
    'exported_at',
    'generated_at',
    'issued_at',
    'last_correction',
    'last_discipline',
    'observed_at',
    'record_created_at',
    'responded_at',
}


def _iter_semantic_event_times(value: Any, path: str = 'semantic_payload') -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f'{path}.{key}'
            if key in SEMANTIC_EVENT_TIME_KEYS and isinstance(child, str):
                yield child_path, child
            yield from _iter_semantic_event_times(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value, start=1):
            yield from _iter_semantic_event_times(child, f'{path}[{index}]')


def check_transport_envelope_temporal(envelope: dict[str, Any]) -> list[str]:
    """Reject semantic event timestamps that occur after envelope ``sent_at``.

    ``sent_at`` is only an artifact ordering boundary.  Passing this check does
    not make the envelope timestamp freshness evidence, profile evidence, or a
    substitute for payload-level current-use metadata.
    """
    errors: list[str] = []
    sent_at = envelope.get('sent_at')
    payload = envelope.get('semantic_payload')
    if not sent_at or not isinstance(payload, dict):
        return errors

    for label, timestamp in _iter_semantic_event_times(payload):
        errors.extend(check_time_not_after(
            timestamp,
            sent_at,
            value_label=label,
            anchor_label='transport envelope sent_at',
            error_message=f'transport envelope sent_at cannot precede {label}',
        ))
    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    valid = {
        'sent_at': '2026-05-10T23:00:00Z',
        'semantic_payload': {
            'profile_assessments': [
                {'assessment_time': '2026-05-10T22:59:00Z'},
            ],
            'validity_horizon': {
                'not_after': '2026-05-11T00:00:00Z',
            },
        },
    }
    if check_transport_envelope_temporal(valid):
        errors.append('transport_envelope_temporal self-test failed: valid envelope rejected')

    future_observation = {
        'sent_at': '2026-05-10T23:00:00Z',
        'semantic_payload': {
            'results': {
                'sync_dimension': {
                    'freshness': {'observed_at': '2026-05-10T23:00:01Z'},
                }
            }
        },
    }
    if not any('sent_at cannot precede semantic_payload.results.sync_dimension.freshness.observed_at' in e for e in check_transport_envelope_temporal(future_observation)):
        errors.append('transport_envelope_temporal self-test failed: future discovery observation accepted')

    ignored_future_window = {
        'sent_at': '2026-05-10T23:00:00Z',
        'semantic_payload': {
            'results': {
                'sync_dimension': {
                    'freshness': {'current_use_not_after': '2026-05-10T23:10:00Z'},
                }
            }
        },
    }
    if check_transport_envelope_temporal(ignored_future_window):
        errors.append('transport_envelope_temporal self-test failed: future window bound treated as event time')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync transport-envelope temporal self-test passed.')

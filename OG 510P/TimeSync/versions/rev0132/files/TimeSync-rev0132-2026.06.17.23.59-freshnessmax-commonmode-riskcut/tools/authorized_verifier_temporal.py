"""Authorized-verifier challenge temporal checks.

This module keeps challenge artifact, response, portable-result, revocation, and
replay timing together. The checks are deliberately about ordering and current-use
reuse only; they do not make authorized-verifier disclosure material profile
evidence, TimeState provenance, or a policy/actionability input.
"""
from __future__ import annotations

from typing import Any

from temporal_coherence import ExactDateTime, parse_dt, check_time_not_after


def _parse(value: Any, label: str, errors: list[str]) -> ExactDateTime | None:
    if not isinstance(value, str):
        errors.append(f'{label} must be a date-time string')
        return None
    try:
        return parse_dt(value)
    except Exception as exc:  # noqa: BLE001
        errors.append(f'{label} parse error: {exc}')
        return None


def check_authorized_verifier_temporal(record: dict[str, Any]) -> list[str]:
    """Validate authorized-verifier challenge/result/replay timestamp order."""
    errors: list[str] = []
    issued = _parse(record.get('issued_at'), 'authorized verifier challenge issued_at', errors)
    expires = _parse(record.get('expires_at'), 'authorized verifier challenge expires_at', errors)
    if issued is not None and expires is not None and issued >= expires:
        errors.append('authorized verifier challenge expires_at must be after issued_at')

    result = record.get('challenge_result') if isinstance(record.get('challenge_result'), dict) else None
    if result is None:
        return errors

    responded = _parse(result.get('responded_at'), 'challenge_result.responded_at', errors)
    if issued is not None and responded is not None and responded < issued:
        errors.append('challenge_result.responded_at cannot be before authorized verifier challenge issued_at')
    if expires is not None and responded is not None and responded > expires:
        errors.append('authorized verifier challenge result responded_at is after expires_at')

    state = result.get('portable_result_state') if isinstance(result.get('portable_result_state'), dict) else {}
    evaluated = _parse(state.get('evaluated_at'), 'portable_result_state evaluated_at', errors) if state else None
    not_after = _parse(state.get('not_after'), 'portable_result_state not_after', errors) if state else None
    if evaluated is not None and not_after is not None and evaluated > not_after:
        errors.append('portable result current status evaluated_at is after not_after')
    if expires is not None and not_after is not None and not_after > expires:
        errors.append('portable result not_after cannot exceed challenge expires_at')
    if responded is not None and evaluated is not None and responded > evaluated:
        errors.append('portable result state cannot be evaluated before challenge_result.responded_at')

    revocation = state.get('revocation_check') if isinstance(state.get('revocation_check'), dict) else {}
    rev_checked = _parse(revocation.get('checked_at'), 'portable result revocation_check.checked_at', errors) if revocation else None
    if rev_checked is not None and evaluated is not None and rev_checked > evaluated:
        errors.append('portable result revocation_check.checked_at cannot be after portable_result_state evaluated_at')
    if rev_checked is not None and responded is not None and rev_checked < responded:
        errors.append('portable result revocation_check.checked_at cannot be before challenge_result.responded_at')

    replay = record.get('replay_context') if isinstance(record.get('replay_context'), dict) else None
    if replay is None:
        return errors

    portability = record.get('portability_boundary') if isinstance(record.get('portability_boundary'), dict) else {}
    if portability.get('replay_policy') == 'not_replayable' or portability.get('portable_result_scope') == 'not_portable':
        errors.append('challenge result replay is not allowed by portability boundary')
    if state.get('current_status') != 'usable_for_commitment_verification_only' or revocation.get('status') != 'checked_not_revoked':
        errors.append('challenge result replay requires usable portable result status')

    replayed = _parse(replay.get('replayed_at'), 'challenge replay replayed_at', errors)
    if replayed is not None and responded is not None and replayed < responded:
        errors.append('challenge result replay cannot occur before challenge_result.responded_at')
    if replayed is not None and evaluated is not None and replayed < evaluated:
        errors.append('challenge result replay cannot occur before portable_result_state.evaluated_at')
    if replayed is not None and not_after is not None and replayed > not_after:
        errors.append('challenge result replay is outside the portable result window')
    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    base = {
        'issued_at': '2026-05-21T09:30:00Z',
        'expires_at': '2026-05-28T09:30:00Z',
        'challenge_result': {
            'responded_at': '2026-05-21T09:35:00Z',
            'portable_result_state': {
                'evaluated_at': '2026-05-21T09:35:02Z',
                'not_after': '2026-05-28T09:30:00Z',
                'current_status': 'usable_for_commitment_verification_only',
                'revocation_check': {'status': 'checked_not_revoked', 'checked_at': '2026-05-21T09:35:01Z'},
            },
        },
        'portability_boundary': {'portable_result_scope': 'local_retained_record_only'},
    }
    if check_authorized_verifier_temporal(base):
        errors.append('authorized verifier temporal self-test rejected valid base record')

    stale_rev = {
        **base,
        'challenge_result': {
            **base['challenge_result'],
            'portable_result_state': {
                **base['challenge_result']['portable_result_state'],
                'revocation_check': {'status': 'checked_not_revoked', 'checked_at': '2026-05-21T09:34:59Z'},
            },
        },
    }
    if not any('cannot be before challenge_result.responded_at' in e for e in check_authorized_verifier_temporal(stale_rev)):
        errors.append('authorized verifier temporal self-test failed: pre-response revocation accepted')

    pre_issue = {
        **base,
        'challenge_result': {**base['challenge_result'], 'responded_at': '2026-05-21T09:29:59Z'},
    }
    if not any('cannot be before authorized verifier challenge issued_at' in e for e in check_authorized_verifier_temporal(pre_issue)):
        errors.append('authorized verifier temporal self-test failed: pre-issue response accepted')

    replay = {
        **base,
        'replay_context': {'replayed_at': '2026-05-21T09:34:00Z'},
        'portability_boundary': {'portable_result_scope': 'local_retained_record_only'},
    }
    if not any('challenge result replay cannot occur before challenge_result.responded_at' in e for e in check_authorized_verifier_temporal(replay)):
        errors.append('authorized verifier temporal self-test failed: pre-response replay accepted')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync authorized-verifier temporal self-test passed.')

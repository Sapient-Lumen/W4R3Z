"""Replay-transparency temporal checks.

This module keeps replay-event, anchor freshness, checkpoint consistency, and
witness/monitor observation timing together. The checks are deliberately about
ordering of evidence relative to the replay-visibility evaluation; they do not
make transparency receipts TimeState freshness, profile evidence, profile
reassessment input, actionability evidence, or transport authentication.
"""
from __future__ import annotations

from typing import Any

from temporal_coherence import ExactDateTime, check_freshness_age, check_time_not_after, parse_dt


def _parse_optional(value: Any, label: str, errors: list[str]) -> ExactDateTime | None:
    if value is None:
        return None
    if not isinstance(value, str):
        errors.append(f'{label} must be a date-time string')
        return None
    try:
        return parse_dt(value)
    except Exception as exc:  # noqa: BLE001
        errors.append(f'{label} parse error: {exc}')
        return None


def _same_time(value: Any, anchor: Any, *, value_label: str, anchor_label: str, mismatch: str) -> list[str]:
    errors: list[str] = []
    value_dt = _parse_optional(value, value_label, errors)
    anchor_dt = _parse_optional(anchor, anchor_label, errors)
    if value_dt is not None and anchor_dt is not None and value_dt != anchor_dt:
        errors.append(mismatch)
    return errors


def check_replay_transparency_temporal(record: dict[str, Any]) -> list[str]:
    """Validate timestamp relations for replay-transparency receipt-like records."""
    errors: list[str] = []
    evaluation = record.get('anchor_evaluation') if isinstance(record.get('anchor_evaluation'), dict) else None
    if evaluation is None:
        return errors

    evaluated_at = evaluation.get('evaluated_at')
    freshness = evaluation.get('anchor_freshness', {}) if isinstance(evaluation.get('anchor_freshness'), dict) else {}
    consistency = evaluation.get('checkpoint_consistency', {}) if isinstance(evaluation.get('checkpoint_consistency'), dict) else {}
    split_view = evaluation.get('split_view_boundary', {}) if isinstance(evaluation.get('split_view_boundary'), dict) else {}
    anchor = record.get('transparency_anchor', {}) if isinstance(record.get('transparency_anchor'), dict) else {}
    replay = record.get('replay_event', {}) if isinstance(record.get('replay_event'), dict) else {}
    witness = record.get('witness_cohort_evaluation', {}) if isinstance(record.get('witness_cohort_evaluation'), dict) else {}

    fstatus = freshness.get('status')
    errors.extend(check_freshness_age(
        evaluated_at=evaluated_at,
        basis_time=freshness.get('basis_time'),
        max_age_seconds=freshness.get('max_age_seconds'),
        status=fstatus,
        fresh_status='fresh_at_evaluation',
        stale_status='stale_at_evaluation',
        label='anchor freshness',
        require_fields_message='anchor freshness fresh/stale status requires basis_time and max_age_seconds',
        future_message='anchor freshness basis_time cannot be after evaluated_at',
        fresh_too_old_message='anchor freshness marked fresh but exceeds max_age_seconds',
        stale_not_old_message='anchor freshness marked stale but does not exceed max_age_seconds',
    ))

    if freshness.get('basis') == 'logged_at' and fstatus in {'fresh_at_evaluation', 'stale_at_evaluation'}:
        if not freshness.get('basis_time') or not anchor.get('logged_at'):
            errors.append('anchor freshness basis logged_at requires transparency_anchor.logged_at and basis_time')
        else:
            errors.extend(_same_time(
                freshness.get('basis_time'),
                anchor.get('logged_at'),
                value_label='anchor freshness basis_time',
                anchor_label='transparency_anchor.logged_at',
                mismatch='anchor freshness basis_time must match transparency_anchor.logged_at when basis is logged_at',
            ))

    if replay.get('replayed_at') and evaluated_at:
        errors.extend(check_time_not_after(
            replay.get('replayed_at'),
            evaluated_at,
            value_label='replay_event.replayed_at',
            anchor_label='anchor_evaluation evaluated_at',
        ))
    if anchor.get('logged_at') and evaluated_at:
        errors.extend(check_time_not_after(
            anchor.get('logged_at'),
            evaluated_at,
            value_label='transparency_anchor.logged_at',
            anchor_label='anchor_evaluation evaluated_at',
        ))
    if consistency.get('checked_at') and evaluated_at:
        errors.extend(check_time_not_after(
            consistency.get('checked_at'),
            evaluated_at,
            value_label='checkpoint consistency checked_at',
            anchor_label='anchor_evaluation evaluated_at',
        ))
    if split_view.get('first_observed_at') and evaluated_at:
        errors.extend(check_time_not_after(
            split_view.get('first_observed_at'),
            evaluated_at,
            value_label='split_view_boundary.first_observed_at',
            anchor_label='anchor_evaluation evaluated_at',
        ))
    if witness.get('observed_at') and evaluated_at:
        errors.extend(check_time_not_after(
            witness.get('observed_at'),
            evaluated_at,
            value_label='witness_cohort_evaluation observed_at',
            anchor_label='anchor_evaluation evaluated_at',
        ))
    witness_split = witness.get('split_view_signal') if isinstance(witness.get('split_view_signal'), dict) else {}
    if witness_split.get('first_observed_at') and evaluated_at:
        errors.extend(check_time_not_after(
            witness_split.get('first_observed_at'),
            evaluated_at,
            value_label='witness_cohort_evaluation.split_view_signal.first_observed_at',
            anchor_label='anchor_evaluation evaluated_at',
        ))
    return errors


def self_test() -> list[str]:
    errors: list[str] = []
    valid = {
        'record_kind': 'challenge_replay_transparency_receipt',
        'replay_event': {'replayed_at': '2026-05-21T10:00:00Z'},
        'transparency_anchor': {'logged_at': '2026-05-21T10:01:00Z'},
        'anchor_evaluation': {
            'evaluated_at': '2026-05-21T10:01:30Z',
            'anchor_freshness': {
                'status': 'fresh_at_evaluation',
                'basis': 'logged_at',
                'basis_time': '2026-05-21T10:01:00Z',
                'max_age_seconds': 120,
            },
            'checkpoint_consistency': {'checked_at': '2026-05-21T10:01:20Z'},
            'split_view_boundary': {'first_observed_at': '2026-05-21T10:01:10Z'},
        },
        'witness_cohort_evaluation': {
            'observed_at': '2026-05-21T10:01:25Z',
            'split_view_signal': {'first_observed_at': '2026-05-21T10:01:05Z'},
        },
    }
    if check_replay_transparency_temporal(valid):
        errors.append('replay-transparency temporal self-test rejected valid timing')

    replay_after_eval = {
        **valid,
        'replay_event': {'replayed_at': '2026-05-21T10:01:31Z'},
    }
    if not any('replay_event.replayed_at cannot be after anchor_evaluation evaluated_at' in e for e in check_replay_transparency_temporal(replay_after_eval)):
        errors.append('replay-transparency temporal self-test failed: future replay accepted')

    logged_after_eval = {
        **valid,
        'transparency_anchor': {'logged_at': '2026-05-21T10:01:31Z'},
        'anchor_evaluation': {
            **valid['anchor_evaluation'],
            'anchor_freshness': {
                **valid['anchor_evaluation']['anchor_freshness'],
                'basis_time': '2026-05-21T10:01:31Z',
            },
        },
    }
    if not any('transparency_anchor.logged_at cannot be after anchor_evaluation evaluated_at' in e for e in check_replay_transparency_temporal(logged_after_eval)):
        errors.append('replay-transparency temporal self-test failed: future anchor log accepted')

    basis_mismatch = {
        **valid,
        'anchor_evaluation': {
            **valid['anchor_evaluation'],
            'anchor_freshness': {
                **valid['anchor_evaluation']['anchor_freshness'],
                'basis_time': '2026-05-21T10:00:59Z',
            },
        },
    }
    if not any('basis_time must match transparency_anchor.logged_at' in e for e in check_replay_transparency_temporal(basis_mismatch)):
        errors.append('replay-transparency temporal self-test failed: logged_at basis mismatch accepted')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync replay-transparency temporal self-test passed.')

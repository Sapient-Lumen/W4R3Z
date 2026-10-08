"""Shared temporal-coherence checks for TimeSync validation.

These checks are deliberately semantic rather than pure JSON Schema. JSON Schema can
assert that timestamp fields exist and are date-time strings, but it cannot prove
that composed guard inputs were evaluated inside the same freshness window or that
stale inputs fail closed instead of being reused for current decisions.

rev0121 replaces ``datetime.fromisoformat`` ordering with exact RFC 3339 arithmetic.
Python ``datetime`` has microsecond resolution, while TimeSync schemas admit longer
fractional seconds and precision profiles may depend on them. The exact representation
below preserves every supplied fractional digit for comparison and subtraction.
Leap-second values remain explicitly unsupported by current evaluator arithmetic and
therefore fail closed rather than being silently normalized.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from fractions import Fraction
import re
from typing import Any


_RFC3339_RE = re.compile(
    r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
    r"[Tt](?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})"
    r"(?:\.(?P<fraction>\d+))?"
    r"(?P<offset>[Zz]|[+-]\d{2}:\d{2})$"
)
_EPOCH_ORDINAL = date(1970, 1, 1).toordinal()


@dataclass(frozen=True, order=True)
class ExactDateTime:
    """UTC instant with an exact fractional second.

    ``epoch_second`` is the signed whole-second count from the Unix epoch. The
    fractional component is always in ``[0, 1)`` and is represented as a rational,
    so comparisons do not collapse nanoseconds into Python microseconds.
    """

    epoch_second: int
    fractional_second: Fraction

    def __sub__(self, other: object) -> "ExactDuration":
        if not isinstance(other, ExactDateTime):
            return NotImplemented
        return ExactDuration(
            Fraction(self.epoch_second - other.epoch_second, 1)
            + self.fractional_second
            - other.fractional_second
        )


@dataclass(frozen=True)
class ExactDuration:
    seconds: Fraction

    def total_seconds(self) -> Fraction:
        return self.seconds


def parse_dt(value: str) -> ExactDateTime:
    """Parse an RFC 3339 timestamp without losing fractional precision.

    Lower-case ``t``/``z`` are accepted as RFC 3339 permits applications to do.
    Leap seconds (``:60``) are rejected until TimeSync has an explicit leap/smear
    arithmetic policy; accepting them through ordinary civil-time arithmetic would
    create a false ordering guarantee.
    """
    if not isinstance(value, str):
        raise ValueError('date-time must be a string')
    match = _RFC3339_RE.fullmatch(value)
    if match is None:
        raise ValueError('date-time must be RFC 3339 with an explicit UTC offset')

    parts = {name: match.group(name) for name in match.groupdict()}
    year = int(parts['year'])
    month = int(parts['month'])
    day = int(parts['day'])
    hour = int(parts['hour'])
    minute = int(parts['minute'])
    second = int(parts['second'])
    if hour > 23 or minute > 59:
        raise ValueError('date-time contains an out-of-range clock field')
    if second == 60:
        raise ValueError('leap-second timestamps are not supported by current semantic arithmetic')
    if second > 59:
        raise ValueError('date-time contains an out-of-range second')

    try:
        ordinal = date(year, month, day).toordinal()
    except ValueError as exc:
        raise ValueError(f'date-time contains an invalid calendar date: {exc}') from exc

    offset_text = parts['offset']
    if offset_text in {'Z', 'z'}:
        offset_seconds = 0
    else:
        offset_hour = int(offset_text[1:3])
        offset_minute = int(offset_text[4:6])
        if offset_hour > 23 or offset_minute > 59:
            raise ValueError('date-time contains an out-of-range UTC offset')
        sign = 1 if offset_text[0] == '+' else -1
        offset_seconds = sign * (offset_hour * 3600 + offset_minute * 60)

    local_whole_second = (
        (ordinal - _EPOCH_ORDINAL) * 86400
        + hour * 3600
        + minute * 60
        + second
    )
    fraction_text = parts['fraction'] or ''
    fractional_second = (
        Fraction(int(fraction_text), 10 ** len(fraction_text))
        if fraction_text
        else Fraction(0, 1)
    )
    return ExactDateTime(local_whole_second - offset_seconds, fractional_second)


REQUIRED_TIME_ROLES_BY_SURFACE: dict[str, set[str]] = {
    'profile_compatibility_drift': {'profile_drift_evaluated_at'},
    'discovery_version_negotiation': {'discovery_negotiated_at'},
    'discovery_digest_binding': {'digest_policy_checked_at'},
    'aggregate_correction_authority_lifecycle': {'lifecycle_checked_at', 'revocation_checked_at'},
    'aggregate_lifecycle_rollup': {'lifecycle_rollup_checked_at'},
    'transparency_trust_policy_lifecycle': {'transparency_policy_checked_at'},
    'transparency_policy_equivalence': {'transparency_policy_checked_at'},
    'external_transparency_receipt': {'transparency_receipt_observed_at'},
    'replay_transparency_anchor': {'transparency_anchor_observed_at'},
    'correction_authority_notification': {'notification_observed_at'},
    'portable_digest_binding_policy': {'digest_policy_checked_at'},
}

FRESH_STATUSES = {'fresh_at_guard_evaluation'}
STALE_OR_UNCHECKED = {'stale_at_guard_evaluation', 'unchecked'}
BLOCKING_EFFECTS = {'suppress_current_use', 'historical_only', 'fail_closed'}


def _safe_parse_dt(value: Any, label: str, errors: list[str]) -> ExactDateTime | None:
    if not isinstance(value, str):
        errors.append(f'{label} must be a date-time string')
        return None
    try:
        return parse_dt(value)
    except Exception as exc:  # noqa: BLE001
        errors.append(f'{label} is not a valid date-time: {exc}')
        return None


def check_time_not_after(
    value: Any,
    anchor: Any,
    *,
    value_label: str,
    anchor_label: str,
    error_message: str | None = None,
) -> list[str]:
    """Return an error when ``value`` is later than ``anchor``.

    This helper intentionally accepts raw JSON values so callers can use it at
    schema-boundaries without duplicating parse/error scaffolding. It is for
    observation relationships such as ``checked_at <= evaluated_at`` and
    ``rollup_window.end <= aggregate_record_created_at``.
    """
    errors: list[str] = []
    value_dt = _safe_parse_dt(value, value_label, errors)
    anchor_dt = _safe_parse_dt(anchor, anchor_label, errors)
    if value_dt is not None and anchor_dt is not None and value_dt > anchor_dt:
        errors.append(error_message or f'{value_label} cannot be after {anchor_label}')
    return errors


def check_time_order(
    start: Any,
    end: Any,
    *,
    start_label: str,
    end_label: str,
    allow_equal: bool = False,
    error_message: str | None = None,
) -> list[str]:
    """Return an error when a declared temporal interval is inverted."""
    errors: list[str] = []
    start_dt = _safe_parse_dt(start, start_label, errors)
    end_dt = _safe_parse_dt(end, end_label, errors)
    if start_dt is None or end_dt is None:
        return errors
    if (start_dt > end_dt) or (not allow_equal and start_dt == end_dt):
        relation = '<=' if allow_equal else '<'
        errors.append(error_message or f'{start_label} must be {relation} {end_label}')
    return errors


def check_freshness_age(
    *,
    evaluated_at: Any,
    basis_time: Any,
    max_age_seconds: Any,
    status: Any,
    fresh_status: str,
    stale_status: str,
    label: str,
    require_fields_message: str,
    future_message: str,
    fresh_too_old_message: str,
    stale_not_old_message: str,
) -> list[str]:
    """Validate a freshness status against evaluated_at, basis_time, and max age.

    The caller supplies status vocabulary and user-facing messages so existing
    semantic-vector expectations stay stable while the arithmetic is centralized.
    """
    errors: list[str] = []
    if status not in {fresh_status, stale_status}:
        return errors
    if basis_time is None or max_age_seconds is None:
        return [require_fields_message]
    evaluated = _safe_parse_dt(evaluated_at, f'{label}.evaluated_at', errors)
    basis = _safe_parse_dt(basis_time, f'{label}.basis_time', errors)
    if not isinstance(max_age_seconds, int):
        errors.append(f'{label}.max_age_seconds must be an integer')
        return errors
    if evaluated is None or basis is None:
        return errors
    age_seconds = (evaluated - basis).total_seconds()
    if age_seconds < 0:
        errors.append(future_message)
    if status == fresh_status and age_seconds > max_age_seconds:
        errors.append(fresh_too_old_message)
    if status == stale_status and age_seconds <= max_age_seconds:
        errors.append(stale_not_old_message)
    return errors


def check_active_window_status(
    *,
    state: Any,
    active_state: str,
    evaluated_at: Any,
    not_before: Any,
    not_after: Any,
    label: str,
    active_outside_message: str,
    expired_state: str | None = None,
    expired_not_after_message: str | None = None,
    pending_state: str | None = None,
    pending_not_before_message: str | None = None,
) -> list[str]:
    """Common not_before/not_after semantics for lifecycle-like references."""
    errors: list[str] = []
    evaluated = _safe_parse_dt(evaluated_at, f'{label}.evaluated_at', errors)
    start = _safe_parse_dt(not_before, f'{label}.not_before', errors)
    end = _safe_parse_dt(not_after, f'{label}.not_after', errors)
    if evaluated is None or start is None or end is None:
        return errors
    if start >= end:
        errors.append(f'{label} not_before must be before not_after')
    if state == active_state and not (start <= evaluated <= end):
        errors.append(active_outside_message)
    if expired_state is not None and state == expired_state and expired_not_after_message and evaluated <= end:
        errors.append(expired_not_after_message)
    if pending_state is not None and state == pending_state and pending_not_before_message and evaluated >= start:
        errors.append(pending_not_before_message)
    return errors


def check_scope_temporal_coherence(
    guard: dict[str, Any],
    *,
    current_guard: bool,
    current_surfaces: set[str],
    composition_scope: str | None,
) -> list[str]:
    """Validate temporal coherence for a scope-composition guard.

    The rule is intentionally conservative: a current-use guard may only be current
    if each current surface has the required observation role(s), every such
    observation is fresh at guard evaluation, and each observation falls inside the
    declared evaluation window. Stale or unchecked observations must explicitly
    block current use.
    """
    errors: list[str] = []
    temporal = guard.get('temporal_coherence')
    if not isinstance(temporal, dict):
        errors.append('scope composition guard requires temporal_coherence object')
        return errors

    window = temporal.get('evaluation_window') if isinstance(temporal.get('evaluation_window'), dict) else {}
    start = _safe_parse_dt(window.get('not_before'), 'temporal coherence evaluation_window.not_before', errors)
    end = _safe_parse_dt(window.get('not_after'), 'temporal coherence evaluation_window.not_after', errors)
    evaluated_at = _safe_parse_dt(guard.get('evaluated_at'), 'scope composition guard evaluated_at', errors)
    max_span = window.get('max_span_seconds')

    if start is not None and end is not None:
        if start > end:
            errors.append('temporal coherence evaluation_window not_before must be <= not_after')
        if isinstance(max_span, int) and (end - start).total_seconds() > max_span:
            errors.append('temporal coherence evaluation_window exceeds max_span_seconds')
    if start is not None and end is not None and evaluated_at is not None:
        if not (start <= evaluated_at <= end):
            errors.append('temporal coherence guard_evaluated_at must fall inside evaluation_window')

    decision = temporal.get('coherence_decision') if isinstance(temporal.get('coherence_decision'), dict) else {}
    if current_guard:
        if decision.get('decision') != 'coherent_current_guard':
            errors.append('current scope composition guard requires coherent_current_guard temporal decision')
        if decision.get('all_current_inputs_within_window') is not True:
            errors.append('current scope composition guard requires all_current_inputs_within_window true')
        if decision.get('guard_evaluated_within_window') is not True:
            errors.append('current scope composition guard requires guard_evaluated_within_window true')
        if decision.get('stale_input_blocks_current_use') is not True:
            errors.append('current scope composition guard requires stale_input_blocks_current_use true')

    boundary = temporal.get('non_provenance_boundary') if isinstance(temporal.get('non_provenance_boundary'), dict) else {}
    for key in (
        'temporal_metadata_updates_timestate',
        'temporal_metadata_updates_profile_assessment',
        'temporal_metadata_updates_actionability',
        'temporal_metadata_interpreted_as_time_source_provenance',
        'stale_input_reuse_allowed_for_current',
    ):
        if boundary.get(key) is not False:
            errors.append(f'temporal coherence boundary.{key} must be false')

    observations = temporal.get('input_observations')
    if not isinstance(observations, list):
        errors.append('temporal coherence input_observations must be a list')
        observations = []

    roles_by_surface: dict[str, set[str]] = {}
    for obs in observations:
        if not isinstance(obs, dict):
            continue
        surface = obs.get('surface')
        role = obs.get('time_role')
        label = f'temporal coherence observation {surface or "<unknown-surface>"}/{role or "<unknown-role>"}'
        if isinstance(surface, str) and isinstance(role, str):
            roles_by_surface.setdefault(surface, set()).add(role)
        observed_at = _safe_parse_dt(obs.get('observed_at'), f'{label}.observed_at', errors)
        if current_guard and isinstance(surface, str) and surface in current_surfaces:
            if obs.get('freshness_status') not in FRESH_STATUSES:
                errors.append('current scope composition guard cannot use stale or unchecked temporal input')
            if start is not None and end is not None and observed_at is not None and not (start <= observed_at <= end):
                errors.append('current scope composition guard input observation must fall inside evaluation_window')
            if observed_at is not None and evaluated_at is not None:
                age_seconds = (evaluated_at - observed_at).total_seconds()
                if age_seconds < 0:
                    errors.append('current scope composition guard cannot use an input observed after guard evaluation')
                obs_max_age = obs.get('max_age_seconds')
                if isinstance(obs_max_age, int) and age_seconds > obs_max_age:
                    errors.append('current scope composition guard input observation exceeds max_age_seconds')
        if obs.get('freshness_status') in STALE_OR_UNCHECKED and obs.get('current_use_effect') not in BLOCKING_EFFECTS:
            errors.append('stale or unchecked temporal input must block current use')

    if current_guard:
        for surface in sorted(current_surfaces):
            required = REQUIRED_TIME_ROLES_BY_SURFACE.get(surface, set())
            missing = required - roles_by_surface.get(surface, set())
            if missing:
                errors.append(f'current scope composition guard missing temporal observation roles for {surface}: {sorted(missing)}')
        if composition_scope == 'mixed_layer_portability_review' and 'decision_matrix_observed_at' not in roles_by_surface.get('scope_composition_decision_matrix', set()):
            errors.append('mixed-layer current scope composition guard requires decision_matrix_observed_at temporal observation')

    return errors



def _current_use_requested(result: dict[str, Any]) -> bool:
    negotiation = result.get('version_negotiation') if isinstance(result.get('version_negotiation'), dict) else {}
    digest_binding = result.get('digest_binding') if isinstance(result.get('digest_binding'), dict) else {}
    return negotiation.get('current_use_allowed') is True or digest_binding.get('current_use_allowed') is True


def _returned_value_timestamp(value: Any) -> Any | None:
    """Return the primary timestamp of a returned discovery object, when present."""
    if not isinstance(value, dict):
        return None
    for key in ('generated_at', 'evaluated_at', 'issued_at', 'responded_at'):
        if key in value:
            return value.get(key)
    return None


def check_discovery_result_freshness(item: str, result: dict[str, Any]) -> list[str]:
    """Validate current-use discovery result freshness without making it provenance.

    Discovery metadata can gate whether a returned object may be interpreted now,
    but it must not update a TimeState, profile assessment, or actionability. A
    current-use discovery result therefore needs a local observation timestamp and
    a bounded basis timestamp, and any timestamp carried by the returned object
    must be the freshness basis being checked.
    """
    errors: list[str] = []
    current = _current_use_requested(result)
    freshness = result.get('freshness') if isinstance(result.get('freshness'), dict) else None
    if current and freshness is None:
        return [f'{item}: current discovery result requires freshness metadata']
    if freshness is None:
        return errors

    if freshness.get('freshness_updates_discovery_interpretation_only') is not True:
        errors.append(f'{item}: discovery freshness may update discovery interpretation only')
    for key in (
        'freshness_updates_profile_assessment',
        'freshness_updates_actionability',
        'freshness_interpreted_as_timesync_provenance',
    ):
        if freshness.get(key) is not False:
            errors.append(f'{item}: discovery freshness {key} must be false')

    status = freshness.get('freshness_status')
    if current and status != 'fresh_for_current_use':
        errors.append(f'{item}: current discovery result requires fresh_for_current_use discovery freshness')

    errors.extend(check_time_order(
        freshness.get('observed_at'),
        freshness.get('current_use_not_after'),
        start_label=f'{item} discovery freshness observed_at',
        end_label=f'{item} discovery freshness current_use_not_after',
        allow_equal=True,
    ))
    errors.extend(check_freshness_age(
        evaluated_at=freshness.get('observed_at'),
        basis_time=freshness.get('basis_time'),
        max_age_seconds=freshness.get('max_age_seconds'),
        status=status,
        fresh_status='fresh_for_current_use',
        stale_status='stale_for_current_use',
        label=f'{item} discovery freshness',
        require_fields_message=f'{item}: discovery freshness status requires basis_time and max_age_seconds',
        future_message=f'{item}: current discovery freshness basis_time cannot be after observed_at',
        fresh_too_old_message=f'{item}: current discovery result marked fresh but exceeds max_age_seconds',
        stale_not_old_message=f'{item}: discovery result marked stale but is within max_age_seconds',
    ))

    value_time = _returned_value_timestamp(result.get('value'))
    if current and value_time is not None and freshness.get('basis_time') != value_time:
        errors.append(f'{item}: discovery freshness basis_time must match returned value timestamp')
    if current and result.get('status') != 'returned':
        errors.append(f'{item}: current discovery result must be returned')
    return errors


def self_test() -> list[str]:
    """Return helper self-test failures without touching archive fixtures."""
    errors: list[str] = []
    if not (
        parse_dt('2026-01-01T00:00:00.123456789Z')
        > parse_dt('2026-01-01T00:00:00.123456788Z')
    ):
        errors.append('parse_dt self-test failed: submicrosecond ordering collapsed')
    if parse_dt('2026-01-01t00:00:00.5z') != parse_dt('2025-12-31T19:00:00.500-05:00'):
        errors.append('parse_dt self-test failed: case or UTC-offset normalization drifted')
    exact_age = (
        parse_dt('2026-01-01T00:00:01.000000001Z')
        - parse_dt('2026-01-01T00:00:00.999999999Z')
    ).total_seconds()
    if exact_age != Fraction(1, 500_000_000):
        errors.append(f'parse_dt self-test failed: exact duration was {exact_age!r}')
    try:
        parse_dt('2016-12-31T23:59:60Z')
    except ValueError as exc:
        if 'leap-second' not in str(exc):
            errors.append(f'parse_dt self-test failed: unclear leap-second rejection: {exc}')
    else:
        errors.append('parse_dt self-test failed: unsupported leap second accepted')
    if not check_time_not_after(
        '2026-05-21T10:02:00Z',
        '2026-05-21T10:01:00Z',
        value_label='observed_at',
        anchor_label='evaluated_at',
    ):
        errors.append('check_time_not_after self-test failed: future observation accepted')
    if check_time_not_after(
        '2026-05-21T10:00:00Z',
        '2026-05-21T10:01:00Z',
        value_label='observed_at',
        anchor_label='evaluated_at',
    ):
        errors.append('check_time_not_after self-test failed: valid observation rejected')
    if not check_freshness_age(
        evaluated_at='2026-05-21T10:01:00Z',
        basis_time='2026-05-21T09:00:00Z',
        max_age_seconds=60,
        status='fresh',
        fresh_status='fresh',
        stale_status='stale',
        label='freshness self-test',
        require_fields_message='missing',
        future_message='future',
        fresh_too_old_message='too old',
        stale_not_old_message='not old',
    ):
        errors.append('check_freshness_age self-test failed: stale fresh status accepted')
    active_errors = check_active_window_status(
        state='active',
        active_state='active',
        evaluated_at='2026-05-21T11:00:00Z',
        not_before='2026-05-21T09:00:00Z',
        not_after='2026-05-21T10:00:00Z',
        label='window self-test',
        active_outside_message='outside',
    )
    if 'outside' not in active_errors:
        errors.append('check_active_window_status self-test failed: active outside window accepted')
    discovery_errors = check_discovery_result_freshness('item', {
        'status': 'returned',
        'version_negotiation': {'current_use_allowed': True},
        'value': {'generated_at': '2026-05-21T10:00:00Z'},
        'freshness': {
            'observed_at': '2026-05-21T10:05:00Z',
            'basis_time': '2026-05-21T10:00:00Z',
            'max_age_seconds': 60,
            'current_use_not_after': '2026-05-21T10:10:00Z',
            'freshness_status': 'fresh_for_current_use',
            'freshness_updates_discovery_interpretation_only': True,
            'freshness_updates_profile_assessment': False,
            'freshness_updates_actionability': False,
            'freshness_interpreted_as_timesync_provenance': False,
        },
    })
    if not any('exceeds max_age_seconds' in e for e in discovery_errors):
        errors.append('check_discovery_result_freshness self-test failed: stale current discovery accepted')
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync temporal coherence helper self-test passed.')

#!/usr/bin/env python3
"""Shared conservative NTP-family bound arithmetic for TimeSync adapters.

The adapter parsers stay implementation-specific.  This module owns only the
repeated arithmetic that should be identical for NTP-family operational-state
surfaces once they have supplied offset, root delay, root dispersion, local rate
error, collection time, and evaluation time.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from fractions import Fraction
from typing import Type

from temporal_coherence import parse_dt

NS_PER_SECOND = 1_000_000_000


@dataclass(frozen=True)
class NtpErrorBound:
    """Conservative interval components in seconds."""

    base_bound_seconds: Decimal
    age_seconds: Decimal
    holdover_growth_seconds: Decimal
    total_bound_seconds: Decimal
    delay_contribution_seconds: Decimal
    negative_root_delay_clamped: bool


def parse_instant_seconds(value: str, *, label: str, error_cls: Type[Exception] = ValueError) -> Fraction:
    """Parse an RFC 3339 instant into exact seconds since Unix epoch."""
    try:
        parsed = parse_dt(value)
    except Exception as exc:  # noqa: BLE001
        raise error_cls(f'{label} must be RFC 3339 with explicit offset: {exc}') from exc
    return Fraction(parsed.epoch_second, 1) + parsed.fractional_second


def fraction_to_decimal(value: Fraction) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def decimal_seconds_to_fraction(value: Decimal) -> Fraction:
    return Fraction(value)


def ceil_fraction_to_ns(value: Fraction) -> int:
    return -((-value.numerator * NS_PER_SECOND) // value.denominator)


def floor_fraction_to_ns(value: Fraction) -> int:
    return (value.numerator * NS_PER_SECOND) // value.denominator


def format_epoch_ns(epoch_ns: int) -> str:
    seconds, nanos = divmod(epoch_ns, NS_PER_SECOND)
    dt = datetime.fromtimestamp(seconds, tz=timezone.utc)
    frac = '' if nanos == 0 else f'.{nanos:09d}'.rstrip('0')
    return dt.strftime('%Y-%m-%dT%H:%M:%S') + frac + 'Z'


def milliseconds(seconds: Decimal) -> Decimal:
    return seconds * Decimal('1000')


def conservative_ntp_error_bound(
    *,
    system_time_offset_seconds: Decimal,
    root_delay_seconds: Decimal,
    root_dispersion_seconds: Decimal,
    rate_error_ppm: Decimal,
    collected_at: str,
    evaluated_at: str,
    error_cls: Type[Exception] = ValueError,
) -> NtpErrorBound:
    """Compute TimeSync's conservative NTP-family replay bound.

    Formula:
        abs(offset) + root_dispersion + 0.5 * max(root_delay, 0)
        + abs(rate_error_ppm) * age / 1_000_000

    Negative root delay is clamped to zero so an implementation anomaly cannot
    shrink a safety interval.  The signed offset is not used to shift or narrow
    the interval because management text is not a packet-level proof.
    """
    collected = parse_instant_seconds(collected_at, label='collected_at', error_cls=error_cls)
    evaluated = parse_instant_seconds(evaluated_at, label='evaluated_at', error_cls=error_cls)
    if evaluated < collected:
        raise error_cls('evaluated_at cannot be before collected_at')
    age = fraction_to_decimal(evaluated - collected)
    delay_contribution = max(root_delay_seconds, Decimal('0')) / Decimal('2')
    base = abs(system_time_offset_seconds) + root_dispersion_seconds + delay_contribution
    growth = age * abs(rate_error_ppm) / Decimal('1000000')
    return NtpErrorBound(
        base_bound_seconds=base,
        age_seconds=age,
        holdover_growth_seconds=growth,
        total_bound_seconds=base + growth,
        delay_contribution_seconds=delay_contribution,
        negative_root_delay_clamped=root_delay_seconds < 0,
    )


def interval_for_bound(effective_at: str, total_bound_seconds: Decimal, *, error_cls: Type[Exception] = ValueError) -> dict[str, str]:
    center = parse_instant_seconds(effective_at, label='effective_at', error_cls=error_cls)
    bound = decimal_seconds_to_fraction(total_bound_seconds)
    return {
        'earliest': format_epoch_ns(floor_fraction_to_ns(center - bound)),
        'latest': format_epoch_ns(ceil_fraction_to_ns(center + bound)),
    }


def self_test() -> list[str]:
    errors: list[str] = []
    bound = conservative_ntp_error_bound(
        system_time_offset_seconds=Decimal('-0.000006'),
        root_delay_seconds=Decimal('0.010'),
        root_dispersion_seconds=Decimal('0.001'),
        rate_error_ppm=Decimal('0.020'),
        collected_at='2026-06-17T18:45:08.000000000Z',
        evaluated_at='2026-06-17T18:45:09.000000000Z',
    )
    if bound.base_bound_seconds != Decimal('0.006006'):
        errors.append(f'expected base bound 0.006006, got {bound.base_bound_seconds}')
    if bound.holdover_growth_seconds != Decimal('0.00000002'):
        errors.append(f'expected growth 0.00000002, got {bound.holdover_growth_seconds}')
    interval = interval_for_bound('2026-06-17T18:45:09.000000000Z', bound.total_bound_seconds)
    if interval != {
        'earliest': '2026-06-17T18:45:08.99399398Z',
        'latest': '2026-06-17T18:45:09.00600602Z',
    }:
        errors.append(f'ntp_bound interval mismatch: {interval}')
    neg = conservative_ntp_error_bound(
        system_time_offset_seconds=Decimal('0'),
        root_delay_seconds=Decimal('-0.010'),
        root_dispersion_seconds=Decimal('0.001'),
        rate_error_ppm=Decimal('0'),
        collected_at='2026-06-17T18:45:08Z',
        evaluated_at='2026-06-17T18:45:08Z',
    )
    if neg.total_bound_seconds != Decimal('0.001') or not neg.negative_root_delay_clamped:
        errors.append('negative root delay was not clamped conservatively')
    try:
        conservative_ntp_error_bound(
            system_time_offset_seconds=Decimal('0'),
            root_delay_seconds=Decimal('0'),
            root_dispersion_seconds=Decimal('0'),
            rate_error_ppm=Decimal('0'),
            collected_at='2026-06-17T18:45:09Z',
            evaluated_at='2026-06-17T18:45:08Z',
        )
        errors.append('accepted evaluation before collection')
    except ValueError:
        pass
    return errors


if __name__ == '__main__':
    failures = self_test()
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        raise SystemExit(1)
    print('TimeSync shared NTP bound self-test passed.')

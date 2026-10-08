#!/usr/bin/env python3
"""chrony replay adapter and minimal TimeSync reference evaluator.

This module is intentionally small and executable. It consumes sanitized or live
`chronyc tracking` text plus optional `chronyc sources`, `sourcestats`,
`authdata`, and `ntpdata` text, produces a typed
chrony observation, derives a conservative six-field TimeState, evaluates one
profile lane, and emits a machine-readable explanation.

It is not a chrony protocol implementation, not an NTS verifier, and not a claim
that chrony's reported UTC realization is traceable. Its first purpose is to make
TimeSync's narrow waist meet a real timing implementation surface without adding
new core fields.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from fractions import Fraction
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

sys.dont_write_bytecode = True

from temporal_coherence import parse_dt
from chrony_capture import extract_replay_inputs, load_capture, self_test as chrony_capture_self_test
from chrony_policy import decide_p1_lane, load_p1_policy, policy_reference
from ntp_bound import (
    conservative_ntp_error_bound,
    interval_for_bound as common_interval_for_bound,
    milliseconds as common_milliseconds,
)

ROOT = Path(__file__).resolve().parents[1]


def _current_revision(root: Path = ROOT) -> str:
    try:
        receipt = json.loads((root / 'REVISION-RECEIPT.json').read_text(encoding='utf-8'))
        revision = receipt.get('revision')
    except Exception:  # noqa: BLE001
        revision = None
    return revision if isinstance(revision, str) else 'rev0000'


NS_PER_SECOND = 1_000_000_000
SUPPORTED_PROFILE = 'P1-general-computing'

TRACKING_REQUIRED_FIELDS = {
    'Reference ID',
    'Stratum',
    'Ref time (UTC)',
    'System time',
    'Skew',
    'Root delay',
    'Root dispersion',
    'Leap status',
}

@dataclass(frozen=True)
class ChronyTracking:
    reference_id: str
    stratum: int
    ref_time_utc: str
    system_time_offset_seconds: Decimal
    skew_ppm: Decimal
    root_delay_seconds: Decimal
    root_dispersion_seconds: Decimal
    leap_status: str
    last_offset_seconds: Decimal | None = None
    rms_offset_seconds: Decimal | None = None
    frequency_ppm: Decimal | None = None
    residual_frequency_ppm: Decimal | None = None
    update_interval_seconds: Decimal | None = None


@dataclass(frozen=True)
class ChronySource:
    mode: str
    state: str
    name: str
    stratum: int | None
    poll: int | None
    reach: str | None
    last_rx: str | None
    raw: str


@dataclass(frozen=True)
class ChronySourceStat:
    name: str
    sample_points: int
    residual_runs: int
    span_seconds: Decimal
    frequency_ppm: Decimal
    freq_skew_ppm: Decimal
    offset_seconds: Decimal
    std_dev_seconds: Decimal
    raw: str


@dataclass(frozen=True)
class ChronyAuthRow:
    name: str
    mode: str
    key_id: int | None
    algorithm_type: int | None
    key_length_bits: int | None
    last_success: str | None
    attempts_since_success: int | None
    nts_nak_seen: int | None
    cookies: int | None
    cookie_length_bytes: int | None
    raw: str


@dataclass(frozen=True)
class ChronyNtpDataBlock:
    remote_address: str | None
    leap_status: str | None
    stratum: int | None
    root_delay_seconds: Decimal | None
    root_dispersion_seconds: Decimal | None
    reference_id: str | None
    reference_time: str | None
    ntp_tests: str | None
    authenticated: bool | None
    interleaved: str | None
    tx_timestamping: str | None
    rx_timestamping: str | None
    raw_fields: dict[str, str]


@dataclass(frozen=True)
class ChronyObservation:
    collected_at: str
    tracking: ChronyTracking
    sources: tuple[ChronySource, ...]
    sourcestats: tuple[ChronySourceStat, ...] = ()
    authdata: tuple[ChronyAuthRow, ...] = ()
    ntpdata: tuple[ChronyNtpDataBlock, ...] = ()
    chronyc_tracking_command: str = 'chronyc -n tracking'
    chronyc_sources_command: str = 'chronyc -n sources'
    input_contract: str = 'chronyc-human-text-v1'
    capture_context: dict[str, Any] | None = None

    def authentication_summary(self) -> dict[str, Any]:
        auth_rows = [
            {
                'name': row.name,
                'mode': row.mode,
                'key_id': row.key_id,
                'algorithm_type': row.algorithm_type,
                'key_length_bits': row.key_length_bits,
                'last_success': row.last_success,
                'attempts_since_success': row.attempts_since_success,
                'nts_nak_seen': row.nts_nak_seen,
                'cookies': row.cookies,
                'cookie_length_bytes': row.cookie_length_bytes,
            }
            for row in self.authdata
        ]
        ntpdata_blocks = [
            {
                'remote_address': block.remote_address,
                'leap_status': block.leap_status,
                'stratum': block.stratum,
                'root_delay_seconds': _decimal_or_none(block.root_delay_seconds),
                'root_dispersion_seconds': _decimal_or_none(block.root_dispersion_seconds),
                'reference_id': block.reference_id,
                'reference_time': block.reference_time,
                'ntp_tests': block.ntp_tests,
                'authenticated': block.authenticated,
                'interleaved': block.interleaved,
                'tx_timestamping': block.tx_timestamping,
                'rx_timestamping': block.rx_timestamping,
            }
            for block in self.ntpdata
        ]
        selected_names = [src.name for src in self.sources if src.state == '*']
        selected_modes = sorted({row.mode for row in self.authdata if row.name in set(selected_names)})
        modes = sorted({row.mode for row in self.authdata})
        authenticated_measurements = sum(1 for block in self.ntpdata if block.authenticated is True)
        unauthenticated_measurements = sum(1 for block in self.ntpdata if block.authenticated is False)
        if authenticated_measurements or any(mode in {'NTS', 'SK'} for mode in modes):
            reported_packet_authentication = 'chrony_reported_authentication_present'
        elif auth_rows or ntpdata_blocks:
            reported_packet_authentication = 'chrony_reported_authentication_absent'
        else:
            reported_packet_authentication = 'not_observed'
        return {
            'authdata_rows_observed': len(auth_rows),
            'ntpdata_blocks_observed': len(ntpdata_blocks),
            'authdata_rows': auth_rows,
            'ntpdata_blocks': ntpdata_blocks,
            'modes_observed': modes,
            'selected_source_names': selected_names,
            'selected_source_auth_modes': selected_modes,
            'chrony_reported_authenticated_measurements': authenticated_measurements,
            'chrony_reported_unauthenticated_measurements': unauthenticated_measurements,
            'reported_packet_authentication': reported_packet_authentication,
            'verification_status': 'not_cryptographically_verified_by_timesync',
            'used_for_decision': False,
            'profile_strengthening': 'none',
            'note': 'chronyc authdata/ntpdata are retained as reported diagnostics only; TimeSync does not verify NTS, symmetric keys, TLS certificates, AEAD tags, cookies, or packet transcripts in this evaluator.',
        }

    def to_json(self) -> dict[str, Any]:
        selected = sum(1 for src in self.sources if src.state == '*')
        combined = sum(1 for src in self.sources if src.state == '+')
        selectable = sum(1 for src in self.sources if src.state in {'*', '+'})
        sourcestats_rows = [
            {
                'name': stat.name,
                'sample_points': stat.sample_points,
                'residual_runs': stat.residual_runs,
                'span_seconds': str(stat.span_seconds),
                'frequency_ppm': str(stat.frequency_ppm),
                'freq_skew_ppm': str(stat.freq_skew_ppm),
                'offset_seconds': str(stat.offset_seconds),
                'std_dev_seconds': str(stat.std_dev_seconds),
            }
            for stat in self.sourcestats
        ]
        obj = {
            'observation_type': 'chrony_tracking_snapshot_v1',
            'input_contract': self.input_contract,
            'collected_at': self.collected_at,
            'commands': {
                'tracking': self.chronyc_tracking_command,
                'sources': self.chronyc_sources_command if self.sources else None,
                'sourcestats': 'chronyc -n sourcestats' if self.sourcestats else None,
                'authdata': 'chronyc authdata -a' if self.authdata else None,
                'ntpdata': 'chronyc -n ntpdata' if self.ntpdata else None,
            },
            'tracking': {
                'reference_id': self.tracking.reference_id,
                'stratum': self.tracking.stratum,
                'ref_time_utc': self.tracking.ref_time_utc,
                'system_time_offset_seconds': str(self.tracking.system_time_offset_seconds),
                'skew_ppm': str(self.tracking.skew_ppm),
                'root_delay_seconds': str(self.tracking.root_delay_seconds),
                'root_dispersion_seconds': str(self.tracking.root_dispersion_seconds),
                'leap_status': self.tracking.leap_status,
                'last_offset_seconds': _decimal_or_none(self.tracking.last_offset_seconds),
                'rms_offset_seconds': _decimal_or_none(self.tracking.rms_offset_seconds),
                'frequency_ppm': _decimal_or_none(self.tracking.frequency_ppm),
                'residual_frequency_ppm': _decimal_or_none(self.tracking.residual_frequency_ppm),
                'update_interval_seconds': _decimal_or_none(self.tracking.update_interval_seconds),
            },
            'sources_summary': {
                'source_rows_observed': len(self.sources),
                'selected_sources': selected,
                'combined_sources': combined,
                'selectable_sources': selectable,
                'states': [{'state': src.state, 'name': src.name, 'mode': src.mode} for src in self.sources],
            },
            'sourcestats_summary': {
                'source_rows_observed': len(sourcestats_rows),
                'rows': sourcestats_rows,
                'max_freq_skew_ppm': _decimal_or_none(max((stat.freq_skew_ppm for stat in self.sourcestats), default=None)),
                'max_std_dev_seconds': _decimal_or_none(max((stat.std_dev_seconds for stat in self.sourcestats), default=None)),
                'used_for_decision': False,
                'note': 'chronyc sourcestats is captured and parsed as estimator diagnostics; P1 interval bounds still use tracking Skew/root fields.',
            },
            'authentication_summary': self.authentication_summary(),
        }
        if self.capture_context is not None:
            obj['capture_context'] = self.capture_context
        return obj


class ChronyAdapterError(ValueError):
    """Raised when a chrony capture cannot be parsed or safely evaluated."""


def _decimal_or_none(value: Decimal | None) -> str | None:
    return None if value is None else str(value)


def _read(path: Path | None) -> str:
    if path is None:
        return ''
    return path.read_text(encoding='utf-8')


def _parse_decimal(text: str, *, field: str) -> Decimal:
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise ChronyAdapterError(f'{field} is not a decimal value: {text!r}') from exc


def _parse_seconds(text: str, *, field: str) -> Decimal:
    match = re.search(r'(?P<value>[+-]?\d+(?:\.\d+)?)\s+seconds?\b', text.strip())
    if not match:
        raise ChronyAdapterError(f'{field} does not contain seconds: {text!r}')
    return _parse_decimal(match.group('value'), field=field)


def _parse_system_time_offset(text: str) -> Decimal:
    text = text.strip()
    match = re.search(r'(?P<value>[+-]?\d+(?:\.\d+)?)\s+seconds?\s+(?P<direction>fast|slow)\s+of\s+NTP\s+time', text, re.IGNORECASE)
    if match:
        magnitude = abs(_parse_decimal(match.group('value'), field='System time'))
        return magnitude if match.group('direction').lower() == 'fast' else -magnitude
    return _parse_seconds(text, field='System time')


def _parse_ppm(text: str, *, field: str, signed_direction: bool = False) -> Decimal:
    match = re.search(r'(?P<value>[+-]?\d+(?:\.\d+)?)\s+ppm\b(?:\s+(?P<direction>fast|slow))?', text.strip(), re.IGNORECASE)
    if not match:
        raise ChronyAdapterError(f'{field} does not contain a ppm value: {text!r}')
    value = _parse_decimal(match.group('value'), field=field)
    if signed_direction and match.group('direction'):
        magnitude = abs(value)
        return magnitude if match.group('direction').lower() == 'fast' else -magnitude
    return abs(value)


def _parse_chrony_ref_time(text: str) -> str:
    value = text.strip()
    try:
        parsed = datetime.strptime(value, '%a %b %d %H:%M:%S %Y').replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise ChronyAdapterError(f'Ref time (UTC) is not in expected chrony format: {text!r}') from exc
    return parsed.strftime('%Y-%m-%dT%H:%M:%SZ')


def parse_tracking(text: str) -> ChronyTracking:
    fields: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        fields[key.strip()] = value.strip()

    missing = sorted(TRACKING_REQUIRED_FIELDS - set(fields))
    if missing:
        raise ChronyAdapterError(f'chronyc tracking capture missing required field(s): {", ".join(missing)}')

    try:
        stratum = int(fields['Stratum'])
    except ValueError as exc:
        raise ChronyAdapterError(f'Stratum is not an integer: {fields["Stratum"]!r}') from exc

    return ChronyTracking(
        reference_id=fields['Reference ID'],
        stratum=stratum,
        ref_time_utc=_parse_chrony_ref_time(fields['Ref time (UTC)']),
        system_time_offset_seconds=_parse_system_time_offset(fields['System time']),
        skew_ppm=_parse_ppm(fields['Skew'], field='Skew'),
        root_delay_seconds=_parse_seconds(fields['Root delay'], field='Root delay'),
        root_dispersion_seconds=_parse_seconds(fields['Root dispersion'], field='Root dispersion'),
        leap_status=fields['Leap status'],
        last_offset_seconds=_optional_seconds(fields.get('Last offset'), 'Last offset'),
        rms_offset_seconds=_optional_seconds(fields.get('RMS offset'), 'RMS offset'),
        frequency_ppm=_optional_ppm(fields.get('Frequency'), 'Frequency', signed_direction=True),
        residual_frequency_ppm=_optional_ppm(fields.get('Residual freq'), 'Residual freq', signed_direction=True),
        update_interval_seconds=_optional_seconds(fields.get('Update interval'), 'Update interval'),
    )


def _optional_seconds(text: str | None, field: str) -> Decimal | None:
    return None if text is None else _parse_seconds(text, field=field)


def _optional_ppm(text: str | None, field: str, *, signed_direction: bool = False) -> Decimal | None:
    return None if text is None else _parse_ppm(text, field=field, signed_direction=signed_direction)


def _maybe_parse_seconds(text: str | None, *, field: str) -> Decimal | None:
    return None if text is None else _parse_seconds(text, field=field)


def parse_sources(text: str) -> tuple[ChronySource, ...]:
    sources: list[ChronySource] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or set(line) <= {'='}:
            continue
        if line.lower().startswith('ms ') or line.lower().startswith('name/ip'):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        marker = parts[0]
        if len(marker) < 2 or marker[0] not in {'^', '=', '#', '?'}:
            continue
        mode, state = marker[0], marker[1]
        name = parts[1]
        stratum = _maybe_int(parts[2]) if len(parts) > 2 else None
        poll = _maybe_int(parts[3]) if len(parts) > 3 else None
        reach = parts[4] if len(parts) > 4 else None
        last_rx = parts[5] if len(parts) > 5 else None
        sources.append(ChronySource(mode=mode, state=state, name=name, stratum=stratum, poll=poll, reach=reach, last_rx=last_rx, raw=line))
    return tuple(sources)


def _maybe_int(value: str) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None


_DURATION_UNITS = {
    None: Decimal('1'),
    '': Decimal('1'),
    'ns': Decimal('0.000000001'),
    'us': Decimal('0.000001'),
    'µs': Decimal('0.000001'),
    'ms': Decimal('0.001'),
    's': Decimal('1'),
    'm': Decimal('60'),
    'h': Decimal('3600'),
    'd': Decimal('86400'),
    'y': Decimal('31536000'),
}


def _parse_duration_token(token: str, *, field: str) -> Decimal:
    match = re.fullmatch(r'(?P<value>[+-]?\d+(?:\.\d+)?)(?P<unit>ns|us|µs|ms|s|m|h|d|y)?', token.strip())
    if not match:
        raise ChronyAdapterError(f'{field} does not contain a chrony duration token: {token!r}')
    unit = match.group('unit') or ''
    value = _parse_decimal(match.group('value'), field=field)
    return value * _DURATION_UNITS[unit]


def parse_sourcestats(text: str) -> tuple[ChronySourceStat, ...]:
    stats: list[ChronySourceStat] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or set(line) <= {'='}:
            continue
        lower = line.lower()
        if lower.startswith('name/ip') or 'freq skew' in lower or lower.startswith('.-') or lower.startswith('/') or lower.startswith('|'):
            continue
        parts = line.split()
        if len(parts) < 8:
            continue
        try:
            stats.append(ChronySourceStat(
                name=parts[0],
                sample_points=int(parts[1]),
                residual_runs=int(parts[2]),
                span_seconds=_parse_duration_token(parts[3], field='sourcestats Span'),
                frequency_ppm=_parse_decimal(parts[4], field='sourcestats Frequency'),
                freq_skew_ppm=abs(_parse_decimal(parts[5], field='sourcestats Freq Skew')),
                offset_seconds=_parse_duration_token(parts[6], field='sourcestats Offset'),
                std_dev_seconds=abs(_parse_duration_token(parts[7], field='sourcestats Std Dev')),
                raw=line,
            ))
        except (ValueError, ChronyAdapterError) as exc:
            raise ChronyAdapterError(f'cannot parse sourcestats row {line!r}: {exc}') from exc
    return tuple(stats)


def _maybe_int_text(value: str) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_authdata(text: str) -> tuple[ChronyAuthRow, ...]:
    rows: list[ChronyAuthRow] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or set(line) <= {'='}:
            continue
        lower = line.lower()
        if lower.startswith('name/ip') or lower.startswith('chronyc'):
            continue
        parts = line.split()
        if len(parts) < 10:
            continue
        try:
            rows.append(ChronyAuthRow(
                name=parts[0],
                mode=parts[1],
                key_id=_maybe_int_text(parts[2]),
                algorithm_type=_maybe_int_text(parts[3]),
                key_length_bits=_maybe_int_text(parts[4]),
                last_success=None if parts[5] == '-' else parts[5],
                attempts_since_success=_maybe_int_text(parts[6]),
                nts_nak_seen=_maybe_int_text(parts[7]),
                cookies=_maybe_int_text(parts[8]),
                cookie_length_bytes=_maybe_int_text(parts[9]),
                raw=line,
            ))
        except Exception as exc:  # noqa: BLE001
            raise ChronyAdapterError(f'cannot parse authdata row {line!r}: {exc}') from exc
    return tuple(rows)


def _parse_yes_no(value: str) -> bool | None:
    lowered = value.strip().lower()
    if lowered == 'yes':
        return True
    if lowered == 'no':
        return False
    return None


def _ntpdata_blocks(text: str) -> list[dict[str, str]]:
    blocks: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if current:
                blocks.append(current)
                current = {}
            continue
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        if key == 'Remote address' and current:
            blocks.append(current)
            current = {}
        current[key] = value
    if current:
        blocks.append(current)
    return blocks


def parse_ntpdata(text: str) -> tuple[ChronyNtpDataBlock, ...]:
    blocks: list[ChronyNtpDataBlock] = []
    for fields in _ntpdata_blocks(text):
        try:
            blocks.append(ChronyNtpDataBlock(
                remote_address=fields.get('Remote address'),
                leap_status=fields.get('Leap status'),
                stratum=_maybe_int_text(fields.get('Stratum', '')),
                root_delay_seconds=_maybe_parse_seconds(fields.get('Root delay'), field='ntpdata Root delay'),
                root_dispersion_seconds=_maybe_parse_seconds(fields.get('Root dispersion'), field='ntpdata Root dispersion'),
                reference_id=fields.get('Reference ID'),
                reference_time=fields.get('Reference time'),
                ntp_tests=fields.get('NTP tests'),
                authenticated=_parse_yes_no(fields.get('Authenticated', '')) if 'Authenticated' in fields else None,
                interleaved=fields.get('Interleaved'),
                tx_timestamping=fields.get('TX timestamping'),
                rx_timestamping=fields.get('RX timestamping'),
                raw_fields=fields,
            ))
        except ChronyAdapterError as exc:
            raise ChronyAdapterError(f'cannot parse ntpdata block for {fields.get("Remote address", "<unknown>")}: {exc}') from exc
    return tuple(blocks)


def build_observation(*, tracking_text: str, sources_text: str, collected_at: str, sourcestats_text: str = '', authdata_text: str = '', ntpdata_text: str = '', input_contract: str = 'chronyc-human-text-v1', capture_context: dict[str, Any] | None = None) -> ChronyObservation:
    _parse_instant_seconds(collected_at, label='collected_at')
    return ChronyObservation(
        collected_at=collected_at,
        tracking=parse_tracking(tracking_text),
        sources=parse_sources(sources_text),
        sourcestats=parse_sourcestats(sourcestats_text),
        authdata=parse_authdata(authdata_text),
        ntpdata=parse_ntpdata(ntpdata_text),
        input_contract=input_contract,
        capture_context=capture_context,
    )


def _parse_instant_seconds(value: str, *, label: str) -> Fraction:
    try:
        parsed = parse_dt(value)
    except Exception as exc:  # noqa: BLE001
        raise ChronyAdapterError(f'{label} must be RFC 3339 with explicit offset: {exc}') from exc
    return Fraction(parsed.epoch_second, 1) + parsed.fractional_second


def _ceil_fraction_to_ns(value: Fraction) -> int:
    return -((-value.numerator * NS_PER_SECOND) // value.denominator)


def _floor_fraction_to_ns(value: Fraction) -> int:
    return (value.numerator * NS_PER_SECOND) // value.denominator


def _format_epoch_ns(epoch_ns: int) -> str:
    seconds, nanos = divmod(epoch_ns, NS_PER_SECOND)
    dt = datetime.fromtimestamp(seconds, tz=timezone.utc)
    if nanos == 0:
        frac = ''
    else:
        frac = f'.{nanos:09d}'.rstrip('0')
    return dt.strftime('%Y-%m-%dT%H:%M:%S') + frac + 'Z'


def _fraction_to_decimal(value: Fraction) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def _milliseconds(value: Decimal) -> Decimal:
    return common_milliseconds(value)


def _decimal_seconds_to_fraction(value: Decimal) -> Fraction:
    return Fraction(value)


def load_profile_catalog(root: Path = ROOT) -> dict[str, Any]:
    with (root / 'profiles/profile-catalog.json').open('r', encoding='utf-8') as f:
        return json.load(f)


def find_profile(catalog: dict[str, Any], profile_id: str) -> dict[str, Any]:
    for profile in catalog.get('profiles', []):
        if profile.get('id') == profile_id:
            return profile
    raise ChronyAdapterError(f'profile not found in catalog: {profile_id}')


def profile_ref(profile: dict[str, Any]) -> dict[str, Any]:
    ref = {
        'authority': profile.get('authority'),
        'id': profile['id'],
        'version': profile.get('version', '1.0.0'),
    }
    digest = profile.get('normative_rules_digest')
    if isinstance(digest, dict):
        ref['digest'] = digest
    return ref


def source_posture(observation: ChronyObservation) -> str:
    tracking = observation.tracking
    if tracking.leap_status != 'Normal' or tracking.stratum <= 0:
        return 'unknown'
    selected = sum(1 for src in observation.sources if src.state == '*')
    combined = sum(1 for src in observation.sources if src.state == '+')
    if selected + combined >= 2:
        return 'multi_source_agreement'
    if selected >= 1 or tracking.reference_id not in {'00000000 ()', '00000000'}:
        return 'single_source'
    return 'unknown'


def chrony_bound_seconds(observation: ChronyObservation, *, evaluated_at: str) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    """Return base bound, age, growth, and total bound in seconds.

    The parser remains chrony-specific, but the conservative NTP-family bound
    arithmetic is shared with the ntpq adapter so equivalent observations cannot
    diverge silently by implementation.
    """
    tracking = observation.tracking
    bound = conservative_ntp_error_bound(
        system_time_offset_seconds=tracking.system_time_offset_seconds,
        root_delay_seconds=tracking.root_delay_seconds,
        root_dispersion_seconds=tracking.root_dispersion_seconds,
        rate_error_ppm=tracking.skew_ppm,
        collected_at=observation.collected_at,
        evaluated_at=evaluated_at,
        error_cls=ChronyAdapterError,
    )
    return bound.base_bound_seconds, bound.age_seconds, bound.holdover_growth_seconds, bound.total_bound_seconds


def interval_for_bound(effective_at: str, total_bound_seconds: Decimal) -> dict[str, str]:
    return common_interval_for_bound(effective_at, total_bound_seconds, error_cls=ChronyAdapterError)


def evaluate(observation: ChronyObservation, *, profile_id: str = SUPPORTED_PROFILE, evaluated_at: str, catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    if profile_id != SUPPORTED_PROFILE:
        raise ChronyAdapterError(f'chrony reference evaluator currently supports only {SUPPORTED_PROFILE}')
    catalog = catalog or load_profile_catalog()
    profile = find_profile(catalog, profile_id)
    base_bound, age, growth, total_bound = chrony_bound_seconds(observation, evaluated_at=evaluated_at)
    bound_ms = _milliseconds(total_bound)
    sp = source_posture(observation)
    auth_summary = observation.authentication_summary()
    auth_hook = _authentication_hook(auth_summary)
    tracking = observation.tracking
    leap_normal = tracking.leap_status == 'Normal'
    stratum_usable = 1 <= tracking.stratum <= 15

    policy = load_p1_policy(ROOT)
    decision = decide_p1_lane(
        policy,
        bound_ms=bound_ms,
        age_seconds=age,
        source_posture=sp,
        leap_normal=leap_normal,
        stratum_usable=stratum_usable,
    )
    conformance = decision['profile_conformance']
    applicability = decision['applicability']
    actionability = decision['actionability']
    policy_status = decision['policy_status']
    fallback_mapping = decision['fallback_mapping']
    regime = decision['regime']
    reason = decision['reason']
    max_staleness_ms = decision['max_staleness_ms']

    rev = _current_revision()
    interval = interval_for_bound(evaluated_at, total_bound)
    assessment_id = f'assess-{profile_id}-chrony-{_safe_id_time(evaluated_at)}'
    evaluation_summary: dict[str, Any] = {
        'matched_profile_catalog': True,
    }
    if fallback_mapping is not None:
        evaluation_summary['fallback_mapping'] = fallback_mapping
    if conformance == 'unsatisfied':
        evaluation_summary['missing_items'] = [decision['missing_item']]

    local_assessed_state = {
        'timestate': {
            'interval': interval,
            'timescale': 'UTC',
            'freshness': {
                'last_discipline': tracking.ref_time_utc,
                'max_staleness_ms': float(max_staleness_ms),
                'profile_expression': f'{rev} P1 chrony replay/capture policy',
            },
            'regime': regime,
            'source_posture': sp,
            'applicability': applicability,
        },
        'extension_hooks': {
            'traceability_posture': {
                'reference_anchor': 'utc_unqualified',
                'evidence_posture': 'claimed',
            },
            'sync_dimension': 'time',
            'time_error_bound': {
                'bound_ms': float(bound_ms),
                'confidence': 'conservative_chrony_tracking_bound_plus_skew_growth',
                'basis': 'abs(system_time_offset)+root_dispersion+0.5*max(root_delay,0) + skew_ppm*age',
            },
            'rate_error_bound': {
                'bound_ppb': float(tracking.skew_ppm * Decimal('1000')),
                'confidence': 'chrony_reported_skew',
                'basis': 'chronyc tracking Skew field',
            },
            'timescale_realization': {
                'scale': 'UTC',
                'realization': 'chrony-reported-UTC-unqualified',
                'leap_handling': 'standard_utc' if leap_normal else 'unknown',
                'tai_utc_offset_state': 'unknown',
                'evidence_posture': 'claimed',
                'note': 'chronyc tracking reports UTC but this adapter does not verify a named UTC realization or leap-smear policy',
            },
            'clock_continuity_posture': {
                'backward_step_policy': 'unknown',
                'smear_policy': 'none' if leap_normal else 'unknown',
                'monotonic_local_time': 'not_claimed',
                'evidence_posture': 'unknown',
                'note': 'chronyc tracking does not prove monotonic application-time behavior',
            },
            'source_diversity_posture': _source_diversity_hook(sp),
            'authentication_posture': auth_hook,
        },
        'profile_assessments': [
            {
                'assessment_time': evaluated_at,
                'assessed_profile': profile_ref(profile),
                'profile_conformance': conformance,
                'applicability': applicability,
                'profile_lifecycle_state': profile.get('lifecycle_state', 'unknown'),
                'policy_acceptance': {
                    'status': policy_status,
                    'checked_at': evaluated_at,
                    'policy_reference': policy_reference(policy, rev),
                    'reason': reason,
                    'actionability': actionability,
                },
                'evaluation_summary': evaluation_summary,
                'assessment_id': assessment_id,
                'note': 'Generated by tools/chrony_adapter.py from chronyc tracking/sources replay input.',
            }
        ],
    }

    explanation = {
        'explanation_type': 'timesync_chrony_reference_evaluation_v1',
        'profile_id': profile_id,
        'evaluated_at': evaluated_at,
        'collection_age_seconds': str(age),
        'chrony_clock_error_formula': 'abs(system_time_offset_seconds) + root_dispersion_seconds + 0.5 * max(root_delay_seconds, 0)',
        'base_bound_seconds': str(base_bound),
        'holdover_growth_seconds': str(growth),
        'total_interval_bound_seconds': str(total_bound),
        'total_interval_bound_ms': str(bound_ms),
        'system_time_offset_sign_used_to_shift_interval': False,
        'source_posture_rule_result': sp,
        'authentication_rule_result': auth_hook,
        'decision': {
            'profile_conformance': conformance,
            'applicability': applicability,
            'actionability': actionability,
            'reason': reason,
        },
        'unsupported_or_not_verified': [
            'named UTC realization traceability',
            'negative root delay interpreted conservatively as zero delay contribution',
            'chrony-reported NTS or symmetric-key authentication was not independently verified by TimeSync',
            'leap-smear detection',
            'application monotonic clock guarantee',
            'PTP or non-chrony NTP implementations',
        ],
        'input_observation': observation.to_json(),
    }
    return {
        'chrony_observation': observation.to_json(),
        'local_assessed_state': local_assessed_state,
        'explanation': explanation,
    }


def _source_diversity_hook(source_posture_value: str) -> dict[str, str]:
    if source_posture_value == 'multi_source_agreement':
        return {
            'dependency_class': 'multiple_sources_same_root',
            'common_mode_risk': 'possible_common_mode',
            'assessment_basis': 'local_measurement_summary',
            'evidence_posture': 'assessed',
            'export_detail': 'summary_only',
            'note': 'chronyc sources shows multiple usable rows, but independence of upstream roots is not proven',
        }
    if source_posture_value == 'single_source':
        return {
            'dependency_class': 'single_source',
            'common_mode_risk': 'not_assessed',
            'assessment_basis': 'local_measurement_summary',
            'evidence_posture': 'assessed',
            'export_detail': 'summary_only',
            'note': 'single selected source or only tracking reference observed',
        }
    return {
        'dependency_class': 'unknown',
        'common_mode_risk': 'unknown',
        'assessment_basis': 'unknown',
        'evidence_posture': 'unknown',
        'export_detail': 'summary_only',
        'note': 'source selection was unusable or unavailable',
    }


def _authentication_hook(summary: dict[str, Any]) -> dict[str, Any]:
    reported = summary.get('reported_packet_authentication', 'not_observed') if isinstance(summary, dict) else 'not_observed'
    if reported == 'chrony_reported_authentication_present':
        evidence_posture = 'reported_not_verified'
        note = 'chrony reports authenticated NTP evidence, but TimeSync did not verify NTS-KE, certificates, AEAD tags, cookies, symmetric keys, or packet transcripts; no TimeState or profile decision is strengthened.'
    elif reported == 'chrony_reported_authentication_absent':
        evidence_posture = 'reported_not_verified'
        note = 'chrony reports no authenticated NTP measurements for the retained ntpdata/authdata evidence; profile decisions remain based on conservative timing bounds only.'
    else:
        evidence_posture = 'not_observed'
        note = 'no chrony authdata/ntpdata diagnostics were supplied; authentication remains unsupported by this evaluator.'
    return {
        'packet_authentication': reported,
        'evidence_posture': evidence_posture,
        'verified_by_timesync': False,
        'used_for_decision': False,
        'profile_strengthening': 'none',
        'note': note,
    }


def _safe_id_time(value: str) -> str:
    return re.sub(r'[^0-9A-Za-z]', '', value.replace('Z', 'UTC'))


def run_live_chronyc(command: str) -> str:
    try:
        return subprocess.check_output(command.split(), text=True, stderr=subprocess.STDOUT, timeout=10)
    except FileNotFoundError as exc:
        raise ChronyAdapterError('chronyc is not installed or not on PATH') from exc
    except subprocess.CalledProcessError as exc:
        raise ChronyAdapterError(f'{command} failed with exit {exc.returncode}: {exc.output.strip()}') from exc
    except subprocess.TimeoutExpired as exc:
        raise ChronyAdapterError(f'{command} timed out') from exc


def run_case(case: dict[str, Any], *, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    cid = case.get('id', '<no-id>')
    try:
        if case.get('capture'):
            replay = extract_replay_inputs(load_capture(root / case['capture']))
            observation = build_observation(
                tracking_text=replay['tracking_text'],
                sources_text=replay['sources_text'],
                sourcestats_text=replay['sourcestats_text'],
                authdata_text=replay['authdata_text'],
                ntpdata_text=replay['ntpdata_text'],
                collected_at=case.get('collected_at') or replay['collected_at'],
                input_contract='chronyc-command-transcript-v1',
                capture_context=replay['capture_context'],
            )
        else:
            tracking_text = (root / case['tracking']).read_text(encoding='utf-8')
            sources_text = (root / case['sources']).read_text(encoding='utf-8') if case.get('sources') else ''
            sourcestats_text = (root / case['sourcestats']).read_text(encoding='utf-8') if case.get('sourcestats') else ''
            authdata_text = (root / case['authdata']).read_text(encoding='utf-8') if case.get('authdata') else ''
            ntpdata_text = (root / case['ntpdata']).read_text(encoding='utf-8') if case.get('ntpdata') else ''
            observation = build_observation(tracking_text=tracking_text, sources_text=sources_text, sourcestats_text=sourcestats_text, authdata_text=authdata_text, ntpdata_text=ntpdata_text, collected_at=case['collected_at'])
        bundle = evaluate(observation, profile_id=case.get('profile_id', SUPPORTED_PROFILE), evaluated_at=case['evaluated_at'])
    except Exception as exc:  # noqa: BLE001
        expected_error = case.get('expect_error_contains')
        if expected_error and expected_error.lower() in str(exc).lower():
            return []
        return [f'{cid}: unexpected adapter error: {exc}']

    if case.get('expect_error_contains'):
        return [f'{cid}: expected adapter error containing {case["expect_error_contains"]!r} but evaluation succeeded']

    expect = case.get('expect', {})
    state = bundle['local_assessed_state']
    ts = state['timestate']
    assessment = state['profile_assessments'][0]
    explanation = bundle['explanation']
    checks = {
        'profile_conformance': assessment.get('profile_conformance'),
        'applicability': assessment.get('applicability'),
        'source_posture': ts.get('source_posture'),
        'regime': ts.get('regime'),
        'actionability': assessment.get('policy_acceptance', {}).get('actionability'),
        'fallback_mapping': assessment.get('evaluation_summary', {}).get('fallback_mapping'),
        'sourcestats_rows': bundle['chrony_observation'].get('sourcestats_summary', {}).get('source_rows_observed'),
        'sourcestats_max_freq_skew_ppm': bundle['chrony_observation'].get('sourcestats_summary', {}).get('max_freq_skew_ppm'),
        'authdata_rows': bundle['chrony_observation'].get('authentication_summary', {}).get('authdata_rows_observed'),
        'ntpdata_blocks': bundle['chrony_observation'].get('authentication_summary', {}).get('ntpdata_blocks_observed'),
        'chrony_reported_authenticated_measurements': bundle['chrony_observation'].get('authentication_summary', {}).get('chrony_reported_authenticated_measurements'),
        'authentication_used_for_decision': bundle['chrony_observation'].get('authentication_summary', {}).get('used_for_decision'),
        'authentication_verification_status': bundle['chrony_observation'].get('authentication_summary', {}).get('verification_status'),
        'authentication_packet_authentication': state.get('extension_hooks', {}).get('authentication_posture', {}).get('packet_authentication'),
        'authentication_profile_strengthening': state.get('extension_hooks', {}).get('authentication_posture', {}).get('profile_strengthening'),
        'collection_age_seconds': explanation.get('collection_age_seconds'),
        'effective_collected_at': bundle['chrony_observation'].get('collected_at'),
        'capture_effective_collected_at_basis': bundle['chrony_observation'].get('capture_context', {}).get('effective_collected_at_basis'),
        'capture_collector_collected_at': bundle['chrony_observation'].get('capture_context', {}).get('collector_collected_at'),
    }
    for key, expected in expect.items():
        if key == 'max_bound_ms_lte':
            if Decimal(explanation['total_interval_bound_ms']) > Decimal(str(expected)):
                errors.append(f'{cid}: bound {explanation["total_interval_bound_ms"]} ms exceeds expected maximum {expected}')
            continue
        if key == 'interval_earliest':
            actual = ts.get('interval', {}).get('earliest')
            if actual != expected:
                errors.append(f'{cid}: expected interval earliest {expected!r}, got {actual!r}')
            continue
        if key == 'interval_latest':
            actual = ts.get('interval', {}).get('latest')
            if actual != expected:
                errors.append(f'{cid}: expected interval latest {expected!r}, got {actual!r}')
            continue
        if checks.get(key) != expected:
            errors.append(f'{cid}: expected {key}={expected!r}, got {checks.get(key)!r}')
    return errors


def self_test(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    errors.extend(chrony_capture_self_test(root))
    try:
        import yaml  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return [f'PyYAML unavailable for chrony adapter golden tests: {exc}']
    cases_path = root / 'tests/chrony-adapter-golden.yaml'
    try:
        cases = yaml.safe_load(cases_path.read_text(encoding='utf-8'))
    except Exception as exc:  # noqa: BLE001
        return [f'cannot load chrony golden tests: {exc}']
    if not isinstance(cases, list) or not cases:
        return ['chrony golden tests must be a non-empty list']
    for case in cases:
        if not isinstance(case, dict):
            errors.append('chrony golden test case is not an object')
            continue
        errors.extend(run_case(case, root=root))
    # Arithmetic sanity: a one-second replay age at 0.129 ppm must add exactly 129 ns.
    obs = build_observation(
        tracking_text=(root / 'examples/chrony/tracking-normal.txt').read_text(encoding='utf-8'),
        sources_text=(root / 'examples/chrony/sources-normal.txt').read_text(encoding='utf-8'),
        authdata_text=(root / 'examples/chrony/authdata-authenticated.txt').read_text(encoding='utf-8'),
        ntpdata_text=(root / 'examples/chrony/ntpdata-authenticated.txt').read_text(encoding='utf-8'),
        collected_at='2026-06-17T18:45:08.000000000Z',
    )
    capture = load_capture(root / 'tests/fixtures/chrony/capture-normal.json')
    replay = extract_replay_inputs(capture)
    cap_obs = build_observation(
        tracking_text=replay['tracking_text'],
        sources_text=replay['sources_text'],
        sourcestats_text=replay['sourcestats_text'],
        authdata_text=replay['authdata_text'],
        ntpdata_text=replay['ntpdata_text'],
        collected_at=replay['collected_at'],
        input_contract='chronyc-command-transcript-v1',
        capture_context=replay['capture_context'],
    )
    cap_bundle = evaluate(cap_obs, evaluated_at='2026-06-17T18:45:09.000000000Z')
    if cap_bundle['chrony_observation'].get('capture_context', {}).get('monotonic_duration_ns') != 13000:
        errors.append('chrony capture replay did not preserve monotonic capture context')
    if cap_bundle['chrony_observation'].get('capture_context', {}).get('effective_collected_at_basis') != 'tracking_command_start_wall_conservative':
        errors.append('chrony capture replay did not preserve effective collection basis')
    delayed = load_capture(root / 'tests/fixtures/chrony/capture-delayed-tracking.json')
    delayed_replay = extract_replay_inputs(delayed)
    if delayed_replay['collected_at'] != '2026-06-17T18:45:08.000000000Z':
        errors.append('delayed capture replay failed to use tracking command start as collected_at')
    if delayed_replay['capture_context'].get('collector_collected_at') != '2026-06-17T18:45:18.000000000Z':
        errors.append('delayed capture replay failed to retain collector final wall time')
    if cap_bundle['chrony_observation'].get('sourcestats_summary', {}).get('source_rows_observed') != 3:
        errors.append('chrony capture replay did not parse sourcestats rows')
    if cap_bundle['chrony_observation'].get('authentication_summary', {}).get('chrony_reported_authenticated_measurements') != 1:
        errors.append('chrony capture replay did not parse ntpdata authenticated measurement')
    _base, _age, growth, _total = chrony_bound_seconds(obs, evaluated_at='2026-06-17T18:45:09.000000000Z')
    if growth != Decimal('0.000000129'):
        errors.append(f'chrony skew growth arithmetic expected 0.000000129, got {growth}')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description='Parse chronyc tracking/sources text and evaluate a TimeSync P1 state.')
    parser.add_argument('--tracking', type=Path, help='Path to chronyc -n tracking text. Omit with --live.')
    parser.add_argument('--sources', type=Path, help='Optional path to chronyc -n sources text. Omit with --live to run sources too.')
    parser.add_argument('--sourcestats', type=Path, help='Optional path to chronyc -n sourcestats text. Omit with --live to run sourcestats too.')
    parser.add_argument('--authdata', type=Path, help='Optional path to chronyc authdata -a text. Omit with --live to run authdata too.')
    parser.add_argument('--ntpdata', type=Path, help='Optional path to chronyc -n ntpdata text. Omit with --live to run ntpdata too.')
    parser.add_argument('--capture', type=Path, help='Path to chrony_command_capture_v1 JSON produced by tools/chrony_capture.py.')
    parser.add_argument('--collected-at', help='RFC3339 collection time from the collecting host clock.')
    parser.add_argument('--evaluated-at', required=False, help='RFC3339 evaluation time. Defaults to collected-at.')
    parser.add_argument('--profile-id', default=SUPPORTED_PROFILE)
    parser.add_argument('--output', choices=['bundle', 'observation', 'state', 'explanation'], default='bundle')
    parser.add_argument('--live', action='store_true', help='Run chronyc -n tracking and chronyc -n sources locally.')
    parser.add_argument('--self-test', action='store_true', help='Run bundled golden tests.')
    args = parser.parse_args()

    if args.self_test:
        failures = self_test()
        if failures:
            for failure in failures:
                print(f'ERROR: {failure}')
            return 1
        print('TimeSync chrony adapter/evaluator self-test passed.')
        return 0

    try:
        input_contract = 'chronyc-human-text-v1'
        capture_context = None
        if args.capture is not None:
            if (
                args.live
                or args.tracking is not None
                or args.sources is not None
                or args.sourcestats is not None
                or args.authdata is not None
                or args.ntpdata is not None
            ):
                raise ChronyAdapterError('--capture cannot be combined with --live or raw chrony command inputs')
            replay = extract_replay_inputs(load_capture(args.capture))
            tracking_text = replay['tracking_text']
            sources_text = replay['sources_text']
            sourcestats_text = replay['sourcestats_text']
            authdata_text = replay['authdata_text']
            ntpdata_text = replay['ntpdata_text']
            collected_at = args.collected_at or replay['collected_at']
            input_contract = 'chronyc-command-transcript-v1'
            capture_context = replay['capture_context']
        elif args.live:
            from chrony_capture import live_capture  # local import keeps replay-only startup minimal
            replay = extract_replay_inputs(live_capture())
            tracking_text = replay['tracking_text']
            sources_text = replay['sources_text']
            sourcestats_text = replay['sourcestats_text']
            authdata_text = replay['authdata_text']
            ntpdata_text = replay['ntpdata_text']
            collected_at = args.collected_at or replay['collected_at']
            input_contract = 'chronyc-command-transcript-v1'
            capture_context = replay['capture_context']
        else:
            if args.tracking is None or args.collected_at is None:
                raise ChronyAdapterError('--tracking and --collected-at are required unless --live or --capture is used')
            tracking_text = _read(args.tracking)
            sources_text = _read(args.sources)
            sourcestats_text = _read(args.sourcestats)
            authdata_text = _read(args.authdata)
            ntpdata_text = _read(args.ntpdata)
            collected_at = args.collected_at
        evaluated_at = args.evaluated_at or collected_at
        observation = build_observation(
            tracking_text=tracking_text,
            sources_text=sources_text,
            sourcestats_text=sourcestats_text,
            authdata_text=authdata_text,
            ntpdata_text=ntpdata_text,
            collected_at=collected_at,
            input_contract=input_contract,
            capture_context=capture_context,
        )
        bundle = evaluate(observation, profile_id=args.profile_id, evaluated_at=evaluated_at)
    except Exception as exc:  # noqa: BLE001
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1

    if args.output == 'observation':
        obj = bundle['chrony_observation']
    elif args.output == 'state':
        obj = bundle['local_assessed_state']
    elif args.output == 'explanation':
        obj = bundle['explanation']
    else:
        obj = bundle
    print(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

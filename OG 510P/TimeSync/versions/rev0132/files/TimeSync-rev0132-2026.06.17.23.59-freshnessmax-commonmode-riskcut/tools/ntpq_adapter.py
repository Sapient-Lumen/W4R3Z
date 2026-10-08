#!/usr/bin/env python3
"""ntpq readvar/peers replay adapter and minimal P1 evaluator.

This adapter is deliberately narrower than the chrony adapter.  It accepts
retained `ntpq -c rv` system variables plus optional `ntpq -pn` peer billboard
text, emits an adapter-local observation, and maps that observation into the same
six-field TimeState/profile decision used by the P1 reference lane.

It is not an NTP packet verifier, not an NTS verifier, and not a generic NTP
interoperability claim.  Its purpose in rev0129 is to reduce chrony monoculture:
one non-chrony operational-state surface must be parsed, bounded, and evaluated
without promoting implementation-specific fields into the TimeState core.
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
from chrony_policy import decide_p1_lane, load_p1_policy, policy_reference
from ntp_bound import (
    conservative_ntp_error_bound,
    interval_for_bound as common_interval_for_bound,
    milliseconds as common_milliseconds,
)

ROOT = Path(__file__).resolve().parents[1]
NS_PER_SECOND = 1_000_000_000
SUPPORTED_PROFILE = 'P1-general-computing'

NTPQ_REQUIRED_FIELDS = {
    'leap',
    'stratum',
    'rootdelay',
    'rootdisp',
    'refid',
    'reftime',
    'offset',
    'clk_wander',
}


@dataclass(frozen=True)
class NtpqSystem:
    leap: str
    stratum: int
    root_delay_seconds: Decimal
    root_dispersion_seconds: Decimal
    reference_id: str
    ref_time_utc: str
    system_time_offset_seconds: Decimal
    clk_wander_ppm: Decimal
    sys_jitter_seconds: Decimal | None = None
    clk_jitter_seconds: Decimal | None = None
    frequency_ppm: Decimal | None = None
    version: str | None = None
    sync_status: str | None = None
    raw_fields: dict[str, str] | None = None


@dataclass(frozen=True)
class NtpqPeer:
    tally: str
    remote: str
    refid: str | None
    stratum: int | None
    peer_type: str | None
    when: str | None
    poll: int | None
    reach: str | None
    delay_seconds: Decimal | None
    offset_seconds: Decimal | None
    jitter_seconds: Decimal | None
    raw: str


@dataclass(frozen=True)
class NtpqObservation:
    collected_at: str
    system: NtpqSystem
    peers: tuple[NtpqPeer, ...]
    ntpq_readvar_command: str = 'ntpq -c rv'
    ntpq_peers_command: str = 'ntpq -pn'
    input_contract: str = 'ntpq-readvar-peers-text-v1'

    def to_json(self) -> dict[str, Any]:
        selected = sum(1 for peer in self.peers if peer.tally in {'*', 'o'})
        combined = sum(1 for peer in self.peers if peer.tally == '+')
        selectable = sum(1 for peer in self.peers if peer.tally in {'*', 'o', '+'})
        return {
            'observation_type': 'ntpq_system_snapshot_v1',
            'input_contract': self.input_contract,
            'collected_at': self.collected_at,
            'commands': {
                'readvar': self.ntpq_readvar_command,
                'peers': self.ntpq_peers_command if self.peers else None,
            },
            'system': {
                'leap': self.system.leap,
                'stratum': self.system.stratum,
                'reference_id': self.system.reference_id,
                'ref_time_utc': self.system.ref_time_utc,
                'system_time_offset_seconds': str(self.system.system_time_offset_seconds),
                'root_delay_seconds': str(self.system.root_delay_seconds),
                'root_dispersion_seconds': str(self.system.root_dispersion_seconds),
                'clk_wander_ppm': str(self.system.clk_wander_ppm),
                'sys_jitter_seconds': _decimal_or_none(self.system.sys_jitter_seconds),
                'clk_jitter_seconds': _decimal_or_none(self.system.clk_jitter_seconds),
                'frequency_ppm': _decimal_or_none(self.system.frequency_ppm),
                'version': self.system.version,
                'sync_status': self.system.sync_status,
            },
            'peers_summary': {
                'peer_rows_observed': len(self.peers),
                'selected_peers': selected,
                'combined_peers': combined,
                'selectable_peers': selectable,
                'states': [
                    {
                        'tally': peer.tally,
                        'remote': peer.remote,
                        'refid': peer.refid,
                        'stratum': peer.stratum,
                        'reach': peer.reach,
                    }
                    for peer in self.peers
                ],
                'used_for_decision': True,
                'note': 'ntpq peer tally is used only to assess local source_posture; independence of upstream roots is not proven.',
            },
            'authentication_summary': {
                'reported_packet_authentication': 'not_observed',
                'verification_status': 'not_cryptographically_verified_by_timesync',
                'used_for_decision': False,
                'profile_strengthening': 'none',
                'note': 'ntpq readvar/peers replay does not include packet-level authentication evidence; TimeSync does not verify NTS, symmetric keys, MACs, AEAD tags, cookies, certificates, or packet transcripts in this evaluator.',
            },
        }


class NtpqAdapterError(ValueError):
    """Raised when ntpq text cannot be parsed or safely evaluated."""


def _current_revision(root: Path = ROOT) -> str:
    try:
        receipt = json.loads((root / 'REVISION-RECEIPT.json').read_text(encoding='utf-8'))
        revision = receipt.get('revision')
    except Exception:  # noqa: BLE001
        revision = None
    return revision if isinstance(revision, str) else 'rev0000'


def _decimal_or_none(value: Decimal | None) -> str | None:
    return None if value is None else str(value)


def _parse_decimal(text: str, *, field: str) -> Decimal:
    try:
        return Decimal(str(text).strip())
    except InvalidOperation as exc:
        raise NtpqAdapterError(f'{field} is not a decimal value: {text!r}') from exc


def _parse_ms_to_seconds(text: str, *, field: str) -> Decimal:
    return _parse_decimal(text, field=field) / Decimal('1000')


def _optional_ms_to_seconds(fields: dict[str, str], key: str) -> Decimal | None:
    return _parse_ms_to_seconds(fields[key], field=key) if key in fields else None


def _optional_decimal(fields: dict[str, str], key: str) -> Decimal | None:
    return _parse_decimal(fields[key], field=key) if key in fields else None


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value


def _split_ntpq_assignments(text: str) -> list[str]:
    assignments: list[str] = []
    current: list[str] = []
    in_quote = False
    for ch in text.replace('\n', ' '):
        if ch == '"':
            in_quote = not in_quote
            current.append(ch)
            continue
        if ch == ',' and not in_quote:
            token = ''.join(current).strip()
            if token:
                assignments.append(token)
            current = []
        else:
            current.append(ch)
    token = ''.join(current).strip()
    if token:
        assignments.append(token)
    return assignments


def parse_readvar_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    statuses: list[str] = []
    last_key: str | None = None
    for token in _split_ntpq_assignments(text):
        if '=' in token:
            key, value = token.split('=', 1)
            last_key = key.strip()
            fields[last_key] = _unquote(value)
        else:
            # ntpq commonly renders reftime/clock as "hex  Day, Mon ..." without
            # quotes, so a naive comma split cuts the human timestamp in two.
            # Reattach such continuations to the immediately preceding timestamp
            # field while retaining ordinary bare status tokens separately.
            if last_key in {'reftime', 'clock'} and re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b', token):
                fields[last_key] = fields[last_key] + ', ' + token.strip()
            else:
                statuses.append(token.strip())
    if statuses:
        fields['_status_tokens'] = ','.join(statuses)
    return fields


def _parse_reftime(value: str) -> str:
    value = value.strip()
    if not value:
        raise NtpqAdapterError('reftime is empty')
    if 'T' in value:
        try:
            parsed = parse_dt(value)
        except Exception as exc:  # noqa: BLE001
            raise NtpqAdapterError(f'reftime RFC 3339 parse failed: {exc}') from exc
        epoch_ns = int((Fraction(parsed.epoch_second, 1) + parsed.fractional_second) * NS_PER_SECOND)
        return _format_epoch_ns(epoch_ns)
    # Common ntpq form: e7171b06.9f5ff604  Thu, Nov 10 2022  6:39:02.622
    match = re.search(
        r'(?P<dow>Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+'
        r'(?P<mon>[A-Za-z]{3})\s+(?P<day>\d{1,2})\s+(?P<year>\d{4})\s+'
        r'(?P<hour>\d{1,2}):(?P<minute>\d{2}):(?P<second>\d{2}(?:\.\d+)?)',
        value,
    )
    if not match:
        raise NtpqAdapterError(f'reftime is not a supported ntpq human timestamp: {value!r}')
    whole_second = match.group('second')
    sec_int, _, frac = whole_second.partition('.')
    dt = datetime.strptime(
        f"{match.group('mon')} {match.group('day')} {match.group('year')} {match.group('hour')} {match.group('minute')} {sec_int}",
        '%b %d %Y %H %M %S',
    ).replace(tzinfo=timezone.utc)
    nanos = 0 if not frac else int((frac + '0' * 9)[:9])
    return _format_epoch_ns(int(dt.timestamp()) * NS_PER_SECOND + nanos)


def parse_readvar(text: str) -> NtpqSystem:
    fields = parse_readvar_fields(text)
    missing = sorted(NTPQ_REQUIRED_FIELDS - set(fields))
    if missing:
        raise NtpqAdapterError(f'ntpq readvar capture missing required field(s): {", ".join(missing)}')
    try:
        stratum = int(fields['stratum'])
    except ValueError as exc:
        raise NtpqAdapterError(f'stratum is not an integer: {fields["stratum"]!r}') from exc
    return NtpqSystem(
        leap=fields['leap'],
        stratum=stratum,
        root_delay_seconds=_parse_ms_to_seconds(fields['rootdelay'], field='rootdelay'),
        root_dispersion_seconds=_parse_ms_to_seconds(fields['rootdisp'], field='rootdisp'),
        reference_id=fields['refid'],
        ref_time_utc=_parse_reftime(fields['reftime']),
        system_time_offset_seconds=_parse_ms_to_seconds(fields['offset'], field='offset'),
        clk_wander_ppm=abs(_parse_decimal(fields['clk_wander'], field='clk_wander')),
        sys_jitter_seconds=_optional_ms_to_seconds(fields, 'sys_jitter'),
        clk_jitter_seconds=_optional_ms_to_seconds(fields, 'clk_jitter'),
        frequency_ppm=_optional_decimal(fields, 'frequency'),
        version=fields.get('version'),
        sync_status=fields.get('_status_tokens'),
        raw_fields=fields,
    )


def _maybe_int(value: str) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None


def _maybe_peer_seconds_ms(value: str | None, field: str) -> Decimal | None:
    if value is None:
        return None
    try:
        return _parse_ms_to_seconds(value, field=field)
    except NtpqAdapterError:
        return None


def parse_peers(text: str) -> tuple[NtpqPeer, ...]:
    peers: list[NtpqPeer] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or set(stripped) <= {'='}:
            continue
        lower = stripped.lower()
        if lower.startswith('remote') or lower.startswith('ntpq'):
            continue
        first = stripped[0]
        tally = first if first in {'*', '+', '-', 'x', '#', '.', 'o'} else ' '
        body = stripped[1:].strip() if tally != ' ' else stripped
        parts = body.split()
        if len(parts) < 3:
            continue
        remote = parts[0]
        refid = parts[1] if len(parts) > 1 else None
        stratum = _maybe_int(parts[2]) if len(parts) > 2 else None
        peer_type = parts[3] if len(parts) > 3 else None
        when = parts[4] if len(parts) > 4 else None
        poll = _maybe_int(parts[5]) if len(parts) > 5 else None
        reach = parts[6] if len(parts) > 6 else None
        delay = _maybe_peer_seconds_ms(parts[7], 'peer delay') if len(parts) > 7 else None
        offset = _maybe_peer_seconds_ms(parts[8], 'peer offset') if len(parts) > 8 else None
        jitter = _maybe_peer_seconds_ms(parts[9], 'peer jitter') if len(parts) > 9 else None
        peers.append(NtpqPeer(tally=tally, remote=remote, refid=refid, stratum=stratum, peer_type=peer_type, when=when, poll=poll, reach=reach, delay_seconds=delay, offset_seconds=offset, jitter_seconds=jitter, raw=stripped))
    return tuple(peers)


def build_observation(*, readvar_text: str, peers_text: str = '', collected_at: str, input_contract: str = 'ntpq-readvar-peers-text-v1') -> NtpqObservation:
    _parse_instant_seconds(collected_at, label='collected_at')
    return NtpqObservation(
        collected_at=collected_at,
        system=parse_readvar(readvar_text),
        peers=parse_peers(peers_text),
        input_contract=input_contract,
    )


def _parse_instant_seconds(value: str, *, label: str) -> Fraction:
    try:
        parsed = parse_dt(value)
    except Exception as exc:  # noqa: BLE001
        raise NtpqAdapterError(f'{label} must be RFC 3339 with explicit offset: {exc}') from exc
    return Fraction(parsed.epoch_second, 1) + parsed.fractional_second


def _ceil_fraction_to_ns(value: Fraction) -> int:
    return -((-value.numerator * NS_PER_SECOND) // value.denominator)


def _floor_fraction_to_ns(value: Fraction) -> int:
    return (value.numerator * NS_PER_SECOND) // value.denominator


def _format_epoch_ns(epoch_ns: int) -> str:
    seconds, nanos = divmod(epoch_ns, NS_PER_SECOND)
    dt = datetime.fromtimestamp(seconds, tz=timezone.utc)
    frac = '' if nanos == 0 else f'.{nanos:09d}'.rstrip('0')
    return dt.strftime('%Y-%m-%dT%H:%M:%S') + frac + 'Z'


def _fraction_to_decimal(value: Fraction) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def _decimal_seconds_to_fraction(value: Decimal) -> Fraction:
    return Fraction(value)


def _milliseconds(value: Decimal) -> Decimal:
    return common_milliseconds(value)


def load_profile_catalog(root: Path = ROOT) -> dict[str, Any]:
    return json.loads((root / 'profiles/profile-catalog.json').read_text(encoding='utf-8'))


def find_profile(catalog: dict[str, Any], profile_id: str) -> dict[str, Any]:
    for profile in catalog.get('profiles', []):
        if profile.get('id') == profile_id:
            return profile
    raise NtpqAdapterError(f'profile not found in catalog: {profile_id}')


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


def leap_normal(system: NtpqSystem) -> bool:
    return system.leap in {'00', 'leap_none', 'none'}


def source_posture(observation: NtpqObservation) -> str:
    system = observation.system
    if not leap_normal(system) or system.stratum <= 0 or system.stratum >= 16:
        return 'unknown'
    selected = sum(1 for peer in observation.peers if peer.tally in {'*', 'o'})
    combined = sum(1 for peer in observation.peers if peer.tally == '+')
    if selected + combined >= 2:
        return 'multi_source_agreement'
    if selected >= 1 or system.reference_id.strip():
        return 'single_source'
    return 'unknown'


def ntpq_bound_seconds(observation: NtpqObservation, *, evaluated_at: str) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    system = observation.system
    bound = conservative_ntp_error_bound(
        system_time_offset_seconds=system.system_time_offset_seconds,
        root_delay_seconds=system.root_delay_seconds,
        root_dispersion_seconds=system.root_dispersion_seconds,
        rate_error_ppm=system.clk_wander_ppm,
        collected_at=observation.collected_at,
        evaluated_at=evaluated_at,
        error_cls=NtpqAdapterError,
    )
    return bound.base_bound_seconds, bound.age_seconds, bound.holdover_growth_seconds, bound.total_bound_seconds


def interval_for_bound(effective_at: str, total_bound_seconds: Decimal) -> dict[str, str]:
    return common_interval_for_bound(effective_at, total_bound_seconds, error_cls=NtpqAdapterError)

def _safe_id_time(value: str) -> str:
    return re.sub(r'[^0-9A-Za-z]', '', value.replace('Z', 'UTC'))


def _source_diversity_hook(source_posture_value: str) -> dict[str, str]:
    if source_posture_value == 'multi_source_agreement':
        return {
            'dependency_class': 'multiple_sources_same_root',
            'common_mode_risk': 'possible_common_mode',
            'assessment_basis': 'local_measurement_summary',
            'evidence_posture': 'assessed',
            'export_detail': 'summary_only',
            'note': 'ntpq peers shows multiple selectable rows, but independence of upstream roots is not proven',
        }
    if source_posture_value == 'single_source':
        return {
            'dependency_class': 'single_source',
            'common_mode_risk': 'not_assessed',
            'assessment_basis': 'local_measurement_summary',
            'evidence_posture': 'assessed',
            'export_detail': 'summary_only',
            'note': 'single selected peer or only system refid observed',
        }
    return {
        'dependency_class': 'unknown',
        'common_mode_risk': 'unknown',
        'assessment_basis': 'unknown',
        'evidence_posture': 'unknown',
        'export_detail': 'summary_only',
        'note': 'ntpq source selection was unusable or unavailable',
    }


def _authentication_hook() -> dict[str, Any]:
    return {
        'packet_authentication': 'not_observed',
        'evidence_posture': 'not_observed',
        'verified_by_timesync': False,
        'used_for_decision': False,
        'profile_strengthening': 'none',
        'note': 'ntpq readvar/peers replay does not include cryptographic packet evidence; no TimeState or profile decision is strengthened by authentication claims.',
    }


def evaluate(observation: NtpqObservation, *, profile_id: str = SUPPORTED_PROFILE, evaluated_at: str, catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    if profile_id != SUPPORTED_PROFILE:
        raise NtpqAdapterError(f'ntpq reference evaluator currently supports only {SUPPORTED_PROFILE}')
    catalog = catalog or load_profile_catalog()
    profile = find_profile(catalog, profile_id)
    base_bound, age, growth, total_bound = ntpq_bound_seconds(observation, evaluated_at=evaluated_at)
    bound_ms = _milliseconds(total_bound)
    sp = source_posture(observation)
    system = observation.system
    normal_leap = leap_normal(system)
    stratum_usable = 1 <= system.stratum <= 15

    policy = load_p1_policy(ROOT)
    decision = decide_p1_lane(
        policy,
        bound_ms=bound_ms,
        age_seconds=age,
        source_posture=sp,
        leap_normal=normal_leap,
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

    evaluation_summary: dict[str, Any] = {'matched_profile_catalog': True}
    if fallback_mapping is not None:
        evaluation_summary['fallback_mapping'] = fallback_mapping
    if conformance == 'unsatisfied':
        evaluation_summary['missing_items'] = [decision['missing_item']]

    state = {
        'timestate': {
            'interval': interval_for_bound(evaluated_at, total_bound),
            'timescale': 'UTC',
            'freshness': {
                'last_discipline': system.ref_time_utc,
                'max_staleness_ms': float(max_staleness_ms),
                'profile_expression': f'{rev} P1 ntpq readvar/peers policy',
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
                'confidence': 'conservative_ntpq_readvar_root_bound_plus_clk_wander_growth',
                'basis': 'abs(offset)+rootdisp+0.5*max(rootdelay,0) + clk_wander_ppm*age',
            },
            'rate_error_bound': {
                'bound_ppb': float(system.clk_wander_ppm * Decimal('1000')),
                'confidence': 'ntpq_reported_clk_wander',
                'basis': 'ntpq readvar clk_wander field',
            },
            'timescale_realization': {
                'scale': 'UTC',
                'realization': 'ntpq-reported-UTC-unqualified',
                'leap_handling': 'standard_utc' if normal_leap else 'unknown',
                'tai_utc_offset_state': 'unknown',
                'evidence_posture': 'claimed',
                'note': 'ntpq readvar reports an NTP system state but this adapter does not verify named UTC realization or leap-smear policy',
            },
            'clock_continuity_posture': {
                'backward_step_policy': 'unknown',
                'smear_policy': 'none' if normal_leap else 'unknown',
                'monotonic_local_time': 'not_claimed',
                'evidence_posture': 'unknown',
                'note': 'ntpq readvar does not prove monotonic application-time behavior',
            },
            'source_diversity_posture': _source_diversity_hook(sp),
            'authentication_posture': _authentication_hook(),
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
                    'policy_reference': policy_reference(policy, rev, adapter_family='ntpq'),
                    'reason': reason.replace('chrony', 'ntpq'),
                    'actionability': actionability,
                },
                'evaluation_summary': evaluation_summary,
                'assessment_id': f'assess-{profile_id}-ntpq-{_safe_id_time(evaluated_at)}',
                'note': 'Generated by tools/ntpq_adapter.py from ntpq readvar/peers replay input.',
            }
        ],
    }

    explanation = {
        'explanation_type': 'timesync_ntpq_reference_evaluation_v1',
        'profile_id': profile_id,
        'evaluated_at': evaluated_at,
        'collection_age_seconds': str(age),
        'ntpq_clock_error_formula': 'abs(offset_seconds) + root_dispersion_seconds + 0.5 * max(root_delay_seconds, 0)',
        'base_bound_seconds': str(base_bound),
        'holdover_growth_seconds': str(growth),
        'total_interval_bound_seconds': str(total_bound),
        'total_interval_bound_ms': str(bound_ms),
        'system_time_offset_sign_used_to_shift_interval': False,
        'source_posture_rule_result': sp,
        'authentication_rule_result': _authentication_hook(),
        'decision': {
            'profile_conformance': conformance,
            'applicability': applicability,
            'actionability': actionability,
            'reason': reason.replace('chrony', 'ntpq'),
        },
        'unsupported_or_not_verified': [
            'named UTC realization traceability',
            'negative root delay interpreted conservatively as zero delay contribution',
            'NTS or symmetric-key authentication was not independently verified by TimeSync',
            'leap-smear detection',
            'application monotonic clock guarantee',
            'PTP implementations',
        ],
        'input_observation': observation.to_json(),
    }
    return {'ntpq_observation': observation.to_json(), 'local_assessed_state': state, 'explanation': explanation}


def run_case(case: dict[str, Any], *, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    cid = case.get('id', '<no-id>')
    try:
        readvar_text = (root / case['readvar']).read_text(encoding='utf-8')
        peers_text = (root / case['peers']).read_text(encoding='utf-8') if case.get('peers') else ''
        observation = build_observation(readvar_text=readvar_text, peers_text=peers_text, collected_at=case['collected_at'])
        bundle = evaluate(observation, profile_id=case.get('profile_id', SUPPORTED_PROFILE), evaluated_at=case['evaluated_at'])
    except Exception as exc:  # noqa: BLE001
        expected_error = case.get('expect_error_contains')
        if expected_error and expected_error.lower() in str(exc).lower():
            return []
        return [f'{cid}: unexpected ntpq adapter error: {exc}']
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
        'peer_rows': bundle['ntpq_observation'].get('peers_summary', {}).get('peer_rows_observed'),
        'selected_peers': bundle['ntpq_observation'].get('peers_summary', {}).get('selected_peers'),
        'combined_peers': bundle['ntpq_observation'].get('peers_summary', {}).get('combined_peers'),
        'collection_age_seconds': explanation.get('collection_age_seconds'),
        'authentication_used_for_decision': bundle['ntpq_observation'].get('authentication_summary', {}).get('used_for_decision'),
        'authentication_verification_status': bundle['ntpq_observation'].get('authentication_summary', {}).get('verification_status'),
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
    try:
        import yaml  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return [f'PyYAML unavailable for ntpq adapter golden tests: {exc}']
    cases_path = root / 'tests/ntpq-adapter-golden.yaml'
    try:
        cases = yaml.safe_load(cases_path.read_text(encoding='utf-8'))
    except Exception as exc:  # noqa: BLE001
        return [f'cannot load ntpq golden tests: {exc}']
    if not isinstance(cases, list) or not cases:
        return ['ntpq golden tests must be a non-empty list']
    for case in cases:
        if not isinstance(case, dict):
            errors.append('ntpq golden test case is not an object')
            continue
        errors.extend(run_case(case, root=root))
    obs = build_observation(
        readvar_text=(root / 'examples/ntpq/rv-normal.txt').read_text(encoding='utf-8'),
        peers_text=(root / 'examples/ntpq/peers-normal.txt').read_text(encoding='utf-8'),
        collected_at='2026-06-17T18:45:08.000000000Z',
    )
    _base, _age, growth, _total = ntpq_bound_seconds(obs, evaluated_at='2026-06-17T18:45:09.000000000Z')
    if growth != Decimal('0.000000018'):
        errors.append(f'ntpq clk_wander growth arithmetic expected 0.000000018, got {growth}')
    if parse_readvar_fields('a=1, b="two, three", c=4').get('b') != 'two, three':
        errors.append('ntpq readvar parser failed quoted comma handling')
    return errors


def _read(path: Path | None) -> str:
    if path is None:
        return ''
    return path.read_text(encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Parse ntpq readvar/peers text and evaluate a TimeSync P1 state.')
    parser.add_argument('--readvar', type=Path, help='Path to ntpq -c rv text.')
    parser.add_argument('--peers', type=Path, help='Optional path to ntpq -pn peer billboard text.')
    parser.add_argument('--collected-at', help='RFC3339 collection time from the collecting host clock.')
    parser.add_argument('--evaluated-at', help='RFC3339 evaluation time. Defaults to collected-at.')
    parser.add_argument('--profile-id', default=SUPPORTED_PROFILE)
    parser.add_argument('--output', choices=['bundle', 'observation', 'state', 'explanation'], default='bundle')
    parser.add_argument('--self-test', action='store_true', help='Run bundled golden tests.')
    args = parser.parse_args()
    if args.self_test:
        failures = self_test()
        if failures:
            for failure in failures:
                print(f'ERROR: {failure}')
            return 1
        print('TimeSync ntpq adapter/evaluator self-test passed.')
        return 0
    try:
        if args.readvar is None or args.collected_at is None:
            raise NtpqAdapterError('--readvar and --collected-at are required')
        collected_at = args.collected_at
        evaluated_at = args.evaluated_at or collected_at
        observation = build_observation(
            readvar_text=_read(args.readvar),
            peers_text=_read(args.peers),
            collected_at=collected_at,
        )
        bundle = evaluate(observation, profile_id=args.profile_id, evaluated_at=evaluated_at)
    except Exception as exc:  # noqa: BLE001
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    if args.output == 'observation':
        obj = bundle['ntpq_observation']
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

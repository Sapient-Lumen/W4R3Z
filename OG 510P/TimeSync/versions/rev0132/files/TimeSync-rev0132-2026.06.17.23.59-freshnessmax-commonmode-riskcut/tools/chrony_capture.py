#!/usr/bin/env python3
"""Chrony command-capture envelope for TimeSync adapter input.

The rev0122 adapter proved that sanitized `chronyc tracking` and `sources` text
can become a conservative TimeState. This helper addresses the next risk: a live
capture needs a bracketed wall-clock sample, a monotonic collection anchor, the
actual command transcript, chrony version observation, and authentication
status diagnostics before the text is eligible for replay.

The envelope is deliberately adapter-local. It does not add TimeState fields and
it treats chrony-reported authentication as diagnostic text, not as
TimeSync cryptographic verification.  For replay, the effective collection instant is the conservative start of the tracking
command, not the collector's final wall timestamp.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time
from typing import Any, Iterable, Sequence

sys.dont_write_bytecode = True

from temporal_coherence import parse_dt

ROOT = Path(__file__).resolve().parents[1]


def _current_revision(root: Path = ROOT) -> str:
    try:
        receipt = json.loads((root / 'REVISION-RECEIPT.json').read_text(encoding='utf-8'))
        revision = receipt.get('revision')
    except Exception:  # noqa: BLE001
        revision = None
    return revision if isinstance(revision, str) else 'rev0000'


CAPTURE_TYPE = 'chrony_command_capture_v1'
DEFAULT_TIMEOUT_SECONDS = 10
ROLE_COMMANDS: dict[str, tuple[str, ...]] = {
    'chronyc_version': ('chronyc', '-v'),
    'tracking': ('chronyc', '-n', 'tracking'),
    'sources': ('chronyc', '-n', 'sources'),
    'sourcestats': ('chronyc', '-n', 'sourcestats'),
    'authdata': ('chronyc', 'authdata', '-a'),
    'ntpdata': ('chronyc', '-n', 'ntpdata'),
}


def utc_now_rfc3339() -> str:
    """Return an RFC 3339 UTC timestamp with microsecond precision."""
    return datetime.now(timezone.utc).isoformat(timespec='microseconds').replace('+00:00', 'Z')


def _command_text(args: Sequence[str]) -> str:
    return ' '.join(shlex.quote(part) for part in args)


def _run_command(role: str, args: Sequence[str], *, timeout_seconds: int) -> dict[str, Any]:
    start_wall = utc_now_rfc3339()
    start_mono = time.monotonic_ns()
    try:
        completed = subprocess.run(
            list(args),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            check=False,
        )
        end_wall = utc_now_rfc3339()
        end_mono = time.monotonic_ns()
        return {
            'role': role,
            'args': list(args),
            'command': _command_text(args),
            'start_wall': start_wall,
            'end_wall': end_wall,
            'start_monotonic_ns': start_mono,
            'end_monotonic_ns': end_mono,
            'duration_monotonic_ns': end_mono - start_mono,
            'timeout_seconds': timeout_seconds,
            'timed_out': False,
            'exit_code': completed.returncode,
            'stdout': completed.stdout,
            'stderr': completed.stderr,
        }
    except subprocess.TimeoutExpired as exc:
        end_wall = utc_now_rfc3339()
        end_mono = time.monotonic_ns()
        stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout.decode('utf-8', errors='replace') if exc.stdout else '')
        stderr = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr.decode('utf-8', errors='replace') if exc.stderr else '')
        return {
            'role': role,
            'args': list(args),
            'command': _command_text(args),
            'start_wall': start_wall,
            'end_wall': end_wall,
            'start_monotonic_ns': start_mono,
            'end_monotonic_ns': end_mono,
            'duration_monotonic_ns': end_mono - start_mono,
            'timeout_seconds': timeout_seconds,
            'timed_out': True,
            'exit_code': None,
            'stdout': stdout,
            'stderr': stderr,
        }
    except FileNotFoundError as exc:
        end_wall = utc_now_rfc3339()
        end_mono = time.monotonic_ns()
        return {
            'role': role,
            'args': list(args),
            'command': _command_text(args),
            'start_wall': start_wall,
            'end_wall': end_wall,
            'start_monotonic_ns': start_mono,
            'end_monotonic_ns': end_mono,
            'duration_monotonic_ns': end_mono - start_mono,
            'timeout_seconds': timeout_seconds,
            'timed_out': False,
            'exit_code': 127,
            'stdout': '',
            'stderr': str(exc),
        }


def live_capture(*, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> dict[str, Any]:
    """Run chronyc commands and return a transcript with wall/monotonic brackets."""
    outer_start_wall = utc_now_rfc3339()
    outer_start_mono = time.monotonic_ns()
    commands = [
        _run_command(role, args, timeout_seconds=timeout_seconds)
        for role, args in ROLE_COMMANDS.items()
    ]
    outer_end_wall = utc_now_rfc3339()
    outer_end_mono = time.monotonic_ns()
    capture = {
        'capture_type': CAPTURE_TYPE,
        'capture_version': _current_revision(),
        'input_contract': 'chronyc-command-transcript-v1',
        'redaction_policy': 'local hostnames/IPs may be redacted before retention; numeric timing fields must not be changed',
        'collector_clock': {
            'wall_start': outer_start_wall,
            'wall_end': outer_end_wall,
            'collected_at': outer_end_wall,
            'monotonic_start_ns': outer_start_mono,
            'monotonic_end_ns': outer_end_mono,
            'duration_monotonic_ns': outer_end_mono - outer_start_mono,
        },
        'commands': commands,
        'unsupported_or_not_verified': [
            'NTS or symmetric-key authentication verification',
            'chrony configuration audit',
            'named UTC realization traceability',
            'leap-smear policy discovery',
        ],
    }
    validate_capture(capture)
    return capture


def make_fixture_capture(*, tracking_text: str, sources_text: str, chronyc_version: str, collected_at: str, sourcestats_text: str = '', authdata_text: str = '', ntpdata_text: str = '') -> dict[str, Any]:
    """Create a deterministic capture envelope around replay text for tests/examples."""
    commands = [
        _fixture_command('chronyc_version', ROLE_COMMANDS['chronyc_version'], chronyc_version, 1000, 2000, collected_at),
        _fixture_command('tracking', ROLE_COMMANDS['tracking'], tracking_text, 3000, 4000, collected_at),
        _fixture_command('sources', ROLE_COMMANDS['sources'], sources_text, 5000, 6000, collected_at),
        _fixture_command('sourcestats', ROLE_COMMANDS['sourcestats'], sourcestats_text, 7000, 8000, collected_at),
        _fixture_command('authdata', ROLE_COMMANDS['authdata'], authdata_text, 9000, 10000, collected_at),
        _fixture_command('ntpdata', ROLE_COMMANDS['ntpdata'], ntpdata_text, 11000, 12000, collected_at),
    ]
    capture = {
        'capture_type': CAPTURE_TYPE,
        'capture_version': _current_revision(),
        'input_contract': 'chronyc-command-transcript-v1',
        'redaction_policy': 'deterministic replay fixture; command stdout is sanitized input text',
        'collector_clock': {
            'wall_start': collected_at,
            'wall_end': collected_at,
            'collected_at': collected_at,
            'monotonic_start_ns': 0,
            'monotonic_end_ns': 13000,
            'duration_monotonic_ns': 13000,
        },
        'commands': commands,
        'unsupported_or_not_verified': [
            'NTS or symmetric-key authentication verification',
            'chrony configuration audit',
            'named UTC realization traceability',
            'leap-smear policy discovery',
        ],
    }
    validate_capture(capture)
    return capture


def _fixture_command(role: str, args: Sequence[str], stdout: str, start_ns: int, end_ns: int, wall: str) -> dict[str, Any]:
    return {
        'role': role,
        'args': list(args),
        'command': _command_text(args),
        'start_wall': wall,
        'end_wall': wall,
        'start_monotonic_ns': start_ns,
        'end_monotonic_ns': end_ns,
        'duration_monotonic_ns': end_ns - start_ns,
        'timeout_seconds': DEFAULT_TIMEOUT_SECONDS,
        'timed_out': False,
        'exit_code': 0,
        'stdout': stdout,
        'stderr': '',
    }



def _command_with_times(role: str, args: Sequence[str], stdout: str, start_wall: str, end_wall: str, start_ns: int, end_ns: int) -> dict[str, Any]:
    return {
        'role': role,
        'args': list(args),
        'command': _command_text(args),
        'start_wall': start_wall,
        'end_wall': end_wall,
        'start_monotonic_ns': start_ns,
        'end_monotonic_ns': end_ns,
        'duration_monotonic_ns': end_ns - start_ns,
        'timeout_seconds': DEFAULT_TIMEOUT_SECONDS,
        'timed_out': False,
        'exit_code': 0,
        'stdout': stdout,
        'stderr': '',
    }


def _delayed_tracking_fixture_capture(*, tracking_text: str, sources_text: str, sourcestats_text: str, authdata_text: str, ntpdata_text: str) -> dict[str, Any]:
    """Fixture where post-tracking commands finish later than the tracking sample."""
    capture = {
        'capture_type': CAPTURE_TYPE,
        'capture_version': _current_revision(),
        'input_contract': 'chronyc-command-transcript-v1',
        'redaction_policy': 'deterministic delayed replay fixture; command stdout is sanitized input text',
        'collector_clock': {
            'wall_start': '2026-06-17T18:45:07.500000000Z',
            'wall_end': '2026-06-17T18:45:18.000000000Z',
            'collected_at': '2026-06-17T18:45:18.000000000Z',
            'monotonic_start_ns': 0,
            'monotonic_end_ns': 10500000000,
            'duration_monotonic_ns': 10500000000,
        },
        'commands': [
            _command_with_times('chronyc_version', ROLE_COMMANDS['chronyc_version'], 'chronyc (chrony) version 4.x delayed-fixture\n', '2026-06-17T18:45:07.600000000Z', '2026-06-17T18:45:07.700000000Z', 100000000, 200000000),
            _command_with_times('tracking', ROLE_COMMANDS['tracking'], tracking_text, '2026-06-17T18:45:08.000000000Z', '2026-06-17T18:45:09.000000000Z', 500000000, 1500000000),
            _command_with_times('sources', ROLE_COMMANDS['sources'], sources_text, '2026-06-17T18:45:13.000000000Z', '2026-06-17T18:45:14.000000000Z', 5500000000, 6500000000),
            _command_with_times('sourcestats', ROLE_COMMANDS['sourcestats'], sourcestats_text, '2026-06-17T18:45:14.500000000Z', '2026-06-17T18:45:15.000000000Z', 7000000000, 7500000000),
            _command_with_times('authdata', ROLE_COMMANDS['authdata'], authdata_text, '2026-06-17T18:45:15.500000000Z', '2026-06-17T18:45:16.000000000Z', 8000000000, 8500000000),
            _command_with_times('ntpdata', ROLE_COMMANDS['ntpdata'], ntpdata_text, '2026-06-17T18:45:17.000000000Z', '2026-06-17T18:45:18.000000000Z', 9500000000, 10500000000),
        ],
        'unsupported_or_not_verified': [
            'NTS or symmetric-key authentication verification',
            'chrony configuration audit',
            'named UTC realization traceability',
            'leap-smear policy discovery',
        ],
    }
    validate_capture(capture)
    return capture

def validate_capture(capture: Any) -> list[str]:
    """Validate envelope shape and collection chronology.

    Raises ValueError on failure, but also returns an empty list on success so it
    is easy to compose with existing TimeSync self-tests.
    """
    errors: list[str] = []
    if not isinstance(capture, dict):
        raise ValueError('capture must be an object')
    if capture.get('capture_type') != CAPTURE_TYPE:
        errors.append(f'capture_type must be {CAPTURE_TYPE}')
    if capture.get('input_contract') != 'chronyc-command-transcript-v1':
        errors.append('input_contract must be chronyc-command-transcript-v1')
    clock = capture.get('collector_clock')
    if not isinstance(clock, dict):
        errors.append('collector_clock must be an object')
        clock = {}
    _check_instant(clock.get('wall_start'), 'collector_clock.wall_start', errors)
    _check_instant(clock.get('wall_end'), 'collector_clock.wall_end', errors)
    _check_instant(clock.get('collected_at'), 'collector_clock.collected_at', errors)
    _check_time_order(clock.get('wall_start'), clock.get('wall_end'), 'collector_clock.wall_start', 'collector_clock.wall_end', errors, allow_equal=True)
    _check_time_order(clock.get('wall_start'), clock.get('collected_at'), 'collector_clock.wall_start', 'collector_clock.collected_at', errors, allow_equal=True)
    _check_time_order(clock.get('collected_at'), clock.get('wall_end'), 'collector_clock.collected_at', 'collector_clock.wall_end', errors, allow_equal=True)
    _check_monotonic_pair(clock, 'collector_clock', errors)

    commands = capture.get('commands')
    if not isinstance(commands, list) or not commands:
        errors.append('commands must be a non-empty list')
        commands = []
    roles_seen: set[str] = set()
    for index, command in enumerate(commands, start=1):
        label = f'commands[{index}]'
        if not isinstance(command, dict):
            errors.append(f'{label} must be an object')
            continue
        role = command.get('role')
        if not isinstance(role, str) or role not in ROLE_COMMANDS:
            errors.append(f'{label}.role must be one of {sorted(ROLE_COMMANDS)}')
        elif role in roles_seen:
            errors.append(f'duplicate chrony command role: {role}')
        else:
            roles_seen.add(role)
        args = command.get('args')
        if role in ROLE_COMMANDS and args != list(ROLE_COMMANDS[role]):
            errors.append(f'{label}.args must be {list(ROLE_COMMANDS[role])!r}')
        _check_instant(command.get('start_wall'), f'{label}.start_wall', errors)
        _check_instant(command.get('end_wall'), f'{label}.end_wall', errors)
        _check_time_order(command.get('start_wall'), command.get('end_wall'), f'{label}.start_wall', f'{label}.end_wall', errors, allow_equal=True)
        _check_time_order(clock.get('wall_start'), command.get('start_wall'), 'collector_clock.wall_start', f'{label}.start_wall', errors, allow_equal=True)
        _check_time_order(command.get('end_wall'), clock.get('wall_end'), f'{label}.end_wall', 'collector_clock.wall_end', errors, allow_equal=True)
        _check_monotonic_pair(command, label, errors)
        _check_command_inside_capture(clock, command, label, errors)
        if command.get('timed_out') is not True and command.get('timed_out') is not False:
            errors.append(f'{label}.timed_out must be a boolean')
        exit_code = command.get('exit_code')
        if exit_code is not None and (isinstance(exit_code, bool) or not isinstance(exit_code, int)):
            errors.append(f'{label}.exit_code must be integer or null')
        if not isinstance(command.get('stdout'), str):
            errors.append(f'{label}.stdout must be a string')
        if not isinstance(command.get('stderr'), str):
            errors.append(f'{label}.stderr must be a string')

    for role in ROLE_COMMANDS:
        if role not in roles_seen:
            errors.append(f'capture missing required command role: {role}')

    if errors:
        raise ValueError('; '.join(errors))
    return []


def _check_instant(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str):
        errors.append(f'{label} must be an RFC 3339 string')
        return
    try:
        parse_dt(value)
    except Exception as exc:  # noqa: BLE001
        errors.append(f'{label} is not valid RFC 3339: {exc}')


def _check_time_order(start: Any, end: Any, start_label: str, end_label: str, errors: list[str], *, allow_equal: bool) -> None:
    if not isinstance(start, str) or not isinstance(end, str):
        return
    try:
        start_dt = parse_dt(start)
        end_dt = parse_dt(end)
    except Exception:  # noqa: BLE001
        return
    if start_dt > end_dt or (not allow_equal and start_dt == end_dt):
        relation = '<=' if allow_equal else '<'
        errors.append(f'{start_label} must be {relation} {end_label}')


def _check_monotonic_pair(obj: dict[str, Any], label: str, errors: list[str]) -> None:
    start = obj.get('monotonic_start_ns') if 'monotonic_start_ns' in obj else obj.get('start_monotonic_ns')
    end = obj.get('monotonic_end_ns') if 'monotonic_end_ns' in obj else obj.get('end_monotonic_ns')
    duration = obj.get('duration_monotonic_ns')
    if isinstance(start, bool) or not isinstance(start, int):
        errors.append(f'{label} monotonic start must be an integer nanosecond counter')
        return
    if isinstance(end, bool) or not isinstance(end, int):
        errors.append(f'{label} monotonic end must be an integer nanosecond counter')
        return
    if end < start:
        errors.append(f'{label} monotonic end cannot be before monotonic start')
    if isinstance(duration, bool) or not isinstance(duration, int):
        errors.append(f'{label}.duration_monotonic_ns must be an integer')
    elif duration != end - start:
        errors.append(f'{label}.duration_monotonic_ns must equal monotonic_end_ns - monotonic_start_ns')



def _check_command_inside_capture(clock: dict[str, Any], command: dict[str, Any], label: str, errors: list[str]) -> None:
    outer_start = clock.get('monotonic_start_ns')
    outer_end = clock.get('monotonic_end_ns')
    start = command.get('start_monotonic_ns')
    end = command.get('end_monotonic_ns')
    if not all(isinstance(value, int) and not isinstance(value, bool) for value in (outer_start, outer_end, start, end)):
        return
    if start < outer_start or end > outer_end:
        errors.append(f'{label} monotonic interval must fall inside collector_clock monotonic interval')

def command_by_role(capture: dict[str, Any], role: str) -> dict[str, Any]:
    validate_capture(capture)
    for command in capture['commands']:
        if command.get('role') == role:
            return command
    raise ValueError(f'capture missing required command role: {role}')


def successful_stdout(capture: dict[str, Any], role: str) -> str:
    command = command_by_role(capture, role)
    if command.get('timed_out'):
        raise ValueError(f'chrony capture command {role} timed out')
    if command.get('exit_code') != 0:
        stderr = command.get('stderr', '').strip()
        detail = f': {stderr}' if stderr else ''
        raise ValueError(f'chrony capture command {role} exited {command.get("exit_code")}{detail}')
    return command.get('stdout', '')


def effective_tracking_collected_at(capture: dict[str, Any]) -> str:
    """Return the conservative observation instant for replayed tracking data.

    The evaluated TimeState interval grows with age.  `chronyc tracking` is the
    command that supplies the offset/dispersion/skew bound, so the safe replay
    anchor is the start of that command.  Using the collector's final timestamp
    would make captures look younger whenever later commands, such as sources or
    sourcestats, run after tracking.
    """
    validate_capture(capture)
    tracking_command = command_by_role(capture, 'tracking')
    return tracking_command['start_wall']


def extract_replay_inputs(capture: dict[str, Any]) -> dict[str, Any]:
    """Return the replay text and conservative collection instant consumed by chrony_adapter."""
    validate_capture(capture)
    return {
        'tracking_text': successful_stdout(capture, 'tracking'),
        'sources_text': successful_stdout(capture, 'sources'),
        'sourcestats_text': successful_stdout(capture, 'sourcestats'),
        'authdata_text': successful_stdout(capture, 'authdata'),
        'ntpdata_text': successful_stdout(capture, 'ntpdata'),
        'collected_at': effective_tracking_collected_at(capture),
        'capture_context': capture_context_summary(capture),
    }


def capture_context_summary(capture: dict[str, Any]) -> dict[str, Any]:
    validate_capture(capture)
    version_command = command_by_role(capture, 'chronyc_version')
    tracking_command = command_by_role(capture, 'tracking')
    clock = capture['collector_clock']
    effective = effective_tracking_collected_at(capture)
    return {
        'input_contract': capture.get('input_contract'),
        'chronyc_version_stdout': version_command.get('stdout', '').strip(),
        'collector_wall_start': clock['wall_start'],
        'collector_wall_end': clock['wall_end'],
        'collector_collected_at': clock['collected_at'],
        'collected_at': effective,
        'effective_collected_at': effective,
        'effective_collected_at_basis': 'tracking_command_start_wall_conservative',
        'tracking_command_start_wall': tracking_command['start_wall'],
        'tracking_command_end_wall': tracking_command['end_wall'],
        'tracking_command_duration_monotonic_ns': tracking_command['duration_monotonic_ns'],
        'monotonic_duration_ns': clock['duration_monotonic_ns'],
        'command_roles': [command['role'] for command in capture['commands']],
        'unsupported_or_not_verified': capture.get('unsupported_or_not_verified', []),
    }


def load_capture(path: Path) -> dict[str, Any]:
    capture = json.loads(path.read_text(encoding='utf-8'))
    validate_capture(capture)
    return capture


def self_test(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        capture = make_fixture_capture(
            tracking_text=(root / 'examples/chrony/tracking-normal.txt').read_text(encoding='utf-8'),
            sources_text=(root / 'examples/chrony/sources-normal.txt').read_text(encoding='utf-8'),
            sourcestats_text=(root / 'examples/chrony/sourcestats-normal.txt').read_text(encoding='utf-8'),
            authdata_text=(root / 'examples/chrony/authdata-authenticated.txt').read_text(encoding='utf-8'),
            ntpdata_text=(root / 'examples/chrony/ntpdata-authenticated.txt').read_text(encoding='utf-8'),
            chronyc_version='chronyc (chrony) version 4.x fixture\n',
            collected_at='2026-06-17T18:45:08.000000000Z',
        )
        extracted = extract_replay_inputs(capture)
        if 'Root delay' not in extracted['tracking_text']:
            errors.append('capture self-test failed to extract tracking stdout')
        if 'Freq Skew' not in extracted['sourcestats_text']:
            errors.append('capture self-test failed to extract sourcestats stdout')
        if 'NTS' not in extracted['authdata_text']:
            errors.append('capture self-test failed to extract authdata stdout')
        if 'Authenticated' not in extracted['ntpdata_text']:
            errors.append('capture self-test failed to extract ntpdata stdout')
        delayed = _delayed_tracking_fixture_capture(
            tracking_text=(root / 'examples/chrony/tracking-normal.txt').read_text(encoding='utf-8'),
            sources_text=(root / 'examples/chrony/sources-normal.txt').read_text(encoding='utf-8'),
            sourcestats_text=(root / 'examples/chrony/sourcestats-normal.txt').read_text(encoding='utf-8'),
            authdata_text=(root / 'examples/chrony/authdata-authenticated.txt').read_text(encoding='utf-8'),
            ntpdata_text=(root / 'examples/chrony/ntpdata-authenticated.txt').read_text(encoding='utf-8'),
        )
        delayed_replay = extract_replay_inputs(delayed)
        if delayed_replay['collected_at'] != '2026-06-17T18:45:08.000000000Z':
            errors.append('capture self-test did not use tracking command start as effective collected_at')
        if delayed_replay['capture_context'].get('collector_collected_at') != '2026-06-17T18:45:18.000000000Z':
            errors.append('capture self-test lost collector final timestamp in context')
        if delayed_replay['capture_context'].get('effective_collected_at_basis') != 'tracking_command_start_wall_conservative':
            errors.append('capture self-test missing effective collection basis')
        tampered = json.loads(json.dumps(capture))
        tampered['commands'][1]['end_monotonic_ns'] = tampered['commands'][1]['start_monotonic_ns'] - 1
        try:
            validate_capture(tampered)
        except ValueError as exc:
            if 'monotonic end cannot be before monotonic start' not in str(exc):
                errors.append(f'capture self-test rejected tampering with unexpected error: {exc}')
        else:
            errors.append('capture self-test accepted inverted monotonic command interval')
        outside = json.loads(json.dumps(capture))
        outside['commands'][1]['end_monotonic_ns'] = outside['collector_clock']['monotonic_end_ns'] + 1
        outside['commands'][1]['duration_monotonic_ns'] = outside['commands'][1]['end_monotonic_ns'] - outside['commands'][1]['start_monotonic_ns']
        try:
            validate_capture(outside)
        except ValueError as exc:
            if 'must fall inside collector_clock' not in str(exc):
                errors.append(f'capture self-test rejected outside command with unexpected error: {exc}')
        else:
            errors.append('capture self-test accepted command outside collector monotonic interval')
        failed = json.loads(json.dumps(capture))
        failed['commands'][1]['exit_code'] = 1
        failed['commands'][1]['stderr'] = 'not synchronised'
        try:
            extract_replay_inputs(failed)
        except ValueError as exc:
            if 'exited 1' not in str(exc):
                errors.append(f'capture self-test rejected failed command with unexpected error: {exc}')
        else:
            errors.append('capture self-test accepted failed tracking command for replay')
        errors.extend(_fake_live_capture_self_test(root))
    except Exception as exc:  # noqa: BLE001
        errors.append(f'capture self-test crashed: {exc}')
    return errors



def _fake_live_capture_self_test(root: Path) -> list[str]:
    """Exercise the real subprocess-based --live capture path with a fake chronyc.

    The cloud container usually has no chronyd/chronyc.  This test is still
    valuable because it proves live_capture() actually runs commands, records
    brackets, validates roles, and can be replayed without relying on hand-built
    fixture envelopes.
    """
    errors: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        fake = Path(tmp) / 'chronyc'
        script = """#!/usr/bin/env python3
from pathlib import Path
import sys
root = Path({root_expr})
args = sys.argv[1:]
if args == ['-v']:
    print('chronyc (chrony) version 4.x fake-live-harness')
elif args == ['-n', 'tracking']:
    print((root / 'examples/chrony/tracking-normal.txt').read_text(encoding='utf-8'), end='')
elif args == ['-n', 'sources']:
    print((root / 'examples/chrony/sources-normal.txt').read_text(encoding='utf-8'), end='')
elif args == ['-n', 'sourcestats']:
    print((root / 'examples/chrony/sourcestats-normal.txt').read_text(encoding='utf-8'), end='')
elif args == ['authdata', '-a']:
    print((root / 'examples/chrony/authdata-authenticated.txt').read_text(encoding='utf-8'), end='')
elif args == ['-n', 'ntpdata']:
    print((root / 'examples/chrony/ntpdata-authenticated.txt').read_text(encoding='utf-8'), end='')
else:
    print('unexpected fake chronyc args: ' + ' '.join(args), file=sys.stderr)
    sys.exit(2)
""".format(root_expr=repr(str(root)))
        fake.write_text(script, encoding='utf-8')
        fake.chmod(0o755)
        old_path = os.environ.get('PATH', '')
        os.environ['PATH'] = str(Path(tmp)) + os.pathsep + old_path
        try:
            captured = live_capture(timeout_seconds=5)
            replay = extract_replay_inputs(captured)
            if captured['commands'][0]['role'] != 'chronyc_version':
                errors.append('fake live capture did not preserve chronyc_version as first role')
            if 'Root dispersion' not in replay['tracking_text']:
                errors.append('fake live capture did not replay tracking stdout')
            if 'Freq Skew' not in replay['sourcestats_text']:
                errors.append('fake live capture did not replay sourcestats stdout')
            if 'NTS' not in replay['authdata_text']:
                errors.append('fake live capture did not replay authdata stdout')
            if 'Authenticated' not in replay['ntpdata_text']:
                errors.append('fake live capture did not replay ntpdata stdout')
            if replay['capture_context']['command_roles'] != list(ROLE_COMMANDS):
                errors.append('fake live capture command_roles do not match required role order')
        except Exception as exc:  # noqa: BLE001
            errors.append(f'fake live capture self-test crashed: {exc}')
        finally:
            os.environ['PATH'] = old_path
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(description='Capture or validate chronyc command transcripts for TimeSync.')
    parser.add_argument('--output', type=Path, help='Write a live capture JSON file. Defaults to stdout.')
    parser.add_argument('--timeout-seconds', type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument('--validate', type=Path, help='Validate an existing capture JSON file.')
    parser.add_argument('--extract', type=Path, help='Validate and print replay inputs from an existing capture JSON file.')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()

    try:
        if args.self_test:
            failures = self_test()
            if failures:
                for failure in failures:
                    print(f'ERROR: {failure}')
                return 1
            print('TimeSync chrony capture self-test passed.')
            return 0
        if args.validate is not None:
            load_capture(args.validate)
            print(f'{args.validate}: valid chrony capture envelope')
            return 0
        if args.extract is not None:
            capture = load_capture(args.extract)
            print(json.dumps(extract_replay_inputs(capture), indent=2, sort_keys=True))
            return 0
        capture = live_capture(timeout_seconds=args.timeout_seconds)
        serialized = json.dumps(capture, indent=2, ensure_ascii=False, sort_keys=True) + '\n'
        if args.output is not None:
            args.output.write_text(serialized, encoding='utf-8')
        else:
            print(serialized, end='')
        failing = [command for command in capture['commands'] if command.get('exit_code') != 0 or command.get('timed_out')]
        return 2 if failing else 0
    except Exception as exc:  # noqa: BLE001
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

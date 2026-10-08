from __future__ import annotations

from pathlib import Path
from shutil import which
from typing import Any, Mapping


def _lower_text(value: object) -> str:
    return str(value or '').strip().lower()


def _unit_file_state_sets() -> tuple[set[str], set[str], set[str]]:
    enabled_like = {'enabled', 'enabled-runtime', 'linked', 'linked-runtime', 'alias'}
    masked_like = {'masked', 'masked-runtime'}
    absent_like = {'', 'disabled', 'indirect', 'static', 'generated', 'transient', 'bad'}
    return enabled_like, masked_like, absent_like


def summarize_autostart_desktop(autostart_desktop: str | Path | None) -> dict[str, Any]:
    path = Path(str(autostart_desktop or '')).expanduser() if autostart_desktop else None
    payload: dict[str, Any] = {
        'path': str(path) if path else '',
        'exists': bool(path and path.exists()),
        'state': 'absent',
        'hidden': False,
        'tryexec': '',
        'tryexec_resolved': None,
        'effective': False,
    }
    if not path or not path.exists():
        payload['summary'] = 'No user autostart desktop entry was found for the reviewed installed lane.'
        return payload
    values: dict[str, str] = {}
    try:
        for raw in path.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            values[key.strip()] = value.strip()
    except Exception as exc:
        payload['state'] = 'error'
        payload['summary'] = f'Autostart desktop entry exists but could not be parsed: {exc}'
        return payload

    hidden = _lower_text(values.get('Hidden')) == 'true'
    tryexec = str(values.get('TryExec') or '').strip()
    tryexec_resolved = None
    if tryexec:
        tryexec_resolved = tryexec if Path(tryexec).is_absolute() and Path(tryexec).exists() else which(tryexec)

    payload['hidden'] = hidden
    payload['tryexec'] = tryexec
    payload['tryexec_resolved'] = tryexec_resolved
    if hidden:
        payload['state'] = 'hidden'
        payload['summary'] = 'The user autostart desktop entry exists but Hidden=true disables it for this user.'
        return payload
    if tryexec and not tryexec_resolved:
        payload['state'] = 'tryexec-missing'
        payload['summary'] = 'The user autostart desktop entry exists, but its TryExec target is not currently resolvable on this host.'
        return payload
    payload['state'] = 'present'
    payload['effective'] = True
    payload['summary'] = 'The user autostart desktop entry exists and does not appear to be hidden or blocked by TryExec.'
    return payload


def summarize_startup_handoff_status(
    *,
    service_mode: str,
    expected_units: list[str] | None = None,
    units: list[Mapping[str, Any]] | None = None,
    autostart_desktop: str | Path | None = None,
    systemctl_available: bool = True,
) -> dict[str, Any]:
    service_mode_value = str(service_mode or 'environment-only').strip() or 'environment-only'
    expected = [str(item) for item in list(expected_units or []) if str(item)]
    unit_rows = [dict(item) for item in list(units or []) if isinstance(item, Mapping)]
    enabled_like, masked_like, absent_like = _unit_file_state_sets()
    analyzed_units: list[dict[str, Any]] = []
    for row in unit_rows:
        unit = str(row.get('unit') or '').strip()
        state = _lower_text(row.get('unit_file_state'))
        load_state = _lower_text(row.get('load_state'))
        if not state and load_state in {'not-found', 'error', 'bad-setting'}:
            state = load_state
        analyzed_units.append(
            {
                'unit': unit,
                'unit_file_state': state or 'unknown',
                'enabled': state in enabled_like,
                'masked': state in masked_like,
                'disabledish': state in absent_like,
            }
        )

    autostart = summarize_autostart_desktop(autostart_desktop)
    counts = {
        'expected_unit_count': len(expected),
        'observed_unit_count': len(analyzed_units),
        'enabled_unit_count': sum(1 for row in analyzed_units if row.get('enabled')),
        'masked_unit_count': sum(1 for row in analyzed_units if row.get('masked')),
        'disabledish_unit_count': sum(1 for row in analyzed_units if row.get('disabledish')),
        'autostart_present': bool(autostart.get('exists')),
        'autostart_effective': bool(autostart.get('effective')),
    }

    verdict = 'unavailable'
    if service_mode_value == 'environment-only' and not expected:
        verdict = 'manual_or_external_owner'
    elif counts['enabled_unit_count'] and autostart.get('effective'):
        verdict = 'duplicate_start_risk'
    elif counts['enabled_unit_count']:
        verdict = 'primary_user_unit_owner'
    elif autostart.get('effective'):
        verdict = 'fallback_autostart_owner'
    elif autostart.get('state') == 'hidden':
        verdict = 'autostart_hidden_no_owner'
    elif autostart.get('state') == 'tryexec-missing':
        verdict = 'autostart_tryexec_missing'
    elif counts['masked_unit_count']:
        verdict = 'masked_no_owner'
    elif expected:
        verdict = 'no_startup_owner'
    elif service_mode_value == 'environment-only':
        verdict = 'manual_or_external_owner'

    summary_headline = {
        'manual_or_external_owner': 'This reviewed lane does not rely on a VHK-owned startup owner, so startup is manual or delegated to some external/session-specific path.',
        'primary_user_unit_owner': 'The reviewed lane has one primary startup owner: at least one VHK user unit is enabled and there is no effective autostart bridge competing with it.',
        'fallback_autostart_owner': 'The reviewed lane currently depends on the XDG autostart bridge as its startup owner instead of an enabled VHK user unit.',
        'duplicate_start_risk': 'The reviewed lane has both an enabled VHK user unit and an effective XDG autostart bridge, which creates duplicate-start risk.',
        'autostart_hidden_no_owner': 'An autostart desktop entry exists, but Hidden=true disables it and no enabled VHK user unit was observed.',
        'autostart_tryexec_missing': 'An autostart desktop entry exists, but its TryExec target is missing and no enabled VHK user unit was observed.',
        'masked_no_owner': 'Expected VHK user units appear masked, so the installed lane currently lacks a valid startup owner.',
        'no_startup_owner': 'The reviewed lane ships expected VHK user units, but neither an enabled unit nor an effective autostart bridge was observed.',
        'unavailable': 'The installed lane could not establish startup ownership from the current host snapshot.',
    }.get(verdict, 'Startup handoff summary unavailable.')
    reasons = [summary_headline]
    if analyzed_units:
        states = []
        for row in analyzed_units[:4]:
            states.append(f"{row['unit']}:{row['unit_file_state']}")
        reasons.append('Observed unit-file states: ' + '; '.join(states) + '.')
    elif expected:
        reasons.append('Expected units: ' + ', '.join(expected[:4]) + '.')
    if autostart.get('path'):
        reasons.append(f"Autostart state: {autostart.get('state')} at {autostart.get('path')}.")
    if expected and not systemctl_available:
        reasons.append('systemctl --user was unavailable, so user-unit ownership could not be inspected directly.')

    return {
        'verdict': verdict,
        'summary': ' '.join(bit for bit in reasons if bit).strip(),
        'service_mode': service_mode_value,
        'counts': counts,
        'units': analyzed_units,
        'autostart': autostart,
    }


def known_startup_handoff_status_verdicts() -> list[str]:
    return [
        'manual_or_external_owner',
        'primary_user_unit_owner',
        'fallback_autostart_owner',
        'duplicate_start_risk',
        'autostart_hidden_no_owner',
        'autostart_tryexec_missing',
        'masked_no_owner',
        'no_startup_owner',
        'unavailable',
    ]

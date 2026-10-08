from __future__ import annotations

import json
from typing import Any, Mapping

_FAILURE_RESULTS = {
    'exit-code',
    'signal',
    'core-dump',
    'timeout',
    'watchdog',
    'resources',
    'protocol',
    'oom-kill',
}

_MISSING_LOAD_STATES = {'not-found', 'bad-setting', 'error', 'masked'}

_INCIDENT_VERDICT_SUMMARY = {
    'healthy_no_recent_incident': 'The reviewed installed lane looks healthy and there is no recent incident signature beyond ordinary service readiness.',
    'stopped_no_recent_incident': 'The reviewed lane was stopped or idle without a strong recent incident signature in the available user-unit/journal evidence.',
    'clean_session_skip': 'The reviewed lane looks intentionally skipped because the live session was not ready yet, not because the service crashed.',
    'condition_skip': 'A systemd condition or exec-condition appears to have skipped the reviewed lane without a hard service failure.',
    'start_limit_churn': 'Recent evidence points to restart churn or start-limit pressure rather than a one-off service failure.',
    'service_failure': 'Recent evidence points to a real service/process failure instead of a clean skip or missing ownership problem.',
    'missing_unit': 'Expected VHK-owned units are missing or not loadable, so the dominant recent incident is install/visibility loss rather than runtime churn.',
    'probe_error': 'The readiness probe failed abnormally, so this should be treated like a service/runtime incident until proven otherwise.',
    'no_owned_service': 'This reviewed lane does not ship a VHK-owned long-lived user service, so there is no installed service incident signature to classify.',
    'journal_unavailable': 'Recent user-journal evidence was unavailable, so incident classification relied only on the installed lane snapshot.',
    'unavailable': 'The installed lane did not expose enough evidence to classify a recent incident signature.',
}

_INCIDENT_VERDICTS = tuple(_INCIDENT_VERDICT_SUMMARY)


def _lower_text(value: object) -> str:
    return str(value or '').strip().lower()


def parse_journal_json_lines(text: str | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in str(text or '').splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except Exception:
            payload = {'MESSAGE': line}
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _journal_message_text(entries: list[Mapping[str, Any]]) -> str:
    bits: list[str] = []
    for entry in entries[:24]:
        message = str(entry.get('MESSAGE') or entry.get('message') or '').strip()
        if message:
            bits.append(message)
    return '\n'.join(bits)


def summarize_session_incident_signature(
    *,
    service_mode: str,
    expected_units: list[str] | None = None,
    units: list[Mapping[str, Any]] | None = None,
    readiness_runtime: Mapping[str, Any] | None = None,
    runtime_health: Mapping[str, Any] | None = None,
    journal_entries: list[Mapping[str, Any]] | None = None,
    journal_text: str | None = None,
    journal_available: bool | None = None,
) -> dict[str, Any]:
    expected_value = [str(item) for item in list(expected_units or []) if str(item)]
    units_value = [dict(item) for item in list(units or []) if isinstance(item, Mapping)]
    readiness_payload = dict(readiness_runtime or {})
    runtime_payload = dict(runtime_health or {})
    entries = [dict(item) for item in list(journal_entries or []) if isinstance(item, Mapping)]
    if not entries and journal_text:
        entries = parse_journal_json_lines(journal_text)
    message_text = _journal_message_text(entries)
    message_text_lc = message_text.lower()
    readiness_verdict = _lower_text(readiness_payload.get('verdict')) or 'unavailable'
    runtime_verdict = _lower_text(runtime_payload.get('verdict')) or 'unavailable'

    has_missing = any(_lower_text(row.get('load_state')) in _MISSING_LOAD_STATES for row in units_value) or runtime_verdict == 'degraded_unit_missing'
    has_condition_skip = (
        any(_lower_text(row.get('condition_result')) in {'no', 'false', '0'} for row in units_value)
        or any(_lower_text(row.get('result')) == 'condition' for row in units_value)
        or "skipped due to 'exec-condition'" in message_text_lc
        or 'condition check resulted in' in message_text_lc
        or 'exec-condition' in message_text_lc
    )
    has_start_limit = (
        any(_lower_text(row.get('result')) == 'start-limit-hit' for row in units_value)
        or 'start request repeated too quickly' in message_text_lc
        or 'scheduled restart job' in message_text_lc
        or runtime_verdict == 'degraded_restart_churn'
    )
    has_service_failure = (
        any(_lower_text(row.get('active_state')) == 'failed' for row in units_value)
        or any(_lower_text(row.get('result')) in _FAILURE_RESULTS for row in units_value)
        or 'failed with result' in message_text_lc
        or 'main process exited' in message_text_lc
        or 'terminated by signal' in message_text_lc
        or 'status=' in message_text_lc
        or runtime_verdict == 'degraded_failed'
    )

    if service_mode == 'environment-only' and not expected_value and not units_value:
        verdict = 'no_owned_service'
    elif readiness_verdict == 'error' or runtime_verdict == 'degraded_probe_error':
        verdict = 'probe_error'
    elif has_missing:
        verdict = 'missing_unit'
    elif readiness_verdict == 'not_ready':
        verdict = 'clean_session_skip'
    elif has_condition_skip:
        verdict = 'condition_skip'
    elif has_start_limit:
        verdict = 'start_limit_churn'
    elif has_service_failure:
        verdict = 'service_failure'
    elif runtime_verdict == 'healthy':
        verdict = 'healthy_no_recent_incident'
    elif runtime_verdict in {'stopped', 'no_owned_service'}:
        verdict = 'stopped_no_recent_incident' if runtime_verdict == 'stopped' else 'no_owned_service'
    elif journal_available is False and not entries:
        verdict = 'journal_unavailable'
    else:
        verdict = 'unavailable'

    reasons = [str(_INCIDENT_VERDICT_SUMMARY.get(verdict) or 'Incident signature unavailable.')]
    reasons.append(f'Readiness verdict: {readiness_verdict}.')
    reasons.append(f'Runtime health verdict: {runtime_verdict}.')
    if units_value:
        unit_bits: list[str] = []
        for row in units_value[:4]:
            piece = f"{row.get('unit') or 'unit'}:{_lower_text(row.get('active_state')) or 'unknown'}"
            sub = _lower_text(row.get('sub_state'))
            if sub:
                piece += f'/{sub}'
            result = _lower_text(row.get('result'))
            if result:
                piece += f' result={result}'
            condition = _lower_text(row.get('condition_result'))
            if condition:
                piece += f' condition={condition}'
            unit_bits.append(piece)
        reasons.append('Observed unit state: ' + '; '.join(unit_bits) + '.')
    if entries:
        msg_bits = [str(entry.get('MESSAGE') or entry.get('message') or '').strip() for entry in entries[:3]]
        msg_bits = [bit for bit in msg_bits if bit]
        if msg_bits:
            reasons.append('Recent journal cues: ' + ' | '.join(msg_bits) + '.')
    elif journal_available is False:
        reasons.append('journalctl --user was unavailable, so no recent journal cues were attached.')

    return {
        'verdict': verdict,
        'summary': ' '.join(bit for bit in reasons if bit).strip(),
        'readiness_verdict': readiness_verdict,
        'runtime_health_verdict': runtime_verdict,
        'journal_available': bool(journal_available) if journal_available is not None else None,
        'journal_entry_count': len(entries),
        'journal_sample': [
            {
                'MESSAGE': str(entry.get('MESSAGE') or entry.get('message') or '').strip(),
                'PRIORITY': entry.get('PRIORITY'),
                '_SYSTEMD_UNIT': str(entry.get('_SYSTEMD_UNIT') or '').strip(),
            }
            for entry in entries[:5]
        ],
        'known_verdicts': list(_INCIDENT_VERDICTS),
    }


def known_session_incident_signature_verdicts() -> list[str]:
    return list(_INCIDENT_VERDICTS)

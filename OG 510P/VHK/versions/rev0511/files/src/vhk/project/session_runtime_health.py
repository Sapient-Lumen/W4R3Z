from __future__ import annotations

from typing import Any, Mapping

from vhk.project.session_readiness_status import parse_session_readiness_exit, verdict_from_session_readiness_exit


def parse_count(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    text = str(value).strip()
    if not text or text == 'missing':
        return None
    if text.lstrip('-').isdigit():
        try:
            return int(text)
        except Exception:
            return -1
    return -1


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


class _UnitSignals(dict):
    pass


def analyze_unit_runtime_signals(unit: Mapping[str, Any] | None) -> dict[str, Any]:
    payload = dict(unit or {})
    unit_name = str(payload.get('unit') or '')
    load_state = str(payload.get('load_state') or '').strip().lower()
    active_state = str(payload.get('active_state') or '').strip().lower()
    sub_state = str(payload.get('sub_state') or '').strip().lower()
    result = str(payload.get('result') or '').strip().lower()
    condition_result = str(payload.get('condition_result') or '').strip().lower()
    unit_file_state = str(payload.get('unit_file_state') or '').strip().lower()
    n_restarts = parse_count(payload.get('n_restarts'))
    unit_kind = 'socket' if unit_name.endswith('.socket') else ('service' if unit_name.endswith('.service') else 'unit')
    query_ok = bool(payload.get('query_ok'))

    missing = load_state in _MISSING_LOAD_STATES
    start_limit = result == 'start-limit-hit'
    restarting = sub_state in {'auto-restart', 'restart', 'reload'} or start_limit
    if n_restarts is not None and n_restarts >= 3:
        restarting = True
    failed = active_state == 'failed' or result in _FAILURE_RESULTS
    healthy = active_state == 'active' and not failed and not missing
    if unit_kind == 'service' and active_state == 'inactive' and sub_state in {'dead', 'exited', ''} and result in {'', 'success'}:
        healthy = False
    idle_socket = unit_kind == 'socket' and active_state == 'active' and sub_state in {'listening', 'running', ''}
    stopped = active_state in {'inactive', 'deactivating'} and not failed and not restarting and not missing

    return {
        'unit': unit_name,
        'unit_kind': unit_kind,
        'query_ok': query_ok,
        'load_state': load_state,
        'active_state': active_state,
        'sub_state': sub_state,
        'result': result,
        'condition_result': condition_result,
        'unit_file_state': unit_file_state,
        'n_restarts': n_restarts,
        'missing': missing,
        'failed': failed,
        'restarting': restarting,
        'start_limit': start_limit,
        'healthy': healthy,
        'idle_socket': idle_socket,
        'stopped': stopped,
    }


_RUNTIME_VERDICT_SUMMARY = {
    'healthy': 'The reviewed installed lane looks alive: at least one owned unit is active and there are no obvious runtime failure signals.',
    'skipped_not_ready': 'The reviewed lane was skipped cleanly because the live session did not look ready yet.',
    'degraded_restart_churn': 'The reviewed lane is showing restart churn or start-limit pressure rather than a clean idle/ready state.',
    'degraded_failed': 'The reviewed lane is reporting a failed user-unit state or a terminal service result.',
    'degraded_probe_error': 'The readiness probe itself failed abnormally, so the installed lane should be treated as unhealthy until that probe/runtime issue is resolved.',
    'degraded_unit_missing': 'Expected VHK-owned units are missing or not loadable on this host.',
    'stopped': 'The session looked ready, but the owned user units were not active when the installed lane was inspected.',
    'no_owned_service': 'This reviewed lane does not ship a VHK-owned long-lived user service, so runtime health is mostly launcher/session truth rather than unit health.',
    'unavailable': 'The installed lane could not collect enough unit/session state to establish runtime health from this host snapshot.',
}


_RUNTIME_VERDICTS = tuple(_RUNTIME_VERDICT_SUMMARY)


def summarize_session_runtime_health(
    *,
    service_mode: str,
    expected_units: list[str] | None = None,
    units: list[dict[str, Any]] | None = None,
    readiness_runtime: Mapping[str, Any] | None = None,
    systemctl_available: bool | None = None,
) -> dict[str, Any]:
    units_value = [dict(item) for item in list(units or []) if isinstance(item, dict)]
    expected_value = [str(item) for item in list(expected_units or []) if str(item)]
    readiness_payload = dict(readiness_runtime or {})
    readiness_verdict = str(readiness_payload.get('verdict') or verdict_from_session_readiness_exit(parse_session_readiness_exit(readiness_payload.get('exit_code'))))
    analyzed = [analyze_unit_runtime_signals(item) for item in units_value]

    counts = {
        'expected_unit_count': len(expected_value),
        'observed_unit_count': len(analyzed),
        'healthy_unit_count': sum(1 for row in analyzed if row.get('healthy') or row.get('idle_socket')),
        'failed_unit_count': sum(1 for row in analyzed if row.get('failed')),
        'missing_unit_count': sum(1 for row in analyzed if row.get('missing')),
        'restart_churn_unit_count': sum(1 for row in analyzed if row.get('restarting')),
        'stopped_unit_count': sum(1 for row in analyzed if row.get('stopped')),
        'start_limit_unit_count': sum(1 for row in analyzed if row.get('start_limit')),
    }

    verdict = 'unavailable'
    if service_mode == 'environment-only' and not expected_value and not analyzed:
        verdict = 'no_owned_service'
    elif readiness_verdict == 'not_ready':
        verdict = 'skipped_not_ready'
    elif readiness_verdict == 'error':
        verdict = 'degraded_probe_error'
    elif counts['missing_unit_count']:
        verdict = 'degraded_unit_missing'
    elif counts['restart_churn_unit_count']:
        verdict = 'degraded_restart_churn'
    elif counts['failed_unit_count']:
        verdict = 'degraded_failed'
    elif counts['healthy_unit_count']:
        verdict = 'healthy'
    elif expected_value and not analyzed:
        verdict = 'unavailable' if not systemctl_available else ('stopped' if readiness_verdict == 'ready' else 'unavailable')
    elif expected_value:
        verdict = 'stopped'
    elif service_mode == 'environment-only':
        verdict = 'no_owned_service'

    reasons = [str(_RUNTIME_VERDICT_SUMMARY.get(verdict) or 'Runtime health summary unavailable.')]
    if readiness_verdict:
        reasons.append(f"Readiness verdict: {readiness_verdict}.")
    if analyzed:
        unit_bits: list[str] = []
        for row in analyzed[:4]:
            piece = f"{row.get('unit') or 'unit'}:{row.get('active_state') or 'unknown'}"
            sub = str(row.get('sub_state') or '').strip()
            if sub:
                piece += f"/{sub}"
            result = str(row.get('result') or '').strip()
            if result:
                piece += f" result={result}"
            n_restarts = row.get('n_restarts')
            if n_restarts not in {None, ''}:
                piece += f" restarts={n_restarts}"
            unit_bits.append(piece)
        reasons.append('Observed unit runtime: ' + '; '.join(unit_bits) + '.')
    elif expected_value:
        reasons.append('Expected units: ' + ', '.join(expected_value[:4]) + '.')
    if systemctl_available is False and expected_value:
        reasons.append('systemctl --user was unavailable, so unit health could not be inspected directly.')

    return {
        'service_mode': str(service_mode or ''),
        'expected_units': expected_value,
        'verdict': verdict,
        'readiness_verdict': readiness_verdict,
        'counts': counts,
        'units': analyzed,
        'summary': ' '.join(bit for bit in reasons if bit).strip(),
        'known_verdicts': list(_RUNTIME_VERDICTS),
    }



def known_session_runtime_health_verdicts() -> list[str]:
    return list(_RUNTIME_VERDICTS)

def summarize_session_runtime_health_brief(runtime: Mapping[str, Any] | None) -> dict[str, Any]:
    payload = dict(runtime or {})
    counts = dict(payload.get('counts') or {})
    return {
        'verdict': str(payload.get('verdict') or 'unknown'),
        'readiness_verdict': str(payload.get('readiness_verdict') or 'unknown'),
        'healthy_unit_count': int(counts.get('healthy_unit_count') or 0),
        'failed_unit_count': int(counts.get('failed_unit_count') or 0),
        'restart_churn_unit_count': int(counts.get('restart_churn_unit_count') or 0),
        'missing_unit_count': int(counts.get('missing_unit_count') or 0),
    }

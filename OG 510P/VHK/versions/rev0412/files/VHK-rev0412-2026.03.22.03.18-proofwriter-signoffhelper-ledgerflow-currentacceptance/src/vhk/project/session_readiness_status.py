from __future__ import annotations

from typing import Any, Mapping


def parse_session_readiness_exit(value: object) -> int | None:
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


def verdict_from_session_readiness_exit(exit_code: int | None) -> str:
    if exit_code == 0:
        return 'ready'
    if exit_code is None:
        return 'unavailable'
    if 1 <= exit_code <= 254:
        return 'not_ready'
    return 'error'


def summarize_session_readiness_runtime(
    *,
    probe_path: str,
    exit_code: int | None,
    probe_output: str,
    units: list[dict[str, Any]] | None = None,
    unit_show_text: str = '',
    probe_present: bool | None = None,
) -> dict[str, Any]:
    exit_value = parse_session_readiness_exit(exit_code)
    verdict = verdict_from_session_readiness_exit(exit_value)
    units_value = [dict(item) for item in list(units or []) if isinstance(item, dict)]
    probe_present_value = bool(probe_present)
    if probe_present is None:
        probe_present_value = bool(probe_path)
    reasons: list[str] = []
    if verdict == 'ready':
        reasons.append('The installed readiness probe returned exit 0, so the live graphical/session prerequisites looked satisfied.')
    elif verdict == 'not_ready':
        reasons.append('The installed readiness probe returned a non-zero non-fatal exit code, so VHK should treat this as a clean session-not-ready skip rather than an ordinary daemon failure.')
    elif verdict == 'error':
        reasons.append('The installed readiness probe exited abnormally or with an unexpected status, so this should be investigated like a real service/runtime problem.')
    else:
        reasons.append('No installed readiness probe verdict was available, so live session readiness could not be established from the installed lane itself.')
    if units_value:
        states = []
        for row in units_value[:4]:
            state = f"{row.get('unit') or 'unit'}:{row.get('active_state') or 'unknown'}"
            sub = str(row.get('sub_state') or '').strip()
            if sub:
                state += f"/{sub}"
            result = str(row.get('result') or '').strip()
            if result:
                state += f" result={result}"
            condition_result = str(row.get('condition_result') or '').strip()
            if condition_result:
                state += f" condition={condition_result}"
            states.append(state)
        reasons.append('Observed unit states: ' + '; '.join(states) + '.')
    elif unit_show_text.strip():
        reasons.append('Unit show text was captured, but it did not yield structured per-unit rows.')
    summary = ' '.join(reason.strip() for reason in reasons if reason.strip())
    return {
        'probe_path': str(probe_path or ''),
        'probe_present': probe_present_value,
        'exit_code': exit_value,
        'verdict': verdict,
        'probe_output': str(probe_output or ''),
        'unit_show_text': str(unit_show_text or ''),
        'units': units_value,
        'summary': summary,
    }


def summarize_session_readiness_runtime_brief(runtime: Mapping[str, Any] | None) -> dict[str, Any]:
    payload = dict(runtime or {})
    return {
        'verdict': str(payload.get('verdict') or 'unknown'),
        'probe_present': bool(payload.get('probe_present')),
        'unit_count': len([dict(item) for item in list(payload.get('units') or []) if isinstance(item, dict)]),
    }

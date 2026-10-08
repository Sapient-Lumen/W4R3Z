from __future__ import annotations

from typing import Any, Mapping


def _dedupe(items: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        text = str(item).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def build_session_readiness_evidence(
    *,
    service_mode: str,
    command_name: str,
    unit_base: str,
    config_rel: str,
    session_readiness_policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    service_mode_value = str(service_mode or 'environment-only').strip() or 'environment-only'
    command_name_value = str(command_name or 'vhk-project').strip() or 'vhk-project'
    unit_base_value = str(unit_base or f'vhk-busd-{command_name_value}').strip() or f'vhk-busd-{command_name_value}'
    config_rel_value = str(config_rel or f'vhk/{command_name_value}/session-service').strip() or f'vhk/{command_name_value}/session-service'
    policy = dict(session_readiness_policy or {})
    probe_path = f"${{XDG_CONFIG_HOME:-$HOME/.config}}/{config_rel_value}/verify_session_readiness.sh"
    show_properties = _dedupe([
        'LoadState',
        'ActiveState',
        'SubState',
        'Result',
        'UnitFileState',
        'FragmentPath',
        'ExecMainCode',
        'ExecMainStatus',
    ])
    if service_mode_value == 'socket-activated-busd':
        units = [f'{unit_base_value}.socket', f'{unit_base_value}.service']
    elif service_mode_value != 'environment-only':
        units = [f'{unit_base_value}.service']
    else:
        units = []

    if service_mode_value == 'environment-only':
        mode = 'documentary-readiness-evidence'
        summary = (
            'Keep session readiness evidence reviewable even when this lane does not ship a first-party long-lived user unit, '
            'so dossier/rehearsal output can still say which live session prerequisites would matter before a graphical lane is treated as ready.'
        )
    else:
        mode = 'probe-and-unit-evidence'
        summary = (
            'Capture one reviewable readiness verdict from the installed verify_session_readiness.sh probe and pair it with '
            'systemctl show properties for the owned unit lane, so operators can separate session-not-ready skips from ordinary user-service failures.'
        )

    return {
        'mode': mode,
        'summary': summary,
        'probe_path': probe_path,
        'probe_name': 'verify_session_readiness.sh',
        'capture_files': {
            'probe_output': 'session_readiness_probe.txt',
            'probe_exit': 'session_readiness_exit.txt',
            'unit_show': 'session_readiness_units.txt',
        },
        'show_properties': show_properties,
        'unit_names': units,
        'service_mode': service_mode_value,
        'config_rel': config_rel_value,
        'requires_probe_execution': service_mode_value != 'environment-only',
        'readiness_modes': {
            'ready': 'probe returned exit 0',
            'not_ready': 'probe returned exit 1-254',
            'error': 'probe returned 255 or shell/exec failed unexpectedly',
            'unavailable': 'probe script or unit visibility was not available on the host',
        },
    }


def summarize_session_readiness_evidence(evidence: Mapping[str, Any] | None) -> dict[str, Any]:
    payload = dict(evidence or {})
    return {
        'mode': str(payload.get('mode') or 'unknown'),
        'unit_count': len([str(x) for x in list(payload.get('unit_names') or []) if str(x)]),
        'requires_probe_execution': bool(payload.get('requires_probe_execution')),
    }

from __future__ import annotations

from typing import Any, Mapping, Sequence

_DEFAULT_BRIDGE_VARIABLES = [
    'DISPLAY',
    'XAUTHORITY',
    'DBUS_SESSION_BUS_ADDRESS',
    'XDG_RUNTIME_DIR',
    'I3SOCK',
]


def _clean(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _dedupe(values: Sequence[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def summarize_activation_environment(
    *,
    shell_env: Mapping[str, Any] | None = None,
    activation_environment: Mapping[str, Any] | None = None,
    bridge_variables: Sequence[str] | None = None,
) -> dict[str, Any]:
    variables = _dedupe(list(bridge_variables or _DEFAULT_BRIDGE_VARIABLES))
    shell = {name: _clean((shell_env or {}).get(name)) for name in variables}
    if activation_environment is None:
        return {
            'available': False,
            'status': 'unavailable',
            'in_sync': None,
            'bridge_variables': variables,
            'shell': shell,
            'activation': {},
            'missing_from_activation': [],
            'mismatched': [],
            'summary': 'The systemd/D-Bus activation environment could not be read, so VHK cannot confirm that socket activation will inherit the live X11/i3 session variables.',
        }

    activation = {name: _clean(activation_environment.get(name)) for name in variables}
    missing_from_activation: list[str] = []
    mismatched: list[dict[str, Any]] = []
    for name in variables:
        shell_value = shell.get(name)
        activation_value = activation.get(name)
        if not shell_value:
            continue
        if activation_value is None:
            missing_from_activation.append(name)
            continue
        if activation_value != shell_value:
            mismatched.append({
                'variable': name,
                'shell_value': shell_value,
                'activation_value': activation_value,
            })
    in_sync = not missing_from_activation and not mismatched
    if in_sync:
        summary = 'The systemd/D-Bus activation environment matches the live shell for the VHK session bridge variables.'
        status = 'in_sync'
    else:
        parts: list[str] = []
        if missing_from_activation:
            parts.append('missing: ' + ', '.join(missing_from_activation))
        if mismatched:
            parts.append('mismatched: ' + ', '.join(item['variable'] for item in mismatched))
        summary = 'The systemd/D-Bus activation environment drifted away from the live shell (' + '; '.join(parts) + ').'
        status = 'drift'
    return {
        'available': True,
        'status': status,
        'in_sync': in_sync,
        'bridge_variables': variables,
        'shell': shell,
        'activation': activation,
        'missing_from_activation': missing_from_activation,
        'mismatched': mismatched,
        'summary': summary,
    }


def summarize_runtime_service_environment(
    *,
    shell_env: Mapping[str, Any] | None = None,
    service_environment: Mapping[str, Any] | None = None,
    bridge_variables: Sequence[str] | None = None,
) -> dict[str, Any]:
    variables = _dedupe(list(bridge_variables or _DEFAULT_BRIDGE_VARIABLES))
    shell = {name: _clean((shell_env or {}).get(name)) for name in variables}
    if service_environment is None:
        return {
            'available': False,
            'status': 'unavailable',
            'in_sync': None,
            'bridge_variables': variables,
            'shell': shell,
            'service': {},
            'missing_from_service': [],
            'mismatched': [],
            'summary': 'The running service environment could not be read, so VHK cannot confirm that the resident daemon itself was started inside the live X11/i3 session.',
        }

    service = {name: _clean(service_environment.get(name)) for name in variables}
    missing_from_service: list[str] = []
    mismatched: list[dict[str, Any]] = []
    for name in variables:
        shell_value = shell.get(name)
        service_value = service.get(name)
        if not shell_value:
            continue
        if service_value is None:
            missing_from_service.append(name)
            continue
        if service_value != shell_value:
            mismatched.append({
                'variable': name,
                'shell_value': shell_value,
                'service_value': service_value,
            })
    in_sync = not missing_from_service and not mismatched
    if in_sync:
        summary = 'The running VHK service process carries the same X11/i3 bridge variables as the live shell.'
        status = 'in_sync'
    else:
        parts: list[str] = []
        if missing_from_service:
            parts.append('missing: ' + ', '.join(missing_from_service))
        if mismatched:
            parts.append('mismatched: ' + ', '.join(item['variable'] for item in mismatched))
        summary = 'The running VHK service process drifted away from the live shell (' + '; '.join(parts) + ').'
        status = 'drift'
    return {
        'available': True,
        'status': status,
        'in_sync': in_sync,
        'bridge_variables': variables,
        'shell': shell,
        'service': service,
        'missing_from_service': missing_from_service,
        'mismatched': mismatched,
        'summary': summary,
    }


def summarize_session_attachment(
    *,
    shell_env: Mapping[str, Any] | None = None,
    activation_environment: Mapping[str, Any] | None = None,
    x11_probe: Mapping[str, Any] | None = None,
    i3_probe: Mapping[str, Any] | None = None,
    service_environment: Mapping[str, Any] | None = None,
    bridge_variables: Sequence[str] | None = None,
) -> dict[str, Any]:
    env = dict(shell_env or {})
    activation = summarize_activation_environment(
        shell_env=env,
        activation_environment=activation_environment,
        bridge_variables=bridge_variables,
    )
    runtime_service_environment = summarize_runtime_service_environment(
        shell_env=env,
        service_environment=service_environment,
        bridge_variables=bridge_variables,
    )
    x11 = dict(x11_probe or {})
    i3 = dict(i3_probe or {})

    blockers: list[str] = []
    warnings: list[str] = []

    display = _clean(env.get('DISPLAY'))
    xauthority = _clean(env.get('XAUTHORITY'))
    xdg_runtime_dir = _clean(env.get('XDG_RUNTIME_DIR'))

    if not display:
        blockers.append('DISPLAY missing')
    if not xdg_runtime_dir:
        blockers.append('XDG_RUNTIME_DIR missing')
    if not xauthority:
        warnings.append('XAUTHORITY missing')

    x11_status = str(x11.get('status') or 'not_checked')
    if display and x11_status not in {'ok', 'not_checked'}:
        blockers.append(f'X11 probe {x11_status}')
    if x11.get('xtest_available') is False:
        blockers.append('XTEST unavailable')
    if x11.get('record_available') is False:
        warnings.append('RECORD extension unavailable')

    i3_status = str(i3.get('status') or 'not_checked')
    i3_wm = _clean(i3.get('wm'))
    if i3_status not in {'ok', 'not_checked'}:
        blockers.append(f'i3 IPC {i3_status}')
    elif i3_wm and i3_wm != 'i3':
        blockers.append(f'window manager {i3_wm}')

    if activation.get('available') and activation.get('in_sync') is False:
        blockers.append('activation environment drift')
    elif not activation.get('available'):
        warnings.append('activation environment unavailable')

    if runtime_service_environment.get('available') and runtime_service_environment.get('in_sync') is False:
        blockers.append('service session drift')
    elif not runtime_service_environment.get('available'):
        warnings.append('service session environment unavailable')

    if blockers:
        primary = blockers[0]
        if primary in {'DISPLAY missing', 'XDG_RUNTIME_DIR missing'}:
            status = 'missing_shell_session_env'
            summary = 'The current shell is not carrying the minimum graphical session variables VHK needs for the flagship X11/i3 runtime.'
        elif primary.startswith('X11 probe') or primary == 'XTEST unavailable':
            status = 'x11_probe_failed'
            summary = 'The live shell has session variables, but VHK could not verify a healthy X11 control path for the warm runtime.'
        elif primary.startswith('i3 IPC') or primary.startswith('window manager '):
            status = 'i3_ipc_unreachable'
            summary = 'The live shell looks graphical, but VHK could not confirm an i3 IPC session for the flagship runtime.'
        elif primary == 'activation environment drift':
            status = 'activation_environment_drift'
            summary = 'The live shell and the systemd/D-Bus activation environment disagree, so socket-activated warm-runtime restarts may bind to the wrong X11/i3 session.'
        elif primary == 'service session drift':
            status = 'service_session_drift'
            summary = 'The running VHK service process was started with different X11/i3 session variables than the live shell, so the warm runtime is attached to the wrong desktop session.'
        else:
            status = 'session_attachment_blocked'
            summary = 'VHK could not prove that the warm runtime is attached to the intended X11/i3 session.'
    elif warnings:
        status = 'attached_with_warnings'
        summary = 'The warm runtime looks attached to the live X11/i3 session, but there are still warning-level attachment issues to review.'
    else:
        status = 'attached'
        summary = 'The warm runtime looks attached to the live X11/i3 session and the activation environment matches the shell.'

    sync_command = 'dbus-update-activation-environment --systemd DISPLAY XAUTHORITY DBUS_SESSION_BUS_ADDRESS XDG_RUNTIME_DIR I3SOCK'
    return {
        'status': status,
        'ready': not blockers,
        'summary': summary,
        'blockers': blockers,
        'warnings': warnings,
        'shell_env': {
            'DISPLAY': display,
            'XAUTHORITY': xauthority,
            'DBUS_SESSION_BUS_ADDRESS': _clean(env.get('DBUS_SESSION_BUS_ADDRESS')),
            'XDG_RUNTIME_DIR': xdg_runtime_dir,
            'I3SOCK': _clean(env.get('I3SOCK')),
        },
        'activation_environment': activation,
        'runtime_service_environment': runtime_service_environment,
        'x11_probe': x11,
        'i3_probe': i3,
        'commands': {
            'sync_activation_environment': sync_command,
            'show_activation_environment': 'systemctl --user show-environment',
            'probe_x11': 'xdpyinfo -queryExtensions',
            'probe_i3': 'i3-msg -t get_workspaces',
        },
    }

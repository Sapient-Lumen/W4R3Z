from __future__ import annotations

from typing import Any, Mapping


def _dedupe(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def build_session_readiness_policy(
    *,
    desktop_backend: str,
    service_mode: str,
    authority_scope: str,
    session_target_policy: dict[str, Any] | None = None,
    session_activation_policy: dict[str, Any] | None = None,
    authority_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    backend = str(desktop_backend or 'unknown').strip().lower() or 'unknown'
    service_mode_value = str(service_mode or 'environment-only').strip() or 'environment-only'
    authority_scope_value = str(authority_scope or 'user-session-owned').strip() or 'user-session-owned'
    target_policy = dict(session_target_policy or {})
    activation_policy = dict(session_activation_policy or {})
    authority = dict(authority_policy or {})

    target_unit = str(target_policy.get('target_unit') or 'graphical-session.target')
    require_graphical_session_target = bool(target_policy.get('binds_to_graphical_session')) and service_mode_value != 'environment-only'

    required_vars = ['XDG_RUNTIME_DIR']
    display_any_of: list[str] = []
    display_requirement = 'none'
    if backend == 'wayland':
        display_requirement = 'wayland-display'
        display_any_of = ['WAYLAND_DISPLAY']
    elif backend == 'x11':
        display_requirement = 'x11-display'
        display_any_of = ['DISPLAY']
    else:
        display_requirement = 'graphical-display-any'
        display_any_of = ['WAYLAND_DISPLAY', 'DISPLAY']

    optional_vars = [str(x) for x in list(activation_policy.get('bridge_variables') or []) if str(x)]
    if display_requirement == 'wayland-display' and 'DISPLAY' not in optional_vars:
        optional_vars.append('DISPLAY')
    if display_requirement == 'x11-display' and 'XAUTHORITY' not in optional_vars:
        optional_vars.append('XAUTHORITY')
    optional_vars = [item for item in _dedupe(optional_vars) if item not in required_vars and item not in display_any_of]

    desktop_mediated_surface_ids = [str(x) for x in list(authority.get('desktop_mediated_surface_ids') or []) if str(x)]
    adjacent_surface_ids = [str(x) for x in list(authority.get('adjacent_privileged_surface_ids') or []) if str(x)]

    if service_mode_value != 'environment-only':
        mode = 'exec-condition-session-ready'
        summary = (
            'Guard the VHK-owned user service lane with an ExecCondition-style readiness probe so systemd can skip startup cleanly when the live graphical/session prerequisites are missing instead of turning wrong-session launches into restart noise.'
        )
    else:
        mode = 'documentary-session-readiness'
        summary = (
            'Document the session prerequisites even when this pack does not ship a first-party long-lived user unit, so operators can review which live session variables and targets still matter.'
        )

    summary_parts = [summary]
    if display_requirement == 'wayland-display':
        summary_parts.append('Wayland-first projects should not claim readiness until the compositor-exported display socket name is present in the user session.')
    elif display_requirement == 'x11-display':
        summary_parts.append('X11-first projects should not treat a generic login as equivalent to a live display session; a DISPLAY binding still matters.')
    else:
        summary_parts.append('Mixed or unknown graphical routes should demand at least one live display identifier instead of pretending the same session contract exists everywhere.')
    if require_graphical_session_target:
        summary_parts.append('Because this lane is explicitly graphical-session-bound, the probe also checks the user target before the VHK-owned unit tries to start.')
    if desktop_mediated_surface_ids:
        summary_parts.append('Desktop-mediated surfaces remain session scoped, so readiness should be checked before assuming portal-facing helpers can wake from the same login path.')
    if adjacent_surface_ids:
        summary_parts.append('Adjacent privileged helpers remain a separate review story; passing the readiness guard only proves the user-session lane is ready, not that evdev/uinput ownership exists.')

    guardrails = [
        'Use an ExecCondition-style probe for live session prerequisites when exporting a graphical-session-bound user unit, so missing display/runtime variables skip startup cleanly instead of causing restart storms.',
        'Keep the probe narrow and reviewable: check session prerequisites VHK actually depends on instead of importing or validating the whole shell environment.',
        'Treat readiness as separate from authority. A ready session does not grant portal consent or privileged helper access by itself.',
    ]
    if require_graphical_session_target:
        guardrails.append(
            'Tie the probe to graphical-session.target only when the service lane is intentionally graphical-session-bound; do not overfit target checks into environment-only or manual lanes.'
        )

    verification_commands = [
        'printf "%s\n" "${XDG_RUNTIME_DIR:-}"',
        f'systemctl --user is-active {target_unit}',
        'printf "%s\n" "${WAYLAND_DISPLAY:-${DISPLAY:-}}"',
    ]

    exec_condition_command = 'sh -lc "$CONFIGURATION_DIRECTORY/verify_session_readiness.sh"'

    return {
        'mode': mode,
        'summary': ' '.join(summary_parts),
        'authority_scope': authority_scope_value,
        'service_mode': service_mode_value,
        'require_graphical_session_target': require_graphical_session_target,
        'target_unit': target_unit,
        'required_variables': required_vars,
        'display_requirement': display_requirement,
        'display_any_of': display_any_of,
        'optional_variables': optional_vars,
        'desktop_mediated_surface_ids': desktop_mediated_surface_ids,
        'adjacent_privileged_surface_ids': adjacent_surface_ids,
        'exec_condition_command': exec_condition_command,
        'guardrails': guardrails,
        'verification_commands': verification_commands,
    }


def summarize_session_readiness_policy(policy: Mapping[str, Any] | None) -> dict[str, Any]:
    payload = dict(policy or {})
    return {
        'mode': str(payload.get('mode') or 'unknown'),
        'require_graphical_session_target': bool(payload.get('require_graphical_session_target')),
        'required_variable_count': len([str(x) for x in list(payload.get('required_variables') or []) if str(x)]),
        'display_requirement': str(payload.get('display_requirement') or 'none'),
    }

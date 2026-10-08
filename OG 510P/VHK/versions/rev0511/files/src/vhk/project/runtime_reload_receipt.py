from __future__ import annotations

from typing import Any, Mapping

from vhk.project.desktop_session_contract import compare_desktop_session_contract


def _clean(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def summarize_runtime_reload_receipt(
    *,
    before_probe: Mapping[str, Any] | None = None,
    after_probe: Mapping[str, Any] | None = None,
    expected_runtime_contract: Mapping[str, Any] | None = None,
    current_desktop_session_contract: Mapping[str, Any] | None = None,
    reload_command: str | None = None,
    restart_runtime_command: str | None = None,
    inspect_runtime_command: str | None = None,
    emit_status: str | None = None,
    emit_error: str | None = None,
) -> dict[str, Any]:
    before = dict(before_probe or {})
    after = dict(after_probe or {})
    before_ack = dict(before.get('ack') or {})
    after_ack = dict(after.get('ack') or {})
    before_state = dict(before_ack.get('runtime_state') or {})
    after_state = dict(after_ack.get('runtime_state') or {})
    before_contract = dict(before_ack.get('runtime_contract') or {})
    after_contract = dict(after_ack.get('runtime_contract') or {})
    expected_contract = dict(expected_runtime_contract or {})

    before_status = _clean(before.get('status')) or 'unavailable'
    after_status = _clean(after.get('status')) or 'unavailable'
    expected_digest = _clean(expected_contract.get('digest'))
    before_digest = _clean(before_contract.get('digest'))
    after_digest = _clean(after_contract.get('digest'))
    before_epoch = _clean(before_state.get('runtime_epoch_id'))
    after_epoch = _clean(after_state.get('runtime_epoch_id'))
    before_pid = before_ack.get('pid')
    after_pid = after_ack.get('pid')
    before_reload_count = before_state.get('reload_count') if before_state else None
    after_reload_count = after_state.get('reload_count') if after_state else None
    reload_count_increased = (
        isinstance(before_reload_count, int)
        and isinstance(after_reload_count, int)
        and after_reload_count > before_reload_count
    )
    epoch_changed = bool(before_epoch and after_epoch and before_epoch != after_epoch)
    pid_changed = before_pid is not None and after_pid is not None and before_pid != after_pid
    contract_in_sync = None if not expected_digest or after_status != 'ok' else (after_digest == expected_digest)

    current_session = dict(current_desktop_session_contract or {})
    before_daemon_session = dict(before_ack.get('desktop_session_contract') or {})
    after_daemon_session = dict(after_ack.get('desktop_session_contract') or {})
    after_daemon_session_status = compare_desktop_session_contract(current_session, after_daemon_session) if current_session or after_daemon_session else {}
    after_desktop_session_in_sync = None if after_status != 'ok' else (bool(after_daemon_session_status.get('in_sync')) if after_daemon_session_status else None)

    reload_observed = reload_count_increased or epoch_changed or pid_changed

    if emit_status == 'reload_disabled':
        status = 'reload_unavailable'
        summary = 'The project does not expose a reload event for the resident daemon.'
    elif emit_status == 'emit_failed':
        status = 'reload_emit_failed'
        summary = 'The resident reload command could not emit onto the warm bus socket.'
    elif after_status != 'ok':
        status = 'reload_not_verified'
        summary = 'The resident reload command was emitted, but the runtime probe could not verify the daemon state afterward.'
    elif contract_in_sync is True and after_desktop_session_in_sync is False and reload_observed:
        status = 'reload_observed_but_daemon_desktop_session_drift'
        summary = 'The resident daemon reloaded or restarted and now reports the current project contract digest, but it is still bound to a different X11/i3 desktop session than the current shell.'
    elif contract_in_sync is True and after_desktop_session_in_sync is False:
        status = 'contract_in_sync_but_daemon_desktop_session_drift'
        summary = 'The resident daemon reports the current project contract digest after reload, but it is still bound to a different X11/i3 desktop session than the current shell.'
    elif contract_in_sync is True and reload_observed:
        status = 'reload_observed_and_in_sync'
        summary = 'The resident daemon acknowledged a new runtime epoch after reload and now reports the current project contract digest on the current X11/i3 desktop session.'
    elif contract_in_sync is True:
        status = 'contract_in_sync_after_reload'
        summary = 'The resident daemon reports the current project contract digest after reload on the current X11/i3 desktop session, but the helper did not observe a distinct new epoch or PID.'
    elif reload_observed:
        status = 'reload_observed_but_contract_stale'
        summary = 'The resident daemon reloaded or restarted, but it still does not report the expected project contract digest.'
        if after_desktop_session_in_sync is False:
            summary += ' Its daemon desktop-session witness also drifted from the current shell.'
    else:
        status = 'reload_not_observed'
        summary = 'The resident reload command was emitted, but the helper did not observe a new daemon epoch, new PID, or incremented reload count.'
        if after_desktop_session_in_sync is False:
            summary += ' The daemon desktop-session witness also drifted from the current shell.'

    followup = None
    if status in {'reload_observed_but_daemon_desktop_session_drift', 'contract_in_sync_but_daemon_desktop_session_drift'}:
        followup = {
            'id': 'restart_runtime_for_daemon_desktop_session',
            'route_id': 'daemon_desktop_session_then_restart',
            'command': _clean(restart_runtime_command) or _clean(inspect_runtime_command),
            'reason': 'The reload reached the resident daemon, but only a restart from the current X11/i3 session can repair a stale daemon desktop-session binding.',
        }
    elif status in {'reload_emit_failed', 'reload_not_verified'}:
        followup = {
            'id': 'inspect_runtime_reload_path',
            'route_id': 'inspect_reload_path',
            'command': _clean(inspect_runtime_command) or _clean(reload_command),
            'reason': 'The reload path did not produce a trustworthy post-reload witness yet, so inspect runtime state before retrying.',
        }
    elif status in {'reload_observed_but_contract_stale', 'reload_not_observed'}:
        followup = {
            'id': 'recheck_runtime_contract_after_reload',
            'route_id': 'reload_then_check',
            'command': _clean(inspect_runtime_command) or _clean(reload_command),
            'reason': 'The reload path did not prove that the resident daemon now serves the current on-disk project contract.',
        }
    elif status == 'reload_unavailable':
        followup = {
            'id': 'inspect_reload_configuration',
            'route_id': 'configure_reload_event',
            'command': _clean(inspect_runtime_command),
            'reason': 'The generated stack cannot ask the resident daemon to reload until a reload event is configured.',
        }
    if followup is not None:
        followup = {key: value for key, value in followup.items() if value not in (None, '', [], {})}

    return {
        'status': status,
        'ok': status in {'reload_observed_and_in_sync', 'contract_in_sync_after_reload'},
        'summary': summary,
        'reload_command': _clean(reload_command),
        'restart_runtime_command': _clean(restart_runtime_command),
        'inspect_runtime_command': _clean(inspect_runtime_command),
        'recommended_followup': followup,
        'emit_status': emit_status,
        'emit_error': _clean(emit_error),
        'expected_runtime_contract_digest': expected_digest,
        'before_runtime_contract_digest': before_digest,
        'after_runtime_contract_digest': after_digest,
        'runtime_contract_in_sync': contract_in_sync,
        'before_probe_status': before_status,
        'after_probe_status': after_status,
        'before_pid': before_pid,
        'after_pid': after_pid,
        'pid_changed': pid_changed,
        'before_runtime_epoch_id': before_epoch,
        'after_runtime_epoch_id': after_epoch,
        'runtime_epoch_changed': epoch_changed,
        'before_reload_count': before_reload_count,
        'after_reload_count': after_reload_count,
        'reload_count_increased': reload_count_increased,
        'reload_observed': reload_observed,
        'last_reload_reason': _clean(after_state.get('last_reload_reason')),
        'last_reload_at': after_state.get('last_reload_at'),
        'current_desktop_session_contract': current_session,
        'before_daemon_desktop_session_contract': before_daemon_session,
        'after_daemon_desktop_session_contract': after_daemon_session,
        'after_daemon_desktop_session_contract_status': after_daemon_session_status,
        'after_desktop_session_contract_in_sync': after_desktop_session_in_sync,
    }

from __future__ import annotations

from typing import Any, Mapping


def _clean(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def summarize_runtime_restart_receipt(
    *,
    before_probe: Mapping[str, Any] | None = None,
    after_probe: Mapping[str, Any] | None = None,
    after_summary: Mapping[str, Any] | None = None,
    restart_command: str | None = None,
    sync_activation_environment_command: str | None = None,
    inspect_runtime_command: str | None = None,
    reload_runtime_command: str | None = None,
    sync_status: str | None = None,
    sync_error: str | None = None,
    restart_status: str | None = None,
    restart_error: str | None = None,
) -> dict[str, Any]:
    before = dict(before_probe or {})
    after = dict(after_probe or {})
    summary = dict(after_summary or {})
    before_ack = dict(before.get('ack') or {})
    after_ack = dict(after.get('ack') or {})
    before_state = dict(before_ack.get('runtime_state') or {})
    after_state = dict(after_ack.get('runtime_state') or {})

    before_status = _clean(before.get('status')) or 'unavailable'
    after_status = _clean(after.get('status')) or 'unavailable'
    sync_status = _clean(sync_status) or 'skipped'
    restart_status = _clean(restart_status) or ('ok' if _clean(restart_command) else 'unavailable')

    before_epoch = _clean(before_state.get('runtime_epoch_id'))
    after_epoch = _clean(after_state.get('runtime_epoch_id'))
    before_pid = before_ack.get('pid')
    after_pid = after_ack.get('pid')
    epoch_changed = bool(before_epoch and after_epoch and before_epoch != after_epoch)
    pid_changed = before_pid is not None and after_pid is not None and before_pid != after_pid
    restart_observed = epoch_changed or pid_changed or (before_status != 'ok' and after_status == 'ok')

    runtime_ready = bool(summary.get('ok'))
    runtime_contract_in_sync = summary.get('runtime_contract_in_sync')
    watchers_in_sync = summary.get('watchers_in_sync')
    desktop_session_in_sync = summary.get('desktop_session_contract_in_sync')
    daemon_desktop_session_status = dict(summary.get('daemon_desktop_session_contract_status') or {})

    status = 'restart_runtime_not_verified'
    human_summary = 'The resident restart helper ran, but the live runtime still needs inspection before it is trustworthy.'
    if restart_status == 'unavailable':
        status = 'restart_runtime_unavailable'
        human_summary = 'The generated stack does not know how to restart the resident VHK service for this project.'
    elif after_status != 'ok':
        status = 'restart_runtime_not_verified'
        human_summary = 'The restart helper ran, but the live emit -> socket -> resident busd probe did not verify the runtime afterward.'
    elif desktop_session_in_sync is False:
        status = 'restart_completed_but_daemon_desktop_session_drift'
        human_summary = 'The resident service answered after restart, but its daemon desktop-session witness is still bound to a different X11/i3 session than the current shell.'
    elif watchers_in_sync is False:
        status = 'restart_completed_but_expected_watcher_contract_drift'
        human_summary = 'The resident service answered after restart, but the expected generated watcher contract is still not loaded in the daemon.'
    elif runtime_contract_in_sync is False:
        status = 'restart_completed_but_runtime_contract_stale'
        human_summary = 'The resident service answered after restart, but it still does not report the current on-disk project contract digest.'
    elif runtime_ready and restart_observed:
        status = 'restart_observed_and_runtime_ready'
        human_summary = 'The resident service answered from a fresh daemon witness after restart and now matches the current project/runtime desktop session.'
    elif runtime_ready:
        status = 'runtime_ready_after_restart'
        human_summary = 'The resident service looks ready after restart, but the helper did not observe a distinct new daemon PID or runtime epoch.'

    if sync_status == 'failed' and status in {'restart_runtime_not_verified', 'restart_completed_but_daemon_desktop_session_drift'}:
        human_summary += ' The activation-environment sync step also failed.'
    elif sync_status == 'failed' and runtime_ready:
        human_summary += ' The activation-environment sync step failed, but the live daemon now matches the current runtime witness anyway.'
    if restart_status == 'failed' and runtime_ready:
        human_summary += ' The explicit restart command returned nonzero even though the daemon now looks ready.'
    elif restart_status == 'failed' and status == 'restart_runtime_not_verified':
        human_summary = 'The explicit resident-runtime restart command returned nonzero and the helper could not prove a healthy post-restart daemon state.'

    followup = None
    if status == 'restart_completed_but_daemon_desktop_session_drift':
        followup = {
            'id': 'inspect_runtime_session_attachment',
            'route_id': 'check_then_sync_session',
            'command': _clean(inspect_runtime_command),
            'reason': 'The daemon still belongs to the wrong X11/i3 session after restart, so inspect the live session-attachment and activation-environment witnesses before retrying.',
        }
    elif status == 'restart_completed_but_expected_watcher_contract_drift':
        followup = {
            'id': 'inspect_runtime_watcher_contract',
            'route_id': 'check_then_restart',
            'command': _clean(inspect_runtime_command),
            'reason': 'The daemon is alive, but the expected watcher contract is still missing after restart.',
        }
    elif status == 'restart_completed_but_runtime_contract_stale':
        followup = {
            'id': 'reload_runtime_for_project_contract',
            'route_id': 'runtime_contract_then_reload',
            'command': _clean(reload_runtime_command) or _clean(inspect_runtime_command),
            'reason': 'The daemon answered after restart, but it still does not advertise the current project contract digest.',
        }
    elif status in {'restart_runtime_unavailable', 'restart_runtime_not_verified'}:
        followup = {
            'id': 'inspect_runtime_restart_path',
            'route_id': 'status_then_check',
            'command': _clean(inspect_runtime_command),
            'reason': 'The restart helper did not produce a trustworthy ready witness yet, so inspect the live runtime before retrying dispatch.',
        }
    if followup is not None:
        followup = {key: value for key, value in followup.items() if value not in (None, '', [], {})}

    return {
        'status': status,
        'ok': status in {'restart_observed_and_runtime_ready', 'runtime_ready_after_restart'},
        'summary': human_summary,
        'restart_command': _clean(restart_command),
        'sync_activation_environment_command': _clean(sync_activation_environment_command),
        'inspect_runtime_command': _clean(inspect_runtime_command),
        'reload_runtime_command': _clean(reload_runtime_command),
        'recommended_followup': followup,
        'sync_status': sync_status,
        'sync_error': _clean(sync_error),
        'restart_status': restart_status,
        'restart_error': _clean(restart_error),
        'before_probe_status': before_status,
        'after_probe_status': after_status,
        'before_pid': before_pid,
        'after_pid': after_pid,
        'pid_changed': pid_changed,
        'before_runtime_epoch_id': before_epoch,
        'after_runtime_epoch_id': after_epoch,
        'runtime_epoch_changed': epoch_changed,
        'restart_observed': restart_observed,
        'after_summary': summary,
        'runtime_contract_in_sync': runtime_contract_in_sync,
        'watchers_in_sync': watchers_in_sync,
        'after_desktop_session_contract_in_sync': desktop_session_in_sync,
        'after_daemon_desktop_session_contract_status': daemon_desktop_session_status,
        'after_reload_count': after_state.get('reload_count'),
        'after_last_reload_reason': _clean(after_state.get('last_reload_reason')),
        'after_last_reload_at': after_state.get('last_reload_at'),
    }

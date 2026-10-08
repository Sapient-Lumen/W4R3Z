from __future__ import annotations

from typing import Any, Mapping


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
    reload_command: str | None = None,
    emit_status: str | None = None,
    emit_error: str | None = None,
) -> dict[str, Any]:
    before = dict(before_probe or {})
    after = dict(after_probe or {})
    before_state = dict((before.get('ack') or {}).get('runtime_state') or {})
    after_state = dict((after.get('ack') or {}).get('runtime_state') or {})
    before_contract = dict((before.get('ack') or {}).get('runtime_contract') or {})
    after_contract = dict((after.get('ack') or {}).get('runtime_contract') or {})
    expected_contract = dict(expected_runtime_contract or {})

    before_status = _clean(before.get('status')) or 'unavailable'
    after_status = _clean(after.get('status')) or 'unavailable'
    expected_digest = _clean(expected_contract.get('digest'))
    before_digest = _clean(before_contract.get('digest'))
    after_digest = _clean(after_contract.get('digest'))
    before_epoch = _clean(before_state.get('runtime_epoch_id'))
    after_epoch = _clean(after_state.get('runtime_epoch_id'))
    before_pid = (before.get('ack') or {}).get('pid')
    after_pid = (after.get('ack') or {}).get('pid')
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
    elif contract_in_sync is True and reload_observed:
        status = 'reload_observed_and_in_sync'
        summary = 'The resident daemon acknowledged a new runtime epoch after reload and now reports the current project contract digest.'
    elif contract_in_sync is True:
        status = 'contract_in_sync_after_reload'
        summary = 'The resident daemon reports the current project contract digest after reload, but the helper did not observe a distinct new epoch or PID.'
    elif reload_observed:
        status = 'reload_observed_but_contract_stale'
        summary = 'The resident daemon reloaded or restarted, but it still does not report the expected project contract digest.'
    else:
        status = 'reload_not_observed'
        summary = 'The resident reload command was emitted, but the helper did not observe a new daemon epoch, new PID, or incremented reload count.'

    return {
        'status': status,
        'ok': status in {'reload_observed_and_in_sync', 'contract_in_sync_after_reload'},
        'summary': summary,
        'reload_command': _clean(reload_command),
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
    }

from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Mapping


_SESSION_VARIABLES = {
    'display': 'DISPLAY',
    'xauthority': 'XAUTHORITY',
    'i3sock': 'I3SOCK',
    'session_type': 'XDG_SESSION_TYPE',
    'current_desktop': 'XDG_CURRENT_DESKTOP',
}


def _clean(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def desktop_session_contract_digest(contract: Mapping[str, Any] | None) -> str | None:
    if not contract:
        return None
    stable = {key: contract.get(key) for key in sorted(_SESSION_VARIABLES.keys())}
    return hashlib.sha256(json.dumps(stable, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()



def summarize_desktop_session_contract(env: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source = dict(os.environ if env is None else env)
    contract: dict[str, Any] = {key: _clean(source.get(var)) for key, var in _SESSION_VARIABLES.items()}
    contract['digest'] = desktop_session_contract_digest(contract)
    return contract



def compare_desktop_session_contract(current: Mapping[str, Any] | None, observed: Mapping[str, Any] | None) -> dict[str, Any]:
    current_contract = dict(current or {})
    observed_contract = dict(observed or {})
    current_digest = str(current_contract.get('digest') or desktop_session_contract_digest(current_contract) or '').strip() or None
    observed_digest = str(observed_contract.get('digest') or desktop_session_contract_digest(observed_contract) or '').strip() or None
    in_sync = bool(current_digest and observed_digest and current_digest == observed_digest)
    display_changed = False
    xauthority_changed = False
    i3sock_changed = False
    session_type_changed = False
    current_desktop_changed = False
    if current_contract or observed_contract:
        display_changed = current_contract.get('display') != observed_contract.get('display')
        xauthority_changed = current_contract.get('xauthority') != observed_contract.get('xauthority')
        i3sock_changed = current_contract.get('i3sock') != observed_contract.get('i3sock')
        session_type_changed = current_contract.get('session_type') != observed_contract.get('session_type')
        current_desktop_changed = current_contract.get('current_desktop') != observed_contract.get('current_desktop')
    reasons: list[str] = []
    status = 'in_sync'
    summary = 'The latest replay proof still matches the current X11/i3 session contract.'
    if not observed_contract:
        status = 'missing'
        summary = 'The latest run predates session-bound replay proof and should be rerun before treating replay as current.'
        reasons.append('run_start desktop_session_contract missing')
    elif not observed_digest:
        status = 'missing_digest'
        summary = 'The latest run did not capture a comparable X11/i3 session digest and should be rerun.'
        reasons.append('run_start desktop_session_contract digest missing')
    elif not in_sync:
        status = 'drifted'
        summary = 'The latest matching replay proof was captured on a different X11/i3 desktop session than the current shell.'
        if display_changed:
            reasons.append('DISPLAY changed since latest healthy replay')
        if xauthority_changed:
            reasons.append('XAUTHORITY changed since latest healthy replay')
        if i3sock_changed:
            reasons.append('I3SOCK changed since latest healthy replay')
        if session_type_changed:
            reasons.append('XDG_SESSION_TYPE changed since latest healthy replay')
        if current_desktop_changed:
            reasons.append('XDG_CURRENT_DESKTOP changed since latest healthy replay')
        if not reasons:
            reasons.append('desktop session contract digest changed')
    return {
        'status': status,
        'in_sync': in_sync,
        'summary': summary,
        'reasons': reasons,
        'display_changed': display_changed,
        'xauthority_changed': xauthority_changed,
        'i3sock_changed': i3sock_changed,
        'session_type_changed': session_type_changed,
        'current_desktop_changed': current_desktop_changed,
        'current_digest': current_digest,
        'observed_digest': observed_digest,
        'current_contract': current_contract,
        'observed_contract': observed_contract,
    }

from __future__ import annotations

import json
import hashlib
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from vhk.project.desktop_session_contract import compare_desktop_session_contract, desktop_session_contract_digest


def _coerce_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clean(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_name_list(items: object) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for item in list(items or []):
        name = _clean(item)
        if not name or name in seen:
            continue
        seen.add(name)
        normalized.append(name)
    return normalized



DEFAULT_WARM_RUNTIME_PROBE_FRESHNESS_WINDOW_S = 45.0


def _parse_timestamp(value: object) -> datetime | None:
    text = _clean(value)
    if not text:
        return None
    normalized = text
    if normalized.endswith('Z'):
        normalized = normalized[:-1] + '+00:00'
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _probe_freshness_summary(*, observed_at: object, freshness_window_s: float = DEFAULT_WARM_RUNTIME_PROBE_FRESHNESS_WINDOW_S, now_utc: datetime | None = None) -> dict[str, Any]:
    now_utc = now_utc or datetime.now(timezone.utc)
    observed_dt = _parse_timestamp(observed_at)
    observed_at_text = _clean(observed_at)
    age_s = None
    is_fresh = None
    freshness_status = 'missing'
    if observed_dt is not None:
        age_s = max(0.0, round((now_utc - observed_dt).total_seconds(), 3))
        is_fresh = age_s <= float(freshness_window_s)
        freshness_status = 'fresh' if is_fresh else 'stale'
    elif observed_at_text:
        freshness_status = 'unknown'
    return {
        'observed_at': observed_at_text,
        'freshness_window_s': float(freshness_window_s),
        'age_s': age_s,
        'is_fresh': is_fresh,
        'freshness_status': freshness_status,
    }

def runtime_state_cache_roots(*, project_root: str | Path, xdg_runtime_dir: str | None = None) -> list[Path]:
    root_path = Path(project_root).expanduser().resolve()
    roots: list[Path] = []
    runtime_dir = _clean(xdg_runtime_dir) or _clean(os.environ.get('XDG_RUNTIME_DIR'))
    if runtime_dir:
        project_key = hashlib.sha256(str(root_path).encode('utf-8')).hexdigest()[:16]
        roots.append(Path(runtime_dir).expanduser() / 'vhk' / 'runtime_state' / project_key)
    roots.append(root_path / '.vhk' / 'runtime_state')
    deduped: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        key = str(root)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(root)
    return deduped


def runtime_state_cache_path(*, project_root: str | Path, xdg_runtime_dir: str | None = None) -> Path:
    root = runtime_state_cache_roots(project_root=project_root, xdg_runtime_dir=xdg_runtime_dir)[0]
    root.mkdir(parents=True, exist_ok=True)
    return root / 'current.json'



def write_runtime_state_cache(
    *,
    project_root: str | Path,
    payload: Mapping[str, Any],
    xdg_runtime_dir: str | None = None,
) -> Path:
    path = runtime_state_cache_path(project_root=project_root, xdg_runtime_dir=xdg_runtime_dir)
    tmp_path = path.with_suffix(path.suffix + '.tmp')
    data = dict(payload)
    data.setdefault('schema_version', 1)
    data.setdefault('stack_kind', 'vhk.project.runtime_state_cache')
    data.setdefault('written_at', time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    data.setdefault('project_root', str(Path(project_root).expanduser().resolve()))
    tmp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp_path.replace(path)
    return path



def load_runtime_state_cache(*, project_root: str | Path, xdg_runtime_dir: str | None = None) -> tuple[dict[str, Any], Path | None]:
    for root in runtime_state_cache_roots(project_root=project_root, xdg_runtime_dir=xdg_runtime_dir):
        path = root / 'current.json'
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            return {}, path
        return (dict(payload) if isinstance(payload, dict) else {}), path
    return {}, None


def record_runtime_dispatch_probe_observation(
    *,
    project_root: str | Path,
    probe_summary: Mapping[str, Any],
    xdg_runtime_dir: str | None = None,
) -> Path:
    current_payload, _ = load_runtime_state_cache(project_root=project_root, xdg_runtime_dir=xdg_runtime_dir)
    payload = dict(current_payload) if current_payload else {}
    summary = dict(probe_summary or {})
    payload['dispatch_probe_observation'] = {
        'status': _clean(summary.get('status')),
        'ok': bool(summary.get('ok')) if 'ok' in summary else None,
        'observed_at': _clean(summary.get('observed_at')) or _clean(summary.get('ack_handled_at')) or time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'roundtrip_latency_ms': _coerce_float(summary.get('roundtrip_latency_ms')),
        'latency_status': _clean(summary.get('latency_status')),
        'latency_budget_ms': _coerce_float(summary.get('latency_budget_ms')),
        'ack_pid': summary.get('ack_pid'),
        'ack_handled_at': _clean(summary.get('ack_handled_at')),
        'probe_id': _clean(summary.get('probe_id')),
    }
    return write_runtime_state_cache(project_root=project_root, payload=payload, xdg_runtime_dir=xdg_runtime_dir)



def summarize_runtime_instance_witness_from_cache(*, project_root: str | Path, xdg_runtime_dir: str | None = None) -> dict[str, Any]:
    payload, path = load_runtime_state_cache(project_root=project_root, xdg_runtime_dir=xdg_runtime_dir)
    runtime_state = dict(payload.get('runtime_state') or {})
    runtime_contract = dict(payload.get('runtime_contract') or {})
    desktop_session_contract = dict(payload.get('desktop_session_contract') or {})
    dispatch_probe_observation = dict(payload.get('dispatch_probe_observation') or {})
    dispatch_probe_freshness = _probe_freshness_summary(observed_at=dispatch_probe_observation.get('observed_at'))
    desktop_session_contract_digest_value = _clean(desktop_session_contract.get('digest')) or desktop_session_contract_digest(desktop_session_contract)
    if desktop_session_contract and desktop_session_contract_digest_value:
        desktop_session_contract['digest'] = desktop_session_contract_digest_value
    return {
        'available': bool(payload),
        'source_id': 'runtime_state_cache.current',
        'cache_path': str(path) if path is not None else None,
        'cache_written_at': payload.get('written_at'),
        'pid': payload.get('pid'),
        'watchers': _normalize_name_list(payload.get('watchers')),
        'runtime_epoch_id': _clean(runtime_state.get('runtime_epoch_id')),
        'reload_count': runtime_state.get('reload_count'),
        'last_reload_reason': _clean(runtime_state.get('last_reload_reason')),
        'last_reload_at': runtime_state.get('last_reload_at'),
        'runtime_contract_digest': _clean(runtime_contract.get('digest')),
        'desktop_session_contract': desktop_session_contract,
        'desktop_session_contract_digest': desktop_session_contract_digest_value,
        'latest_dispatch_probe_status': _clean(dispatch_probe_observation.get('status')),
        'latest_dispatch_probe_ok': dispatch_probe_observation.get('ok'),
        'latest_dispatch_probe_observed_at': dispatch_probe_freshness.get('observed_at'),
        'latest_dispatch_probe_freshness_window_s': dispatch_probe_freshness.get('freshness_window_s'),
        'latest_dispatch_probe_age_s': dispatch_probe_freshness.get('age_s'),
        'latest_dispatch_probe_is_fresh': dispatch_probe_freshness.get('is_fresh'),
        'latest_dispatch_probe_freshness_status': dispatch_probe_freshness.get('freshness_status'),
        'latest_dispatch_probe_latency_ms': _coerce_float(dispatch_probe_observation.get('roundtrip_latency_ms')),
        'latest_dispatch_probe_latency_status': _clean(dispatch_probe_observation.get('latency_status')),
        'latest_dispatch_probe_latency_budget_ms': _coerce_float(dispatch_probe_observation.get('latency_budget_ms')),
        'latest_dispatch_probe_ack_pid': dispatch_probe_observation.get('ack_pid'),
        'latest_dispatch_probe_ack_handled_at': _clean(dispatch_probe_observation.get('ack_handled_at')),
        'latest_dispatch_probe_id': _clean(dispatch_probe_observation.get('probe_id')),
    }



def compare_runtime_instance_witness(
    current: Mapping[str, Any] | None,
    observed: Mapping[str, Any] | None,
) -> dict[str, Any]:
    current_witness = dict(current or {})
    observed_witness = dict(observed or {})
    current_available = bool(current_witness.get('available'))
    observed_available = bool(observed_witness.get('available')) if observed_witness else False
    current_epoch = _clean(current_witness.get('runtime_epoch_id'))
    observed_epoch = _clean(observed_witness.get('runtime_epoch_id'))
    current_pid = current_witness.get('pid')
    observed_pid = observed_witness.get('pid')
    current_contract_digest = _clean(current_witness.get('runtime_contract_digest'))
    observed_contract_digest = _clean(observed_witness.get('runtime_contract_digest'))
    current_watchers = _normalize_name_list(current_witness.get('watchers'))
    observed_watchers = _normalize_name_list(observed_witness.get('watchers'))
    current_desktop_session_contract = dict(current_witness.get('desktop_session_contract') or {})
    observed_desktop_session_contract = dict(observed_witness.get('desktop_session_contract') or {})
    current_desktop_session_digest = _clean(current_witness.get('desktop_session_contract_digest')) or desktop_session_contract_digest(current_desktop_session_contract)
    observed_desktop_session_digest = _clean(observed_witness.get('desktop_session_contract_digest')) or desktop_session_contract_digest(observed_desktop_session_contract)
    desktop_session_status = compare_desktop_session_contract(current_desktop_session_contract, observed_desktop_session_contract) if (current_desktop_session_contract or observed_desktop_session_contract) else {}
    if desktop_session_status:
        desktop_session_status = dict(desktop_session_status)
        status_id = str(desktop_session_status.get('status') or '')
        if status_id == 'in_sync':
            desktop_session_status['summary'] = 'The resident daemon desktop session still matches the current daemon cache.'
        elif status_id == 'missing':
            desktop_session_status['summary'] = 'The compared resident-runtime witness predates daemon desktop-session capture and should be refreshed.'
        elif status_id == 'missing_digest':
            desktop_session_status['summary'] = 'The compared resident-runtime witness did not capture a comparable daemon desktop-session digest and should be refreshed.'
        elif status_id == 'drifted':
            desktop_session_status['summary'] = 'The compared resident-runtime witnesses describe different X11/i3 desktop sessions for the resident daemon.'

    epoch_changed = bool(current_epoch and observed_epoch and current_epoch != observed_epoch)
    pid_changed = current_pid is not None and observed_pid is not None and current_pid != observed_pid
    runtime_contract_changed = bool(current_contract_digest and observed_contract_digest and current_contract_digest != observed_contract_digest)
    watcher_set_changed = bool(current_watchers and observed_watchers and current_watchers != observed_watchers)
    desktop_session_contract_changed = bool(current_desktop_session_digest and observed_desktop_session_digest and current_desktop_session_digest != observed_desktop_session_digest)

    current_probe_status = _clean(current_witness.get('latest_dispatch_probe_status'))
    observed_probe_status = _clean(observed_witness.get('latest_dispatch_probe_status'))
    current_probe_freshness_status = _clean(current_witness.get('latest_dispatch_probe_freshness_status'))
    observed_probe_freshness_status = _clean(observed_witness.get('latest_dispatch_probe_freshness_status'))
    current_probe_latency_status = _clean(current_witness.get('latest_dispatch_probe_latency_status'))
    observed_probe_latency_status = _clean(observed_witness.get('latest_dispatch_probe_latency_status'))
    current_probe_status_comparable = bool(current_probe_status)
    observed_probe_status_comparable = bool(observed_probe_status)
    current_probe_failure = current_probe_status_comparable and current_probe_status != 'ok'
    observed_probe_failure = observed_probe_status_comparable and observed_probe_status != 'ok'
    current_probe_refresh_attention = current_probe_status == 'ok' and current_probe_freshness_status == 'stale'
    observed_probe_refresh_attention = observed_probe_status == 'ok' and observed_probe_freshness_status == 'stale'
    current_probe_latency_attention = current_probe_status == 'ok' and current_probe_latency_status == 'over_budget'
    observed_probe_latency_attention = observed_probe_status == 'ok' and observed_probe_latency_status == 'over_budget'
    runtime_probe_status_changed = bool(current_probe_status_comparable and observed_probe_status_comparable and current_probe_status != observed_probe_status)
    runtime_probe_failure_changed = bool(current_probe_status_comparable and observed_probe_status_comparable and current_probe_failure != observed_probe_failure)
    runtime_probe_freshness_attention_changed = bool(current_probe_status_comparable and observed_probe_status_comparable and current_probe_refresh_attention != observed_probe_refresh_attention)
    runtime_probe_latency_attention_changed = bool(current_probe_status_comparable and observed_probe_status_comparable and current_probe_latency_attention != observed_probe_latency_attention)

    if not observed_witness and not current_available:
        status = 'comparison_unavailable'
        in_sync: bool | None = None
        summary = 'No current resident-runtime cache or receipt witness was available, so warm-dispatch history cannot be tied to a specific daemon epoch yet.'
        reasons = ['current runtime state cache missing', 'dispatch runtime witness missing']
    elif not observed_witness:
        status = 'missing'
        in_sync = False
        summary = 'The latest warm-dispatch receipt predates resident-runtime witness capture and should be refreshed before treating it as current warm-runtime evidence.'
        reasons = ['dispatch runtime witness missing']
    elif not observed_available:
        status = 'missing'
        in_sync = False
        summary = 'The latest warm-dispatch receipt did not capture a usable resident-runtime witness and should be refreshed.'
        reasons = ['dispatch runtime witness unavailable in receipt']
    elif not current_available:
        status = 'current_cache_missing'
        in_sync = None
        summary = 'No current resident-runtime cache was available to compare against the latest warm-dispatch receipt.'
        reasons = ['current runtime state cache missing']
    elif epoch_changed:
        status = 'runtime_epoch_drift'
        in_sync = False
        summary = 'The latest warm-dispatch receipt was emitted against an older resident-runtime epoch than the one currently advertised by the daemon cache.'
        reasons = ['resident runtime epoch changed since latest warm dispatch receipt']
    elif pid_changed:
        status = 'runtime_pid_drift'
        in_sync = False
        summary = 'The latest warm-dispatch receipt was emitted by a different resident busd process than the one currently advertised by the daemon cache.'
        reasons = ['resident runtime pid changed since latest warm dispatch receipt']
    elif runtime_contract_changed:
        status = 'runtime_contract_drift'
        in_sync = False
        summary = 'The resident-runtime contract cached for the latest warm-dispatch receipt no longer matches the current daemon cache.'
        reasons = ['resident runtime contract digest changed since latest warm dispatch receipt']
    elif watcher_set_changed:
        status = 'runtime_watcher_drift'
        in_sync = False
        summary = 'The latest warm-dispatch receipt was emitted against a different resident watcher set than the current daemon cache.'
        reasons = ['resident watcher set changed since latest warm dispatch receipt']
    elif desktop_session_contract_changed:
        status = 'runtime_desktop_session_drift'
        in_sync = False
        summary = 'The latest warm-dispatch receipt was emitted against a resident daemon bound to a different X11/i3 desktop session than the one currently advertised by the daemon cache.'
        reasons = ['resident daemon desktop session changed since latest warm dispatch receipt']
        if desktop_session_status.get('display_changed'):
            reasons.append('resident daemon DISPLAY changed since latest warm dispatch receipt')
        if desktop_session_status.get('xauthority_changed'):
            reasons.append('resident daemon XAUTHORITY changed since latest warm dispatch receipt')
        if desktop_session_status.get('i3sock_changed'):
            reasons.append('resident daemon I3SOCK changed since latest warm dispatch receipt')
        if desktop_session_status.get('session_type_changed'):
            reasons.append('resident daemon XDG_SESSION_TYPE changed since latest warm dispatch receipt')
        if desktop_session_status.get('current_desktop_changed'):
            reasons.append('resident daemon XDG_CURRENT_DESKTOP changed since latest warm dispatch receipt')
    elif runtime_probe_status_changed:
        status = 'runtime_probe_status_drift'
        in_sync = False
        summary = 'The latest warm-dispatch receipt was emitted under a different resident warm-path probe result than the one currently cached for the daemon.'
        reasons = ['resident warm-runtime probe result changed since latest warm dispatch receipt']
        if current_probe_status and observed_probe_status:
            reasons.append(f"resident warm-runtime probe moved from {observed_probe_status} to {current_probe_status}")
        if runtime_probe_failure_changed:
            reasons.append('resident warm-runtime probe crossed the success/failure boundary since latest warm dispatch receipt')
    elif runtime_probe_freshness_attention_changed:
        status = 'runtime_probe_freshness_drift'
        in_sync = False
        summary = "The latest warm-dispatch receipt no longer matches the daemon's current warm-runtime probe freshness posture."
        reasons = ['resident warm-runtime probe freshness attention changed since latest warm dispatch receipt']
    elif runtime_probe_latency_attention_changed:
        status = 'runtime_probe_latency_drift'
        in_sync = False
        summary = "The latest warm-dispatch receipt no longer matches the daemon's current warm-runtime probe latency posture."
        reasons = ['resident warm-runtime probe latency attention changed since latest warm dispatch receipt']
    else:
        status = 'in_sync'
        in_sync = True
        summary = 'The latest warm-dispatch receipt still matches the current cached resident-runtime epoch and desktop session.'
        reasons = []

    return {
        'status': status,
        'in_sync': in_sync,
        'summary': summary,
        'reasons': reasons,
        'epoch_changed': epoch_changed,
        'pid_changed': pid_changed,
        'runtime_contract_changed': runtime_contract_changed,
        'watcher_set_changed': watcher_set_changed,
        'desktop_session_contract_changed': desktop_session_contract_changed,
        'runtime_probe_status_changed': runtime_probe_status_changed,
        'runtime_probe_failure_changed': runtime_probe_failure_changed,
        'runtime_probe_freshness_attention_changed': runtime_probe_freshness_attention_changed,
        'runtime_probe_latency_attention_changed': runtime_probe_latency_attention_changed,
        'current_probe_status': current_probe_status,
        'observed_probe_status': observed_probe_status,
        'current_probe_freshness_status': current_probe_freshness_status,
        'observed_probe_freshness_status': observed_probe_freshness_status,
        'current_probe_latency_status': current_probe_latency_status,
        'observed_probe_latency_status': observed_probe_latency_status,
        'current_probe_refresh_attention': current_probe_refresh_attention,
        'observed_probe_refresh_attention': observed_probe_refresh_attention,
        'current_probe_latency_attention': current_probe_latency_attention,
        'observed_probe_latency_attention': observed_probe_latency_attention,
        'desktop_session_contract': desktop_session_status,
        'current_witness': current_witness,
        'observed_witness': observed_witness,
        'current_runtime_epoch_id': current_epoch,
        'observed_runtime_epoch_id': observed_epoch,
        'current_pid': current_pid,
        'observed_pid': observed_pid,
        'current_runtime_contract_digest': current_contract_digest,
        'observed_runtime_contract_digest': observed_contract_digest,
        'current_watchers': current_watchers,
        'observed_watchers': observed_watchers,
        'current_desktop_session_contract_digest': current_desktop_session_digest,
        'observed_desktop_session_contract_digest': observed_desktop_session_digest,
    }

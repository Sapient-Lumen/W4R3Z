from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Mapping

from vhk.system.event_bus import emit_bus_event

_INTERNAL_RUNTIME_PROBE_EVENT = 'vhk.runtime.probe'


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


def runtime_dispatch_probe_roots(*, project_root: Path, xdg_runtime_dir: str | None = None) -> list[Path]:
    roots: list[Path] = []
    runtime_dir = _clean(xdg_runtime_dir) or _clean(os.environ.get('XDG_RUNTIME_DIR'))
    if runtime_dir:
        roots.append(Path(runtime_dir).expanduser() / 'vhk' / 'runtime_probes')
    roots.append(Path(project_root).expanduser().resolve() / '.vhk' / 'runtime_probes')
    deduped: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        key = str(root)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(root)
    return deduped


def allocate_runtime_dispatch_probe_ack_path(*, project_root: Path, xdg_runtime_dir: str | None = None, probe_id: str | None = None) -> tuple[str, Path]:
    probe_id = _clean(probe_id) or uuid.uuid4().hex
    root = runtime_dispatch_probe_roots(project_root=project_root, xdg_runtime_dir=xdg_runtime_dir)[0]
    root.mkdir(parents=True, exist_ok=True)
    return probe_id, root / f'{probe_id}.json'


def is_allowed_runtime_dispatch_probe_ack_path(path: str | Path | None, *, project_root: Path, xdg_runtime_dir: str | None = None) -> bool:
    if path is None:
        return False
    try:
        resolved = Path(path).expanduser().resolve(strict=False)
    except Exception:
        return False
    for root in runtime_dispatch_probe_roots(project_root=project_root, xdg_runtime_dir=xdg_runtime_dir):
        try:
            resolved.relative_to(root.resolve(strict=False))
            return True
        except Exception:
            continue
    return False


def _safe_unlink(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        return
    except Exception:
        return


def probe_runtime_dispatch_path(
    *,
    project_root: Path,
    bus_socket: str | Path,
    timeout_s: float = 0.75,
    event_name: str = _INTERNAL_RUNTIME_PROBE_EVENT,
    xdg_runtime_dir: str | None = None,
) -> dict[str, Any]:
    bus_socket_path = Path(bus_socket)
    probe_id, ack_path = allocate_runtime_dispatch_probe_ack_path(project_root=project_root, xdg_runtime_dir=xdg_runtime_dir)
    _safe_unlink(ack_path)
    emitted_at = time.time()
    started = time.perf_counter()
    payload: dict[str, Any] = {
        'available': True,
        'attempted': True,
        'status': 'pending',
        'summary': 'Runtime dispatch probe has not completed yet.',
        'probe_id': probe_id,
        'event_name': event_name,
        'bus_socket': str(bus_socket_path),
        'ack_path': str(ack_path),
        'timeout_s': float(timeout_s),
        'emit_latency_ms': None,
        'roundtrip_latency_ms': None,
        'ack': None,
        'ack_exists': False,
        'error': None,
    }
    try:
        emit_started = time.perf_counter()
        emit_bus_event(
            bus_socket_path,
            event_name,
            {'probe_id': probe_id, 'ack_path': str(ack_path), 'sent_at': emitted_at},
        )
        payload['emit_latency_ms'] = round((time.perf_counter() - emit_started) * 1000.0, 3)
    except Exception as exc:
        payload['status'] = 'emit_failed'
        payload['summary'] = 'The warm-runtime dispatch probe could not emit to the resident bus socket.'
        payload['error'] = str(exc)
        return payload

    deadline = time.perf_counter() + max(float(timeout_s), 0.01)
    while time.perf_counter() < deadline:
        if ack_path.exists():
            payload['ack_exists'] = True
            try:
                ack_payload = json.loads(ack_path.read_text(encoding='utf-8'))
            except Exception as exc:
                payload['status'] = 'invalid_ack'
                payload['summary'] = 'The resident runtime wrote a malformed dispatch-probe acknowledgment.'
                payload['error'] = str(exc)
                return payload
            finally:
                _safe_unlink(ack_path)
            payload['ack'] = ack_payload
            payload['roundtrip_latency_ms'] = round((time.perf_counter() - started) * 1000.0, 3)
            payload['status'] = 'ok'
            payload['summary'] = 'The emit -> socket -> resident busd path completed a bounded internal round trip.'
            return payload
        time.sleep(0.02)

    _safe_unlink(ack_path)
    payload['status'] = 'ack_timeout'
    payload['summary'] = 'The warm-runtime dispatch probe reached the bus socket, but no bounded acknowledgment came back from the resident daemon.'
    payload['roundtrip_latency_ms'] = round((time.perf_counter() - started) * 1000.0, 3)
    return payload


def summarize_runtime_dispatch_probe(
    *,
    shell_env: Mapping[str, Any] | None = None,
    probe_payload: Mapping[str, Any] | None = None,
    expected_watchers: list[str] | tuple[str, ...] | None = None,
    expected_runtime_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    shell_env = dict(shell_env or {})
    probe = dict(probe_payload or {})
    status = _clean(probe.get('status')) or 'unavailable'
    ack = dict(probe.get('ack') or {})
    ack_env = dict(ack.get('environment') or {})
    variables = ['DISPLAY', 'XAUTHORITY', 'DBUS_SESSION_BUS_ADDRESS', 'XDG_RUNTIME_DIR', 'I3SOCK']
    shell = {name: _clean(shell_env.get(name)) for name in variables}
    daemon = {name: _clean(ack_env.get(name)) for name in variables}
    mismatched: list[dict[str, Any]] = []
    missing_from_daemon: list[str] = []
    for name in variables:
        shell_value = shell.get(name)
        if not shell_value:
            continue
        daemon_value = daemon.get(name)
        if daemon_value is None:
            missing_from_daemon.append(name)
        elif daemon_value != shell_value:
            mismatched.append({'variable': name, 'shell_value': shell_value, 'daemon_value': daemon_value})
    env_in_sync = None if status != 'ok' else (not missing_from_daemon and not mismatched)

    expected = _normalize_name_list(expected_watchers)
    daemon_watchers = _normalize_name_list(ack.get('watchers'))
    missing_expected_watchers = [name for name in expected if name not in daemon_watchers]
    extra_watchers = [name for name in daemon_watchers if name not in expected]
    watchers_in_sync = None if status != 'ok' or not expected else (not missing_expected_watchers)

    expected_contract = dict(expected_runtime_contract or {})
    daemon_contract = dict(ack.get('runtime_contract') or {})
    daemon_runtime_state = dict(ack.get('runtime_state') or {})
    expected_contract_digest = _clean(expected_contract.get('digest'))
    daemon_contract_digest = _clean(daemon_contract.get('digest'))
    runtime_contract_in_sync = None if status != 'ok' or not expected_contract_digest else (daemon_contract_digest == expected_contract_digest)

    if status == 'ok':
        drift_bits: list[str] = []
        if env_in_sync is False:
            if missing_from_daemon:
                drift_bits.append('missing session vars: ' + ', '.join(missing_from_daemon))
            if mismatched:
                drift_bits.append('mismatched session vars: ' + ', '.join(item['variable'] for item in mismatched))
        if watchers_in_sync is False:
            drift_bits.append('missing watchers: ' + ', '.join(missing_expected_watchers))
        if runtime_contract_in_sync is False:
            drift_bits.append('runtime contract digest drift')
        if drift_bits:
            summary = 'The resident bus daemon acknowledged the probe, but its live runtime contract drifted from the generated stack (' + '; '.join(drift_bits) + ').'
        else:
            summary = 'The resident bus daemon acknowledged the probe and reported the same session bridge variables plus the expected watcher contract as the live stack.'
    elif status == 'emit_failed':
        summary = 'The dispatch probe could not emit to the resident bus socket.'
    elif status == 'ack_timeout':
        summary = 'The dispatch probe reached the bus socket but the resident daemon did not answer within the bounded timeout.'
    elif status == 'invalid_ack':
        summary = 'The resident daemon answered the dispatch probe with malformed data.'
    else:
        summary = 'The resident runtime dispatch probe was unavailable.'
    return {
        'available': bool(probe),
        'status': status,
        'ok': status == 'ok',
        'env_in_sync': env_in_sync,
        'watchers_in_sync': watchers_in_sync,
        'runtime_contract_in_sync': runtime_contract_in_sync,
        'summary': summary,
        'roundtrip_latency_ms': probe.get('roundtrip_latency_ms'),
        'ack_pid': ack.get('pid'),
        'shell': shell,
        'daemon': daemon,
        'missing_from_daemon': missing_from_daemon,
        'mismatched': mismatched,
        'expected_watchers': expected,
        'daemon_watchers': daemon_watchers,
        'missing_expected_watchers': missing_expected_watchers,
        'extra_watchers': extra_watchers,
        'expected_runtime_contract_digest': expected_contract_digest,
        'daemon_runtime_contract_digest': daemon_contract_digest,
        'daemon_runtime_contract': daemon_contract,
        'daemon_runtime_state': daemon_runtime_state,
        'daemon_runtime_epoch_id': _clean(daemon_runtime_state.get('runtime_epoch_id')),
        'daemon_reload_count': daemon_runtime_state.get('reload_count'),
        'daemon_last_reload_reason': _clean(daemon_runtime_state.get('last_reload_reason')),
        'daemon_last_reload_at': daemon_runtime_state.get('last_reload_at'),
        'daemon_started_at': daemon_runtime_state.get('started_at'),
        'probe_id': probe.get('probe_id'),
        'event_name': probe.get('event_name'),
    }

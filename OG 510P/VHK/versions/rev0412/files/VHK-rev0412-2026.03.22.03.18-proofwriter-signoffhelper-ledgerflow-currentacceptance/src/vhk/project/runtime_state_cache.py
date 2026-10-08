from __future__ import annotations

import json
import hashlib
import os
import time
from pathlib import Path
from typing import Any, Mapping


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



def summarize_runtime_instance_witness_from_cache(*, project_root: str | Path, xdg_runtime_dir: str | None = None) -> dict[str, Any]:
    payload, path = load_runtime_state_cache(project_root=project_root, xdg_runtime_dir=xdg_runtime_dir)
    runtime_state = dict(payload.get('runtime_state') or {})
    runtime_contract = dict(payload.get('runtime_contract') or {})
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

    epoch_changed = bool(current_epoch and observed_epoch and current_epoch != observed_epoch)
    pid_changed = current_pid is not None and observed_pid is not None and current_pid != observed_pid
    runtime_contract_changed = bool(current_contract_digest and observed_contract_digest and current_contract_digest != observed_contract_digest)
    watcher_set_changed = bool(current_watchers and observed_watchers and current_watchers != observed_watchers)

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
    else:
        status = 'in_sync'
        in_sync = True
        summary = 'The latest warm-dispatch receipt still matches the current cached resident-runtime epoch.'
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
    }

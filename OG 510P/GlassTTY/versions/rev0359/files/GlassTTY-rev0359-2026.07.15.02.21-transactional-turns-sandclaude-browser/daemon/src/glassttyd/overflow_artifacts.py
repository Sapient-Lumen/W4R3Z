from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

JsonDict = dict[str, Any]


DEFAULT_HOME = Path(os.environ.get('GLASSTTY_HOME', Path.home() / '.local' / 'share' / 'glasstty'))


def default_home(home: Path | None = None) -> Path:
    return home or Path(os.environ.get('GLASSTTY_HOME', DEFAULT_HOME))


def overflow_latest_path(home: Path | None = None) -> Path:
    return default_home(home) / 'state' / 'latest' / 'oversized-host-outbound.json'


def overflow_fixtures_dir(home: Path | None = None) -> Path:
    return default_home(home) / 'state' / 'fixtures'


def read_json_if_exists(path: Path | None) -> JsonDict | None:
    if path is None or not path.exists():
        return None
    return json.loads(path.read_text(encoding='utf-8'))


def latest_overflow_summary(home: Path | None = None) -> JsonDict | None:
    return read_json_if_exists(overflow_latest_path(home))


def _parse_iso_datetime(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip()
    if raw.endswith('Z'):
        raw = raw[:-1] + '+00:00'
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _sort_key(entry: JsonDict) -> tuple[float, str]:
    captured = _parse_iso_datetime(entry.get('captured_at'))
    if captured is not None:
        return (captured.timestamp(), str(entry.get('path') or ''))
    mtime = entry.get('mtime')
    if isinstance(mtime, (int, float)):
        return (float(mtime), str(entry.get('path') or ''))
    return (0.0, str(entry.get('path') or ''))


def list_overflow_artifacts(home: Path | None = None) -> list[JsonDict]:
    fixtures_dir = overflow_fixtures_dir(home)
    entries: list[JsonDict] = []
    for path in fixtures_dir.glob('oversized-host-outbound-*.json'):
        stat = path.stat()
        entry: JsonDict = {
            'path': str(path),
            'name': path.name,
            'size_on_disk_bytes': stat.st_size,
            'mtime': stat.st_mtime,
            'parse_ok': False,
        }
        payload = read_json_if_exists(path)
        if isinstance(payload, dict):
            entry['parse_ok'] = True
            entry['kind'] = payload.get('kind')
            entry['captured_at'] = payload.get('captured_at')
            budget = payload.get('budget') if isinstance(payload.get('budget'), dict) else None
            if isinstance(budget, dict):
                entry['reported_size_bytes'] = budget.get('size_bytes')
                entry['limit_bytes'] = budget.get('limit_bytes')
                entry['fits'] = budget.get('fits')
            message = payload.get('message') if isinstance(payload.get('message'), dict) else None
            if isinstance(message, dict):
                entry['message_type'] = message.get('type')
                entry['request_id'] = message.get('request_id')
                entry['tab_id'] = message.get('tab_id')
        entries.append(entry)
    return sorted(entries, key=_sort_key, reverse=True)


def summarize_overflow_inventory(home: Path | None = None) -> JsonDict:
    latest = latest_overflow_summary(home)
    latest_path = overflow_latest_path(home)
    artifacts = list_overflow_artifacts(home)
    total_disk_bytes = sum(int(entry.get('size_on_disk_bytes') or 0) for entry in artifacts)
    total_reported_message_bytes = sum(int(entry.get('reported_size_bytes') or 0) for entry in artifacts if isinstance(entry.get('reported_size_bytes'), int))
    message_type_counts: dict[str, int] = {}
    for entry in artifacts:
        key = str(entry.get('message_type') or 'unknown')
        message_type_counts[key] = message_type_counts.get(key, 0) + 1
    latest_artifact_path = latest.get('artifact_path') if isinstance(latest, dict) else None
    newest = artifacts[0] if artifacts else None
    oldest = artifacts[-1] if artifacts else None
    return {
        'latest_path': str(latest_path),
        'latest_exists': latest_path.exists(),
        'artifact_count': len(artifacts),
        'total_disk_bytes': total_disk_bytes,
        'total_reported_message_bytes': total_reported_message_bytes,
        'message_type_counts': message_type_counts,
        'newest_captured_at': newest.get('captured_at') if isinstance(newest, dict) else None,
        'oldest_captured_at': oldest.get('captured_at') if isinstance(oldest, dict) else None,
        'latest_artifact_path': latest_artifact_path,
        'latest_artifact_exists': bool(isinstance(latest_artifact_path, str) and latest_artifact_path and Path(latest_artifact_path).expanduser().exists()),
        'latest_artifact_in_inventory': bool(isinstance(latest_artifact_path, str) and latest_artifact_path and any(entry.get('path') == latest_artifact_path for entry in artifacts)),
        'artifacts': artifacts,
    }


def compact_overflow_inventory_summary(home: Path | None = None, *, recent_limit: int = 3) -> JsonDict:
    inventory = summarize_overflow_inventory(home)
    recent_limit = max(0, int(recent_limit))
    recent = []
    for entry in inventory.get('artifacts') or []:
        if not isinstance(entry, dict):
            continue
        recent.append({
            'path': entry.get('path'),
            'name': entry.get('name'),
            'captured_at': entry.get('captured_at'),
            'message_type': entry.get('message_type'),
            'request_id': entry.get('request_id'),
            'tab_id': entry.get('tab_id'),
            'reported_size_bytes': entry.get('reported_size_bytes'),
            'size_on_disk_bytes': entry.get('size_on_disk_bytes'),
            'parse_ok': entry.get('parse_ok'),
        })
        if len(recent) >= recent_limit:
            break
    return {
        'latest_path': inventory.get('latest_path'),
        'latest_exists': inventory.get('latest_exists'),
        'artifact_count': inventory.get('artifact_count'),
        'total_disk_bytes': inventory.get('total_disk_bytes'),
        'total_reported_message_bytes': inventory.get('total_reported_message_bytes'),
        'message_type_counts': inventory.get('message_type_counts'),
        'newest_captured_at': inventory.get('newest_captured_at'),
        'oldest_captured_at': inventory.get('oldest_captured_at'),
        'latest_artifact_path': inventory.get('latest_artifact_path'),
        'latest_artifact_exists': inventory.get('latest_artifact_exists'),
        'latest_artifact_in_inventory': inventory.get('latest_artifact_in_inventory'),
        'recent_limit': recent_limit,
        'recent_artifacts': recent,
    }


def plan_overflow_prune(
    *,
    home: Path | None = None,
    keep: int = 10,
    max_age_days: float | None = None,
    max_disk_bytes: int | None = None,
    keep_latest_artifact: bool = True,
    now: datetime | None = None,
) -> JsonDict:
    keep = max(0, int(keep))
    now = now.astimezone(timezone.utc) if now else datetime.now(timezone.utc)
    inventory = summarize_overflow_inventory(home)
    artifacts = [dict(entry) for entry in inventory.get('artifacts') or [] if isinstance(entry, dict)]
    latest_artifact_path = inventory.get('latest_artifact_path') if isinstance(inventory.get('latest_artifact_path'), str) else None
    protected_paths = {latest_artifact_path} if keep_latest_artifact and latest_artifact_path else set()
    planned_deletes: dict[str, JsonDict] = {}

    for index, entry in enumerate(artifacts):
        reasons: list[str] = []
        if index >= keep:
            reasons.append(f'beyond-keep:{keep}')
        captured = _parse_iso_datetime(entry.get('captured_at'))
        if max_age_days is not None and captured is not None:
            age_days = (now - captured).total_seconds() / 86400.0
            entry['age_days'] = round(age_days, 3)
            if age_days > max_age_days:
                reasons.append(f'older-than-days:{max_age_days:g}')
        if reasons:
            entry['prune_reasons'] = reasons
            planned_deletes[str(entry['path'])] = entry

    retained = [entry for entry in artifacts if str(entry.get('path')) not in planned_deletes and str(entry.get('path')) not in protected_paths]
    protected = [entry for entry in artifacts if str(entry.get('path')) in protected_paths]
    if max_disk_bytes is not None:
        retained_total = sum(int(entry.get('size_on_disk_bytes') or 0) for entry in artifacts if str(entry.get('path')) not in planned_deletes)
        if retained_total > max_disk_bytes:
            for entry in sorted(retained, key=_sort_key):
                if retained_total <= max_disk_bytes:
                    break
                path = str(entry.get('path'))
                if path in protected_paths:
                    continue
                payload = planned_deletes.setdefault(path, entry)
                reasons = list(payload.get('prune_reasons') or [])
                reasons.append(f'exceeds-max-disk-bytes:{max_disk_bytes}')
                payload['prune_reasons'] = reasons
                retained_total -= int(entry.get('size_on_disk_bytes') or 0)

    delete_entries = sorted(planned_deletes.values(), key=_sort_key)
    keep_entries = [entry for entry in artifacts if str(entry.get('path')) not in planned_deletes]
    return {
        'keep': keep,
        'max_age_days': max_age_days,
        'max_disk_bytes': max_disk_bytes,
        'keep_latest_artifact': keep_latest_artifact,
        'inventory': inventory,
        'protected_paths': sorted(path for path in protected_paths if path),
        'delete_count': len(delete_entries),
        'delete_total_disk_bytes': sum(int(entry.get('size_on_disk_bytes') or 0) for entry in delete_entries),
        'keep_count': len(keep_entries),
        'keep_total_disk_bytes': sum(int(entry.get('size_on_disk_bytes') or 0) for entry in keep_entries),
        'delete': delete_entries,
        'keep_entries': keep_entries,
    }


def apply_overflow_prune(plan: JsonDict) -> JsonDict:
    deleted: list[JsonDict] = []
    missing: list[JsonDict] = []
    freed_bytes = 0
    for entry in plan.get('delete') or []:
        if not isinstance(entry, dict):
            continue
        path_value = entry.get('path')
        if not isinstance(path_value, str) or not path_value:
            continue
        path = Path(path_value).expanduser()
        if not path.exists():
            missing.append({'path': str(path), 'size_on_disk_bytes': entry.get('size_on_disk_bytes')})
            continue
        size = path.stat().st_size
        path.unlink()
        freed_bytes += size
        deleted.append({'path': str(path), 'size_on_disk_bytes': size, 'prune_reasons': entry.get('prune_reasons')})
    return {
        'deleted_count': len(deleted),
        'deleted_total_disk_bytes': freed_bytes,
        'deleted': deleted,
        'missing': missing,
    }

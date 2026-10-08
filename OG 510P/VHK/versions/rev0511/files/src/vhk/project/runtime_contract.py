from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from vhk.core.models import Project
from vhk.project.loader import load_project


_RUNTIME_CONTRACT_SCHEMA_VERSION = 1


def _semantic_project_payload(project: Project) -> dict[str, Any]:
    payload = project.model_dump(mode='json', by_alias=True, exclude_none=True)
    payload.pop('root_dir', None)
    return payload



def _digest_payload(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return hashlib.sha256(encoded.encode('utf-8')).hexdigest()



def summarize_project_runtime_contract(project: Project) -> dict[str, Any]:
    semantic_payload = _semantic_project_payload(project)
    digest = _digest_payload(semantic_payload)
    macros = semantic_payload.get('macros') or {}
    bus_watchers = semantic_payload.get('bus_watchers') or []
    settings = semantic_payload.get('settings') or {}
    return {
        'schema_version': _RUNTIME_CONTRACT_SCHEMA_VERSION,
        'digest': digest,
        'project_name': str(project.name),
        'macro_count': len(macros) if isinstance(macros, dict) else None,
        'macro_names': sorted(str(name) for name in (macros.keys() if isinstance(macros, dict) else [])),
        'bus_watcher_count': len(bus_watchers) if isinstance(bus_watchers, list) else None,
        'bus_watcher_names': sorted(
            str((item or {}).get('name')).strip()
            for item in bus_watchers
            if isinstance(item, dict) and str((item or {}).get('name')).strip()
        ) if isinstance(bus_watchers, list) else [],
        'bus_reload_event': str(settings.get('bus_reload_event')).strip() if settings.get('bus_reload_event') is not None else None,
        'bus_stop_event': str(settings.get('bus_stop_event')).strip() if settings.get('bus_stop_event') is not None else None,
    }



def summarize_project_runtime_contract_from_root(project_root: str | Path) -> dict[str, Any]:
    project = load_project(Path(project_root).expanduser().resolve())
    return summarize_project_runtime_contract(project)

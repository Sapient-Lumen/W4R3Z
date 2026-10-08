from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from vhk.project.macro_files import resolve_macro_path, resolve_macro_recording_sidecar_path


def _file_info(path: Path, root: Path) -> dict[str, Any]:
    payload: dict[str, Any] = {
        'path': str(path.relative_to(root)) if path.exists() or str(path).startswith(str(root)) else str(path),
        'exists': path.exists(),
        'sha256': None,
        'size': None,
        'mtime': None,
    }
    if not path.exists() or not path.is_file():
        return payload
    payload['size'] = path.stat().st_size
    payload['mtime'] = path.stat().st_mtime
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(65536), b''):
            h.update(chunk)
    payload['sha256'] = h.hexdigest()
    return payload


def _recording_freshness(source: dict[str, Any], recording: dict[str, Any]) -> str:
    if not recording.get('exists'):
        return 'missing_recording_sidecar'
    if not source.get('exists'):
        return 'missing_macro_source'
    src_m = float(source.get('mtime') or 0)
    rec_m = float(recording.get('mtime') or 0)
    if src_m > rec_m:
        return 'source_newer_than_recording'
    if rec_m > src_m:
        return 'recording_newer_than_source'
    return 'aligned'


def macro_proof_contract_digest(contract: Mapping[str, Any] | None) -> str | None:
    if not contract:
        return None
    stable = {
        'macro_name': contract.get('macro_name'),
        'source': {
            'path': ((contract.get('source') or {}).get('path')),
            'exists': ((contract.get('source') or {}).get('exists')),
            'sha256': ((contract.get('source') or {}).get('sha256')),
        },
        'recording': {
            'path': ((contract.get('recording') or {}).get('path')),
            'exists': ((contract.get('recording') or {}).get('exists')),
            'sha256': ((contract.get('recording') or {}).get('sha256')),
            'freshness_status': ((contract.get('recording') or {}).get('freshness_status')),
        },
    }
    return hashlib.sha256(json.dumps(stable, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


def summarize_macro_proof_contract(project_root: str | Path, macro_name: str) -> dict[str, Any]:
    root = Path(project_root).resolve()
    source_path, source_rel = resolve_macro_path(root, macro_name)
    recording_path, recording_rel = resolve_macro_recording_sidecar_path(root, macro_name)
    source = _file_info(source_path, root)
    source['path'] = source_rel
    recording = _file_info(recording_path, root)
    recording['path'] = recording_rel
    recording['freshness_status'] = _recording_freshness(source, recording)
    contract: dict[str, Any] = {
        'macro_name': macro_name,
        'source': source,
        'recording': recording,
    }
    contract['digest'] = macro_proof_contract_digest(contract)
    return contract


def compare_macro_proof_contract(current: Mapping[str, Any] | None, observed: Mapping[str, Any] | None) -> dict[str, Any]:
    current_contract = dict(current or {})
    observed_contract = dict(observed or {})
    current_digest = str(current_contract.get('digest') or macro_proof_contract_digest(current_contract) or '').strip() or None
    observed_digest = str(observed_contract.get('digest') or macro_proof_contract_digest(observed_contract) or '').strip() or None
    in_sync = bool(current_digest and observed_digest and current_digest == observed_digest)
    source_changed = False
    recording_changed = False
    if current_contract or observed_contract:
        source_changed = ((current_contract.get('source') or {}).get('sha256') != (observed_contract.get('source') or {}).get('sha256')) or ((current_contract.get('source') or {}).get('exists') != (observed_contract.get('source') or {}).get('exists'))
        recording_changed = ((current_contract.get('recording') or {}).get('sha256') != (observed_contract.get('recording') or {}).get('sha256')) or ((current_contract.get('recording') or {}).get('exists') != (observed_contract.get('recording') or {}).get('exists')) or ((current_contract.get('recording') or {}).get('freshness_status') != (observed_contract.get('recording') or {}).get('freshness_status'))
    reasons: list[str] = []
    status = 'in_sync'
    summary = 'The latest replay proof still matches the current macro source and recorder contract.'
    if not observed_contract:
        status = 'missing'
        summary = 'The latest run predates contract-bound replay proof and should be rerun before treating replay as current.'
        reasons.append('run_start macro_proof_contract missing')
    elif not observed_digest:
        status = 'missing_digest'
        summary = 'The latest run did not capture a comparable replay-proof digest and should be rerun.'
        reasons.append('run_start macro_proof_contract digest missing')
    elif not in_sync:
        status = 'drifted'
        summary = 'The latest matching replay proof no longer matches the current macro or recorder contract.'
        if source_changed:
            reasons.append('macro source changed since latest healthy replay')
        if recording_changed:
            reasons.append('recorder sidecar or freshness changed since latest healthy replay')
        if not reasons:
            reasons.append('macro proof contract digest changed')
    return {
        'status': status,
        'in_sync': in_sync,
        'summary': summary,
        'reasons': reasons,
        'source_changed': source_changed,
        'recording_changed': recording_changed,
        'current_digest': current_digest,
        'observed_digest': observed_digest,
        'current_contract': current_contract,
        'observed_contract': observed_contract,
    }

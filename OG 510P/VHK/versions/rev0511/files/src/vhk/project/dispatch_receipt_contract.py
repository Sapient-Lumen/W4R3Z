from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from vhk.project.macro_proof_contract import summarize_macro_proof_contract


def _canonical_dispatch_target_selector(selector: Mapping[str, Any] | None) -> dict[str, Any] | None:
    normalized: dict[str, Any] = {}
    for key, value in dict(selector or {}).items():
        if value is None or value == '' or value == [] or value == {}:
            continue
        if isinstance(value, bool) and value is False:
            continue
        normalized[str(key)] = value
    return normalized or None


def _canonical_dispatch_receipt_contract(contract: Mapping[str, Any] | None) -> dict[str, Any]:
    payload = dict(contract or {})
    dispatch_contract = dict(payload.get('dispatch_contract') or {})
    desktop_target = dict(payload.get('desktop_target') or {})
    return {
        'macro_name': payload.get('macro_name'),
        'bus_event': payload.get('bus_event'),
        'preferred_execution_mode': payload.get('preferred_execution_mode'),
        'dispatch_contract': {
            'bus_payload_minimal': dispatch_contract.get('bus_payload_minimal'),
        },
        'desktop_target': {
            'selector_source_id': desktop_target.get('selector_source_id'),
            'selector': _canonical_dispatch_target_selector(desktop_target.get('selector')),
        },
        'macro_proof_contract_digest': payload.get('macro_proof_contract_digest'),
    }


def dispatch_receipt_contract_digest(contract: Mapping[str, Any] | None) -> str | None:
    if not contract:
        return None
    stable = _canonical_dispatch_receipt_contract(contract)
    return hashlib.sha256(json.dumps(stable, sort_keys=True, separators=(",", ":")).encode('utf-8')).hexdigest()


def summarize_dispatch_receipt_contract(project_root: str | Path, macro_name: str, *, bus_event: str, gate_payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    root = Path(project_root).resolve()
    gate = dict(gate_payload or {})
    dispatch_contract = dict(gate.get('dispatch_contract') or {})
    readiness = dict(gate.get('dispatch_readiness') or {})
    desktop_target = dict(readiness.get('desktop_target') or {})
    try:
        macro_proof_contract = summarize_macro_proof_contract(root, macro_name)
    except Exception:
        macro_proof_contract = {}
    contract: dict[str, Any] = {
        'macro_name': macro_name,
        'bus_event': str(bus_event or '').strip() or None,
        'preferred_execution_mode': gate.get('preferred_execution_mode'),
        'dispatch_contract': {
            'bus_payload_minimal': dispatch_contract.get('bus_payload_minimal'),
        },
        'desktop_target': {
            'selector_source_id': desktop_target.get('selector_source_id'),
            'selector': _canonical_dispatch_target_selector(desktop_target.get('selector')),
        },
        'macro_proof_contract_digest': macro_proof_contract.get('digest'),
    }
    contract['digest'] = dispatch_receipt_contract_digest(contract)
    return contract


def compare_dispatch_receipt_contract(current: Mapping[str, Any] | None, observed: Mapping[str, Any] | None) -> dict[str, Any]:
    current_contract = _canonical_dispatch_receipt_contract(current)
    observed_contract = _canonical_dispatch_receipt_contract(observed)
    current_digest = dispatch_receipt_contract_digest(current_contract)
    observed_digest = dispatch_receipt_contract_digest(observed_contract)
    in_sync = bool(current_digest and observed_digest and current_digest == observed_digest)
    reasons: list[str] = []
    status = 'in_sync'
    summary = 'The latest warm-dispatch receipt still matches the current macro and dispatch contract.'
    bus_event_changed = (current_contract.get('bus_event') != observed_contract.get('bus_event')) if (current_contract or observed_contract) else False
    execution_mode_changed = (current_contract.get('preferred_execution_mode') != observed_contract.get('preferred_execution_mode')) if (current_contract or observed_contract) else False
    payload_changed = ((current_contract.get('dispatch_contract') or {}).get('bus_payload_minimal') != (observed_contract.get('dispatch_contract') or {}).get('bus_payload_minimal')) if (current_contract or observed_contract) else False
    desktop_target_changed = ((current_contract.get('desktop_target') or {}).get('selector_source_id') != (observed_contract.get('desktop_target') or {}).get('selector_source_id')) or ((current_contract.get('desktop_target') or {}).get('selector') != (observed_contract.get('desktop_target') or {}).get('selector')) if (current_contract or observed_contract) else False
    macro_proof_contract_changed = (current_contract.get('macro_proof_contract_digest') != observed_contract.get('macro_proof_contract_digest')) if (current_contract or observed_contract) else False
    if not observed_contract:
        status = 'missing'
        summary = 'The latest warm-dispatch receipt predates contract-bound dispatch proof and should be refreshed before treating dispatch history as current.'
        reasons.append('dispatch receipt contract missing')
    elif not observed_digest:
        status = 'missing_digest'
        summary = 'The latest warm-dispatch receipt did not capture a comparable dispatch-proof digest and should be refreshed.'
        reasons.append('dispatch receipt contract digest missing')
    elif not in_sync:
        status = 'drifted'
        summary = 'The latest warm-dispatch receipt no longer matches the current macro or warm-dispatch contract.'
        if macro_proof_contract_changed:
            reasons.append('macro or recorder contract changed since latest warm dispatch receipt')
        if bus_event_changed:
            reasons.append('warm dispatch bus event changed since latest receipt')
        if execution_mode_changed:
            reasons.append('preferred execution mode changed since latest receipt')
        if payload_changed:
            reasons.append('minimal dispatch payload changed since latest receipt')
        if desktop_target_changed:
            reasons.append('desktop target selector changed since latest receipt')
        if not reasons:
            reasons.append('dispatch receipt contract digest changed')
    return {
        'status': status,
        'in_sync': in_sync,
        'summary': summary,
        'reasons': reasons,
        'bus_event_changed': bus_event_changed,
        'execution_mode_changed': execution_mode_changed,
        'payload_changed': payload_changed,
        'desktop_target_changed': desktop_target_changed,
        'macro_proof_contract_changed': macro_proof_contract_changed,
        'current_digest': current_digest,
        'observed_digest': observed_digest,
        'current_contract': current_contract,
        'observed_contract': observed_contract,
    }

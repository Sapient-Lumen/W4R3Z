from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


def runtime_acceptance_contract_digest(contract: Mapping[str, Any] | None) -> str | None:
    if not contract:
        return None
    stable = {
        'macro_name': contract.get('macro_name'),
        'runtime_posture_id': contract.get('runtime_posture_id'),
        'preferred_execution_mode': contract.get('preferred_execution_mode'),
        'replay_posture_id': contract.get('replay_posture_id'),
        'macro_proof_contract_digest': contract.get('macro_proof_contract_digest'),
        'dispatch_receipt_contract_digest': contract.get('dispatch_receipt_contract_digest'),
        'dispatch_history_posture_id': contract.get('dispatch_history_posture_id'),
        'dispatch_history_attention_id': contract.get('dispatch_history_attention_id'),
        'resident_runtime_epoch_id': contract.get('resident_runtime_epoch_id'),
        'resident_runtime_contract_digest': contract.get('resident_runtime_contract_digest'),
        'desktop_session_contract_digest': contract.get('desktop_session_contract_digest'),
        'warm_runtime_probe_latency_attention_id': contract.get('warm_runtime_probe_latency_attention_id'),
        'warm_runtime_probe_freshness_attention_id': contract.get('warm_runtime_probe_freshness_attention_id'),
    }
    return hashlib.sha256(json.dumps(stable, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


def summarize_runtime_acceptance_contract(
    *,
    macro_name: str,
    runtime_posture_id: str | None,
    preferred_execution_mode: str | None,
    replay_posture_id: str | None,
    macro_proof_contract_digest: str | None,
    dispatch_receipt_contract_digest: str | None,
    dispatch_history_posture_id: str | None = None,
    dispatch_history_attention_id: str | None = None,
    resident_runtime_epoch_id: str | None = None,
    resident_runtime_contract_digest: str | None = None,
    desktop_session_contract_digest: str | None = None,
    warm_runtime_probe_latency_attention_id: str | None = None,
    warm_runtime_probe_freshness_attention_id: str | None = None,
) -> dict[str, Any]:
    contract: dict[str, Any] = {
        'macro_name': str(macro_name or '').strip() or None,
        'runtime_posture_id': str(runtime_posture_id or '').strip() or None,
        'preferred_execution_mode': str(preferred_execution_mode or '').strip() or None,
        'replay_posture_id': str(replay_posture_id or '').strip() or None,
        'macro_proof_contract_digest': str(macro_proof_contract_digest or '').strip() or None,
        'dispatch_receipt_contract_digest': str(dispatch_receipt_contract_digest or '').strip() or None,
        'dispatch_history_posture_id': str(dispatch_history_posture_id or '').strip() or None,
        'dispatch_history_attention_id': str(dispatch_history_attention_id or '').strip() or None,
        'resident_runtime_epoch_id': str(resident_runtime_epoch_id or '').strip() or None,
        'resident_runtime_contract_digest': str(resident_runtime_contract_digest or '').strip() or None,
        'desktop_session_contract_digest': str(desktop_session_contract_digest or '').strip() or None,
        'warm_runtime_probe_latency_attention_id': str(warm_runtime_probe_latency_attention_id or '').strip() or None,
        'warm_runtime_probe_freshness_attention_id': str(warm_runtime_probe_freshness_attention_id or '').strip() or None,
    }
    contract['digest'] = runtime_acceptance_contract_digest(contract)
    return contract


def compare_runtime_acceptance_contract(current: Mapping[str, Any] | None, observed: Mapping[str, Any] | None) -> dict[str, Any]:
    current_contract = dict(current or {})
    observed_contract = dict(observed or {})
    current_digest = str(current_contract.get('digest') or runtime_acceptance_contract_digest(current_contract) or '').strip() or None
    observed_digest = str(observed_contract.get('digest') or runtime_acceptance_contract_digest(observed_contract) or '').strip() or None
    in_sync = bool(current_digest and observed_digest and current_digest == observed_digest)
    runtime_posture_changed = False
    preferred_execution_mode_changed = False
    replay_posture_changed = False
    macro_proof_contract_changed = False
    dispatch_receipt_contract_changed = False
    dispatch_history_posture_changed = False
    dispatch_history_attention_changed = False
    resident_runtime_epoch_changed = False
    resident_runtime_contract_changed = False
    desktop_session_contract_changed = False
    warm_runtime_probe_latency_attention_changed = False
    warm_runtime_probe_freshness_attention_changed = False
    if current_contract or observed_contract:
        runtime_posture_changed = current_contract.get('runtime_posture_id') != observed_contract.get('runtime_posture_id')
        preferred_execution_mode_changed = current_contract.get('preferred_execution_mode') != observed_contract.get('preferred_execution_mode')
        replay_posture_changed = current_contract.get('replay_posture_id') != observed_contract.get('replay_posture_id')
        macro_proof_contract_changed = current_contract.get('macro_proof_contract_digest') != observed_contract.get('macro_proof_contract_digest')
        dispatch_receipt_contract_changed = current_contract.get('dispatch_receipt_contract_digest') != observed_contract.get('dispatch_receipt_contract_digest')
        dispatch_history_posture_changed = current_contract.get('dispatch_history_posture_id') != observed_contract.get('dispatch_history_posture_id')
        dispatch_history_attention_changed = current_contract.get('dispatch_history_attention_id') != observed_contract.get('dispatch_history_attention_id')
        resident_runtime_epoch_changed = current_contract.get('resident_runtime_epoch_id') != observed_contract.get('resident_runtime_epoch_id')
        resident_runtime_contract_changed = current_contract.get('resident_runtime_contract_digest') != observed_contract.get('resident_runtime_contract_digest')
        desktop_session_contract_changed = current_contract.get('desktop_session_contract_digest') != observed_contract.get('desktop_session_contract_digest')
        warm_runtime_probe_latency_attention_changed = current_contract.get('warm_runtime_probe_latency_attention_id') != observed_contract.get('warm_runtime_probe_latency_attention_id')
        warm_runtime_probe_freshness_attention_changed = current_contract.get('warm_runtime_probe_freshness_attention_id') != observed_contract.get('warm_runtime_probe_freshness_attention_id')
    reasons: list[str] = []
    status = 'in_sync'
    summary = 'The durable runtime signoff still matches the current runtime proof contract.'
    if not observed_contract:
        status = 'missing'
        summary = 'The durable runtime signoff predates proof-bound acceptance and should be refreshed before treating acceptance as current.'
        reasons.append('runtime acceptance proof contract missing')
    elif not observed_digest:
        status = 'missing_digest'
        summary = 'The durable runtime signoff does not include a comparable proof-contract digest and should be refreshed.'
        reasons.append('runtime acceptance proof contract digest missing')
    elif not in_sync:
        status = 'drifted'
        summary = 'The durable runtime signoff no longer matches the current runtime proof contract.'
        if runtime_posture_changed:
            reasons.append('runtime posture changed since durable signoff')
        if preferred_execution_mode_changed:
            reasons.append('preferred execution mode changed since durable signoff')
        if replay_posture_changed:
            reasons.append('replay posture changed since durable signoff')
        if macro_proof_contract_changed:
            reasons.append('macro or recorder proof changed since durable signoff')
        if dispatch_receipt_contract_changed:
            reasons.append('dispatch proof contract changed since durable signoff')
        if dispatch_history_posture_changed:
            reasons.append('warm dispatch history posture changed since durable signoff')
        if dispatch_history_attention_changed:
            reasons.append('warm dispatch attention changed since durable signoff')
        if resident_runtime_epoch_changed:
            reasons.append('resident runtime epoch changed since durable signoff')
        if resident_runtime_contract_changed:
            reasons.append('resident runtime contract changed since durable signoff')
        if desktop_session_contract_changed:
            reasons.append('desktop session changed since durable signoff')
        if warm_runtime_probe_latency_attention_changed:
            reasons.append('warm runtime latency attention changed since durable signoff')
        if warm_runtime_probe_freshness_attention_changed:
            reasons.append('warm runtime probe freshness attention changed since durable signoff')
        if not reasons:
            reasons.append('runtime acceptance proof contract digest changed')
    return {
        'status': status,
        'in_sync': in_sync,
        'summary': summary,
        'reasons': reasons,
        'runtime_posture_changed': runtime_posture_changed,
        'preferred_execution_mode_changed': preferred_execution_mode_changed,
        'replay_posture_changed': replay_posture_changed,
        'macro_proof_contract_changed': macro_proof_contract_changed,
        'dispatch_receipt_contract_changed': dispatch_receipt_contract_changed,
        'dispatch_history_posture_changed': dispatch_history_posture_changed,
        'dispatch_history_attention_changed': dispatch_history_attention_changed,
        'resident_runtime_epoch_changed': resident_runtime_epoch_changed,
        'resident_runtime_contract_changed': resident_runtime_contract_changed,
        'desktop_session_contract_changed': desktop_session_contract_changed,
        'warm_runtime_probe_latency_attention_changed': warm_runtime_probe_latency_attention_changed,
        'warm_runtime_probe_freshness_attention_changed': warm_runtime_probe_freshness_attention_changed,
        'current_digest': current_digest,
        'observed_digest': observed_digest,
        'current_contract': current_contract,
        'observed_contract': observed_contract,
    }

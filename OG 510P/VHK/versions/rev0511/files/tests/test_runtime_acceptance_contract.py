from __future__ import annotations

from vhk.project.runtime_acceptance_contract import (
    summarize_runtime_acceptance_contract,
    compare_runtime_acceptance_contract,
)


def test_runtime_acceptance_contract_digest_is_stable():
    a = summarize_runtime_acceptance_contract(
        macro_name='sig',
        runtime_posture_id='warm_dispatch_ready',
        preferred_execution_mode='warm_runtime_dispatch',
        replay_posture_id='verified_recent',
        macro_proof_contract_digest='aaa',
        dispatch_receipt_contract_digest='bbb',
    )
    b = summarize_runtime_acceptance_contract(
        macro_name='sig',
        runtime_posture_id='warm_dispatch_ready',
        preferred_execution_mode='warm_runtime_dispatch',
        replay_posture_id='verified_recent',
        macro_proof_contract_digest='aaa',
        dispatch_receipt_contract_digest='bbb',
    )
    assert a['digest']
    assert a['digest'] == b['digest']


def test_runtime_acceptance_contract_detects_macro_and_dispatch_drift():
    current = summarize_runtime_acceptance_contract(
        macro_name='sig',
        runtime_posture_id='warm_dispatch_ready',
        preferred_execution_mode='warm_runtime_dispatch',
        replay_posture_id='verified_recent',
        macro_proof_contract_digest='new-macro',
        dispatch_receipt_contract_digest='new-dispatch',
    )
    observed = summarize_runtime_acceptance_contract(
        macro_name='sig',
        runtime_posture_id='warm_dispatch_ready',
        preferred_execution_mode='warm_runtime_dispatch',
        replay_posture_id='verified_recent',
        macro_proof_contract_digest='old-macro',
        dispatch_receipt_contract_digest='old-dispatch',
    )
    payload = compare_runtime_acceptance_contract(current, observed)
    assert payload['status'] == 'drifted'
    assert payload['in_sync'] is False
    assert payload['macro_proof_contract_changed'] is True
    assert payload['dispatch_receipt_contract_changed'] is True


def test_runtime_acceptance_contract_missing_observed_contract():
    current = summarize_runtime_acceptance_contract(
        macro_name='sig',
        runtime_posture_id='warm_dispatch_ready',
        preferred_execution_mode='warm_runtime_dispatch',
        replay_posture_id='verified_recent',
        macro_proof_contract_digest='aaa',
        dispatch_receipt_contract_digest='bbb',
    )
    payload = compare_runtime_acceptance_contract(current, None)
    assert payload['status'] == 'missing'
    assert payload['in_sync'] is False


def test_runtime_acceptance_contract_detects_dispatch_history_drift():
    current = summarize_runtime_acceptance_contract(
        macro_name='sig',
        runtime_posture_id='warm_dispatch_ready',
        preferred_execution_mode='warm_runtime_dispatch',
        replay_posture_id='verified_recent',
        macro_proof_contract_digest='aaa',
        dispatch_receipt_contract_digest='bbb',
        dispatch_history_posture_id='dispatch_receipt_session_stale',
        dispatch_history_attention_id='refresh_dispatch_after_session_change',
    )
    observed = summarize_runtime_acceptance_contract(
        macro_name='sig',
        runtime_posture_id='warm_dispatch_ready',
        preferred_execution_mode='warm_runtime_dispatch',
        replay_posture_id='verified_recent',
        macro_proof_contract_digest='aaa',
        dispatch_receipt_contract_digest='bbb',
        dispatch_history_posture_id='clean_recent_dispatch',
        dispatch_history_attention_id='none',
    )
    payload = compare_runtime_acceptance_contract(current, observed)
    assert payload['status'] == 'drifted'
    assert payload['dispatch_history_posture_changed'] is True
    assert payload['dispatch_history_attention_changed'] is True



def test_runtime_acceptance_contract_detects_resident_runtime_drift():
    current = summarize_runtime_acceptance_contract(
        macro_name='sig',
        runtime_posture_id='warm_dispatch_ready',
        preferred_execution_mode='warm_runtime_dispatch',
        replay_posture_id='verified_recent',
        macro_proof_contract_digest='aaa',
        dispatch_receipt_contract_digest='bbb',
        resident_runtime_epoch_id='epoch-b',
        resident_runtime_contract_digest='contract-b',
    )
    observed = summarize_runtime_acceptance_contract(
        macro_name='sig',
        runtime_posture_id='warm_dispatch_ready',
        preferred_execution_mode='warm_runtime_dispatch',
        replay_posture_id='verified_recent',
        macro_proof_contract_digest='aaa',
        dispatch_receipt_contract_digest='bbb',
        resident_runtime_epoch_id='epoch-a',
        resident_runtime_contract_digest='contract-a',
    )
    payload = compare_runtime_acceptance_contract(current, observed)
    assert payload['status'] == 'drifted'
    assert payload['resident_runtime_epoch_changed'] is True
    assert payload['resident_runtime_contract_changed'] is True


def test_runtime_acceptance_contract_detects_desktop_session_drift():
    current = summarize_runtime_acceptance_contract(
        macro_name='sig',
        runtime_posture_id='warm_dispatch_ready',
        preferred_execution_mode='warm_runtime_dispatch',
        replay_posture_id='verified_recent',
        macro_proof_contract_digest='aaa',
        dispatch_receipt_contract_digest='bbb',
        desktop_session_contract_digest='session-b',
    )
    observed = summarize_runtime_acceptance_contract(
        macro_name='sig',
        runtime_posture_id='warm_dispatch_ready',
        preferred_execution_mode='warm_runtime_dispatch',
        replay_posture_id='verified_recent',
        macro_proof_contract_digest='aaa',
        dispatch_receipt_contract_digest='bbb',
        desktop_session_contract_digest='session-a',
    )
    payload = compare_runtime_acceptance_contract(current, observed)
    assert payload['status'] == 'drifted'
    assert payload['desktop_session_contract_changed'] is True
    assert 'desktop session changed since durable signoff' in payload['reasons']


def test_runtime_acceptance_contract_detects_latency_attention_drift():
    current = summarize_runtime_acceptance_contract(
        macro_name='sig',
        runtime_posture_id='warm_dispatch_ready',
        preferred_execution_mode='warm_runtime_dispatch',
        replay_posture_id='verified_recent',
        macro_proof_contract_digest='aaa',
        dispatch_receipt_contract_digest='bbb',
        warm_runtime_probe_latency_attention_id='inspect_runtime_latency',
    )
    observed = summarize_runtime_acceptance_contract(
        macro_name='sig',
        runtime_posture_id='warm_dispatch_ready',
        preferred_execution_mode='warm_runtime_dispatch',
        replay_posture_id='verified_recent',
        macro_proof_contract_digest='aaa',
        dispatch_receipt_contract_digest='bbb',
        warm_runtime_probe_latency_attention_id=None,
    )
    payload = compare_runtime_acceptance_contract(current, observed)
    assert payload['status'] == 'drifted'
    assert payload['warm_runtime_probe_latency_attention_changed'] is True
    assert 'warm runtime latency attention changed since durable signoff' in payload['reasons']


def test_runtime_acceptance_contract_detects_probe_freshness_attention_drift():
    current = summarize_runtime_acceptance_contract(
        macro_name='sig',
        runtime_posture_id='warm_dispatch_ready',
        preferred_execution_mode='warm_runtime_dispatch',
        replay_posture_id='verified_recent',
        macro_proof_contract_digest='aaa',
        dispatch_receipt_contract_digest='bbb',
        warm_runtime_probe_freshness_attention_id='refresh_runtime_probe',
    )
    observed = summarize_runtime_acceptance_contract(
        macro_name='sig',
        runtime_posture_id='warm_dispatch_ready',
        preferred_execution_mode='warm_runtime_dispatch',
        replay_posture_id='verified_recent',
        macro_proof_contract_digest='aaa',
        dispatch_receipt_contract_digest='bbb',
        warm_runtime_probe_freshness_attention_id=None,
    )
    payload = compare_runtime_acceptance_contract(current, observed)
    assert payload['status'] == 'drifted'
    assert payload['warm_runtime_probe_freshness_attention_changed'] is True
    assert 'warm runtime probe freshness attention changed since durable signoff' in payload['reasons']

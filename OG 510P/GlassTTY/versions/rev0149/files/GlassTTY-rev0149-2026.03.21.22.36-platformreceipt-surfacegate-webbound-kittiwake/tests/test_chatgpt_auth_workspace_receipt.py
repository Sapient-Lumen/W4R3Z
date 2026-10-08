from __future__ import annotations

import importlib.util
from pathlib import Path

from test_chatgpt_composer_witness_receipt import _seed
from test_chatgpt_promotion_stability_receipt import _promotion_windows

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('chatgpt_auth_workspace_receipt', ROOT / 'scripts' / 'chatgpt_auth_workspace_receipt.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_chatgpt_auth_workspace_receipt = MODULE.build_chatgpt_auth_workspace_receipt
evaluate_chatgpt_auth_workspace_receipt = MODULE.evaluate_chatgpt_auth_workspace_receipt
capture_chatgpt_auth_workspace_receipt = MODULE.capture_chatgpt_auth_workspace_receipt
write_root_chatgpt_auth_workspace_receipt = MODULE.write_root_chatgpt_auth_workspace_receipt
summarize_capture_history = MODULE.summarize_capture_history


def test_auth_workspace_receipt_builds_contract(tmp_path: Path) -> None:
    _seed(tmp_path)
    payload = build_chatgpt_auth_workspace_receipt(root=tmp_path)
    assert payload['surface_key'] == 'chatgpt'
    assert payload['auth_workspace_axes'][0]['axis'] == 'auth-posture'
    assert [item['state'] for item in payload['auth_workspace_readiness_states']][0] == 'provisional-auth-envelope'


def test_auth_workspace_receipt_grades_planning_experimental_provisional_hold_and_stop(tmp_path: Path) -> None:
    _seed(tmp_path)
    planning = evaluate_chatgpt_auth_workspace_receipt({}, root=tmp_path)
    assert planning['auth_workspace_readiness'] == 'planning-only'

    experimental_input = _promotion_windows()
    experimental_input['proof_windows'] = experimental_input['proof_windows'][:1]
    experimental = evaluate_chatgpt_auth_workspace_receipt(experimental_input, root=tmp_path)
    assert experimental['auth_workspace_readiness'] == 'experimental-auth-envelope'
    assert experimental['recommended_support_record_tier'] == 'experimental'
    assert experimental['auth_workspace_envelope']['workspace_kind_scope'] == ['guest']

    provisional = evaluate_chatgpt_auth_workspace_receipt(_promotion_windows(), root=tmp_path)
    assert provisional['auth_workspace_readiness'] == 'provisional-auth-envelope'
    assert provisional['recommended_support_record_tier'] == 'provisional'
    assert provisional['auth_workspace_envelope']['auth_posture_scope'] == ['logged-out']

    hold_input = _promotion_windows()
    for window in hold_input['proof_windows']:
        window['route_witness']['auth_posture'] = 'logged-in'
    hold = evaluate_chatgpt_auth_workspace_receipt(hold_input, root=tmp_path)
    assert hold['auth_workspace_readiness'] == 'hold-for-auth-clarification'
    assert 'workspace_kind_explicit' in hold['missing_required_check_keys']

    stop_input = _promotion_windows()
    stop_input['proof_windows'][1]['route_witness']['auth_posture'] = 'logged-in'
    stop_input['proof_windows'][1]['workspace_kind'] = 'personal'
    stop = evaluate_chatgpt_auth_workspace_receipt(stop_input, root=tmp_path)
    assert stop['auth_workspace_readiness'] == 'stop'
    assert stop['auth_workspace_envelope']['workspace_kind_scope'] == ['guest', 'personal']


def test_auth_workspace_receipt_capture_and_write_root(tmp_path: Path) -> None:
    _seed(tmp_path)
    output_dir = tmp_path / 'validation' / 'latest' / 'chatgpt-auth-workspace-receipt'
    history_path = tmp_path / 'validation' / 'chatgpt-auth-workspace-receipt-captures.json'
    payload = capture_chatgpt_auth_workspace_receipt(root=tmp_path, output_dir=output_dir, history_path=history_path)
    assert (output_dir / 'chatgpt-auth-workspace-receipt.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert payload['history_update']['capture_count_after_write'] == 1
    history = summarize_capture_history(history_path)
    assert history['capture_count'] == 1
    root_payload = write_root_chatgpt_auth_workspace_receipt(root=tmp_path)
    assert (tmp_path / 'CHATGPT-AUTH-WORKSPACE-RECEIPT.json').exists()
    assert len(root_payload['auth_workspace_readiness_states']) == 6

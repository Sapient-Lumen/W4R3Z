from __future__ import annotations

import importlib.util
from pathlib import Path

from test_chatgpt_composer_witness_receipt import _seed
from test_chatgpt_promotion_stability_receipt import _promotion_windows

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('chatgpt_plan_envelope_receipt', ROOT / 'scripts' / 'chatgpt_plan_envelope_receipt.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_chatgpt_plan_envelope_receipt = MODULE.build_chatgpt_plan_envelope_receipt
evaluate_chatgpt_plan_envelope_receipt = MODULE.evaluate_chatgpt_plan_envelope_receipt
capture_chatgpt_plan_envelope_receipt = MODULE.capture_chatgpt_plan_envelope_receipt
write_root_chatgpt_plan_envelope_receipt = MODULE.write_root_chatgpt_plan_envelope_receipt
summarize_capture_history = MODULE.summarize_capture_history


def test_plan_envelope_receipt_builds_contract(tmp_path: Path) -> None:
    _seed(tmp_path)
    payload = build_chatgpt_plan_envelope_receipt(root=tmp_path)
    assert payload['surface_key'] == 'chatgpt'
    assert payload['plan_envelope_axes'][0]['axis'] == 'account-tier'
    assert [item['state'] for item in payload['plan_envelope_readiness_states']][0] == 'provisional-plan-envelope'


def test_plan_envelope_receipt_grades_planning_experimental_provisional_hold_and_stop(tmp_path: Path) -> None:
    _seed(tmp_path)
    planning = evaluate_chatgpt_plan_envelope_receipt({}, root=tmp_path)
    assert planning['plan_envelope_readiness'] == 'planning-only'

    experimental_input = _promotion_windows()
    experimental_input['proof_windows'] = experimental_input['proof_windows'][:1]
    experimental = evaluate_chatgpt_plan_envelope_receipt(experimental_input, root=tmp_path)
    assert experimental['plan_envelope_readiness'] == 'experimental-plan-envelope'
    assert experimental['recommended_support_record_tier'] == 'experimental'
    assert experimental['plan_envelope']['plan_tier_scope'] == ['free-guest']

    provisional = evaluate_chatgpt_plan_envelope_receipt(_promotion_windows(), root=tmp_path)
    assert provisional['plan_envelope_readiness'] == 'provisional-plan-envelope'
    assert provisional['recommended_support_record_tier'] == 'provisional'
    assert provisional['plan_envelope']['plan_tier_scope'] == ['free-guest']

    hold_input = _promotion_windows()
    for window in hold_input['proof_windows']:
        window['route_witness']['auth_posture'] = 'logged-in'
        window['workspace_kind'] = 'personal'
    hold = evaluate_chatgpt_plan_envelope_receipt(hold_input, root=tmp_path)
    assert hold['plan_envelope_readiness'] == 'hold-for-plan-clarification'
    assert 'signed_in_personal_plan_explicit' in hold['missing_required_check_keys']

    stop_input = _promotion_windows()
    stop_input['proof_windows'][0]['route_witness']['auth_posture'] = 'logged-in'
    stop_input['proof_windows'][0]['workspace_kind'] = 'personal'
    stop_input['proof_windows'][0]['plan_tier'] = 'plus'
    stop = evaluate_chatgpt_plan_envelope_receipt(stop_input, root=tmp_path)
    assert stop['plan_envelope_readiness'] == 'stop'
    assert set(stop['plan_envelope']['plan_tier_scope']) == {'plus', 'free-guest'}


def test_plan_envelope_receipt_capture_and_write_root(tmp_path: Path) -> None:
    _seed(tmp_path)
    output_dir = tmp_path / 'validation' / 'latest' / 'chatgpt-plan-envelope-receipt'
    history_path = tmp_path / 'validation' / 'chatgpt-plan-envelope-receipt-captures.json'
    payload = capture_chatgpt_plan_envelope_receipt(root=tmp_path, output_dir=output_dir, history_path=history_path)
    assert (output_dir / 'chatgpt-plan-envelope-receipt.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert payload['history_update']['capture_count_after_write'] == 1
    history = summarize_capture_history(history_path)
    assert history['capture_count'] == 1
    root_payload = write_root_chatgpt_plan_envelope_receipt(root=tmp_path)
    assert (tmp_path / 'CHATGPT-PLAN-ENVELOPE-RECEIPT.json').exists()
    assert len(root_payload['plan_envelope_readiness_states']) == 6

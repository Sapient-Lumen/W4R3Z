from __future__ import annotations

import importlib.util
from pathlib import Path

from test_chatgpt_composer_witness_receipt import _seed
from test_chatgpt_promotion_stability_receipt import _promotion_windows

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('chatgpt_support_claim_receipt', ROOT / 'scripts' / 'chatgpt_support_claim_receipt.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_chatgpt_support_claim_receipt = MODULE.build_chatgpt_support_claim_receipt
evaluate_chatgpt_support_claim_receipt = MODULE.evaluate_chatgpt_support_claim_receipt
capture_chatgpt_support_claim_receipt = MODULE.capture_chatgpt_support_claim_receipt
write_root_chatgpt_support_claim_receipt = MODULE.write_root_chatgpt_support_claim_receipt
summarize_capture_history = MODULE.summarize_capture_history


def test_support_claim_receipt_builds_contract(tmp_path: Path) -> None:
    _seed(tmp_path)
    payload = build_chatgpt_support_claim_receipt(root=tmp_path)
    assert payload['surface_key'] == 'chatgpt'
    assert payload['claim_axes'][0]['axis'] == 'browser-lane'
    assert [item['state'] for item in payload['claim_readiness_states']][0] == 'provisional-lane-bound'


def test_support_claim_receipt_grades_planning_experimental_provisional_and_stop(tmp_path: Path) -> None:
    _seed(tmp_path)
    planning = evaluate_chatgpt_support_claim_receipt({}, root=tmp_path)
    assert planning['claim_readiness'] == 'planning-only'
    assert planning['recommended_support_record_tier'] == 'investigated'

    experimental_input = _promotion_windows()
    experimental_input['proof_windows'] = experimental_input['proof_windows'][:1]
    experimental = evaluate_chatgpt_support_claim_receipt(experimental_input, root=tmp_path)
    assert experimental['claim_readiness'] == 'experimental-lane-bound'
    assert experimental['recommended_support_record_tier'] == 'experimental'
    assert experimental['claim_envelope']['tier_ceiling'] == 'experimental'

    provisional = evaluate_chatgpt_support_claim_receipt(_promotion_windows(), root=tmp_path)
    assert provisional['claim_readiness'] == 'provisional-lane-bound'
    assert provisional['recommended_support_record_tier'] == 'provisional'
    assert provisional['claim_envelope']['browser_lane_scope'] == ['chromium-live']

    hold_input = _promotion_windows()
    hold_input.pop('browser_lane', None)
    for window in hold_input['proof_windows']:
        window.pop('browser_lane', None)
        window['official_surface_live'] = True
    hold = evaluate_chatgpt_support_claim_receipt(hold_input, root=tmp_path)
    assert hold['claim_readiness'] == 'hold-for-scope-expansion'
    assert 'browser_lane_explicit' in hold['missing_required_check_keys']

    stop_input = _promotion_windows()
    for window in stop_input['proof_windows']:
        window['route_witness']['path'] = '/gpts/editor'
    stop = evaluate_chatgpt_support_claim_receipt(stop_input, root=tmp_path)
    assert stop['claim_readiness'] == 'stop'


def test_support_claim_receipt_capture_and_write_root(tmp_path: Path) -> None:
    _seed(tmp_path)
    output_dir = tmp_path / 'validation' / 'latest' / 'chatgpt-support-claim-receipt'
    history_path = tmp_path / 'validation' / 'chatgpt-support-claim-receipt-captures.json'
    payload = capture_chatgpt_support_claim_receipt(root=tmp_path, output_dir=output_dir, history_path=history_path)
    assert (output_dir / 'chatgpt-support-claim-receipt.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert payload['history_update']['capture_count_after_write'] == 1
    history = summarize_capture_history(history_path)
    assert history['capture_count'] == 1
    root_payload = write_root_chatgpt_support_claim_receipt(root=tmp_path)
    assert (tmp_path / 'CHATGPT-SUPPORT-CLAIM-RECEIPT.json').exists()
    assert len(root_payload['claim_readiness_states']) == 6

from __future__ import annotations

import importlib.util
from pathlib import Path

from test_chatgpt_composer_witness_receipt import _seed
from test_chatgpt_promotion_stability_receipt import _promotion_windows

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('chatgpt_browser_envelope_receipt', ROOT / 'scripts' / 'chatgpt_browser_envelope_receipt.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_chatgpt_browser_envelope_receipt = MODULE.build_chatgpt_browser_envelope_receipt
evaluate_chatgpt_browser_envelope_receipt = MODULE.evaluate_chatgpt_browser_envelope_receipt
capture_chatgpt_browser_envelope_receipt = MODULE.capture_chatgpt_browser_envelope_receipt
write_root_chatgpt_browser_envelope_receipt = MODULE.write_root_chatgpt_browser_envelope_receipt
summarize_capture_history = MODULE.summarize_capture_history


def test_browser_envelope_receipt_builds_contract(tmp_path: Path) -> None:
    _seed(tmp_path)
    payload = build_chatgpt_browser_envelope_receipt(root=tmp_path)
    assert payload['surface_key'] == 'chatgpt'
    assert payload['browser_envelope_axes'][0]['axis'] == 'browser-engine'
    assert [item['state'] for item in payload['browser_envelope_readiness_states']][0] == 'provisional-browser-envelope'


def test_browser_envelope_receipt_grades_planning_experimental_provisional_hold_and_stop(tmp_path: Path) -> None:
    _seed(tmp_path)
    planning = evaluate_chatgpt_browser_envelope_receipt({}, root=tmp_path)
    assert planning['browser_envelope_readiness'] == 'planning-only'

    experimental_input = _promotion_windows()
    experimental_input['proof_windows'] = experimental_input['proof_windows'][:1]
    experimental = evaluate_chatgpt_browser_envelope_receipt(experimental_input, root=tmp_path)
    assert experimental['browser_envelope_readiness'] == 'experimental-browser-envelope'
    assert experimental['recommended_support_record_tier'] == 'experimental'
    assert experimental['browser_envelope']['browser_engine_scope'] == ['chromium']

    provisional = evaluate_chatgpt_browser_envelope_receipt(_promotion_windows(), root=tmp_path)
    assert provisional['browser_envelope_readiness'] == 'provisional-browser-envelope'
    assert provisional['recommended_support_record_tier'] == 'provisional'
    assert provisional['browser_envelope']['browser_lane_scope'] == ['chromium-live']

    hold_input = _promotion_windows()
    for window in hold_input['proof_windows']:
        window['browser_lane'] = 'browser-live'
    hold = evaluate_chatgpt_browser_envelope_receipt(hold_input, root=tmp_path)
    assert hold['browser_envelope_readiness'] == 'hold-for-browser-clarification'
    assert 'browser_engine_explicit' in hold['missing_required_check_keys']

    stop_input = _promotion_windows()
    stop_input['proof_windows'][1]['browser_lane'] = 'firefox-live'
    stop = evaluate_chatgpt_browser_envelope_receipt(stop_input, root=tmp_path)
    assert stop['browser_envelope_readiness'] == 'stop'
    assert stop['browser_envelope']['browser_engine_scope'] == ['chromium', 'firefox']


def test_browser_envelope_receipt_capture_and_write_root(tmp_path: Path) -> None:
    _seed(tmp_path)
    output_dir = tmp_path / 'validation' / 'latest' / 'chatgpt-browser-envelope-receipt'
    history_path = tmp_path / 'validation' / 'chatgpt-browser-envelope-receipt-captures.json'
    payload = capture_chatgpt_browser_envelope_receipt(root=tmp_path, output_dir=output_dir, history_path=history_path)
    assert (output_dir / 'chatgpt-browser-envelope-receipt.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert payload['history_update']['capture_count_after_write'] == 1
    history = summarize_capture_history(history_path)
    assert history['capture_count'] == 1
    root_payload = write_root_chatgpt_browser_envelope_receipt(root=tmp_path)
    assert (tmp_path / 'CHATGPT-BROWSER-ENVELOPE-RECEIPT.json').exists()
    assert len(root_payload['browser_envelope_readiness_states']) == 6

from __future__ import annotations

import importlib.util
from pathlib import Path

from test_chatgpt_composer_witness_receipt import _seed
from test_chatgpt_proof_bundle_receipt import _good_bundle

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('chatgpt_promotion_stability_receipt', ROOT / 'scripts' / 'chatgpt_promotion_stability_receipt.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_chatgpt_promotion_stability_receipt = MODULE.build_chatgpt_promotion_stability_receipt
evaluate_chatgpt_promotion_stability_receipt = MODULE.evaluate_chatgpt_promotion_stability_receipt
capture_chatgpt_promotion_stability_receipt = MODULE.capture_chatgpt_promotion_stability_receipt
write_root_chatgpt_promotion_stability_receipt = MODULE.write_root_chatgpt_promotion_stability_receipt
summarize_capture_history = MODULE.summarize_capture_history


def _promotion_windows() -> dict:
    first = _good_bundle()
    second = _good_bundle()
    second['route_witness']['capture_window_id'] = 'proof-window-2'
    second['composer_witness']['capture_window_id'] = 'proof-window-2'
    second['submit_witness']['capture_window_id'] = 'proof-window-2'
    return {
        'proof_windows': [first, second],
        'artifact_refs': [
            {'path': 'playwright-trace.zip', 'kind': 'trace'},
            {'path': 'locator-notes.md', 'kind': 'locator-note'},
        ],
    }


def test_promotion_stability_receipt_builds_contract(tmp_path: Path) -> None:
    _seed(tmp_path)
    payload = build_chatgpt_promotion_stability_receipt(root=tmp_path)
    assert payload['surface_key'] == 'chatgpt'
    assert payload['promotion_contract']['minimum_reviewable_windows'] == 2
    assert [item['state'] for item in payload['stability_readiness_states']][0] == 'ready-for-provisional'


def test_promotion_stability_receipt_grades_ready_caution_and_hold(tmp_path: Path) -> None:
    _seed(tmp_path)
    ready = evaluate_chatgpt_promotion_stability_receipt(_promotion_windows(), root=tmp_path)
    assert ready['stability_readiness'] == 'ready-for-provisional'
    assert ready['recommended_support_record_tier'] == 'provisional'

    caution_input = _promotion_windows()
    caution_input.pop('artifact_refs')
    caution = evaluate_chatgpt_promotion_stability_receipt(caution_input, root=tmp_path)
    assert caution['stability_readiness'] == 'ready-with-caution'
    assert 'missing-trace-artifact' in caution['caution_flags']

    hold_input = _promotion_windows()
    hold_input['proof_windows'][1]['route_witness']['capture_window_id'] = 'proof-window-1'
    hold_input['proof_windows'][1]['composer_witness']['capture_window_id'] = 'proof-window-1'
    hold_input['proof_windows'][1]['submit_witness']['capture_window_id'] = 'proof-window-1'
    hold = evaluate_chatgpt_promotion_stability_receipt(hold_input, root=tmp_path)
    assert hold['stability_readiness'] == 'hold-for-recapture'
    assert 'distinct_window_tokens' in hold['missing_required_check_keys']

    planning = evaluate_chatgpt_promotion_stability_receipt({}, root=tmp_path)
    assert planning['stability_readiness'] == 'planning-only'


def test_promotion_stability_receipt_capture_and_write_root(tmp_path: Path) -> None:
    _seed(tmp_path)
    output_dir = tmp_path / 'validation' / 'latest' / 'chatgpt-promotion-stability-receipt'
    history_path = tmp_path / 'validation' / 'chatgpt-promotion-stability-receipt-captures.json'
    payload = capture_chatgpt_promotion_stability_receipt(root=tmp_path, output_dir=output_dir, history_path=history_path)
    assert (output_dir / 'chatgpt-promotion-stability-receipt.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert payload['history_update']['capture_count_after_write'] == 1
    history = summarize_capture_history(history_path)
    assert history['capture_count'] == 1
    root_payload = write_root_chatgpt_promotion_stability_receipt(root=tmp_path)
    assert (tmp_path / 'CHATGPT-PROMOTION-STABILITY-RECEIPT.json').exists()
    assert len(root_payload['stability_readiness_states']) == 8

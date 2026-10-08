from __future__ import annotations

import importlib.util
from pathlib import Path

from test_chatgpt_composer_witness_receipt import _seed
from test_chatgpt_promotion_stability_receipt import _promotion_windows

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('chatgpt_platform_envelope_receipt', ROOT / 'scripts' / 'chatgpt_platform_envelope_receipt.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_chatgpt_platform_envelope_receipt = MODULE.build_chatgpt_platform_envelope_receipt
evaluate_chatgpt_platform_envelope_receipt = MODULE.evaluate_chatgpt_platform_envelope_receipt
capture_chatgpt_platform_envelope_receipt = MODULE.capture_chatgpt_platform_envelope_receipt
write_root_chatgpt_platform_envelope_receipt = MODULE.write_root_chatgpt_platform_envelope_receipt
summarize_capture_history = MODULE.summarize_capture_history


def test_platform_envelope_receipt_builds_contract(tmp_path: Path) -> None:
    _seed(tmp_path)
    payload = build_chatgpt_platform_envelope_receipt(root=tmp_path)
    assert payload['surface_key'] == 'chatgpt'
    assert payload['platform_envelope_axes'][0]['axis'] == 'product-surface'
    assert [item['state'] for item in payload['platform_envelope_readiness_states']][0] == 'provisional-platform-envelope'


def test_platform_envelope_receipt_grades_planning_experimental_provisional_hold_and_stop(tmp_path: Path) -> None:
    _seed(tmp_path)
    planning = evaluate_chatgpt_platform_envelope_receipt({}, root=tmp_path)
    assert planning['platform_envelope_readiness'] == 'planning-only'

    experimental_input = _promotion_windows()
    experimental_input['proof_windows'] = experimental_input['proof_windows'][:1]
    experimental = evaluate_chatgpt_platform_envelope_receipt(experimental_input, root=tmp_path)
    assert experimental['platform_envelope_readiness'] == 'experimental-platform-envelope'
    assert experimental['recommended_support_record_tier'] == 'experimental'
    assert experimental['platform_envelope']['platform_surface_scope'] == ['desktop-web']

    provisional = evaluate_chatgpt_platform_envelope_receipt(_promotion_windows(), root=tmp_path)
    assert provisional['platform_envelope_readiness'] == 'provisional-platform-envelope'
    assert provisional['recommended_support_record_tier'] == 'provisional'
    assert provisional['platform_envelope']['app_runtime_scope'] == ['chatgpt-web']

    hold_input = _promotion_windows()
    for window in hold_input['proof_windows']:
        window['route_witness']['host'] = 'example.com'
        window['route_witness']['title'] = 'Generic Browser'
        window['route_witness'].pop('visible_text', None)
        window['route_witness'].pop('main_region_text', None)
    hold = evaluate_chatgpt_platform_envelope_receipt(hold_input, root=tmp_path)
    assert hold['platform_envelope_readiness'] == 'hold-for-platform-clarification'
    assert 'platform_surface_explicit' in hold['missing_required_check_keys']

    stop_input = _promotion_windows()
    stop_input['proof_windows'][1]['platform_surface'] = 'windows-app'
    stop = evaluate_chatgpt_platform_envelope_receipt(stop_input, root=tmp_path)
    assert stop['platform_envelope_readiness'] == 'stop'
    assert stop['platform_envelope']['platform_surface_scope'] == ['desktop-web', 'windows-app']


def test_platform_envelope_receipt_capture_and_write_root(tmp_path: Path) -> None:
    _seed(tmp_path)
    output_dir = tmp_path / 'validation' / 'latest' / 'chatgpt-platform-envelope-receipt'
    history_path = tmp_path / 'validation' / 'chatgpt-platform-envelope-receipt-captures.json'
    payload = capture_chatgpt_platform_envelope_receipt(root=tmp_path, output_dir=output_dir, history_path=history_path)
    assert (output_dir / 'chatgpt-platform-envelope-receipt.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert payload['history_update']['capture_count_after_write'] == 1
    history = summarize_capture_history(history_path)
    assert history['capture_count'] == 1
    root_payload = write_root_chatgpt_platform_envelope_receipt(root=tmp_path)
    assert (tmp_path / 'CHATGPT-PLATFORM-ENVELOPE-RECEIPT.json').exists()
    assert len(root_payload['platform_envelope_readiness_states']) == 6

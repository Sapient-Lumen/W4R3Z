from __future__ import annotations

import importlib.util
from pathlib import Path

from test_chatgpt_composer_witness_receipt import _seed

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('chatgpt_submit_witness_receipt', ROOT / 'scripts' / 'chatgpt_submit_witness_receipt.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_chatgpt_submit_witness_receipt = MODULE.build_chatgpt_submit_witness_receipt
evaluate_chatgpt_submit_witness_receipt = MODULE.evaluate_chatgpt_submit_witness_receipt
capture_chatgpt_submit_witness_receipt = MODULE.capture_chatgpt_submit_witness_receipt
write_root_chatgpt_submit_witness_receipt = MODULE.write_root_chatgpt_submit_witness_receipt
summarize_capture_history = MODULE.summarize_capture_history


def test_submit_witness_receipt_builds_quality_contract(tmp_path: Path) -> None:
    _seed(tmp_path)
    payload = build_chatgpt_submit_witness_receipt(root=tmp_path)
    assert payload['surface_key'] == 'chatgpt'
    assert payload['witness_contract']['required_fields'] == ['submit_candidate_family']
    assert [item['quality'] for item in payload['quality_tiers']] == ['strong', 'usable', 'fragile', 'insufficient']


def test_submit_witness_receipt_grades_ready_blocked_and_prerequisite_cases(tmp_path: Path) -> None:
    _seed(tmp_path)
    ready = evaluate_chatgpt_submit_witness_receipt(
        {
            'host': 'chatgpt.com',
            'path': '/',
            'auth_posture': 'logged-out',
            'title': 'ChatGPT',
            'visible_text': ['ChatGPT', 'Text box'],
            'main_region_text': ['Main conversation'],
            'composer_candidate_family': 'accessible-textbox',
            'locator_strategy': 'getByRole(textbox)',
            'main_region_scoped': True,
            'actionability': {'visible': True, 'enabled': True, 'editable': True, 'stable': True, 'receives_events': True},
            'write_method': 'fill',
            'after_text': 'GLASSTTY-CHECKPOINT',
            'expected_probe_text': 'GLASSTTY-CHECKPOINT',
            'submit_candidate_family': 'visible-submit-button',
            'submit_method': 'click',
            'submit_actionability': {'visible': True, 'enabled': True, 'stable': True, 'receives_events': True},
            'submit_attempted': True,
            'composer_cleared_after_submit': True,
            'generation_cues': ['streaming-started'],
            'completion_cues': ['response-actions-visible'],
            'latest_turn_scope': 'main conversation region',
            'latest_turn_text': 'GLASSTTY-CHECKPOINT',
            'generation_timeline': ['submit', 'streaming', 'complete'],
            'expected_exact_reply': 'GLASSTTY-CHECKPOINT',
        },
        root=tmp_path,
    )
    assert ready['submit_quality'] == 'strong'
    assert ready['submit_readiness'] == 'ready'

    blocked = evaluate_chatgpt_submit_witness_receipt(
        {
            'host': 'chatgpt.com',
            'path': '/',
            'title': 'ChatGPT',
            'visible_text': ['ChatGPT', 'Text box'],
            'main_region_text': ['Main conversation'],
            'composer_candidate_family': 'accessible-textbox',
            'main_region_scoped': True,
            'actionability': {'visible': True, 'enabled': True, 'editable': True},
            'after_text': 'GLASSTTY-CHECKPOINT',
            'submit_candidate_family': 'visible-submit-button',
            'submit_actionability': {'visible': True, 'enabled': False},
            'submit_blockers': ['disabled'],
        },
        root=tmp_path,
    )
    assert blocked['submit_readiness'] == 'blocked'
    assert 'submit-disabled' in blocked['submit_blockers']

    blocked_by_composer = evaluate_chatgpt_submit_witness_receipt(
        {
            'host': 'chatgpt.com',
            'path': '/',
            'title': 'ChatGPT',
            'visible_text': ['ChatGPT', 'Text box'],
            'main_region_text': ['Main conversation'],
            'composer_candidate_family': 'contenteditable',
            'main_region_scoped': True,
            'actionability': {'visible': True, 'enabled': True, 'editable': True},
            'submit_candidate_family': 'keyboard-submit',
            'submit_actionability': {'composer_focused': True},
            'submit_attempted': True,
            'latest_turn_text': 'GLASSTTY-CHECKPOINT',
            'completion_cues': ['response-actions-visible'],
        },
        root=tmp_path,
    )
    assert blocked_by_composer['submit_readiness'] == 'blocked-by-composer'

    caution = evaluate_chatgpt_submit_witness_receipt(
        {
            'host': 'chatgpt.com',
            'path': '/',
            'title': 'ChatGPT Search',
            'visible_text': ['ChatGPT', 'Search the web'],
            'main_region_text': ['Main conversation'],
            'composer_candidate_family': 'accessible-textbox',
            'main_region_scoped': True,
            'actionability': {'visible': True, 'enabled': True, 'editable': True},
            'after_text': 'GLASSTTY-CHECKPOINT',
            'submit_candidate_family': 'keyboard-submit',
            'submit_method': 'press Enter',
            'submit_actionability': {'composer_focused': True},
            'submit_attempted': True,
            'generation_cues': ['streaming-started'],
            'completion_cues': ['response-actions-visible'],
            'latest_turn_scope': 'main conversation region',
            'latest_turn_text': 'GLASSTTY-CHECKPOINT',
            'expected_exact_reply': 'GLASSTTY-CHECKPOINT',
        },
        root=tmp_path,
    )
    assert caution['submit_readiness'] == 'ready-with-caution'
    assert 'keyboard-submit-fallback' in caution['caution_flags']


def test_submit_witness_receipt_capture_and_write_root(tmp_path: Path) -> None:
    _seed(tmp_path)
    output_dir = tmp_path / 'validation' / 'latest' / 'chatgpt-submit-witness-receipt'
    history_path = tmp_path / 'validation' / 'chatgpt-submit-witness-receipt-captures.json'
    payload = capture_chatgpt_submit_witness_receipt(root=tmp_path, output_dir=output_dir, history_path=history_path)
    assert (output_dir / 'chatgpt-submit-witness-receipt.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert payload['history_update']['capture_count_after_write'] == 1
    history = summarize_capture_history(history_path)
    assert history['capture_count'] == 1
    root_payload = write_root_chatgpt_submit_witness_receipt(root=tmp_path)
    assert (tmp_path / 'CHATGPT-SUBMIT-WITNESS-RECEIPT.json').exists()
    assert len(root_payload['submit_readiness_states']) == 8
